"""Read File Tool - 读取文件内容

基于 LangChain 的 ReadFileTool，添加：
- 路径安全检查 (resolve_safe_path)
- 自动截断 (20000 字符)
- 支持多种编码
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from langchain_core.tools import BaseTool

from graph.path_utils import PathSecurityError, resolve_safe_path_from_cwd


class ReadFileToolInput(BaseModel):
    """Public tool schema exposed to the model."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="File path to read, relative to the workspace or the supplied cwd.")
    cwd: str = Field(".", description="Workspace-relative base directory used to resolve `path`.")


class ReadFileTool(BaseTool):
    """读取文件内容"""

    name: str = "read_file"
    description: str = """Read file contents from the workspace.
Use this to access memory files and assets.
Path must be relative to the workspace directory or the supplied cwd."""
    args_schema: type[BaseModel] = ReadFileToolInput

    workspace_dir: Path

    def _run(self, path: str, cwd: str = ".") -> str:
        """读取文件"""
        try:
            safe_path = resolve_safe_path_from_cwd(
                self.workspace_dir,
                path,
                cwd=cwd,
                require_writable=False,
            )

            # 读取文件
            content = safe_path.read_text(encoding='utf-8')

            # 自动截断
            if len(content) > 20000:
                content = content[:20000] + "\n... (content truncated)"

            return content

        except PathSecurityError as e:
            return f"Error: Path security violation: {str(e)}"
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                content = safe_path.read_text(encoding='gbk')
                if len(content) > 20000:
                    content = content[:20000] + "\n... (content truncated)"
                return content
            except Exception:
                return f"Error: Cannot decode file (not a text file): {path}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, path: str, cwd: str = ".") -> str:
        """异步执行（暂不支持）"""
        return self._run(path, cwd=cwd)
