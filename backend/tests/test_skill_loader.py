"""Phase 5.1 - SkillLoader unit tests.

Coverage:
1. Snapshot includes all merged skill metadata, including source and runtime_path
2. System skill mirror under workspace/skills/_system is created once and not overwritten
3. Workspace registry and workspace-private skill are merged into the catalog
4. Snapshot file is refreshed when generated content changes
5. Missing system registry degrades safely
6. PromptBuilder.build() remains backward compatible with skills_snapshot
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config as cfg
from graph.prompt_builder import PromptBuilder
from graph.skill_loader import SkillLoader


class SkillLoaderTests(unittest.TestCase):
    """SkillLoader functional tests."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.workspace = Path(self.tmp) / "workspace"
        self.workspace.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapshot_contains_merged_skill_metadata(self) -> None:
        loader = SkillLoader(self.workspace)
        snapshot = loader.get_snapshot()

        self.assertIn("# Skills Snapshot", snapshot)
        self.assertIn("source", snapshot)
        self.assertIn("runtime_path", snapshot)

        for skill in loader.registry.get("skills", []):
            self.assertIn(skill["id"], snapshot, f"snapshot missing {skill['id']}")
            self.assertIn(skill["name"], snapshot, f"snapshot missing {skill['name']}")
            self.assertIn(skill["source"], snapshot, f"snapshot missing source for {skill['id']}")
            self.assertIn(skill["runtime_path"], snapshot, f"snapshot missing runtime path for {skill['id']}")

        self.assertIn("skills/_system/skill_creator/SKILL.md", snapshot)

    def test_system_skill_mirror_does_not_overwrite_existing_file(self) -> None:
        custom_content = "# My Custom System Skill\nworkspace override copy"
        mirrored_path = self.workspace / "skills" / "_system" / "synthesis_checklist" / "SKILL.md"
        mirrored_path.parent.mkdir(parents=True, exist_ok=True)
        mirrored_path.write_text(custom_content, encoding="utf-8")

        SkillLoader(self.workspace)

        actual = mirrored_path.read_text(encoding="utf-8")
        self.assertEqual(actual, custom_content, "existing mirrored system skill was overwritten")

    def test_workspace_skill_registry_is_merged_without_hiding_system_skills(self) -> None:
        skills_dir = self.workspace / "skills"
        private_skill_path = skills_dir / "custom_protocol" / "SKILL.md"
        private_skill_path.parent.mkdir(parents=True, exist_ok=True)
        private_skill_path.write_text("# Custom Protocol\n", encoding="utf-8")

        registry = {
            "version": "0.1",
            "skills": [
                {
                    "id": "custom_protocol",
                    "name": "自定义流程",
                    "category": "analysis",
                    "entry": "skills/custom_protocol/SKILL.md",
                    "triggers": ["自定义流程"],
                    "use_cases": "测试 workspace 私有 skill",
                    "preferred_routes": ["experiment"],
                }
            ],
        }
        (skills_dir / "registry.json").write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        loader = SkillLoader(self.workspace)
        snapshot = loader.get_snapshot()

        merged = loader.registry["skills"]
        self.assertTrue(any(skill["source"] == "system" for skill in merged))
        workspace_skill = next(skill for skill in merged if skill["id"] == "custom_protocol")
        self.assertEqual(workspace_skill["source"], "workspace")
        self.assertEqual(workspace_skill["runtime_path"], "skills/custom_protocol/SKILL.md")
        self.assertIn("custom_protocol", snapshot)
        self.assertIn("skills/custom_protocol/SKILL.md", snapshot)
        self.assertIn("skill_creator", snapshot)

    def test_snapshot_file_refreshes_when_content_changes(self) -> None:
        loader = SkillLoader(self.workspace)
        snapshot1 = loader.get_snapshot()

        snapshot_path = self.workspace / "skills" / "SKILLS_SNAPSHOT.md"
        self.assertTrue(snapshot_path.exists(), "first call should write snapshot")

        snapshot_path.write_text("modified content", encoding="utf-8")
        snapshot2 = loader.get_snapshot()
        self.assertEqual(snapshot1, snapshot2)
        self.assertEqual(snapshot_path.read_text(encoding="utf-8"), snapshot1)

        refreshed = loader.get_snapshot(force_refresh=True)
        self.assertEqual(refreshed, snapshot1)
        self.assertEqual(snapshot_path.read_text(encoding="utf-8"), snapshot1)

    def test_legacy_workspace_registry_entry_without_entry_is_still_loaded(self) -> None:
        skills_dir = self.workspace / "skills"
        legacy_skill_path = skills_dir / "legacy_skill" / "SKILL.md"
        legacy_skill_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_skill_path.write_text("# Legacy Skill\n", encoding="utf-8")

        registry = {
            "version": "1.0",
            "skills": [
                {
                    "id": "legacy_skill",
                    "name": "旧版技能",
                    "category": "analysis",
                    "description": "旧结构里只有 description，没有 entry/use_cases",
                    "triggers": ["旧版技能"],
                }
            ],
        }
        (skills_dir / "registry.json").write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        loader = SkillLoader(self.workspace)
        legacy_skill = next(skill for skill in loader.registry["skills"] if skill["id"] == "legacy_skill")

        self.assertEqual(legacy_skill["source"], "workspace")
        self.assertEqual(legacy_skill["runtime_path"], "skills/legacy_skill/SKILL.md")
        self.assertEqual(legacy_skill["use_cases"], "旧结构里只有 description，没有 entry/use_cases")

    def test_missing_system_registry_returns_empty_snapshot(self) -> None:
        original_skills_dir = cfg.SKILLS_DIR
        cfg.SKILLS_DIR = Path(self.tmp) / "nonexistent_skills"
        try:
            loader = SkillLoader(self.workspace)
            snapshot = loader.get_snapshot()
            self.assertEqual(snapshot, "", "missing system registry should return empty snapshot")
            self.assertEqual(loader.registry["skills"], [])
            self.assertTrue((self.workspace / "skills" / "registry.json").exists())
        finally:
            cfg.SKILLS_DIR = original_skills_dir

    def test_system_skills_are_mirrored_to_workspace_namespace(self) -> None:
        loader = SkillLoader(self.workspace)

        system_skills = [skill for skill in loader.registry["skills"] if skill["source"] == "system"]
        self.assertTrue(system_skills, "expected at least one system skill")

        for skill in system_skills:
            src = cfg.SKILLS_DIR.parent / skill["entry"]
            dst = self.workspace / skill["runtime_path"]
            self.assertTrue(src.exists(), f"system source missing for {skill['id']}")
            self.assertTrue(dst.exists(), f"system mirror missing for {skill['id']}")


class PromptBuilderBackwardCompatTests(unittest.TestCase):
    """PromptBuilder.build() backward compatibility tests."""

    def test_build_without_skills_snapshot(self) -> None:
        workspace = cfg.DEFAULT_WORKSPACE_DIR
        pb = PromptBuilder(workspace)
        memory_map = {"layer1": [], "layer2": [], "layer3": [], "assets": []}
        prompt = pb.build(memory_map=memory_map, metadata={"current_date": "2026-03-12"})
        self.assertIn("OpenClaw", prompt)
        self.assertNotIn("Skills Menu", prompt)

    def test_build_with_skills_snapshot(self) -> None:
        workspace = cfg.DEFAULT_WORKSPACE_DIR
        pb = PromptBuilder(workspace)
        memory_map = {"layer1": [], "layer2": [], "layer3": [], "assets": []}
        snapshot = "## analysis\n### `csv_plot_kobs` - CSV plotting"
        prompt = pb.build(
            memory_map=memory_map,
            skills_snapshot=snapshot,
            metadata={"current_date": "2026-03-12"},
        )
        self.assertIn("Skills Menu", prompt)
        self.assertIn("csv_plot_kobs", prompt)

    def test_skills_snapshot_block_between_control_plane_and_memory_map(self) -> None:
        workspace = cfg.DEFAULT_WORKSPACE_DIR
        pb = PromptBuilder(workspace)
        memory_map = {"layer1": [], "layer2": [], "layer3": [], "assets": []}
        snapshot = "SKILLS_MARKER_FOR_TEST"
        prompt = pb.build(
            memory_map=memory_map,
            skills_snapshot=snapshot,
            metadata={"current_date": "2026-03-12"},
        )
        control_plane_pos = prompt.find("# Project Context")
        skills_pos = prompt.find("SKILLS_MARKER_FOR_TEST")
        memory_map_pos = prompt.find("# Memory Map")
        self.assertGreater(skills_pos, control_plane_pos)
        self.assertLess(skills_pos, memory_map_pos)


if __name__ == "__main__":
    unittest.main()
