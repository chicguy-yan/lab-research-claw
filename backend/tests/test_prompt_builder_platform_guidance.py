from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config as cfg
from graph.prompt_builder import PromptBuilder


class PromptBuilderPlatformGuidanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = cfg.DEFAULT_WORKSPACE_DIR
        self.builder = PromptBuilder(self.workspace)
        self.memory_map = {"layer1": [], "layer2": [], "layer3": [], "assets": []}

    def test_windows_platform_prefers_windows_commands(self) -> None:
        prompt = self.builder.build(
            memory_map=self.memory_map,
            metadata={"current_date": "2026-03-20", "platform": "win32"},
        )

        self.assertIn("Trusted platform hint: Windows", prompt)
        self.assertIn("`dir`, `where`, `type`, `findstr`", prompt)
        self.assertIn("dir /s /b skills", prompt)
        self.assertIn("findstr /n terminal AGENTS.md", prompt)
        self.assertNotIn("Prefer macOS terminal commands first", prompt)

    def test_macos_platform_prefers_macos_commands(self) -> None:
        prompt = self.builder.build(
            memory_map=self.memory_map,
            metadata={"current_date": "2026-03-20", "platform": "darwin"},
        )

        self.assertIn("Trusted platform hint: macOS", prompt)
        self.assertIn("`ls`, `find`, `sed`", prompt)
        self.assertIn("find skills -maxdepth 2 -type f", prompt)
        self.assertIn("sed -n 1,80p AGENTS.md", prompt)
        self.assertNotIn("Prefer Windows terminal commands first", prompt)

    def test_unknown_platform_includes_detection_command(self) -> None:
        prompt = self.builder.build(
            memory_map=self.memory_map,
            metadata={"current_date": "2026-03-20"},
        )

        self.assertIn("Trusted platform hint: unknown", prompt)
        self.assertIn('python -c "import platform; print(platform.system())"', prompt)
        self.assertIn("After detection, use Windows commands", prompt)
        self.assertIn("After detection, use macOS commands", prompt)


if __name__ == "__main__":
    unittest.main()