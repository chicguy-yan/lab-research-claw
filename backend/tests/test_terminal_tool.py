from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.terminal_tool import TerminalTool


class TerminalToolTests(unittest.TestCase):
    def test_runs_command_in_relative_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "memory" / "concepts"
            target_dir.mkdir(parents=True, exist_ok=True)
            tool = TerminalTool(workspace_dir=workspace)

            result = tool._run("pwd", cwd="memory/concepts", timeout=5).strip()

            self.assertEqual(result, str(target_dir.resolve()))

    def test_rejects_cwd_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = TerminalTool(workspace_dir=workspace)

            result = tool._run("pwd", cwd="../outside", timeout=5)

            self.assertIn("Path security violation", result)

    def test_rejects_invalid_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = TerminalTool(workspace_dir=workspace)

            result = tool._run("pwd", timeout=0)

            self.assertIn("Invalid timeout", result)

    def test_wrong_path_kwarg_returns_friendly_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = TerminalTool(workspace_dir=workspace)

            result = tool._run(path="memory/tasks/demo.md")

            self.assertIn("expects `command`, not `path`", result)

    def test_schema_does_not_expose_path_argument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tool = TerminalTool(workspace_dir=workspace)

            self.assertEqual(set(tool.args.keys()), {"command", "cwd", "timeout"})


if __name__ == "__main__":
    unittest.main()
