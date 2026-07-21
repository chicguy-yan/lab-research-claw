
"""Scenario B trace checks prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scenario_B_registry import CriterionResult


BINARY_TOOLS = {"terminal", "python_repl"}
READ_LIKE_TOOLS = {"read_file", "terminal", "python_repl"}
MEMORY_MARKERS = ("memory/", "concepts/", "tasks/", "packs/")


def _tool_name(event: dict[str, Any]) -> str:
    return str(
        event.get("tool_name")
        or event.get("tool")
        or event.get("name")
        or event.get("tool_call_name")
        or ""
    )


def _event_text(event: dict[str, Any]) -> str:
    return json.dumps(event, ensure_ascii=False)


def _has_binary_upload(turn: dict[str, Any]) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    return any(Path(p).suffix.lower() in binary_exts for p in turn.get("user_upload", []))


def _uploads_mentioned_in_trace(turn: dict[str, Any], trace_events: list[dict[str, Any]]) -> bool:
    uploads = [Path(p).name for p in turn.get("user_upload", [])]
    trace_blob = " ".join(_event_text(event) for event in trace_events)
    return any(name in trace_blob for name in uploads)


def _has_tool(trace_events: list[dict[str, Any]], candidates: set[str]) -> bool:
    return any(_tool_name(event) in candidates for event in trace_events)


def _has_memory_read(trace_events: list[dict[str, Any]]) -> bool:
    trace_blob = " ".join(_event_text(event) for event in trace_events)
    return any(marker in trace_blob for marker in MEMORY_MARKERS)


def evaluate_trace_rule(
    criterion_id: str,
    turn: dict[str, Any],
    trace_events: list[dict[str, Any]],
    assistant_text: str = "",
    created_paths: list[str] | None = None,
) -> CriterionResult:
    created_paths = created_paths or []
    score = 100.0
    reasons: list[str] = []

    if turn.get("expected_artifacts"):
        expected_paths = [artifact["path"] for artifact in turn["expected_artifacts"]]
        if not _has_tool(trace_events, {"write_file"}):
            score -= 35.0
            reasons.append("预期本 turn 生成 artifact，但 trace 中没有出现 write_file。")
        if expected_paths and not any(path in created_paths for path in expected_paths):
            score -= 25.0
            reasons.append(f"created_paths 未包含预期 artifact：{expected_paths}")
        if not _has_tool(trace_events, READ_LIKE_TOOLS) and turn.get("user_upload"):
            score -= 15.0
            reasons.append("存在上传源文件，但 trace 中缺少明显读取行为。")
        if turn.get("user_upload") and not _uploads_mentioned_in_trace(turn, trace_events):
            score -= 10.0
            reasons.append("trace 中缺少对本轮上传文件名的明显引用。")
    elif turn.get("binary_grounding_required") or _has_binary_upload(turn):
        if not _has_tool(trace_events, BINARY_TOOLS):
            score -= 40.0
            reasons.append("该 turn 需要 binary grounding，但 trace 中没有 terminal/python_repl。")
        if turn.get("user_upload") and not _uploads_mentioned_in_trace(turn, trace_events):
            score -= 20.0
            reasons.append("binary turn 的 trace 中没有明显出现上传文件名。")
        if not _has_tool(trace_events, READ_LIKE_TOOLS):
            score -= 10.0
            reasons.append("binary turn 里缺少明显读取/解析动作。")
    else:
        if turn.get("user_upload") and not _has_tool(trace_events, READ_LIKE_TOOLS):
            score -= 25.0
            reasons.append("存在上传文件，但 trace 中未见 read_file/terminal/python_repl 等读取动作。")
        if turn.get("requires_workspace_memory_from_prior_sessions") and not _has_memory_read(trace_events):
            score -= 15.0
            reasons.append("该 turn 依赖 prior workspace memory，但 trace 中缺少明显 memory 读取痕迹。")

    if "Error:" in assistant_text or "无法读取" in assistant_text:
        reasons.append("回答中出现了读取受限/错误提示；需要结合业务预期判断是否合理。")

    verdict = "pass" if score >= 80 else "partial" if score >= 60 else "fail"
    return CriterionResult(
        criterion_id=criterion_id,
        score=max(0.0, score),
        verdict=verdict,
        reasons=reasons,
        evidence={
            "trace_focus": turn.get("trace_focus", ""),
            "tool_count": len(trace_events),
            "created_paths": created_paths,
        },
    )
