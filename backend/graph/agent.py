"""AgentManager — build LangChain Agent via create_agent and stream SSE events.

Uses `from langchain.agents import create_agent` (LangGraph runtime).
AgentManager only yields: token / tool_start / tool_end / new_response / error.
The `done` event is NOT emitted here — it is sent by api/chat.py after persistence.

Phase 3+4: Registers 5 core tools (terminal/python_repl/read_file/write_file/fetch_url)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, AsyncGenerator

from langchain_openai import ChatOpenAI

import config as cfg
from tools.fetch_url_tool import FetchURLTool
from tools.python_repl_tool import PythonREPLTool
from tools.read_file_tool import ReadFileTool
from tools.terminal_tool import TerminalTool
from tools.write_file_tool import WriteFileTool

logger = logging.getLogger(__name__)


class AgentManager:
    """Build and stream a LangChain Agent per request."""

    def __init__(self) -> None:
        self.llm: ChatOpenAI | None = None
        self.tools: list = []
        self.workspace_dir: Path | None = None
        self.config_error: str = ""

    def initialize(self, workspace_dir: Path = None) -> None:
        """Create the LLM instance and tools from env config. Called once at startup.

        Args:
            workspace_dir: Workspace directory for tools (Phase 3+4)
        """
        self.config_error = cfg.openai_api_key_error()
        if self.config_error:
            logger.warning("%s", self.config_error)
            self.llm = None
            self.tools = []
            return

        self.llm = ChatOpenAI(
            api_key=cfg.OPENAI_API_KEY,
            base_url=cfg.OPENAI_BASE_URL,
            model=cfg.OPENAI_MODEL,
            streaming=True,
        )

        # Phase 3+4: Register 5 core tools
        if workspace_dir:
            self.workspace_dir = workspace_dir
            self.tools = [
                TerminalTool(workspace_dir=workspace_dir),
                PythonREPLTool(workspace_dir=workspace_dir),
                ReadFileTool(workspace_dir=workspace_dir),
                WriteFileTool(workspace_dir=workspace_dir),
                FetchURLTool(),
            ]
            logger.info("AgentManager: Registered 5 core tools")
        else:
            self.tools = []

        logger.info(
            "AgentManager initialized — model=%s base_url=%s tools=%d",
            cfg.OPENAI_MODEL,
            cfg.OPENAI_BASE_URL,
            len(self.tools),
        )

    def _build_agent(self, system_prompt: str) -> Any:
        """Build a fresh agent graph for this request.

        Uses `create_agent` from langchain.agents (LangGraph runtime).
        Rebuilds every request so workspace/skills edits take immediate effect.
        """
        if self.llm is None:
            # lazy re-check in case env was updated after startup
            if cfg.has_valid_openai_api_key():
                self.initialize()
            else:
                self.config_error = cfg.openai_api_key_error()

        if self.llm is None:
            raise RuntimeError(self.config_error or "OPENAI_API_KEY is not configured.")

        from langchain.agents import create_agent

        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        return agent

    async def astream(
        self,
        messages: list[dict],
        system_prompt: str,
    ) -> AsyncGenerator[dict, None]:
        """Stream agent execution, yielding standardized SSE event dicts.

        Uses stream_mode="messages" for true token-by-token streaming.

        Yields:
            {"event": "token", "data": {"content": "..."}}
            {"event": "tool_start", "data": {"tool_call_id": "...", "tool": "...", "input": {...}}}
            {"event": "tool_end", "data": {"tool_call_id": "...", "tool": "...", "output": "..."}}
            {"event": "new_response", "data": {}}
            {"event": "error", "data": {"error": "..."}}

        Does NOT yield "done" — that is handled by api/chat.py.
        """
        try:
            agent = self._build_agent(system_prompt)

            prev_node = None

            # Buffer to aggregate tool_call_chunks by tool_call_id
            tool_call_buffer = {}  # {tool_call_id: {"name": str, "args": str}}

            async for chunk, metadata in agent.astream(
                {"messages": messages},
                stream_mode="messages",
            ):
                node_name = metadata.get("langgraph_node", "")
                msg_type = type(chunk).__name__

                if node_name == "model":
                    # AIMessageChunk from the model node
                    # Check for tool_calls first
                    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                        for tc in chunk.tool_call_chunks:
                            call_id = tc.get("id")
                            if not call_id and tc.get("name") and tc.get("index") is not None:
                                # Some providers omit chunk id during streaming but later
                                # report tool_call_id as "<name>:<index>" on ToolMessage.
                                call_id = f"{tc['name']}:{tc['index']}"
                            if not call_id:
                                continue

                            # Initialize buffer entry if not exists
                            if call_id not in tool_call_buffer:
                                tool_call_buffer[call_id] = {"name": None, "args": ""}

                            # Accumulate name and args
                            if tc.get("name"):
                                tool_call_buffer[call_id]["name"] = tc["name"]
                            if tc.get("args"):
                                tool_call_buffer[call_id]["args"] += tc["args"]

                            # Check if this chunk marks completion (LangChain sends index field)
                            # When we have both name and args, emit tool_start
                            if tool_call_buffer[call_id]["name"] and tool_call_buffer[call_id]["args"]:
                                try:
                                    import json
                                    parsed_args = json.loads(tool_call_buffer[call_id]["args"])
                                except json.JSONDecodeError:
                                    # Args still incomplete, wait for more chunks
                                    continue

                                # Complete tool call received, emit tool_start
                                yield {
                                    "event": "tool_start",
                                    "data": {
                                        "tool_call_id": call_id,
                                        "tool": tool_call_buffer[call_id]["name"],
                                        "input": parsed_args,
                                    },
                                }
                                # Keep in buffer for tool_end matching

                    elif chunk.content:
                        # Text token from assistant
                        if prev_node == "tools":
                            yield {"event": "new_response", "data": {}}
                        yield {
                            "event": "token",
                            "data": {"content": chunk.content},
                        }

                elif node_name == "tools":
                    # Tool execution result (ToolMessage)
                    if msg_type == "ToolMessage" and hasattr(chunk, "content"):
                        tool_name = chunk.name if hasattr(chunk, "name") else "unknown"
                        # Extract tool_call_id from ToolMessage
                        call_id = chunk.tool_call_id if hasattr(chunk, "tool_call_id") else None

                        yield {
                            "event": "tool_end",
                            "data": {
                                "tool_call_id": call_id,
                                "tool": tool_name,
                                "output": str(chunk.content)[:2000],
                            },
                        }

                        # Clean up buffer
                        if call_id and call_id in tool_call_buffer:
                            del tool_call_buffer[call_id]

                prev_node = node_name

        except Exception as e:
            logger.exception("Agent stream error")
            yield {"event": "error", "data": {"error": str(e)}}
