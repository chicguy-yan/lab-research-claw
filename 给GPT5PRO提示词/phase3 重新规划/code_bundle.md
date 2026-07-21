# Backend Code Bundle

以下内容打包自 `backend` 目录中的 3 个文件：

- `config.py`
- `api/chat.py`
- `graph/agent.py`

## `config.py`

```python
"""Global configuration for Experimental-Research-OpenClaw backend."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# --- Path constants ---
BASE_DIR = Path(__file__).resolve().parent
OPENCLAW_DIR = BASE_DIR / ".openclaw"
WORKSPACE_TEMPLATES_DIR = BASE_DIR / "workspace-templates"
DEFAULT_WORKSPACE_DIR = OPENCLAW_DIR / "workspace-default"
SKILLS_DIR = BASE_DIR / "skills"
CONFIG_JSON_PATH = BASE_DIR / "config.json"

# --- LLM configuration ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Embedding configuration (Phase 5, RAG) ---
EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# --- Optional API keys ---
BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")

# --- Server ---
DEFAULT_AGENT_ID = "default"


def load_config() -> dict:
    """Load persistent config from config.json. Returns empty dict if not found."""
    if CONFIG_JSON_PATH.exists():
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rag_mode": False}


def save_config(config: dict) -> None:
    """Save persistent config to config.json."""
    with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
```

## `api/chat.py`

```python
"""Chat API — POST /api/chat with SSE streaming.

The `done` event is sent here (not by AgentManager) after:
  1. Agent stream completes
  2. Messages are persisted to session file
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Phase 1 hardcoded system prompt (Phase 3 will use PromptBuilder)
SYSTEM_PROMPT = "You are a personal assistant running inside OpenClaw."


class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True


@router.post("/chat")
async def chat(body: ChatRequest, request: Request):
    """POST /api/chat — SSE streaming chat endpoint."""
    sm = request.app.state.session_manager
    am = request.app.state.agent_manager

    # Ensure session exists (auto-create if missing)
    sm.ensure_session(body.session_id, title="未命名会话")

    async def event_generator():
        # Load history
        history = sm.load_session_for_agent(body.session_id)

        # Collect full assistant text for persistence
        assistant_text = ""

        # Stream agent events
        async for event in am.astream(body.message, history, SYSTEM_PROMPT):
            event_type = event["event"]
            event_data = event["data"]

            # Accumulate assistant text from token events
            if event_type == "token":
                assistant_text += event_data.get("content", "")

            # Format as SSE
            yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        # Persist messages after stream completes
        sm.save_message(body.session_id, "user", body.message)
        if assistant_text:
            sm.save_message(body.session_id, "assistant", assistant_text)

        # Send done event (only here, not in AgentManager)
        done_data = {"session_id": body.session_id}
        yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

## `graph/agent.py`

```python
"""AgentManager — build LangChain Agent via create_agent and stream SSE events.

Uses `from langchain.agents import create_agent` (LangGraph runtime).
AgentManager only yields: token / tool_start / tool_end / new_response / error.
The `done` event is NOT emitted here — it is sent by api/chat.py after persistence.
"""

from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from langchain_openai import ChatOpenAI

import config as cfg

logger = logging.getLogger(__name__)


class AgentManager:
    """Build and stream a LangChain Agent per request."""

    def __init__(self) -> None:
        self.llm: ChatOpenAI | None = None
        self.tools: list = []

    def initialize(self) -> None:
        """Create the LLM instance from env config. Called once at startup."""
        if not cfg.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY is empty. Chat endpoint will return error events until configured."
            )
            self.llm = None
            self.tools = []
            return

        self.llm = ChatOpenAI(
            api_key=cfg.OPENAI_API_KEY,
            base_url=cfg.OPENAI_BASE_URL,
            model=cfg.OPENAI_MODEL,
            streaming=True,
        )
        # Phase 1: no tools. Phase 4 will register 6 core tools.
        self.tools = []
        logger.info(
            "AgentManager initialized — model=%s base_url=%s",
            cfg.OPENAI_MODEL,
            cfg.OPENAI_BASE_URL,
        )

    def _build_agent(self, system_prompt: str) -> Any:
        """Build a fresh agent graph for this request.

        Uses `create_agent` from langchain.agents (LangGraph runtime).
        Rebuilds every request so workspace/skills edits take immediate effect.
        """
        if self.llm is None:
            # lazy re-check in case env was updated after startup
            if cfg.OPENAI_API_KEY:
                self.initialize()

        if self.llm is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Please set it in backend/.env before calling /api/chat."
            )

        from langchain.agents import create_agent

        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        return agent

    async def astream(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
    ) -> AsyncGenerator[dict, None]:
        """Stream agent execution, yielding standardized SSE event dicts.

        Uses stream_mode="messages" for true token-by-token streaming.

        Yields:
            {"event": "token", "data": {"content": "..."}}
            {"event": "tool_start", "data": {"tool": "...", "input": "..."}}
            {"event": "tool_end", "data": {"tool": "...", "output": "..."}}
            {"event": "new_response", "data": {}}
            {"event": "error", "data": {"error": "..."}}

        Does NOT yield "done" — that is handled by api/chat.py.
        """
        try:
            agent = self._build_agent(system_prompt)

            # Build messages list: history + current user message
            messages = list(history) + [{"role": "user", "content": message}]

            prev_node = None

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
                            name = tc.get("name", "")
                            args = tc.get("args", "")
                            if name:  # Only emit tool_start when we have the name
                                yield {
                                    "event": "tool_start",
                                    "data": {
                                        "tool": name,
                                        "input": args,
                                    },
                                }
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
                        yield {
                            "event": "tool_end",
                            "data": {
                                "tool": tool_name,
                                "output": str(chunk.content)[:2000],
                            },
                        }

                prev_node = node_name

        except Exception as e:
            logger.exception("Agent stream error")
            yield {"event": "error", "data": {"error": str(e)}}
```
