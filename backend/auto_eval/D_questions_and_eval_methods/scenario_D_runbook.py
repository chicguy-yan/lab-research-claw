
"""Scenario D runtime blueprint prototype."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scenario_D_artifact_checks import artifact_preview, evaluate_artifact_rule
from scenario_D_content_checks import evaluate_content_rule
from scenario_D_hallucination_checks import aggregate_hallucination_metrics, compute_turn_flags
from scenario_D_llm_judges import build_llm_prompt, choose_prompt_ref
from scenario_D_registry import build_default_criteria, load_scenario_document, summarize_registry
from scenario_D_trace_checks import evaluate_trace_rule


def build_runtime_blueprint() -> dict[str, Any]:
    scenario = load_scenario_document()
    return {
        "scenario_id": scenario["scenario_id"],
        "criteria_count": len(build_default_criteria()),
        "session_count": len(scenario["sessions"]),
        "turn_count": sum(len(session["dialogue"]) for session in scenario["sessions"]),
        "summary": summarize_registry(),
    }


def evaluate_trace_and_artifact(
    trace_criterion_id: str,
    artifact_criterion_id: str | None,
    turn: dict[str, Any],
    trace_events: list[dict[str, Any]],
    assistant_text: str,
    workspace_root: str | Path,
    created_paths: list[str] | None = None,
) -> list[dict[str, Any]]:
    created_paths = created_paths or []
    results = []
    trace_result = evaluate_trace_rule(trace_criterion_id, turn, trace_events, assistant_text, created_paths)
    results.append({
        "criterion_id": trace_result.criterion_id,
        "score": trace_result.score,
        "verdict": trace_result.verdict,
        "reasons": trace_result.reasons,
        "evidence": trace_result.evidence,
    })
    if artifact_criterion_id and turn.get("expected_artifacts"):
        artifact_result = evaluate_artifact_rule(artifact_criterion_id, turn, workspace_root)
        results.append({
            "criterion_id": artifact_result.criterion_id,
            "score": artifact_result.score,
            "verdict": artifact_result.verdict,
            "reasons": artifact_result.reasons,
            "evidence": artifact_result.evidence,
        })
    return results


def evaluate_turn(
    session: dict[str, Any],
    turn: dict[str, Any],
    assistant_text: str,
    trace_events: list[dict[str, Any]],
    workspace_root: str | Path,
    created_paths: list[str] | None = None,
) -> dict[str, Any]:
    created_paths = created_paths or []
    session_index = next(
        idx for idx, candidate in enumerate(load_scenario_document()["sessions"], start=1)
        if candidate["session_id"] == session["session_id"]
    )
    base = "D-S{:03d}-T{:02d}".format(session_index, turn["turn_id"])

    content_result = evaluate_content_rule(base + "-C1", turn, assistant_text)
    trace_result = evaluate_trace_rule(base + "-C2", turn, trace_events, assistant_text, created_paths)
    artifact_result = None
    if turn.get("expected_artifacts"):
        artifact_result = evaluate_artifact_rule(base + "-C2A", turn, workspace_root)

    preview_chunks = []
    for expected in turn.get("expected_artifacts", []):
        preview = artifact_preview(workspace_root, expected["path"])
        if preview:
            preview_chunks.append(preview)

    prompt = build_llm_prompt(
        session=session,
        turn=turn,
        assistant_text=assistant_text,
        trace_summary=str(trace_events[:8]),
        artifact_preview="\n\n".join(preview_chunks),
    )
    hallucination_flags = compute_turn_flags(turn, assistant_text, trace_events)

    result = {
        "content_result": {
            "criterion_id": content_result.criterion_id,
            "score": content_result.score,
            "verdict": content_result.verdict,
            "reasons": content_result.reasons,
        },
        "trace_result": {
            "criterion_id": trace_result.criterion_id,
            "score": trace_result.score,
            "verdict": trace_result.verdict,
            "reasons": trace_result.reasons,
        },
        "artifact_result": None if artifact_result is None else {
            "criterion_id": artifact_result.criterion_id,
            "score": artifact_result.score,
            "verdict": artifact_result.verdict,
            "reasons": artifact_result.reasons,
        },
        "llm_job": {
            "criterion_id": base + "-C3",
            "prompt_ref": choose_prompt_ref(turn),
            "prompt_text": prompt,
        },
        "hallucination_flags": hallucination_flags,
        "provisional_turn_score": round(
            (
                content_result.score
                + trace_result.score
                + (artifact_result.score if artifact_result is not None else trace_result.score)
            ) / 3.0,
            2,
        ),
    }
    return result


def summarize_scenario(turn_results: list[dict[str, Any]]) -> dict[str, Any]:
    total = max(1, len(turn_results))
    provisional_avg = round(sum(item.get("provisional_turn_score", 0.0) for item in turn_results) / total, 2)
    hallucination = aggregate_hallucination_metrics(turn_results)
    return {
        "runtime_blueprint": build_runtime_blueprint(),
        "turn_count": len(turn_results),
        "provisional_avg": provisional_avg,
        "hallucination_summary": hallucination,
    }


if __name__ == "__main__":
    print(build_runtime_blueprint())
