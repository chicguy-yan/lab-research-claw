
"""Scenario E hallucination flags and aggregate metrics prototype."""

from __future__ import annotations

import re
from typing import Any

SCENARIO_METRIC_DESCRIPTIONS = {'E_H1_schema_runtime_fidelity': '统计 scenario/session/turn/criterion 字段建议是否真正可被 loader-runner-scorer 消费，而非高层空话。', 'E_H2_bridge_source_honesty': '统计是否正确区分 bridge 层索引文件与原始科研证据，避免把 mapping 说成事实本身。', 'E_H3_priority_coverage_integrity': '统计 benchmark prioritization 是否同时覆盖 bootstrap、binary、artifact、memory、guardrail 等关键能力。', 'E_H4_cross_closure_failure_awareness': '统计是否识别 literature→experiment→writing 的断链点与误迁移模式。', 'E_H5_evaluator_self_guardrails': '统计是否把 binary_grounding_required、source-layer honesty、stop-rule、abstain 等 evaluator 自身护栏落到接口层。'}

ABSOLUTE_PATTERNS = [
    r"已经证明",
    r"必然",
    r"毫无疑问",
    r"直接说明",
    r"完全证实",
]

SOURCE_CONFUSION_PATTERNS = [
    r"原文已经明确",
    r"ppt 明确证明",
    r"docx 里已经给出最终条件",
]


def detect_unsupported_specificity(text: str) -> bool:
    numeric_fragments = re.findall(r"\d+(?:\.\d+)?\s?(?:mg|g|mL|mM|min|h|页|slide)", text or "", flags=re.IGNORECASE)
    return len(numeric_fragments) >= 5


def detect_absolute_overclaim(text: str) -> list[str]:
    hits = []
    for pattern in ABSOLUTE_PATTERNS:
        if re.search(pattern, text or ""):
            hits.append(pattern)
    return hits


def detect_source_confusion(text: str) -> list[str]:
    hits = []
    for pattern in SOURCE_CONFUSION_PATTERNS:
        if re.search(pattern, text or ""):
            hits.append(pattern)
    return hits


def detect_trace_free_binary_certainty(turn: dict[str, Any], trace_events: list[dict[str, Any]], assistant_text: str) -> bool:
    binary_exts = {".pdf", ".docx", ".pptx"}
    has_binary = any(turn.get("binary_grounding_required") for _ in [0]) or any(
        any(path.lower().endswith(ext) for ext in binary_exts)
        for path in turn.get("user_upload", [])
    )
    if not has_binary:
        return False
    blob = str(trace_events)
    used_binary_tool = ("terminal" in blob) or ("python_repl" in blob)
    certainty_hits = bool(re.search(r"第\d+页|第\d+张|明确证明|清楚显示", assistant_text or ""))
    return certainty_hits and not used_binary_tool


def detect_overtransfer(text: str) -> bool:
    patterns = [
        r"可以直接套用",
        r"已经在本体系中证明",
        r"直接迁移到 chlorite",
        r"可直接写进正文",
    ]
    return any(re.search(pattern, text or "", flags=re.IGNORECASE) for pattern in patterns)


def compute_turn_flags(turn: dict[str, Any], assistant_text: str, trace_events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "unsupported_specificity": detect_unsupported_specificity(assistant_text),
        "absolute_overclaim_hits": detect_absolute_overclaim(assistant_text),
        "source_confusion_hits": detect_source_confusion(assistant_text),
        "trace_free_binary_certainty": detect_trace_free_binary_certainty(turn, trace_events, assistant_text),
        "cross_system_overtransfer": detect_overtransfer(assistant_text),
    }


def aggregate_hallucination_metrics(turn_results: list[dict[str, Any]]) -> dict[str, Any]:
    total = max(1, len(turn_results))
    counters = {
        "unsupported_specificity": 0,
        "trace_free_binary_certainty": 0,
        "cross_system_overtransfer": 0,
        "absolute_overclaim_turns": 0,
        "source_confusion_turns": 0,
    }
    for result in turn_results:
        flags = result.get("hallucination_flags", {})
        counters["unsupported_specificity"] += int(bool(flags.get("unsupported_specificity")))
        counters["trace_free_binary_certainty"] += int(bool(flags.get("trace_free_binary_certainty")))
        counters["cross_system_overtransfer"] += int(bool(flags.get("cross_system_overtransfer")))
        counters["absolute_overclaim_turns"] += int(bool(flags.get("absolute_overclaim_hits")))
        counters["source_confusion_turns"] += int(bool(flags.get("source_confusion_hits")))
    return {
        "metric_descriptions": SCENARIO_METRIC_DESCRIPTIONS,
        "raw_counters": counters,
        "rates": {key: round(value / total, 4) for key, value in counters.items()},
    }
