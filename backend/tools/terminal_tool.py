from __future__ import annotations

import locale
import subprocess
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field

from langchain_core.tools import BaseTool

from graph.path_utils import PathSecurityError, resolve_safe_dir


class TerminalToolInput(BaseModel):
    """Public tool schema exposed to the model."""

    command: str = Field(..., description="Shell command to execute inside the workspace.")
    cwd: str = Field(".", description="Workspace-relative directory to run the command from.")
    timeout: int = Field(30, description="Timeout in seconds. Must be between 1 and 300.")


class TerminalTool(BaseTool):
    """Execute shell commands in a restricted workspace."""

    name: str = "terminal"
    description: str = """Execute Windows shell commands in a restricted environment.
Use this for system operations like listing files and searching text.
Prefer Windows-native commands such as `dir`, `where`, `type`, `findstr`, or `powershell -Command Get-ChildItem`.
Avoid Unix-only commands like `ls`, `find`, or `sed` because this workspace runs on Windows.
CWD is limited to the workspace directory.
Dangerous commands are blocked."""
    args_schema: type[BaseModel] = TerminalToolInput

    workspace_dir: Path
    DEFAULT_TIMEOUT: ClassVar[int] = 30
    MAX_TIMEOUT: ClassVar[int] = 300

    BLACKLIST: ClassVar[list[str]] = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        "> /dev/",
        ":(){ :|:& };:",
        "chmod 777",
        "chown",
    ]

    def _resolve_cwd(self, cwd: str) -> Path:
        return resolve_safe_dir(self.workspace_dir, cwd)

    def _normalize_timeout(self, timeout: int) -> int:
        if timeout < 1:
            raise ValueError("timeout must be >= 1")
        if timeout > self.MAX_TIMEOUT:
            raise ValueError(f"timeout must be <= {self.MAX_TIMEOUT}")
        return timeout

    def _decode_output(self, data: bytes) -> str:
        if not data:
            return ""
        candidates = ["utf-8", locale.getpreferredencoding(False), "gb18030", "gbk"]
        seen: set[str] = set()
        for encoding in candidates:
            if not encoding or encoding in seen:
                continue
            seen.add(encoding)
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def _run(
        self,
        command: str | None = None,
        cwd: str = ".",
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> str:
        if command is None:
            if "path" in kwargs:
                return "Error: terminal expects `command`, not `path`. Use read_file(path) for files."
            return "Error: terminal requires `command`."

        for dangerous in self.BLACKLIST:
            if dangerous in command:
                return f"Error: Dangerous command blocked: {dangerous}"

        try:
            safe_cwd = self._resolve_cwd(cwd)
            normalized_timeout = self._normalize_timeout(timeout)
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(safe_cwd),
                capture_output=True,
                text=False,
                timeout=normalized_timeout,
            )

            output = self._decode_output(result.stdout)
            stderr = self._decode_output(result.stderr)
            if stderr:
                output += f"\nSTDERR:\n{stderr}"

            if len(output) > 10000:
                output = output[:10000] + "\n... (output truncated)"

            return output

        except PathSecurityError as exc:
            return f"Error: Path security violation: {exc}"
        except ValueError as exc:
            return f"Error: Invalid timeout: {exc}"
        except subprocess.TimeoutExpired:
            return f"Error: Command timeout ({timeout}s)"
        except Exception as exc:
            return f"Error: {exc}"

    async def _arun(
        self,
        command: str | None = None,
        cwd: str = ".",
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> str:
        return self._run(command, cwd=cwd, timeout=timeout, **kwargs)
