from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from graph.session_manager import SessionManager
from runtime.bootstrap_runner import BOOTSTRAP_SESSION_ID, BootstrapRunner, sync_bootstrap_file


BOOTSTRAP_TEMPLATE = """# BOOTSTRAP\n\n## Bootstrap Question\n<!-- BOOTSTRAP_QUESTION_START -->\nPlease describe this workspace in a few short sentences.\n<!-- BOOTSTRAP_QUESTION_END -->\n\n## Recorded First QA\n<!-- BOOTSTRAP_QA_START -->\nstatus: pending\n<!-- BOOTSTRAP_QA_END -->\n"""


def _seed_workspace(workspace: Path) -> None:
    for relative in [
        "context_trace",
        "memory/identity",
        "memory/concepts",
        "memory/tasks",
        "memory/packs",
        "memory/timeline",
    ]:
        (workspace / relative).mkdir(parents=True, exist_ok=True)


class BootstrapRunnerTests(unittest.TestCase):
    def test_start_seeds_bootstrap_session_with_question(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            (workspace / "BOOTSTRAP.md").write_text(BOOTSTRAP_TEMPLATE, encoding="utf-8")
            session_manager = SessionManager(workspace)
            runner = BootstrapRunner("lab-a", workspace)

            result = runner.start(session_manager)

            self.assertEqual(result.session_id, BOOTSTRAP_SESSION_ID)
            self.assertIn("Please describe this workspace", result.prompt)
            history = session_manager.load_session(BOOTSTRAP_SESSION_ID)
            self.assertEqual(history[0]["role"], "assistant")
            self.assertIn("Please describe this workspace", history[0]["content"])

    def test_record_first_answer_updates_bootstrap_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            bootstrap_path = workspace / "BOOTSTRAP.md"
            bootstrap_path.write_text(BOOTSTRAP_TEMPLATE, encoding="utf-8")
            runner = BootstrapRunner("lab-b", workspace)

            runner.record_first_answer(
                "This workspace is for Ce-Co3O4 chlorite mechanism notes.",
                [{
                    "saved_path": "assets/uploads/paper.pdf",
                    "file_type": "pdf",
                    "summary": "core paper",
                }],
            )

            content = bootstrap_path.read_text(encoding="utf-8")
            self.assertIn("status: answered", content)
            self.assertIn("Ce-Co3O4", content)
            self.assertIn("assets/uploads/paper.pdf", content)

    def test_complete_removes_bootstrap_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _seed_workspace(workspace)
            bootstrap_path = workspace / "BOOTSTRAP.md"
            bootstrap_path.write_text(BOOTSTRAP_TEMPLATE, encoding="utf-8")
            runner = BootstrapRunner("lab-c", workspace)

            runner.complete()

            self.assertFalse(bootstrap_path.exists())

    def test_sync_bootstrap_file_follows_manifest_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            workspace.mkdir(parents=True, exist_ok=True)
            template = root / "BOOTSTRAP.template.md"
            template.write_text(BOOTSTRAP_TEMPLATE, encoding="utf-8")

            sync_bootstrap_file(workspace, template, "pending")
            self.assertTrue((workspace / "BOOTSTRAP.md").exists())

            sync_bootstrap_file(workspace, template, "completed")
            self.assertFalse((workspace / "BOOTSTRAP.md").exists())


if __name__ == "__main__":
    unittest.main()
