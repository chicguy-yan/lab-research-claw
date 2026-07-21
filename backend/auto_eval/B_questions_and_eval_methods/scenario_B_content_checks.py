
"""Scenario B content-rule checks prototype."""

from __future__ import annotations

import re
from typing import Any

from scenario_B_registry import CriterionResult


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _match_count(text: str, items: list[str]) -> int:
    normalized = normalize_text(text)
    return sum(1 for item in items if item and item.lower() in normalized)


def _extract_forbidden_hits(text: str, forbidden_terms: list[str]) -> list[str]:
    normalized = normalize_text(text)
    return [term for term in forbidden_terms if term and term.lower() in normalized]


def _has_prior_memory_signal(text: str) -> bool:
    normalized = normalize_text(text)
    signals = [
        "memory/",
        "前面",
        "之前",
        "上一个",
        "概念卡",
        "task",
        "pack",
        "上一轮",
        "已沉淀",
    ]
    return any(signal in normalized for signal in signals)


def evaluate_content_rule(criterion_id: str, turn: dict[str, Any], assistant_text: str) -> CriterionResult:
    key_terms = list(turn.get("key_terms", []))
    forbidden_terms = list(turn.get("forbidden_terms", []))
    required_hits = min(len(key_terms), 3) if key_terms else 0
    hit_count = _match_count(assistant_text, key_terms)
    forbidden_hits = _extract_forbidden_hits(assistant_text, forbidden_terms)

    score = 100.0
    reasons: list[str] = []

    if required_hits and hit_count < required_hits:
        missing = required_hits - hit_count
        score -= min(45.0, 15.0 * missing)
        reasons.append(f"关键术语命中不足：需要至少 {required_hits} 个，实际 {hit_count} 个。")
    else:
        reasons.append(f"关键术语命中 {hit_count} 个，达到阈值。")

    if forbidden_hits:
        score -= min(40.0, 15.0 * len(forbidden_hits))
        reasons.append(f"命中禁词/危险表述：{forbidden_hits}")

    if turn.get("requires_workspace_memory_from_prior_sessions") and not _has_prior_memory_signal(assistant_text):
        score -= 15.0
        reasons.append("该 turn 预期复用 prior workspace memory，但回答中缺少明显的前序产物/记忆引用痕迹。")

    if turn.get("expected_artifacts"):
        for expected in turn["expected_artifacts"]:
            filename = expected["path"].split("/")[-1]
            if filename.lower() not in normalize_text(assistant_text):
                reasons.append(f"回答未显式提及目标 artifact 名称 {filename}；允许继续通过 artifact 检查补偿。")
                score -= 5.0

    verdict = "pass" if score >= 80 else "partial" if score >= 60 else "fail"
    return CriterionResult(
        criterion_id=criterion_id,
        score=max(0.0, score),
        verdict=verdict,
        reasons=reasons,
        evidence={
            "key_terms": key_terms,
            "forbidden_terms": forbidden_terms,
            "content_focus": turn.get("content_focus", ""),
        },
    )


def batch_preview(turn: dict[str, Any], assistant_text: str) -> dict[str, Any]:
    return {
        "hit_count": _match_count(assistant_text, list(turn.get("key_terms", []))),
        "forbidden_hits": _extract_forbidden_hits(assistant_text, list(turn.get("forbidden_terms", []))),
        "needs_prior_memory": bool(turn.get("requires_workspace_memory_from_prior_sessions")),
        "has_prior_memory_signal": _has_prior_memory_signal(assistant_text),
    }
