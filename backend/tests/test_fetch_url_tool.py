from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.fetch_url_tool import FetchURLTool


class FetchURLToolTests(unittest.TestCase):
    @patch("tools.fetch_url_tool.requests.get")
    def test_accepts_path_alias_for_url(self, mock_get) -> None:
        response = Mock()
        response.text = "<html><body><h1>Hello</h1></body></html>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response
        tool = FetchURLTool()

        result = tool._run(path="https://example.com")

        self.assertIn("Hello", result)
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], "https://example.com")

    def test_rejects_non_http_urls(self) -> None:
        tool = FetchURLTool()

        result = tool._run(path="memory/concepts/hello.md")

        self.assertIn("only supports http:// or https:// URLs", result)

    def test_schema_exposes_url_and_path(self) -> None:
        tool = FetchURLTool()

        self.assertEqual(set(tool.args.keys()), {"url", "path"})


if __name__ == "__main__":
    unittest.main()
