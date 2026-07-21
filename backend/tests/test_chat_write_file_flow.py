from __future__ import annotations

import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api.chat import router as chat_router
from graph.session_manager import SessionManager

HAS_LANGCHAIN_CORE = importlib.util.find_spec("langchain_core") is not None


def _seed_workspace(workspace: Path) -> None:
    (workspace / "memory" / "identity").mkdir(parents=True, exist_ok=True)
    (workspace / "context_trace").mkdir(parents=True, exist_ok=True)

    files = {
        "AGENTS.md": "# AGENTS\n",
        "SOUL.md": "# SOUL\n",
        "IDENTITY.md": "# IDENTITY\n",
        "USER.md": "# USER\n",
        "BOOTSTRAP.md": "# BOOTSTRAP\n",
        "MEMORY.md": "# MEMORY\n",
        "TOOLS.md": "# TOOLS\n",
        "memory/identity/project.md": "# PROJECT\n",
    }
    for relative, content in files.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class FakeWriteFileAgent:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    async def astream(self, messages: list[dict], system_prompt: str):
        from tools.write_file_tool import WriteFileTool

        path = "memory/concepts/hello.md"
        content = "# hello\n"
        tool = WriteFileTool(workspace_dir=self.workspace)
        yield {
            "event": "tool_start",
            "data": {
                "tool_call_id": "call-write-1",
                "tool": "write_file",
                "input": {"path": path, "content": content},
            },
        }
        output = tool._run(path, content)
        yield {
            "event": "tool_end",
            "data": {
                "tool_call_id": "call-write-1",
                "tool": "write_file",
                "output": output,
            },
        }
        yield {"event": "token", "data": {"content": f"工具返回：{output}"}}


class FakeHallucinatingAgent:
    async def astream(self, messages: list[dict], system_prompt: str):
        yield {
            "event": "token",
            "data": {"content": "已写 `memory/concepts/hello.md`"},
        }


class FakePromptCaptureAgent:
    def __init__(self) -> None:
        self.last_system_prompt = ""
        self.last_messages = []

    async def astream(self, messages: list[dict], system_prompt: str):
        self.last_system_prompt = system_prompt
        self.last_messages = messages
        yield {"event": "token", "data": {"content": "ok"}}


class ChatWriteFileFlowTests(unittest.TestCase):
    def _build_client(self, workspace: Path, agent_manager) -> TestClient:
        app = FastAPI()
        app.include_router(chat_router, prefix="/api")
        app.state.session_manager = SessionManager(workspace)
        app.state.agent_manager = agent_manager
        return TestClient(app)

    @unittest.skipUnless(HAS_LANGCHAIN_CORE, "langchain_core is required for write_file tool flow")
    def test_real_write_file_tool_creates_file_and_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            client = self._build_client(workspace, FakeWriteFileAgent(workspace))

            response = client.post(
                "/api/chat",
                json={"message": "write hello", "session_id": "s1"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertTrue((workspace / "memory" / "concepts" / "hello.md").exists())

            envelope = json.loads((workspace / "context_trace" / "s1.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["traces"][0]["tool"], "write_file")
            self.assertEqual(envelope["traces"][0]["status"], "completed")
            self.assertEqual(envelope["prompt"]["messages"][-1]["content"], "write hello")

    def test_plain_text_claim_does_not_create_file_or_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            client = self._build_client(workspace, FakeHallucinatingAgent())

            response = client.post(
                "/api/chat",
                json={"message": "write hello", "session_id": "s2"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertFalse((workspace / "memory" / "concepts" / "hello.md").exists())

            envelope = json.loads((workspace / "context_trace" / "s2.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["traces"], [])
            self.assertEqual(envelope["prompt"]["messages"][-1]["content"], "write hello")

    def test_prompt_context_fields_are_injected_into_system_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            agent = FakePromptCaptureAgent()
            client = self._build_client(workspace, agent)

            response = client.post(
                "/api/chat",
                json={
                    "message": "hello",
                    "session_id": "s3",
                    "route": "experiment",
                    "prompt_context": {
                        "session_type": "deep_research",
                        "workspace_mode": "planning",
                        "empty_value": "   ",
                        "nested": {
                            "goal": "trace coverage",
                            "blank": "",
                        },
                    },
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn('"route": "experiment"', agent.last_system_prompt)
            self.assertIn('"session_type": "deep_research"', agent.last_system_prompt)
            self.assertIn('"workspace_mode": "planning"', agent.last_system_prompt)
            self.assertIn('"goal": "trace coverage"', agent.last_system_prompt)
            self.assertNotIn("empty_value", agent.last_system_prompt)
            self.assertNotIn('"blank"', agent.last_system_prompt)
            self.assertEqual(agent.last_messages[-1]["content"], "hello")

            envelope = json.loads((workspace / "context_trace" / "s3.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["prompt"]["system_prompt"], agent.last_system_prompt)
            self.assertEqual(envelope["prompt"]["messages"], agent.last_messages)


if __name__ == "__main__":
    unittest.main()
