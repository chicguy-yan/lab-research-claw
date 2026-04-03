"""Python REPL Tool - 执行 Python 代码

基于 LangChain 的 PythonREPLTool，添加：
- 隔离环境
- workspace_dir 自动添加到 sys.path
- 异常捕获
- 输出截断 (10000 字符)
"""

from __future__ import annotations

import os
import sys
from io import StringIO
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from langchain_core.tools import BaseTool

from graph.path_utils import PathSecurityError, resolve_safe_dir


class PythonREPLToolInput(BaseModel):
    """Public tool schema exposed to the model."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Python code to execute.")
    cwd: str = Field(".", description="Workspace-relative working directory used for relative file access inside Python.")


class PythonREPLTool(BaseTool):
    """执行 Python 代码"""

    name: str = "python_repl"
    description: str = """Execute Python code for data analysis and visualization.
The workspace directory is automatically added to sys.path.
Use this for data processing, plotting, statistical analysis, etc."""
    args_schema: type[BaseModel] = PythonREPLToolInput

    workspace_dir: Path

    def _run(self, code: str, cwd: str = ".") -> str:
        """执行 Python 代码"""
        # 添加 workspace_dir 到 sys.path
        workspace_str = str(self.workspace_dir)
        if workspace_str not in sys.path:
            sys.path.insert(0, workspace_str)

        # 捕获输出
        old_stdout = sys.stdout
        old_cwd = Path.cwd()
        sys.stdout = StringIO()

        try:
            safe_cwd = resolve_safe_dir(self.workspace_dir, cwd)
            os.chdir(safe_cwd)

            # 执行代码
            exec(
                code,
                {
                    "__builtins__": __builtins__,
                    "__name__": "__main__",
                    "workspace_dir": self.workspace_dir,
                    "cwd": safe_cwd,
                },
            )
            output = sys.stdout.getvalue()

            # 输出截断
            if len(output) > 10000:
                output = output[:10000] + "\n... (output truncated)"

            return output if output else "Code executed successfully (no output)"

        except PathSecurityError as e:
            return f"Error: Path security violation: {str(e)}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"

        finally:
            os.chdir(old_cwd)
            sys.stdout = old_stdout

    async def _arun(self, code: str, cwd: str = ".") -> str:
        """异步执行（暂不支持）"""
        return self._run(code, cwd=cwd)
