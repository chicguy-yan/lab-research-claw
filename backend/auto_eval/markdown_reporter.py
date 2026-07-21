from __future__ import annotations

from collections import defaultdict
from typing import Any


def build_scenario_summary_markdown(
    run_id: str,
    scenario: dict[str, Any],
    scenario_summary: dict[str, Any],
    turn_results: list[dict[str, Any]],
) -> str:
    lines = [
        f"# {scenario.get('scenario_name', scenario['scenario_id'])} Summary",
        "",
        f"- run_id: `{run_id}`",
        f"- scenario_id: `{scenario['scenario_id']}`",
        f"- turn_count: `{len(turn_results)}`",
        f"- average_score: `{scenario_summary.get('average_score', 0):.2f}`",
        f"- pass_rate: `{scenario_summary.get('pass_rate', 0):.2%}`",
        f"- temporary_turn_count: `{scenario_summary.get('temporary_turn_count', 0)}`",
        "",
        "## Hallucination Metrics",
    ]

    hallucination = scenario_summary.get("hallucination_summary", {})
    if hallucination:
        for key, value in sorted(hallucination.items()):
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Session Scores"])
    session_scores: dict[str, list[float]] = defaultdict(list)
    for item in turn_results:
        session_scores[item["session_id"]].append(item["final_turn_score"])
    for session_id, values in session_scores.items():
        average = sum(values) / max(1, len(values))
        lines.append(f"- {session_id}: `{average:.2f}`")

    failed = [item for item in turn_results if item["final_turn_score"] < 80]
    lines.extend(["", "## Lowest Turns"])
    if failed:
        for item in sorted(failed, key=lambda row: row["final_turn_score"])[:10]:
            lines.append(
                f"- {item['session_id']} / turn {item['turn_id']}: "
                f"`{item['final_turn_score']:.2f}` ({item['judge_result']['verdict']})"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Artifact Outputs"])
    seen_artifacts = False
    for item in turn_results:
        for artifact in item.get("expected_artifacts", []):
            seen_artifacts = True
            lines.append(f"- {artifact['path']}")
    if not seen_artifacts:
        lines.append("- none")

    lines.extend(["", "## Temporary Dir Activity"])
    temporary_turns = [
        item for item in turn_results if item.get("temporary_dir_snapshot", {}).get("file_count", 0) > 0
    ]
    if temporary_turns:
        for item in temporary_turns[:10]:
            snapshot = item.get("temporary_dir_snapshot", {})
            sample = ", ".join(snapshot.get("session_relative_files", [])[:3]) or "none"
            lines.append(
                f"- {item['session_id']} / turn {item['turn_id']}: "
                f"`{snapshot.get('file_count', 0)}` files ({sample})"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Temporary Dir Checks"])
    temp_checks = [item for item in turn_results if item.get("temporary_result")]
    if temp_checks:
        for item in temp_checks[:10]:
            temporary_result = item["temporary_result"]
            lines.append(
                f"- {item['session_id']} / turn {item['turn_id']}: "
                f"`{temporary_result['score']:.2f}` ({temporary_result['verdict']})"
            )
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def build_overall_report_markdown(run_id: str, overall_summary: dict[str, Any]) -> str:
    lines = [
        f"# Auto Eval Report `{run_id}`",
        "",
        f"- overall_score: `{overall_summary.get('overall_score', 0):.2f}`",
        f"- completed_turns: `{overall_summary.get('completed_turns', 0)}`",
        "",
        "## Scenario Scoreboard",
    ]
    for scenario in overall_summary.get("scenario_summaries", []):
        lines.append(
            f"- {scenario['scenario_id']}: "
            f"`{scenario.get('average_score', 0):.2f}` "
            f"(pass_rate `{scenario.get('pass_rate', 0):.2%}`, temporary_turns `{scenario.get('temporary_turn_count', 0)}`)"
        )
    return "\n".join(lines) + "\n"
