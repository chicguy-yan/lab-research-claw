from __future__ import annotations

from typing import Any


class HeuristicJudge:
    def __init__(self, mode: str = "heuristic") -> None:
        self.mode = mode

    def evaluate(
        self,
        llm_job: dict[str, Any],
        turn: dict[str, Any],
        assistant_text: str,
        trace_events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if self.mode == "off":
            return {
                "criterion_id": llm_job.get("criterion_id", "judge-off"),
                "score": 50.0,
                "verdict": "skipped",
                "strengths": [],
                "risks": ["LLM judge disabled"],
                "missing": [],
                "raw_text": "",
            }

        assistant_lower = assistant_text.lower()
        key_terms = [term for term in turn.get("key_terms", []) if term]
        forbidden_terms = [term for term in turn.get("forbidden_terms", []) if term]

        matched_key_terms = [term for term in key_terms if term.lower() in assistant_lower]
        missing_key_terms = [term for term in key_terms if term.lower() not in assistant_lower][:5]
        triggered_forbidden = [term for term in forbidden_terms if term.lower() in assistant_lower]

        score = 100.0
        score -= min(35.0, 7.0 * len(missing_key_terms))
        score -= min(45.0, 15.0 * len(triggered_forbidden))

        trace_tools = {event.get("tool", "") for event in trace_events}
        if turn.get("binary_grounding_required"):
            has_grounding_tool = bool(trace_tools.intersection({"read_file", "terminal", "python_repl"}))
            uncertainty_markers = ("不确定", "需回原文", "需要核对", "无法确认", "可能")
            if not has_grounding_tool and not any(marker in assistant_text for marker in uncertainty_markers):
                score -= 20.0

        if turn.get("expected_artifacts") and "memory/" not in assistant_text:
            score -= 10.0

        score = max(0.0, round(score, 2))
        verdict = "pass" if score >= 80 else "partial" if score >= 60 else "fail"

        strengths = []
        if matched_key_terms:
            strengths.append(f"命中了 {len(matched_key_terms)} 个关键术语")
        if trace_tools:
            strengths.append(f"检测到工具使用: {', '.join(sorted(item for item in trace_tools if item))}")

        risks = []
        if triggered_forbidden:
            risks.append(f"命中了禁用术语: {triggered_forbidden}")
        if missing_key_terms:
            risks.append(f"缺失关键术语: {missing_key_terms}")

        return {
            "criterion_id": llm_job.get("criterion_id", "judge-heuristic"),
            "score": score,
            "verdict": verdict,
            "strengths": strengths,
            "risks": risks,
            "missing": missing_key_terms,
            "raw_text": llm_job.get("prompt_text", "")[:1000],
        }
