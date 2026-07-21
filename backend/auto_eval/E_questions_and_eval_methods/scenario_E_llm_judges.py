
"""Scenario E LLM-judge prompt builders prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_LIBRARY = {'E_PROMPT_EVIDENCE_EXPERT': '你是一名长期设计 benchmark、evaluator、数据集包架构与科研智能体协议的系统评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补系统设计。你要重点检查：回答是否真正站在 bridge/eval 视角而不是研究内容视角；是否清楚区分 package architecture、closure mapping、ecosystem map、test cases 与 downstream representative assets 的角色；是否把 loader / runner / scorer / llm-judge / report 等对象说清楚；是否明确哪些是 runtime 必须字段、哪些只是 analyst 注释；是否避免泛泛而谈的“平台化建议”。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'E_PROMPT_CLOSURE_EXPERT': '你是一名擅长把复杂 benchmark 设计收束成可实现协议的系统架构师。请判断这条回答能否作为 bridge/eval closure 的稳定对象：它是否真正形成了 read-order、priority、schema、prompt contract、failure mode 或 handoff 这类可执行对象；是否区分了 scenario/session/turn/criterion 层级；是否兼顾实现成本、覆盖度与可评分性；是否能够被 Codex 直接消费为实现输入。不要用自己的经验替模型补上尚未写出的系统约束，只按现有回答评分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'E_PROMPT_HALLUCINATION_EXPERT': '你是一名专门审查 evaluator 自身幻觉的系统评估专家。请重点盯住：模型是否把 bridge 层索引文件说成原始科研证据；是否把 schema / prompt contract 讲得很完整却没有落到 loader-runner-scorer 的真实接口；是否忽略 binary grounding、source-layer honesty、stop rule、跨 session memory 等关键 guardrail；是否把 benchmark 选型说成“覆盖全面”但其实没有能力覆盖矩阵；是否在没有 trace/文件依据的情况下臆测 closure mapping 中的字段含义。遇到这种系统性自我欺骗要严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。'}


def _has_binary_upload(turn: dict[str, Any]) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    return any(Path(p).suffix.lower() in binary_exts for p in turn.get("user_upload", []))


def choose_prompt_ref(turn: dict[str, Any]) -> str:
    if turn.get("expected_artifacts"):
        return "E_PROMPT_CLOSURE_EXPERT"
    if turn.get("binary_grounding_required") or _has_binary_upload(turn):
        return "E_PROMPT_HALLUCINATION_EXPERT"
    return "E_PROMPT_EVIDENCE_EXPERT"


def build_llm_prompt(
    session: dict[str, Any],
    turn: dict[str, Any],
    assistant_text: str,
    trace_summary: str = "",
    artifact_preview: str = "",
) -> str:
    ref = choose_prompt_ref(turn)
    base_prompt = PROMPT_LIBRARY[ref]
    payload = {
        "session_id": session["session_id"],
        "turn_id": turn["turn_id"],
        "user_input": turn["user_input"],
        "user_upload": turn.get("user_upload", []),
        "assistant_text": assistant_text,
        "trace_summary": trace_summary,
        "artifact_preview": artifact_preview,
        "content_focus": turn.get("content_focus", ""),
        "trace_focus": turn.get("trace_focus", ""),
        "llm_focus": turn.get("llm_focus", ""),
        "key_terms": turn.get("key_terms", []),
        "forbidden_terms": turn.get("forbidden_terms", []),
        "expected_artifacts": turn.get("expected_artifacts", []),
        "binary_grounding_required": turn.get("binary_grounding_required", False),
        "requires_workspace_memory_from_prior_sessions": turn.get("requires_workspace_memory_from_prior_sessions", False),
    }
    return base_prompt + "\n\n【评测输入】\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def parse_judge_response(raw_text: str) -> dict[str, Any]:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw_text[start:end + 1])
        raise


def judge_output_schema() -> dict[str, Any]:
    return {
        "score": "0-100 number",
        "verdict": "pass|partial|fail",
        "strengths": ["string"],
        "risks": ["string"],
        "missing": ["string"],
    }
