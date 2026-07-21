"""Fetch URL Tool - 获取网页内容并转换为 Markdown

基于 LangChain 的 RequestsGetTool，添加：
- HTML 转 Markdown (使用 html2text)
- 内容截断 (避免 Token 过多)
- 基础内容清洗
"""

from __future__ import annotations

import html2text
import requests
from pydantic import BaseModel, ConfigDict, Field, model_validator
from langchain_core.tools import BaseTool


class FetchURLToolInput(BaseModel):
    """Public tool schema exposed to the model."""

    model_config = ConfigDict(extra="forbid")

    url: str | None = Field(
        default=None,
        description="HTTP(S) URL to fetch.",
    )
    path: str | None = Field(
        default=None,
        description="Fallback alias for providers that incorrectly label the URL field as `path`.",
    )

    @model_validator(mode="after")
    def normalize_url(self) -> "FetchURLToolInput":
        if not self.url and self.path:
            self.url = self.path
        if not self.url:
            raise ValueError("fetch_url requires `url`.")
        return self


class FetchURLTool(BaseTool):
    """获取网页内容并转换为 Markdown"""

    name: str = "fetch_url"
    description: str = """Fetch web content and convert to Markdown format.
Use this to retrieve information from the internet for research.
Returns cleaned Markdown text."""
    args_schema: type[BaseModel] = FetchURLToolInput

    def _normalize_url(self, url: str | None, path: str | None = None) -> str:
        candidate = (url or path or "").strip()
        if not candidate:
            raise ValueError("fetch_url requires `url`.")
        if not candidate.startswith(("http://", "https://")):
            raise ValueError("fetch_url only supports http:// or https:// URLs.")
        return candidate

    def _run(self, url: str | None = None, path: str | None = None) -> str:
        """获取网页内容"""
        try:
            normalized_url = self._normalize_url(url, path)

            # 发送请求
            response = requests.get(normalized_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)'
            })
            response.raise_for_status()

            # HTML 转 Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.ignore_emphasis = False
            h.body_width = 0  # 不自动换行

            markdown = h.handle(response.text)

            # 内容截断
            if len(markdown) > 20000:
                markdown = markdown[:20000] + "\n... (content truncated)"

            return markdown

        except ValueError as e:
            return f"Error: {str(e)}"
        except requests.exceptions.Timeout:
            return f"Error: Request timeout (10s): {normalized_url}"
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to fetch URL: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, url: str | None = None, path: str | None = None) -> str:
        """异步执行（暂不支持）"""
        return self._run(url, path=path)
