"""Trace Writer - 记录工具调用到 trace

Phase 3 职责：
- 记录工具调用到 context_trace/{session_id}.json
- 遵循 envelope schema: {"messages": [...], "traces": [...], "prompt": {...}}
- 只更新 traces / prompt 字段，保留 messages 字段
"""

from __future__ import annotations

import json
from pathlib import Path


class TraceWriter:
    """记录工具调用到 trace"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.trace_dir = workspace_dir / "context_trace"
        self.trace_dir.mkdir(exist_ok=True)

    def write_trace(self, session_id: str, tool_calls: list[dict], prompt: dict | None = None):
        """
        写入 trace（遵循 Phase 1 envelope schema）

        Args:
            session_id: 会话 ID
            tool_calls: 工具调用列表
                [
                    {
                        "tool": "read_file",
                        "args": {"path": "..."},
                        "result": "...",
                        "timestamp": "..."
                    },
                    ...
                ]
            prompt: 最终传给模型的 prompt 载荷
        """
        trace_file = self.trace_dir / f"{session_id}.json"

        # 读取完整 envelope（遵循 Phase 1 schema）
        if trace_file.exists():
            envelope = json.loads(trace_file.read_text(encoding='utf-8'))
            # 兼容旧格式
            if isinstance(envelope, dict) and "messages" not in envelope:
                envelope = {"messages": [], "traces": []}
        else:
            envelope = {"messages": [], "traces": []}

        # 只更新 traces 字段，保留 messages
        if "traces" not in envelope:
            envelope["traces"] = []
        envelope["traces"].extend(tool_calls)
        if prompt is not None:
            envelope["prompt"] = prompt

        # 写回完整 envelope
        trace_file.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding='utf-8')
