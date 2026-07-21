
"""Scenario D LLM-judge prompt builders prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_LIBRARY = {'D_PROMPT_EVIDENCE_EXPERT': '你是一名长期指导博士论文、开题答辩、组会汇报与科研写作 pack 设计的导师型评审。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补写作结构。你要重点检查：回答是否真正围绕 pack-quality 交付件组织；是否区分最终稿、工作文档、中间版本、排版示例、背景论文等不同 authority level；是否能够把 thesis / proposal / group meeting / storyboard / layout rule 转成可复用的交付对象；是否在二进制 PPTX/DOCX/PDF 信息不足时保持诚实；是否避免把版本草稿说成稳定结论。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'D_PROMPT_CLOSURE_EXPERT': '你是一名擅长把科研写作碎片收束成 Pack 的高级编辑与课题导师。请判断这条回答是否已经形成可复用的 writing closure 对象：是否清晰指向某个交付件（storyline、gap map、revision matrix、layout rule、handoff）；是否含有足够的结构、权威来源排序、风险提示与下一步动作；是否能够在后续 thesis / proposal / group meeting 中直接复用；是否避免只做普通摘要而没有 pack 的组织价值。不要根据经验替模型补出未写出的结构，要严格按现有回答给分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'D_PROMPT_HALLUCINATION_EXPERT': '你是一名专门审查科研写作与二进制文档幻觉的评估专家。请重点检查：模型是否在未真正解析 PPTX/DOCX/PDF 的情况下伪造页数、版式、章节内容或版本差异；是否把工作文档和最终稿混为一谈；是否把排版/风格参考误写成科学主张来源；是否把旁支 bridge 或背景论文过度包装成 thesis 主证；是否用‘最终稿明确说明’‘这页 PPT 证明了’等强断言而没有真实依据。出现明显二进制臆测、版本混淆或 authority level 失真时应严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。'}


def _has_binary_upload(turn: dict[str, Any]) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    return any(Path(p).suffix.lower() in binary_exts for p in turn.get("user_upload", []))


def choose_prompt_ref(turn: dict[str, Any]) -> str:
    if turn.get("expected_artifacts"):
        return "D_PROMPT_CLOSURE_EXPERT"
    if turn.get("binary_grounding_required") or _has_binary_upload(turn):
        return "D_PROMPT_HALLUCINATION_EXPERT"
    return "D_PROMPT_EVIDENCE_EXPERT"


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
