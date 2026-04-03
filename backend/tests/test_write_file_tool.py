from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.write_file_tool import WriteFileTool


class WriteFileToolTests(unittest.TestCase):
    def test_writes_file_relative_to_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "memory" / "concepts").mkdir(parents=True, exist_ok=True)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("hello.md", "# hello\n", cwd="memory/concepts")

            self.assertEqual(result, "File written successfully: memory/concepts/hello.md")
            self.assertEqual(
                (workspace / "memory" / "concepts" / "hello.md").read_text(encoding="utf-8"),
                "# hello\n",
            )

    def test_writes_nested_file_under_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("memory/concepts/hello.md", "# hello\n")

            self.assertEqual(result, "File written successfully: memory/concepts/hello.md")
            self.assertEqual(
                (workspace / "memory" / "concepts" / "hello.md").read_text(encoding="utf-8"),
                "# hello\n",
            )

    def test_writes_skill_file_under_workspace_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("skills/demo_skill/SKILL.md", "# Demo Skill\n")

            self.assertEqual(result, "File written successfully: skills/demo_skill/SKILL.md")
            self.assertEqual(
                (workspace / "skills" / "demo_skill" / "SKILL.md").read_text(encoding="utf-8"),
                "# Demo Skill\n",
            )

    def test_writes_root_control_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("IDENTITY.md", "# Identity\n")

            self.assertEqual(result, "File written successfully: IDENTITY.md")
            self.assertEqual((workspace / "IDENTITY.md").read_text(encoding="utf-8"), "# Identity\n")

    def test_rejects_non_whitelisted_root_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("notes.txt", "nope")

            self.assertIn("Path security violation", result)
            self.assertFalse((workspace / "notes.txt").exists())

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            result = tool._run("../outside.md", "nope")

            self.assertIn("Path security violation", result)
            self.assertFalse((workspace.parent / "outside.md").exists())

    def test_schema_exposes_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = WriteFileTool(workspace_dir=workspace)

            self.assertEqual(set(tool.args.keys()), {"path", "content", "cwd", "source_assets"})


if __name__ == "__main__":
    unittest.main()
