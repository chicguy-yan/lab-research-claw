from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.read_file_tool import ReadFileTool


class ReadFileToolTests(unittest.TestCase):
    def test_reads_file_relative_to_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "memory" / "concepts"
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "hello.md").write_text("# hello\n", encoding="utf-8")
            tool = ReadFileTool(workspace_dir=workspace)

            result = tool._run("hello.md", cwd="memory/concepts")

            self.assertEqual(result, "# hello\n")

    def test_rejects_cwd_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = ReadFileTool(workspace_dir=workspace)

            result = tool._run("hello.md", cwd="../outside")

            self.assertIn("Path security violation", result)

    def test_schema_exposes_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = ReadFileTool(workspace_dir=workspace)

            self.assertEqual(set(tool.args.keys()), {"path", "cwd"})


if __name__ == "__main__":
    unittest.main()
