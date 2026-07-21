"""Skill Loader — 生成 Skills Snapshot 菜单，并合并 system/workspace skills。

Phase 5.1 职责：
- 读取 backend/skills/registry.json（system skills）
- 读取 workspace/skills/registry.json（workspace skills）
- 生成 SKILLS_SNAPSHOT.md 菜单摘要（包含所有技能的元信息）
- 确保 backend skills 被复制到 workspace/skills/_system/<skill_id>/SKILL.md
- 不负责：trigger 匹配、route 排序、自动注入完整 SKILL.md
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillRecord:
    """运行时统一 skill 记录。"""

    id: str
    name: str
    source: str
    category: str
    entry: str
    runtime_path: str
    triggers: list[str]
    use_cases: str
    preferred_routes: list[str]
    origin_registry: str
    overrides: str = ""


class SkillLoader:
    """Skills 管理：生成 snapshot 菜单，确保 SKILL.md 在 workspace 可访问。"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.skills_dir = self.workspace_dir / "skills"
        self.workspace_registry_path = self.skills_dir / "registry.json"

        self._ensure_workspace_registry()
        self.skills = self._load_all_skills()
        self.registry = {"version": "0.3", "skills": [asdict(skill) for skill in self.skills]}
        self._sync_system_skills_to_workspace(self.skills)

    def _ensure_workspace_registry(self) -> None:
        """确保 workspace 有私有 skills registry。"""
        if self.workspace_registry_path.exists():
            return

        self.workspace_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.workspace_registry_path.write_text(
            json.dumps({"version": "0.1", "skills": []}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _load_registry_file(self, path: Path) -> dict:
        """加载 registry；异常或缺失时降级为空。"""
        if not path.exists():
            return {"skills": []}

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"skills": []}

    def _load_all_registries(self) -> list[tuple[str, Path, dict]]:
        """按固定顺序加载全部 registry。"""
        from config import SKILLS_DIR

        return [
            ("system", SKILLS_DIR / "registry.json", self._load_registry_file(SKILLS_DIR / "registry.json")),
            ("workspace", self.workspace_registry_path, self._load_registry_file(self.workspace_registry_path)),
        ]

    def _normalize_registry(self, source: str, registry_path: Path, registry: dict) -> list[SkillRecord]:
        """归一化单个 registry。"""
        normalized: list[SkillRecord] = []

        for raw_skill in registry.get("skills", []):
            skill_id = str(raw_skill.get("id", "")).strip()
            name = str(raw_skill.get("name", "")).strip()
            entry = str(raw_skill.get("entry", "")).strip()
            if source == "workspace" and not entry and skill_id:
                entry = f"skills/{skill_id}/SKILL.md"
            if not skill_id or not name or not entry:
                continue

            if source == "system":
                runtime_path = f"skills/_system/{skill_id}/SKILL.md"
            else:
                runtime_path = entry if entry.startswith("skills/") else f"skills/{skill_id}/SKILL.md"

            normalized.append(
                SkillRecord(
                    id=skill_id,
                    name=name,
                    source=source,
                    category=str(raw_skill.get("category", "misc")).strip() or "misc",
                    entry=entry,
                    runtime_path=runtime_path,
                    triggers=[str(item) for item in raw_skill.get("triggers", []) if str(item).strip()],
                    use_cases=(
                        str(raw_skill.get("use_cases", "")).strip()
                        or str(raw_skill.get("description", "")).strip()
                    ),
                    preferred_routes=[
                        str(item) for item in raw_skill.get("preferred_routes", []) if str(item).strip()
                    ],
                    origin_registry=str(registry_path),
                    overrides=str(raw_skill.get("overrides", "")).strip(),
                )
            )

        return normalized

    def _merge_skills(self, skill_lists: list[list[SkillRecord]]) -> list[SkillRecord]:
        """合并多个来源的 skills，默认并存不覆盖。"""
        merged = [skill for skills in skill_lists for skill in skills]
        return sorted(merged, key=lambda skill: (skill.category, skill.id, skill.source))

    def _load_all_skills(self) -> list[SkillRecord]:
        """读取并归一化全部来源 skills。"""
        normalized_lists = [
            self._normalize_registry(source, registry_path, registry)
            for source, registry_path, registry in self._load_all_registries()
        ]
        return self._merge_skills(normalized_lists)

    def _system_skill_source_path(self, skill: SkillRecord) -> Path:
        """返回 system skill 的模板源路径。"""
        from config import SKILLS_DIR

        return (SKILLS_DIR.parent / skill.entry).resolve()

    def _workspace_skill_path(self, skill: SkillRecord) -> Path:
        """返回 skill 在 workspace 内的运行时路径。"""
        return self.workspace_dir / skill.runtime_path

    def _sync_system_skills_to_workspace(self, skills: list[SkillRecord]) -> None:
        """将 system skills 镜像到 workspace 命名空间目录。"""
        for skill in skills:
            if skill.source != "system":
                continue

            src = self._system_skill_source_path(skill)
            dst = self._workspace_skill_path(skill)
            if src.exists() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    def _build_snapshot(self, skills: list[SkillRecord]) -> str:
        """构建 snapshot 文本。"""
        if not skills:
            return ""

        lines = ["# Skills Snapshot", ""]
        lines.append("以下技能可通过 read_file 工具读取；请优先使用每条 skill 的 runtime_path。")
        lines.append("")

        by_category: dict[str, list[SkillRecord]] = {}
        for skill in skills:
            by_category.setdefault(skill.category, []).append(skill)

        for category in sorted(by_category):
            lines.append(f"## {category}")
            for skill in by_category[category]:
                lines.append(f"### `{skill.id}` — {skill.name}")
                lines.append(f"- **source**: {skill.source}")
                lines.append(f"- **runtime_path**: {skill.runtime_path}")
                if skill.triggers:
                    lines.append(f"- **triggers**: {', '.join(skill.triggers)}")
                if skill.use_cases:
                    lines.append(f"- **use_cases**: {skill.use_cases}")
                if skill.preferred_routes:
                    lines.append(
                        f"- **preferred_routes** (仅供参考): {', '.join(skill.preferred_routes)}"
                    )
                lines.append("")

        return "\n".join(lines)

    def get_snapshot(self, force_refresh: bool = False) -> str:
        """
        生成菜单型技能摘要（SKILLS_SNAPSHOT），每轮注入 prompt。

        写盘策略：
        - 每轮生成 snapshot 文本并返回（用于注入 prompt）
        - 默认只在 workspace/skills/SKILLS_SNAPSHOT.md 不存在时写盘
        - 若 force_refresh=True，则强制覆盖写盘
        """
        snapshot = self._build_snapshot(self.skills)
        if not snapshot:
            return ""

        snapshot_path = self.skills_dir / "SKILLS_SNAPSHOT.md"
        existing_snapshot = ""
        if snapshot_path.exists():
            try:
                existing_snapshot = snapshot_path.read_text(encoding="utf-8")
            except OSError:
                existing_snapshot = ""

        if force_refresh or existing_snapshot != snapshot:
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(snapshot, encoding="utf-8")

        return snapshot
