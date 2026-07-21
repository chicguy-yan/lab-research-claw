from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.python_repl_tool import PythonREPLTool


class PythonREPLToolTests(unittest.TestCase):
    def test_executes_code_relative_to_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "memory" / "identity"
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "project.md").write_text("# project\n", encoding="utf-8")
            tool = PythonREPLTool(workspace_dir=workspace)

            result = tool._run("print(open('project.md').read().strip())", cwd="memory/identity")

            self.assertEqual(result.strip(), "# project")

    def test_rejects_cwd_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = PythonREPLTool(workspace_dir=workspace)

            result = tool._run("print('x')", cwd="../outside")

            self.assertIn("Path security violation", result)

    def test_schema_exposes_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = PythonREPLTool(workspace_dir=workspace)

            self.assertEqual(set(tool.args.keys()), {"code", "cwd"})


if __name__ == "__main__":
    unittest.main()
