"""SessionManager — JSON session persistence.

Storage layout:
  context_trace/{session_id}.json   → envelope schema (PRD §4.3):
      {"messages": [...], "traces": [], "prompt": {...}}
      - messages: OpenAI messages array (SessionManager 读写)
      - traces: 审计信息数组 (TraceWriter 读写, Phase 3)
      - prompt: 最终传给模型的 prompt 载荷 (TraceWriter 读写)
  context_trace/_sessions_index.json → session metadata (title, timestamps)
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionManager:
    """Manage chat sessions backed by local JSON files."""

    def __init__(self, workspace_dir: Path) -> None:
        self._workspace_dir = workspace_dir
        self._trace_dir = workspace_dir / "context_trace"
        self._temporary_dir = workspace_dir / "temporary_dir"
        self._trace_dir.mkdir(parents=True, exist_ok=True)
        self._temporary_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Index helpers
    # ------------------------------------------------------------------

    @property
    def _index_path(self) -> Path:
        return self._trace_dir / "_sessions_index.json"

    def _load_index(self) -> dict[str, Any]:
        if self._index_path.exists():
            with open(self._index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sessions": []}

    def _save_index(self, index: dict[str, Any]) -> None:
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def _touch_updated_at(self, session_id: str) -> None:
        """Update the updated_at timestamp for a session in the index."""
        index = self._load_index()
        now = _now_iso()
        for s in index["sessions"]:
            if s["id"] == session_id:
                s["updated_at"] = now
                break
        self._save_index(index)

    # ------------------------------------------------------------------
    # Session message file helpers
    # ------------------------------------------------------------------

    def _session_path(self, session_id: str) -> Path:
        return self._trace_dir / f"{session_id}.json"

    def _session_temp_dir(self, session_id: str) -> Path:
        return self._temporary_dir / session_id

    def _read_envelope(self, session_id: str) -> dict:
        """Read the full envelope for a session."""
        path = self._session_path(session_id)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Migration: handle legacy pure-array format
            if isinstance(data, list):
                return {"messages": data, "traces": []}
            return data
        return {"messages": [], "traces": []}

    def _write_envelope(self, session_id: str, envelope: dict) -> None:
        """Write the full envelope for a session."""
        path = self._session_path(session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2, ensure_ascii=False)

    def _read_messages(self, session_id: str) -> list[dict]:
        return self._read_envelope(session_id)["messages"]

    def _write_messages(self, session_id: str, messages: list[dict]) -> None:
        envelope = self._read_envelope(session_id)
        envelope["messages"] = messages
        self._write_envelope(session_id, envelope)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_sessions(self) -> list[dict]:
        """Return session list sorted by updated_at descending."""
        index = self._load_index()
        sessions = index.get("sessions", [])
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return sessions

    def ensure_session(self, session_id: str, title: str = "未命名会话") -> dict:
        """Ensure a given session_id exists. Create it if missing."""
        index = self._load_index()
        for s in index["sessions"]:
            if s["id"] == session_id:
                return s

        now = _now_iso()
        meta = {
            "id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        self._write_envelope(session_id, {"messages": [], "traces": []})
        self._session_temp_dir(session_id).mkdir(parents=True, exist_ok=True)
        index["sessions"].append(meta)
        self._save_index(index)
        return meta

    def create_session(self, title: str = "未命名会话") -> dict:
        """Create a new session. Returns the session metadata dict."""
        session_id = uuid.uuid4().hex[:12]
        return self.ensure_session(session_id=session_id, title=title)


    def rename_session(self, session_id: str, title: str) -> dict | None:
        """Rename a session. Returns updated metadata or None if not found."""
        index = self._load_index()
        for s in index["sessions"]:
            if s["id"] == session_id:
                s["title"] = title
                s["updated_at"] = _now_iso()
                self._save_index(index)
                return s
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session file and remove from index. Returns True if found."""
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()

        temp_dir = self._session_temp_dir(session_id)
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

        index = self._load_index()
        original_len = len(index["sessions"])
        index["sessions"] = [s for s in index["sessions"] if s["id"] != session_id]
        self._save_index(index)
        return len(index["sessions"]) < original_len

    def load_session(self, session_id: str) -> list[dict]:
        """Load raw messages array for a session."""
        return self._read_messages(session_id)

    def load_session_for_agent(self, session_id: str) -> list[dict]:
        """Load messages with consecutive assistant messages merged."""
        raw = self._read_messages(session_id)
        if not raw:
            return []
        merged: list[dict] = []
        for msg in raw:
            if (
                merged
                and merged[-1].get("role") == "assistant"
                and msg.get("role") == "assistant"
            ):
                # Merge consecutive assistant messages
                prev_content = merged[-1].get("content", "") or ""
                curr_content = msg.get("content", "") or ""
                merged[-1]["content"] = prev_content + "\n" + curr_content
            else:
                merged.append(dict(msg))
        return merged

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict] | None = None,
    ) -> None:
        """Append a message to the session file and update the index timestamp."""
        messages = self._read_messages(session_id)
        msg: dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        messages.append(msg)
        self._write_messages(session_id, messages)
        self._touch_updated_at(session_id)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
