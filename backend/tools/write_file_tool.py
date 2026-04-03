"""Write File Tool - 写入文件

基于 LangChain 的 WriteFileTool，添加：
- 自动创建父目录
- 相对路径默认写入当前 workspace
- Phase 5.2: source_assets 溯源强制注入
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from langchain_core.tools import BaseTool

from graph.path_utils import PathSecurityError, resolve_safe_path_from_cwd


class WriteFileToolInput(BaseModel):
    """Public tool schema exposed to the model."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="File path to write, relative to the workspace or the supplied cwd.")
    content: str = Field(..., description="Text content to write into the target file.")
    cwd: str = Field(".", description="Workspace-relative base directory used to resolve `path`.")
    source_assets: list[str] = Field(
        default_factory=list,
        description="List of asset paths (relative to workspace) this file is derived from. "
                    "When writing memory files based on uploaded assets, always include the source paths.",
    )


def _inject_source_assets_frontmatter(content: str, source_assets: list[str]) -> str:
    """If content targets memory/ and source_assets is non-empty, inject YAML frontmatter."""
    if not source_assets:
        return content

    assets_yaml = "\n".join(f"  - {p}" for p in source_assets)
    frontmatter = (
        f"---\n"
        f"source_assets:\n{assets_yaml}\n"
        f"created: {date.today().isoformat()}\n"
        f"---\n\n"
    )

    # If content already has frontmatter, merge source_assets into it
    if content.startswith("---\n"):
        end_idx = content.find("\n---\n", 4)
        if end_idx > 0:
            existing_fm = content[4:end_idx]
            rest = content[end_idx + 5:]
            # Only add if source_assets not already present
            if "source_assets:" not in existing_fm:
                merged_fm = existing_fm.rstrip() + f"\nsource_assets:\n{assets_yaml}\n"
                return f"---\n{merged_fm}---\n{rest}"
            return content  # Already has source_assets, don't duplicate

    # No existing frontmatter — prepend
    return frontmatter + content


class WriteFileTool(BaseTool):
    """写入文件到 workspace"""

    name: str = "write_file"
    description: str = """Write content to a file in the workspace.
Use this to persist insights, analysis results, and structured knowledge.
When writing memory files derived from assets, include source_assets for traceability.
Relative paths are resolved from the workspace directory or the supplied cwd."""
    args_schema: type[BaseModel] = WriteFileToolInput

    workspace_dir: Path

    def _run(self, path: str, content: str, cwd: str = ".", source_assets: list[str] | None = None) -> str:
        """写入文件"""
        if source_assets is None:
            source_assets = []

        try:
            target_path = resolve_safe_path_from_cwd(
                self.workspace_dir,
                path,
                cwd=cwd,
                require_writable=True,
            )
            relative_path = str(target_path.relative_to(self.workspace_dir.resolve())).replace("\\", "/")

            # Phase 5.2: 仅对 memory/ 路径下的文件注入 source_assets frontmatter
            if source_assets and relative_path.startswith("memory/"):
                content = _inject_source_assets_frontmatter(content, source_assets)

            # 自动创建父目录
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            target_path.write_text(content, encoding='utf-8')

            return f"File written successfully: {relative_path}"

        except PathSecurityError as e:
            return f"Error: Path security violation: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, path: str, content: str, cwd: str = ".", source_assets: list[str] | None = None) -> str:
        """异步执行"""
        return self._run(path, content, cwd=cwd, source_assets=source_assets)
