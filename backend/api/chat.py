"""Chat API - POST /api/chat with SSE streaming."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.runtime_context import get_registry, get_runtime
import config as cfg
from graph.context_orchestrator import ContextOrchestrator
from graph.prompt_builder import PromptBuilder
from graph.skill_loader import SkillLoader
from graph.trace_writer import TraceWriter
from runtime.bootstrap_runner import BOOTSTRAP_SESSION_ID, BootstrapRunner

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class AttachmentInfo(BaseModel):
    """Front-end metadata for uploaded attachments."""

    saved_path: str
    file_type: str = ""
    summary: str = ""


class ChatRequest(BaseModel):
    message: str
    session_id: str
    workspace_id: str = ""
    stream: bool = True
    route: str = ""
    prompt_context: dict[str, Any] = Field(default_factory=dict)
    attachments: list[AttachmentInfo] = Field(default_factory=list)


def _clean_prompt_context(value: Any) -> Any:
    """Recursively remove empty values from trusted prompt metadata."""
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, Mapping):
        cleaned_dict: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                continue
            cleaned_item = _clean_prompt_context(item)
            if cleaned_item is not None:
                cleaned_dict[key] = cleaned_item
        return cleaned_dict or None
    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            cleaned_item = _clean_prompt_context(item)
            if cleaned_item is not None:
                cleaned_list.append(cleaned_item)
        return cleaned_list or None
    return value


def _build_prompt_metadata(body: ChatRequest) -> dict[str, Any]:
    """Build trusted metadata injected into the system prompt."""
    metadata: dict[str, Any] = {
        "platform": "darwin",
        "timezone": "Asia/Shanghai",
        "language": "zh-CN",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    if body.route.strip():
        metadata["route"] = body.route.strip()

    cleaned_prompt_context = _clean_prompt_context(body.prompt_context) or {}
    if isinstance(cleaned_prompt_context, dict):
        metadata.update(cleaned_prompt_context)

    if body.attachments:
        metadata["attachments"] = [
            {"path": a.saved_path, "type": a.file_type, "summary": a.summary}
            for a in body.attachments
        ]

    return metadata


def _build_model_prompt_payload(system_prompt: str, history: list[dict], message: str) -> dict[str, Any]:
    """Build the exact prompt payload passed into the agent runtime."""
    return {
        "system_prompt": system_prompt,
        "messages": list(history) + [{"role": "user", "content": message}],
    }


def _attachment_payloads(body: ChatRequest) -> list[dict[str, str]]:
    return [
        {
            "saved_path": item.saved_path,
            "file_type": item.file_type,
            "summary": item.summary,
        }
        for item in body.attachments
    ]


def _build_persisted_user_message(body: ChatRequest) -> str:
    user_msg = body.message
    if body.attachments:
        att_lines = ["[附件已上传]"]
        for item in body.attachments:
            att_lines.append(f"- {item.saved_path} ({item.file_type}, {item.summary})")
        att_lines.append("")
        user_msg = "\n".join(att_lines) + user_msg
    return user_msg


@router.post("/chat")
async def chat(body: ChatRequest, request: Request):
    """POST /api/chat SSE streaming endpoint."""
    registry = get_registry(request)
    rt = get_runtime(request, body.workspace_id or None)
    shared = registry.get_shared()
    sm = rt.session_manager
    workspace_dir = rt.workspace_dir
    manifest = registry.load_manifest(rt.workspace_id)
    bootstrap_status = manifest.get("bootstrap_status", "completed")
    is_bootstrap_route = body.route.strip().lower() == "bootstrap"
    bootstrap_runner: BootstrapRunner | None = None

    if is_bootstrap_route:
        if body.session_id != BOOTSTRAP_SESSION_ID:
            raise HTTPException(400, f"Bootstrap chat requires session_id={BOOTSTRAP_SESSION_ID}")
        if bootstrap_status != "running":
            raise HTTPException(409, f"Bootstrap chat requires bootstrap_status=running, got {bootstrap_status}")
        bootstrap_runner = BootstrapRunner(rt.workspace_id, workspace_dir)
        try:
            bootstrap_runner.record_first_answer(body.message, _attachment_payloads(body))
        except Exception as exc:
            registry.update_bootstrap_status(rt.workspace_id, "failed", error=str(exc))
            raise HTTPException(500, f"Failed to record bootstrap answer: {exc}")
    elif bootstrap_status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Workspace bootstrap is not completed: {bootstrap_status}. Use route=bootstrap first.",
        )

    if shared.llm is None:
        if cfg.has_valid_openai_api_key():
            registry.initialize_shared()
            shared = registry.get_shared()
        if shared.llm is None:
            raise HTTPException(
                status_code=503,
                detail=shared.config_error or "OPENAI_API_KEY is not configured.",
            )

    sm.ensure_session(body.session_id, title="未命名会话")
    all_tools = registry.get_all_tools(rt.workspace_id)

    async def event_generator():
        try:
            orchestrator = ContextOrchestrator(workspace_dir)
            memory_map = orchestrator.generate_memory_map(body.message)

            skill_loader = SkillLoader(workspace_dir)
            skills_snapshot = skill_loader.get_snapshot()

            prompt_builder = PromptBuilder(workspace_dir)
            metadata = _build_prompt_metadata(body)
            system_prompt = prompt_builder.build(
                memory_map=memory_map,
                skills_snapshot=skills_snapshot,
                metadata=metadata,
            )

            history = sm.load_session_for_agent(body.session_id)
            prompt_payload = _build_model_prompt_payload(system_prompt, history, body.message)

            assistant_text = ""
            tool_calls = []
            active_tool_calls = {}

            from langchain.agents import create_agent

            agent = create_agent(
                model=shared.llm,
                tools=all_tools,
                system_prompt=system_prompt,
            )

            prev_node = None
            tool_call_buffer = {}

            async for chunk, metadata in agent.astream(
                {"messages": prompt_payload["messages"]},
                stream_mode="messages",
            ):
                node_name = metadata.get("langgraph_node", "")
                msg_type = type(chunk).__name__

                if node_name == "model":
                    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                        for tc in chunk.tool_call_chunks:
                            call_id = tc.get("id")
                            if not call_id and tc.get("name") and tc.get("index") is not None:
                                call_id = f"{tc['name']}:{tc['index']}"
                            if not call_id:
                                continue
                            if call_id not in tool_call_buffer:
                                tool_call_buffer[call_id] = {"name": None, "args": ""}
                            if tc.get("name"):
                                tool_call_buffer[call_id]["name"] = tc["name"]
                            if tc.get("args"):
                                tool_call_buffer[call_id]["args"] += tc["args"]
                            if tool_call_buffer[call_id]["name"] and tool_call_buffer[call_id]["args"]:
                                try:
                                    import json as _json

                                    parsed_args = _json.loads(tool_call_buffer[call_id]["args"])
                                except json.JSONDecodeError:
                                    continue
                                event_data = {
                                    "tool_call_id": call_id,
                                    "tool": tool_call_buffer[call_id]["name"],
                                    "input": parsed_args,
                                }
                                active_tool_calls[call_id] = {
                                    "tool_call_id": call_id,
                                    "tool": tool_call_buffer[call_id]["name"],
                                    "args": parsed_args,
                                    "timestamp": datetime.now().isoformat(),
                                    "status": "running",
                                }
                                yield f"event: tool_start\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                    elif chunk.content:
                        if prev_node == "tools":
                            yield f"event: new_response\ndata: {json.dumps({}, ensure_ascii=False)}\n\n"
                        assistant_text += chunk.content
                        yield f"event: token\ndata: {json.dumps({'content': chunk.content}, ensure_ascii=False)}\n\n"

                elif node_name == "tools":
                    if msg_type == "ToolMessage" and hasattr(chunk, "content"):
                        tool_name = chunk.name if hasattr(chunk, "name") else "unknown"
                        call_id = chunk.tool_call_id if hasattr(chunk, "tool_call_id") else None
                        event_data = {
                            "tool_call_id": call_id,
                            "tool": tool_name,
                            "output": str(chunk.content)[:2000],
                        }
                        if call_id and call_id in active_tool_calls:
                            active_tool_calls[call_id]["result"] = event_data["output"]
                            active_tool_calls[call_id]["status"] = "completed"
                            tool_calls.append(active_tool_calls[call_id])
                            del active_tool_calls[call_id]
                        else:
                            tool_calls.append(
                                {
                                    "tool_call_id": call_id,
                                    "tool": tool_name,
                                    "args": None,
                                    "timestamp": datetime.now().isoformat(),
                                    "status": "completed_unmatched",
                                    "result": event_data["output"],
                                }
                            )
                        if call_id and call_id in tool_call_buffer:
                            del tool_call_buffer[call_id]
                        yield f"event: tool_end\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

                prev_node = node_name

            sm.save_message(body.session_id, "user", _build_persisted_user_message(body))
            if assistant_text:
                sm.save_message(body.session_id, "assistant", assistant_text)

            trace_writer = TraceWriter(workspace_dir)
            trace_writer.write_trace(body.session_id, tool_calls, prompt=prompt_payload)

            if bootstrap_runner is not None:
                bootstrap_runner.complete()
                registry.update_bootstrap_status(rt.workspace_id, "completed")

            done_data = {"session_id": body.session_id}
            yield f"event: done\ndata: {json.dumps(done_data)}\n\n"
        except Exception as exc:
            logger.exception("Chat route failed for workspace %s", rt.workspace_id)
            if bootstrap_runner is not None:
                registry.update_bootstrap_status(rt.workspace_id, "failed", error=str(exc))
            yield f"event: error\ndata: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

