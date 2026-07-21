"""Prompt Builder for the OpenClaw system prompt."""

from __future__ import annotations

import json
from pathlib import Path


class PromptBuilder:
    """Build the runtime system prompt."""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def build(self, memory_map: dict, skills_snapshot: str = "", metadata: dict = None) -> str:
        """Build the full system prompt."""
        blocks = []

        # Block 1: Identity
        blocks.append("You are a personal assistant running inside OpenClaw.")

        # Block 2: Tooling
        blocks.append(self._build_tooling_block(metadata))

        # Block 3: Workspace / Metadata
        blocks.append(self._build_workspace_block())
        if metadata:
            blocks.append(self._build_metadata_block(metadata))

        # Block 4: Control Plane
        blocks.append(self._build_control_plane_block())

        # Block 5: Skills Snapshot
        if skills_snapshot:
            blocks.append(self._build_skills_snapshot_block(skills_snapshot))

        # Block 6: Execution Contract
        blocks.append(self._build_execution_contract_block())

        # Block 7: Memory Map
        blocks.append(self._build_memory_map_block(memory_map))

        return "\n\n".join(blocks)

    def _build_tooling_block(self, metadata: dict | None = None) -> str:
        platform_family, platform_display = self._resolve_platform_family(metadata)
        platform_guidance = self._build_terminal_platform_guidance(
            platform_family,
            platform_display,
        )
        terminal_examples = self._build_terminal_examples(platform_family)

        return f"""## Tooling

Available tools:
- **terminal(command, cwd='.', timeout=30)**: execute shell commands in a restricted environment
- **python_repl(code, cwd='.')**: execute Python code
- **read_file(path, cwd='.')**: read file contents
- **write_file(path, content, cwd='.')**: write files into writable workspace directories
- **fetch_url(url)**: fetch web content as Markdown

Tool usage guidelines:
1. Use terminal for system operations and file listing. `cwd` must stay inside the workspace and `timeout` is in seconds.
2. Use python_repl for data analysis and visualization.
3. Use read_file to access memory and assets.
4. Use write_file to persist insights into writable workspace directories.
5. Use fetch_url to retrieve web content for research.

Terminal platform policy:
{platform_guidance}

Parameter contract:
- `terminal` only accepts `command`, optional `cwd`, and optional `timeout`
- `read_file`, `write_file`, and `python_repl` accept optional `cwd`; `path` is resolved relative to that directory
- `fetch_url` expects `url`; if a provider sends `path` for the URL field, the tool will normalize it automatically
- Do not pass `path` to `terminal`; file reads belong to `read_file`
- Prefer `read_file(path, cwd)` for opening a file and `terminal(command, cwd, timeout)` for listing, searching, and command execution
- Always send tool calls as structured argument objects that match the tool schema exactly
- Do not imitate pseudo-code from prior chat history such as `terminal("ls")` or `read_file("foo.md")`

Examples:
- `terminal({{"command":"{terminal_examples[0]}", "cwd":".", "timeout":10}})`
- `terminal({{"command":"{terminal_examples[1]}", "cwd":".", "timeout":10}})`
- `read_file({{"path":"SKILL.md", "cwd":"skills/_system/mechanism_evidence_chain"}})`
- `write_file({{"path":"CONCEPT_demo.md", "cwd":"memory/concepts", "content":"# demo"}})`
- `python_repl({{"code":"print(open('project.md').read())", "cwd":"memory/identity"}})`
- `fetch_url({{"url":"https://api.openalex.org/works?search=high-valent%20cobalt"}})`"""

    def _resolve_platform_family(self, metadata: dict | None) -> tuple[str, str]:
        if not metadata:
            return "unknown", "unknown"

        raw_platform = str(metadata.get("platform", "")).strip()
        normalized = raw_platform.lower()

        if normalized in {"darwin", "mac", "macos", "osx"}:
            return "macos", raw_platform or "darwin"
        if normalized.startswith("win") or normalized in {"windows", "cygwin", "msys"}:
            return "windows", raw_platform or "windows"

        return "unknown", raw_platform or "unknown"

    def _build_terminal_platform_guidance(self, platform_family: str, platform_display: str) -> str:
        detection_command = 'python -c "import platform; print(platform.system())"'

        if platform_family == "windows":
            lines = [
                f"- Trusted platform hint: Windows (`platform={platform_display}`)",
                "- Prefer Windows terminal commands first: `dir`, `where`, `type`, `findstr`.",
                "- Avoid defaulting to macOS/Linux commands like `ls`, `find`, or `sed` unless the environment proves they are supported.",
                f"- If the terminal behavior conflicts with metadata, detect the OS with `{detection_command}` before sending more shell-specific commands.",
            ]
            return "\n".join(lines)

        if platform_family == "macos":
            lines = [
                f"- Trusted platform hint: macOS (`platform={platform_display}`)",
                "- Prefer macOS terminal commands first: `ls`, `find`, `sed`.",
                "- Avoid Windows-specific commands like `dir`, `where`, `type`, or `findstr` unless the environment proves they are supported.",
                f"- If the terminal behavior conflicts with metadata, detect the OS with `{detection_command}` before sending more shell-specific commands.",
            ]
            return "\n".join(lines)

        lines = [
            f"- Trusted platform hint: unknown (`platform={platform_display}`)",
            f"- Detect the host OS first with `{detection_command}`.",
            "- After detection, use Windows commands (`dir`, `where`, `type`, `findstr`) on Windows hosts.",
            "- After detection, use macOS commands (`ls`, `find`, `sed`) on macOS hosts.",
        ]
        return "\n".join(lines)

    def _build_terminal_examples(self, platform_family: str) -> tuple[str, str]:
        if platform_family == "windows":
            return (
                "dir /s /b skills",
                "findstr /n terminal AGENTS.md",
            )

        if platform_family == "macos":
            return (
                "find skills -maxdepth 2 -type f",
                "sed -n 1,80p AGENTS.md",
            )

        return (
            "find skills -maxdepth 2 -type f",
            "python -V",
        )

    def _build_workspace_block(self) -> str:
        return f"""## Workspace

工作目录: {self.workspace_dir}

规则:
- **Memory Map is navigation only**: the Memory Map below lists available files, not files you already opened.
- **When information is insufficient**: use `read_file` to inspect the relevant files.
- **When you need to persist output**: use `write_file` only in writable directories.
- **Do not fabricate facts**: ground statements in actual file contents and tool results.
- **Keep asset traceability**: when writing into `memory/`, preserve the original asset paths."""

    def _build_execution_contract_block(self) -> str:
        return """## Execution Contract

- Control Plane Files are preloaded by the system prompt. They are not tool calls.
- Memory Map and Recommended Files are navigation hints. They do not mean you already opened those files.
- Only say “已读/已查看 <file>” when you actually called `read_file` in this turn and received content.
- Only say “已写/已落盘 <file>” when you actually called `write_file` in this turn and the tool returned success.
- If you are proposing a file operation, label it as “建议读取/建议写入”, not as a completed action.
- If no tool was called, do not fabricate Context Trace / Memory Patch as completed facts. State that your answer is based on preloaded context and suggestions only.

## Asset Traceability Rule

When you create or update any file in memory/ (TASK_*, PACK_*, CONCEPT_*, day logs, etc.)
that is derived from one or more assets, you MUST:
1. Pass the `source_assets` parameter to `write_file` with the list of asset paths
2. The tool will automatically inject a YAML frontmatter block with source_assets and created date
3. Role values for reference: primary_input / data_source / reference / figure_source
4. This ensures every piece of knowledge can be traced back to its source material

Example:
```
write_file({
  "path": "TASK_literature_cobalt.md",
  "cwd": "memory/tasks",
  "content": "# TASK ...",
  "source_assets": ["assets/uploads/a1b2c3d4_paper.pdf", "assets/data/e5f6g7h8_kinetics.csv"]
})
```"""

    def _build_metadata_block(self, metadata: dict) -> str:
        return f"""## Inbound Context (trusted metadata)

```json
{json.dumps(metadata, indent=2, ensure_ascii=False)}
```"""

    def _build_control_plane_block(self) -> str:
        """Read and inject control-plane files."""
        blocks = ["# Project Context"]

        control_files = [
            "AGENTS.md",
            "SOUL.md",
            "IDENTITY.md",
            "USER.md",
            "TOOLS.md",
            "BOOTSTRAP.md",
            "MEMORY.md",
            "memory/identity/project.md",
        ]

        for file in control_files:
            file_path = self.workspace_dir / file
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                blocks.append(f"## {file}")
                blocks.append(content)

        return "\n\n".join(blocks)

    def _build_skills_snapshot_block(self, snapshot: str) -> str:
        """Build the Skills snapshot block."""
        return f"# Skills Menu\n\n{snapshot}"

    def _build_memory_map_block(self, memory_map: dict) -> str:
        """Build the Memory Map block."""
        lines = ["# Memory Map", ""]

        lines.append("## Layer 1 - Identity")
        for file in memory_map.get("layer1", []):
            lines.append(f"- {file}")
        lines.append("")

        lines.append("## Layer 2 - Timeline")
        for file in memory_map.get("layer2", []):
            lines.append(f"- {file}")
        lines.append("")

        lines.append("## Layer 3 - Atom Notes")
        for file in memory_map.get("layer3", []):
            lines.append(f"- {file}")
        lines.append("")

        lines.append("## Assets")
        assets = memory_map.get("assets", [])
        if assets and isinstance(assets[0], dict):
            for item in assets:
                size_kb = item.get("size", 0) / 1024
                lines.append(f"- {item['path']} ({item.get('type', '?')}, {size_kb:.0f}KB)")
        else:
            for entry in assets:
                lines.append(f"- {entry}")
        if not assets:
            lines.append("- (no files)")
        lines.append("")

        if memory_map.get("recommended"):
            lines.append("## Recommended Files")
            lines.append("Based on your query, you may want to read:")
            for file in memory_map["recommended"]:
                lines.append(f"- {file}")
            lines.append("")

        lines.append("**Hint**: use `read_file(path)` to inspect any file you actually need.")

        return "\n".join(lines)
