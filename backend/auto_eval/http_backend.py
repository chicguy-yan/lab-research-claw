from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import requests

from auto_eval.models import AttachmentPayload, SSEEvent


class HttpBackendClient:
    def __init__(self, base_url: str, timeout_seconds: int = 180) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def _headers(self, workspace_id: str | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if workspace_id:
            headers["X-Workspace-Id"] = workspace_id
        return headers

    def _json(self, response: requests.Response) -> dict[str, Any]:
        response.raise_for_status()
        return response.json()

    def create_workspace(self, workspace_id: str, display_name: str, description: str) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/workspaces",
            json={
                "workspace_id": workspace_id,
                "display_name": display_name,
                "description": description,
            },
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def get_manifest(self, workspace_id: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/workspaces/{workspace_id}/manifest",
            headers=self._headers(workspace_id),
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def start_bootstrap(self, workspace_id: str) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/workspaces/{workspace_id}/bootstrap/start",
            headers=self._headers(workspace_id),
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def create_session(self, workspace_id: str, title: str) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/sessions",
            headers=self._headers(workspace_id),
            json={"title": title},
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def rename_session(self, workspace_id: str, session_id: str, title: str) -> dict[str, Any]:
        response = self.session.put(
            f"{self.base_url}/api/sessions/{session_id}",
            headers=self._headers(workspace_id),
            json={"title": title},
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def upload_asset(self, workspace_id: str, file_path: Path, target_dir: str = "auto") -> dict[str, Any]:
        with file_path.open("rb") as fh:
            response = self.session.post(
                f"{self.base_url}/api/assets/upload",
                headers={"X-Workspace-Id": workspace_id},
                params={"target_dir": target_dir},
                files={"file": (file_path.name, fh)},
                timeout=self.timeout_seconds,
            )
        return self._json(response)

    def stream_chat(
        self,
        workspace_id: str,
        session_id: str,
        message: str,
        route: str,
        attachments: list[AttachmentPayload],
        prompt_context: dict[str, Any] | None = None,
    ) -> Iterator[SSEEvent]:
        payload = {
            "message": message,
            "session_id": session_id,
            "workspace_id": workspace_id,
            "stream": True,
            "route": route,
            "prompt_context": prompt_context or {},
            "attachments": [
                {
                    "saved_path": item.saved_path,
                    "file_type": item.file_type,
                    "summary": item.summary,
                }
                for item in attachments
            ],
        }

        with self.session.post(
            f"{self.base_url}/api/chat",
            headers={"X-Workspace-Id": workspace_id, "Accept": "text/event-stream"},
            json=payload,
            stream=True,
            timeout=self.timeout_seconds,
        ) as response:
            response.raise_for_status()

            current_event: str | None = None
            data_lines: list[str] = []
            for raw_line in response.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue
                line = raw_line.strip()
                if not line:
                    if current_event:
                        data = {}
                        if data_lines:
                            data = json.loads("\n".join(data_lines))
                        yield SSEEvent(event=current_event, data=data)
                    current_event = None
                    data_lines = []
                    continue
                if line.startswith("event:"):
                    current_event = line.split(":", 1)[1].strip()
                    continue
                if line.startswith("data:"):
                    data_lines.append(line.split(":", 1)[1].strip())

    def get_history(self, workspace_id: str, session_id: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/sessions/{session_id}/history",
            headers=self._headers(workspace_id),
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def read_text_file(self, workspace_id: str, path: str) -> str:
        response = self.session.get(
            f"{self.base_url}/api/files",
            headers=self._headers(workspace_id),
            params={"path": path},
            timeout=self.timeout_seconds,
        )
        return self._json(response)["content"]

    def get_file_tree(self, workspace_id: str, path: str = "", max_depth: int = 3) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/files/tree",
            headers=self._headers(workspace_id),
            params={"path": path, "max_depth": max_depth},
            timeout=self.timeout_seconds,
        )
        return self._json(response)

    def write_text_file(self, workspace_id: str, path: str, content: str) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/files",
            headers=self._headers(workspace_id),
            json={"path": path, "content": content},
            timeout=self.timeout_seconds,
        )
        return self._json(response)
