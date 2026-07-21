
"""Scenario B LLM-judge prompt builders prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_LIBRARY = {'B_PROMPT_EVIDENCE_EXPERT': '你是一名长期从事环境催化、亚氯酸盐活化、高价金属氧物种机理研究的评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】进行评分，不要凭领域常识替模型补答案。你要重点检查五件事：第一，回答是否严格区分论文原文、个人笔记、以及从旁支体系借来的启发；第二，是否真正抓住 Co3O4/chlorite 基线机制的 OAT、PCET、ClO2/Co(IV)=O 双物种与 pH/质子增强等关键关系；第三，是否把 selective oxidation、PMS/Fenton-like、Ce 电子结构论文的迁移边界说清楚；第四，是否在证据不足时主动保留限定词；第五，是否围绕用户要求的对象（概念卡、对照表、handoff）组织内容。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'B_PROMPT_CLOSURE_EXPERT': '你是一名擅长把复杂文献线索收束为 Concept/Pack 的材料科研导师。现在你的任务不是判断回答“像不像总结”，而是判断它能否作为 literature closure 的稳定对象被后续 session 复用。请重点看：对象是否真正完成了用户要求的收束（例如共同机制/关键差异/边界/禁区）；是否保留了 source-layer 与不确定性；是否明确哪些结论已稳定、哪些仍需回原文核对；是否避免把旁支体系启发包装成已验证事实；是否足以在后续写作、问答、handoff 中直接使用。仍然只基于给定材料评分，不允许替模型脑补未说出的合理内容。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'B_PROMPT_HALLUCINATION_EXPERT': '你是一名专门审查科研智能体幻觉风险的化学材料评估专家。请重点审查：模型是否对 PDF 中的具体机理、表征、结论做了无依据的细节臆测；是否把笔记里的压缩说法误当成原文直接结论；是否把 d-band / PMS / Fenton-like / Ce 旁支论文的结果直接说成 chlorite 体系已证实的事实；是否使用了“已经证明、必然导致、直接说明”等过强表述而没有给出限定；是否忽略了二进制文件需要进一步解析这一事实。请以严格保守的标准评分：有明显过度断言、伪造页结论、或混淆 source layer 时要重罚。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。'}


def _has_binary_upload(turn: dict[str, Any]) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    return any(Path(p).suffix.lower() in binary_exts for p in turn.get("user_upload", []))


def choose_prompt_ref(turn: dict[str, Any]) -> str:
    if turn.get("expected_artifacts"):
        return "B_PROMPT_CLOSURE_EXPERT"
    if turn.get("binary_grounding_required") or _has_binary_upload(turn):
        return "B_PROMPT_HALLUCINATION_EXPERT"
    return "B_PROMPT_EVIDENCE_EXPERT"


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
