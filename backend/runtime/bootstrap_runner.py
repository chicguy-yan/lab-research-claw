"""Bootstrap helpers for first-run workspace onboarding."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil

from graph.session_manager import SessionManager

BOOTSTRAP_SESSION_ID = "__bootstrap__"

QUESTION_START = "<!-- BOOTSTRAP_QUESTION_START -->"
QUESTION_END = "<!-- BOOTSTRAP_QUESTION_END -->"
QA_START = "<!-- BOOTSTRAP_QA_START -->"
QA_END = "<!-- BOOTSTRAP_QA_END -->"


@dataclass
class BootstrapStartResult:
    session_id: str
    prompt: str


class BootstrapRunner:
    """Manage the single-turn bootstrap file lifecycle."""

    def __init__(self, workspace_id: str, workspace_dir: Path) -> None:
        self.workspace_id = workspace_id
        self.workspace_dir = workspace_dir
        self.bootstrap_path = workspace_dir / "BOOTSTRAP.md"

    def start(self, session_manager: SessionManager) -> BootstrapStartResult:
        """Reset the bootstrap session and seed the onboarding question."""
        prompt = self.read_bootstrap_prompt()
        session_manager.delete_session(BOOTSTRAP_SESSION_ID)
        session_manager.ensure_session(BOOTSTRAP_SESSION_ID, title="Bootstrap Initialization")
        session_manager.save_message(BOOTSTRAP_SESSION_ID, "assistant", prompt)
        return BootstrapStartResult(session_id=BOOTSTRAP_SESSION_ID, prompt=prompt)

    def read_bootstrap_prompt(self) -> str:
        content = self._read_bootstrap_text()
        prompt = _extract_between(content, QUESTION_START, QUESTION_END).strip()
        if not prompt:
            raise ValueError("BOOTSTRAP.md is missing the bootstrap question block")
        return prompt

    def record_first_answer(self, message: str, attachments: list[dict[str, str]]) -> None:
        """Persist the user's first bootstrap answer into BOOTSTRAP.md."""
        content = self._read_bootstrap_text()
        replacement = self._render_first_answer(message, attachments)
        updated = _replace_between(content, QA_START, QA_END, replacement)
        self.bootstrap_path.write_text(updated, encoding="utf-8")

    def complete(self) -> None:
        """Remove BOOTSTRAP.md after the first-run bootstrap finishes."""
        if self.bootstrap_path.exists():
            self.bootstrap_path.unlink()

    def _read_bootstrap_text(self) -> str:
        if not self.bootstrap_path.exists():
            raise FileNotFoundError(f"Bootstrap file not found: {self.bootstrap_path}")
        return self.bootstrap_path.read_text(encoding="utf-8")

    def _render_first_answer(self, message: str, attachments: list[dict[str, str]]) -> str:
        lines = [
            "status: answered",
            f"recorded_at: {_now_iso()}",
            "",
            "### User First Answer",
            _indent_block(message.strip() or "(empty)"),
            "",
            "### Uploaded Assets",
        ]
        if attachments:
            for item in attachments:
                saved_path = item.get("saved_path", "").strip() or "(unknown path)"
                file_type = item.get("file_type", "").strip() or "unknown"
                summary = item.get("summary", "").strip() or "no summary"
                lines.append(f"- `{saved_path}` ({file_type}): {summary}")
        else:
            lines.append("- (no uploaded assets)")
        return "\n".join(lines)


def sync_bootstrap_file(workspace_dir: Path, template_path: Path, bootstrap_status: str) -> None:
    """Keep BOOTSTRAP.md aligned with manifest lifecycle."""
    bootstrap_path = workspace_dir / "BOOTSTRAP.md"
    if bootstrap_status == "completed":
        if bootstrap_path.exists():
            bootstrap_path.unlink()
        return

    if bootstrap_status in {"pending", "running", "failed"} and not bootstrap_path.exists():
        bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, bootstrap_path)


def _extract_between(content: str, start_marker: str, end_marker: str) -> str:
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end == -1 or end < start:
        return ""
    return content[start + len(start_marker):end].strip("\n")


def _replace_between(content: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise ValueError("BOOTSTRAP.md is missing the first-answer placeholder block")
    prefix = content[: start + len(start_marker)]
    suffix = content[end:]
    return f"{prefix}\n{replacement}\n{suffix}"


def _indent_block(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

