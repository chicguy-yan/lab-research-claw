
"""Scenario C LLM-judge prompt builders prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_LIBRARY = {'C_PROMPT_EVIDENCE_EXPERT': '你是一名长期负责环境催化实验设计、SOP 审核与研究生 task board 把关的评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补完实验条件。你要重点检查：回答是否把 stage2 合成、PMSO/ClO2、EPR、quencher、CeO2 合成等内容真正翻译成可执行 task；是否清楚区分原始记录、SOP、通用方法文档与当前体系的既定条件；是否避免编造浓度、加样量、容器、时序、仪器条件；是否解释了每一步要回答的机制问题；是否在信息不足时诚实提示‘需回 SOP / 回 docx / 回记录’。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'C_PROMPT_CLOSURE_EXPERT': '你是一名擅长把实验主线压缩成 Task/Pack 的材料科研项目经理。请判断这条回答能否被当作 experiment closure 的稳定对象：它是否有清晰的任务目标、执行顺序、依赖关系、回退路线与结果判读；是否真的把实验对象落到 checklist / matrix / task board，而不是写成机理散文；是否保留了条件边界与误判风险；是否足够具体到研究生日常可以照着执行或继续补充。请严格只基于给定材料评分，不要用你自己的实验经验替模型补缺。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。', 'C_PROMPT_HALLUCINATION_EXPERT': '你是一名专门审查科研实验规划幻觉的化学评估专家。请重点盯住四类风险：第一，模型是否捏造了称量量、浓度、加样量、时间、容器、仪器设置等具体条件；第二，是否把通用方法参考（尤其 docx、通用 SOP）直接当成当前 chlorite 体系的既定条件；第三，是否在没有 trace 解析二进制文档的情况下，装作已经看到了其中的细节；第四，是否忽略了依赖关系、把失败回退路线说成可选装饰。只要出现明显编条件、伪造可执行细节、或不诚实地越过信息边界，就应严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。'}


def _has_binary_upload(turn: dict[str, Any]) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    return any(Path(p).suffix.lower() in binary_exts for p in turn.get("user_upload", []))


def choose_prompt_ref(turn: dict[str, Any]) -> str:
    if turn.get("expected_artifacts"):
        return "C_PROMPT_CLOSURE_EXPERT"
    if turn.get("binary_grounding_required") or _has_binary_upload(turn):
        return "C_PROMPT_HALLUCINATION_EXPERT"
    return "C_PROMPT_EVIDENCE_EXPERT"


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
