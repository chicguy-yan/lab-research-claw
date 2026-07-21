
"""Scenario B artifact checks prototype."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scenario_B_registry import CriterionResult


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _has_frontmatter_source_assets(content: str) -> bool:
    return content.startswith("---\n") and "source_assets:" in content


def _sections_present(content: str, required_sections: list[str]) -> list[str]:
    return [section for section in required_sections if section in content]


def artifact_preview(workspace_root: str | Path, relative_path: str, limit: int = 600) -> str:
    target = Path(workspace_root) / relative_path
    if not target.exists():
        return ""
    text = _read_text(target)
    return text[:limit]


def evaluate_artifact_rule(
    criterion_id: str,
    turn: dict[str, Any],
    workspace_root: str | Path,
) -> CriterionResult:
    score = 100.0
    reasons: list[str] = []
    previews: dict[str, Any] = {}

    for expected in turn.get("expected_artifacts", []):
        target = Path(workspace_root) / expected["path"]
        previews[expected["path"]] = {"exists": target.exists()}

        if not target.exists():
            score -= 60.0
            reasons.append(f"缺少预期 artifact：{expected['path']}")
            continue

        content = _read_text(target)
        hit_sections = _sections_present(content, list(expected.get("required_sections", [])))
        missed_sections = [section for section in expected.get("required_sections", []) if section not in hit_sections]
        previews[expected["path"]]["hit_sections"] = hit_sections

        if missed_sections:
            score -= min(30.0, 10.0 * len(missed_sections))
            reasons.append(f"artifact 缺少 section：{missed_sections}")

        if expected["path"].startswith("memory/") and turn.get("user_upload"):
            if not _has_frontmatter_source_assets(content):
                score -= 15.0
                reasons.append("memory artifact 缺少 source_assets frontmatter。")

    verdict = "pass" if score >= 80 else "partial" if score >= 60 else "fail"
    return CriterionResult(
        criterion_id=criterion_id,
        score=max(0.0, score),
        verdict=verdict,
        reasons=reasons,
        evidence=previews,
    )
