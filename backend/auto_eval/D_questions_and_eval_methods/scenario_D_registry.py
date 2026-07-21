
"""Scenario D registry and criterion catalog prototype."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

SCENARIO_ID = "scenario_D"
QUESTION_FILE = Path(__file__).with_name("D_scenario_questions.json")
CRITERIA_PER_TURN = 3


class CriterionKind(str, Enum):
    RULE = "rule"
    TRACE = "trace"
    ARTIFACT = "artifact"
    LLM_JUDGE = "llm_judge"


@dataclass
class TurnAddress:
    scenario_id: str
    session_id: str
    turn_id: int
    session_index: int


@dataclass
class CriterionSpec:
    criterion_id: str
    address: TurnAddress
    kind: CriterionKind
    title: str
    max_score: int = 100
    implementation_entrypoint: str = ""
    prompt_ref: str | None = None
    tags: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class CriterionResult:
    criterion_id: str
    score: float
    verdict: str
    reasons: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


def load_scenario_document() -> dict[str, Any]:
    payload = json.loads(QUESTION_FILE.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("Scenario question file must be a single-item list.")
    return payload[0]


def iter_sessions() -> Iterable[tuple[int, dict[str, Any]]]:
    scenario = load_scenario_document()
    for idx, session in enumerate(scenario["sessions"], start=1):
        yield idx, session


def iter_turns() -> Iterable[tuple[int, dict[str, Any], dict[str, Any]]]:
    for session_index, session in iter_sessions():
        for turn in session["dialogue"]:
            yield session_index, session, turn


def all_declared_uploads() -> set[str]:
    uploads: set[str] = set()
    for _, _, turn in iter_turns():
        uploads.update(turn.get("user_upload", []))
    return uploads


def expected_file_coverage() -> set[str]:
    scenario = load_scenario_document()
    return set(scenario["file_coverage_assertion"]["all_source_files"])


def validate_file_coverage() -> list[str]:
    expected = expected_file_coverage()
    actual = all_declared_uploads()
    return sorted(expected - actual)


def count_binary_turns() -> int:
    binary_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".xls"}
    count = 0
    for _, _, turn in iter_turns():
        uploads = turn.get("user_upload", [])
        if turn.get("binary_grounding_required") or any(Path(p).suffix.lower() in binary_exts for p in uploads):
            count += 1
    return count


def count_prior_memory_turns() -> int:
    return sum(1 for _, _, turn in iter_turns() if turn.get("requires_workspace_memory_from_prior_sessions"))


def expected_criteria_count() -> int:
    return sum(1 for _ in iter_turns()) * CRITERIA_PER_TURN


def _secondary_kind(turn: dict[str, Any]) -> CriterionKind:
    if turn.get("expected_artifacts"):
        return CriterionKind.ARTIFACT
    return CriterionKind.TRACE


def build_default_criteria() -> list[CriterionSpec]:
    from scenario_D_llm_judges import choose_prompt_ref

    criteria: list[CriterionSpec] = []
    for session_index, session, turn in iter_turns():
        address = TurnAddress(
            scenario_id=SCENARIO_ID,
            session_id=session["session_id"],
            turn_id=turn["turn_id"],
            session_index=session_index,
        )
        base = "D-S{:03d}-T{:02d}".format(session_index, turn["turn_id"])
        criteria.append(
            CriterionSpec(
                criterion_id=base + "-C1",
                address=address,
                kind=CriterionKind.RULE,
                title="content-rule",
                implementation_entrypoint="scenario_D_content_checks.evaluate_content_rule",
                tags=list(turn.get("eval_tags", [])) + ["rule"],
                notes=turn.get("content_focus", ""),
            )
        )
        criteria.append(
            CriterionSpec(
                criterion_id=base + "-C2",
                address=address,
                kind=_secondary_kind(turn),
                title="trace-or-artifact",
                implementation_entrypoint="scenario_D_runbook.evaluate_trace_and_artifact",
                tags=list(turn.get("eval_tags", [])) + ["trace_or_artifact"],
                notes=turn.get("trace_focus", ""),
            )
        )
        criteria.append(
            CriterionSpec(
                criterion_id=base + "-C3",
                address=address,
                kind=CriterionKind.LLM_JUDGE,
                title="llm-judge",
                implementation_entrypoint="scenario_D_llm_judges.build_llm_prompt",
                prompt_ref=choose_prompt_ref(turn),
                tags=list(turn.get("eval_tags", [])) + ["llm_judge"],
                notes=turn.get("llm_focus", ""),
            )
        )
    expected_count = expected_criteria_count()
    if len(criteria) != expected_count:
        raise AssertionError(
            f"Scenario D should expose {expected_count} criteria, got {len(criteria)}"
        )
    missing = validate_file_coverage()
    if missing:
        raise AssertionError(f"Scenario D is missing declared uploads for: {missing}")
    return criteria


def summarize_registry() -> dict[str, Any]:
    scenario = load_scenario_document()
    return {
        "scenario_id": scenario["scenario_id"],
        "session_count": len(scenario["sessions"]),
        "turn_count": sum(len(session["dialogue"]) for session in scenario["sessions"]),
        "criterion_count": len(build_default_criteria()),
        "binary_turn_count": count_binary_turns(),
        "prior_memory_turn_count": count_prior_memory_turns(),
        "missing_uploads": validate_file_coverage(),
    }


if __name__ == "__main__":
    print(json.dumps(summarize_registry(), ensure_ascii=False, indent=2))
