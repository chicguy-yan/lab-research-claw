import tempfile
import unittest
from pathlib import Path

from graph.session_manager import SessionManager


class SessionManagerTemporaryDirTest(unittest.TestCase):
    def test_create_and_delete_session_temp_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            manager = SessionManager(workspace)

            meta = manager.create_session(title="temp-test")
            session_id = meta["id"]
            session_temp_dir = workspace / "temporary_dir" / session_id
            self.assertTrue(session_temp_dir.exists())
            self.assertTrue(session_temp_dir.is_dir())

            temp_file = session_temp_dir / "script.py"
            temp_file.write_text("print(1)\n", encoding="utf-8")
            self.assertTrue(temp_file.exists())

            deleted = manager.delete_session(session_id)
            self.assertTrue(deleted)
            self.assertFalse(session_temp_dir.exists())


if __name__ == "__main__":
    unittest.main()
