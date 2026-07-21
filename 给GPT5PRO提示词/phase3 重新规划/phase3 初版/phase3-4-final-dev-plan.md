# Phase 3+4 最终开发计划 (Tool-Driven + 渐进式披露)

**版本**: v3.0 (Final) | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## 一、核心设计原则

### 1.1 核心理念

✅ **Tool-Driven**: LLM 通过工具主动访问 memory/skills/assets
✅ **渐进式披露**: System Prompt 只提供目录结构,LLM 按需读取
✅ **极简架构**: ❌ 不需要 ContextOrchestrator,只需要基础的 Prompt 拼接
✅ **LangChain 原生工具**: 优先使用 LangChain 内置工具

### 1.2 System Prompt 结构

```
System Prompt:
├── Block 1: Identity (身份)
├── Block 2: Tooling (6个核心工具说明)
├── Block 3: Workspace (工作目录 + 规则)
├── Block 4: Inbound Context (元数据)
├── Block 5: Control Plane (控制层文件完整内容)
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── USER.md
│   ├── SKILLS_SNAPSHOT.md
│   └── memory/identity/project.md
└── Block 6: Memory Map (仅目录结构,不注入内容)
    ├── Layer1: memory/identity/
    ├── Layer2: memory/timeline/
    ├── Layer3: memory/concepts/, tasks/, packs/
    └── Assets: assets/uploads/, data/, figures/, ppt_pack/
```

**关键**: Block 6 只列出文件路径,不注入文件内容,让 LLM 通过 read_file 工具按需读取

---

## 二、Phase 3: 基础 Prompt Builder

### 2.1 PromptBuilder (极简版)

**职责**: 拼接 System Prompt,不做任何文件选择

**文件**: `backend/graph/prompt_builder.py`

```python
from pathlib import Path
import json

class PromptBuilder:
    """极简版 Prompt Builder - 只拼接,不选择"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def build(self, metadata: dict = None) -> str:
        """
        构建 System Prompt

        Args:
            metadata: 元数据 (platform/timezone/language/current_date)

        Returns:
            完整的 System Prompt
        """
        blocks = []

        # Block 1: Identity
        blocks.append("You are a personal assistant running inside OpenClaw.")

        # Block 2: Tooling (6个核心工具)
        blocks.append(self._build_tooling_block())

        # Block 3: Workspace
        blocks.append(self._build_workspace_block())

        # Block 4: Inbound Context
        if metadata:
            blocks.append(self._build_metadata_block(metadata))

        # Block 5: Control Plane Files (完整内容)
        blocks.append(self._build_control_plane_block())

        # Block 6: Memory Map (仅目录结构)
        blocks.append(self._build_memory_map_block())

        return "\n\n".join(blocks)

    def _build_tooling_block(self) -> str:
        """Block 2: 工具说明"""
        return """## Tooling

Available tools (6 core tools):

1. **read_file(path)**: 读取文件内容
   - 用于读取 memory, skills, assets 中的任何文件
   - 示例: read_file("memory/identity/project.md")

2. **terminal(command)**: 执行 Shell 命令 (受限环境)
   - 用于系统操作
   - 示例: terminal("ls -la memory/tasks")

3. **python_repl(code)**: 执行 Python 代码
   - 用于数据分析、作图、计算
   - 示例: python_repl("import pandas as pd\\ndf = pd.read_csv('assets/data/exp.csv')")

4. **fetch_url(url)**: 抓取网页内容
   - 用于获取网页信息
   - 返回 Markdown 格式

5. **search_knowledge_base(query)**: RAG 检索
   - 用于检索 knowledge/ 目录下的文档
   - 混合检索 (BM25 + Vector)

6. **web_search(query)**: 网络搜索
   - 用于联网搜索 (Brave API / Tavily)
   - 返回结构化摘要

Tool usage guidelines:
- **渐进式披露**: 先看 Memory Map,再用 read_file 按需读取
- **溯源规则**: 写入 memory 时,必须包含 assets 原始路径
- **禁止脑补**: 必须基于实际文件内容,不要编造"""

    def _build_workspace_block(self) -> str:
        """Block 3: 工作目录"""
        return f"""## Workspace

工作目录: {self.workspace_dir}

核心规则:
1. **Memory Map 是你的导航**: 下面的 Memory Map 列出了所有文件路径
2. **按需读取**: 使用 read_file(path) 读取你需要的文件
3. **溯源写入**: 使用 write_file 写入 memory 时,必须包含 assets 路径
4. **禁止脑补**: 必须基于实际文件内容

示例工作流:
1. 看到用户请求 → 查看 Memory Map
2. 决定需要哪些文件 → 使用 read_file 读取
3. 处理数据 → 使用 python_repl 分析
4. 写入结果 → 使用 write_file (带 assets 路径)"""

    def _build_metadata_block(self, metadata: dict) -> str:
        """Block 4: 元数据"""
        return f"""## Inbound Context (trusted metadata)

```json
{json.dumps(metadata, indent=2, ensure_ascii=False)}
```"""

    def _build_control_plane_block(self) -> str:
        """Block 5: 控制层文件 (完整内容)"""
        blocks = ["# Project Context"]

        # 控制层文件列表
        control_files = [
            "AGENTS.md",
            "SOUL.md",
            "IDENTITY.md",
            "USER.md",
            "SKILLS_SNAPSHOT.md",
            "memory/identity/project.md",
        ]

        for file in control_files:
            file_path = self.workspace_dir / file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                # 截断超长文件
                if len(content) > 20000:
                    content = content[:20000] + "\n\n...[truncated]"
                blocks.append(f"## {file}")
                blocks.append(content)

        return "\n\n".join(blocks)

    def _build_memory_map_block(self) -> str:
        """Block 6: Memory Map (仅目录结构)"""
        lines = ["# Memory Map", ""]
        lines.append("以下是你的工作空间文件结构。使用 read_file(path) 读取任何你需要的文件。")
        lines.append("")

        # Layer 1
        lines.append("## Layer 1 — Identity (长期稳定)")
        layer1_files = self._scan_directory("memory/identity")
        for file in layer1_files:
            lines.append(f"- {file}")
        lines.append("")

        # Layer 2
        lines.append("## Layer 2 — Timeline (时间轴)")
        lines.append("- memory/timeline/180d_index.md")
        lines.append("- memory/timeline/phases/ (P01-P05)")
        lines.append("- memory/timeline/weeks/ (最近的周报)")
        lines.append("- memory/timeline/days/ (最近的日志)")
        lines.append("- memory/timeline/stage_reports/ (阶段汇报)")
        lines.append("")

        # Layer 3
        lines.append("## Layer 3 — Atom Notes (原子资产)")
        lines.append("- memory/concepts/ (研究主题)")
        lines.append("- memory/tasks/ (实验任务)")
        lines.append("- memory/packs/ (交付物)")
        lines.append("")

        # Assets
        lines.append("## Assets (原始资产)")
        lines.append("- assets/uploads/ (用户上传)")
        lines.append("- assets/data/ (实验数据)")
        lines.append("- assets/figures/ (图表)")
        lines.append("- assets/ppt_pack/ (汇报素材)")
        lines.append("")

        lines.append("**提示**: 使用 read_file(path) 读取任何文件,使用 terminal('ls path') 列出目录内容")

        return "\n".join(lines)

    def _scan_directory(self, rel_path: str) -> list[str]:
        """扫描目录,返回文件路径列表"""
        dir_path = self.workspace_dir / rel_path
        if not dir_path.exists():
            return []

        files = []
        for item in sorted(dir_path.iterdir()):
            if item.is_file() and item.suffix == '.md':
                files.append(str(item.relative_to(self.workspace_dir)))

        return files
```

### 2.2 TraceWriter

**职责**: 记录工具调用

**文件**: `backend/graph/trace_writer.py`

```python
import json
from pathlib import Path
from datetime import datetime

class TraceWriter:
    """记录工具调用到 trace"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.trace_dir = workspace_dir / "context_trace"
        self.trace_dir.mkdir(exist_ok=True)

    def write_trace(self, session_id: str, tool_calls: list[dict]):
        """
        写入 trace

        Args:
            session_id: 会话 ID
            tool_calls: 工具调用列表
        """
        trace_file = self.trace_dir / f"{session_id}.json"

        # 读取现有 trace
        if trace_file.exists():
            trace_data = json.loads(trace_file.read_text())
        else:
            trace_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "tool_calls": []
            }

        # 追加新的工具调用
        trace_data["tool_calls"].extend(tool_calls)
        trace_data["updated_at"] = datetime.now().isoformat()

        # 写入
        trace_file.write_text(json.dumps(trace_data, indent=2, ensure_ascii=False))
```

---

## 三、Phase 4: 6 个核心工具 (LangChain 原生)

### 3.1 工具列表

| # | 工具 | LangChain 类 | 文件 |
|---|------|-------------|------|
| 1 | read_file | `ReadFileTool` | `backend/tools/read_file_tool.py` |
| 2 | terminal | `ShellTool` | `backend/tools/terminal_tool.py` |
| 3 | python_repl | `PythonREPLTool` | `backend/tools/python_repl_tool.py` |
| 4 | fetch_url | `RequestsGetTool` (封装) | `backend/tools/fetch_url_tool.py` |
| 5 | search_knowledge_base | LlamaIndex | `backend/tools/search_knowledge_tool.py` |
| 6 | web_search | Brave API / Tavily | `backend/tools/web_search_tool.py` |

### 3.2 Tool 1: read_file

**文件**: `backend/tools/read_file_tool.py`

```python
from langchain_community.tools.file_management import ReadFileTool
from pathlib import Path

def create_read_file_tool(workspace_dir: Path):
    """创建 read_file 工具 (LangChain 原生)"""
    return ReadFileTool(
        root_dir=str(workspace_dir),
        name="read_file",
        description=(
            "读取文件内容。"
            "参数: file_path (相对于 workspace 的路径)"
            "返回: 文件内容"
        )
    )
```

### 3.3 Tool 2: terminal

**文件**: `backend/tools/terminal_tool.py`

```python
from langchain_community.tools import ShellTool
from pathlib import Path

# 危险命令黑名单
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "dd",
    "mkfs",
    "format",
    "> /dev/sda",
    ":(){ :|:& };:",
    "chmod -R 777 /",
]

def is_dangerous(command: str) -> bool:
    """检查是否是危险命令"""
    cmd_lower = command.lower()
    return any(dangerous.lower() in cmd_lower for dangerous in DANGEROUS_COMMANDS)

def create_terminal_tool(workspace_dir: Path):
    """创建 terminal 工具 (LangChain 原生 + 安全检查)"""

    # 创建 ShellTool
    shell_tool = ShellTool()

    # 包装安全检查
    original_run = shell_tool._run

    def safe_run(command: str, **kwargs):
        if is_dangerous(command):
            return f"❌ 危险命令被拦截: {command}"
        return original_run(command, **kwargs)

    shell_tool._run = safe_run
    shell_tool.name = "terminal"
    shell_tool.description = (
        "执行 Shell 命令 (受限环境)。"
        "参数: command (Shell 命令)"
        "返回: 命令输出"
    )

    return shell_tool
```

### 3.4 Tool 3: python_repl

**文件**: `backend/tools/python_repl_tool.py`

```python
from langchain_experimental.tools import PythonREPLTool

def create_python_repl_tool():
    """创建 python_repl 工具 (LangChain 原生)"""
    return PythonREPLTool(
        name="python_repl",
        description=(
            "执行 Python 代码。"
            "参数: code (Python 代码字符串)"
            "返回: 代码输出"
        )
    )
```

### 3.5 Tool 4: fetch_url

**文件**: `backend/tools/fetch_url_tool.py`

```python
from langchain_community.tools import RequestsGetTool
from langchain.tools import Tool
import html2text

def create_fetch_url_tool():
    """创建 fetch_url 工具 (LangChain 原生 + HTML 清洗)"""

    # 创建 RequestsGetTool
    requests_tool = RequestsGetTool()

    # 创建 HTML 转 Markdown 转换器
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False

    def fetch_and_clean(url: str) -> str:
        """抓取 URL 并清洗为 Markdown"""
        try:
            # 获取原始 HTML
            html_content = requests_tool._run(url)

            # 转换为 Markdown
            markdown = h.handle(html_content)

            # 截断超长内容
            if len(markdown) > 10000:
                markdown = markdown[:10000] + "\n\n...[truncated]"

            return markdown
        except Exception as e:
            return f"❌ 抓取失败: {str(e)}"

    return Tool(
        name="fetch_url",
        description=(
            "抓取网页内容并转换为 Markdown。"
            "参数: url (网页 URL)"
            "返回: Markdown 格式的网页内容"
        ),
        func=fetch_and_clean
    )
```

### 3.6 Tool 5: search_knowledge_base

**文件**: `backend/tools/search_knowledge_tool.py`

```python
from langchain.tools import Tool
from pathlib import Path

def create_search_knowledge_tool(workspace_dir: Path):
    """创建 search_knowledge_base 工具 (LlamaIndex)"""

    # TODO: Phase 5 实现
    # 这里先返回一个占位工具

    def search_placeholder(query: str) -> str:
        return "⚠️ RAG 检索功能将在 Phase 5 实现"

    return Tool(
        name="search_knowledge_base",
        description=(
            "检索 knowledge/ 目录下的文档 (RAG)。"
            "参数: query (检索查询)"
            "返回: 相关文档片段"
        ),
        func=search_placeholder
    )
```

### 3.7 Tool 6: web_search

**文件**: `backend/tools/web_search_tool.py`

```python
from langchain.tools import Tool
import os

def create_web_search_tool():
    """创建 web_search 工具 (Brave API / Tavily)"""

    # 检查是否配置了 API Key
    brave_api_key = os.getenv("BRAVE_API_KEY")

    if not brave_api_key:
        # 未配置,返回占位工具
        def search_placeholder(query: str) -> str:
            return "⚠️ 网络搜索功能需要配置 BRAVE_API_KEY"

        return Tool(
            name="web_search",
            description="网络搜索 (需要配置 BRAVE_API_KEY)",
            func=search_placeholder
        )

    # TODO: Phase 5 实现 Brave API 集成
    def search_placeholder(query: str) -> str:
        return "⚠️ 网络搜索功能将在 Phase 5 实现"

    return Tool(
        name="web_search",
        description=(
            "网络搜索 (Brave API)。"
            "参数: query (搜索查询)"
            "返回: 搜索结果摘要"
        ),
        func=search_placeholder
    )
```

---

## 四、Assets 上传与溯源

### 4.1 Assets Upload API

**文件**: `backend/api/assets.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import hashlib

router = APIRouter(prefix="/api/assets", tags=["assets"])

@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    target_dir: str = "uploads"
):
    """上传文件到 assets"""
    # 验证 target_dir
    allowed_dirs = ["uploads", "data", "figures", "ppt_pack"]
    if target_dir not in allowed_dirs:
        raise HTTPException(400, f"Invalid target_dir: {target_dir}")

    # 保存文件
    workspace_dir = get_current_workspace()
    target_path = workspace_dir / "assets" / target_dir / file.filename
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入
    content = await file.read()
    target_path.write_bytes(content)

    # 计算 SHA256
    sha256 = hashlib.sha256(content).hexdigest()

    return {
        "saved_path": str(target_path.relative_to(workspace_dir)),
        "sha256": sha256,
        "size": len(content)
    }
```

### 4.2 溯源格式示例

**Memory 文件** (`memory/tasks/TASK_exp_005.md`):

```markdown
# 实验 005: XRD 表征

## 数据来源
**原始数据**: [XRD数据](assets/data/exp_005_xrd.csv)
**谱图**: [XRD谱图](assets/figures/exp_005_xrd.png)

## 分析结果
...
```

---

## 五、开发步骤

### Step 1: 实现 PromptBuilder (极简版)
- [ ] 创建 `backend/graph/prompt_builder.py`
- [ ] 实现 6 个 block 的拼接逻辑
- [ ] ❌ 不实现 ContextOrchestrator

### Step 2: 实现 TraceWriter
- [ ] 创建 `backend/graph/trace_writer.py`

### Step 3: 实现 6 个核心工具
- [ ] `backend/tools/read_file_tool.py` (LangChain ReadFileTool)
- [ ] `backend/tools/terminal_tool.py` (LangChain ShellTool + 安全检查)
- [ ] `backend/tools/python_repl_tool.py` (LangChain PythonREPLTool)
- [ ] `backend/tools/fetch_url_tool.py` (LangChain RequestsGetTool + HTML清洗)
- [ ] `backend/tools/search_knowledge_tool.py` (占位,Phase 5 实现)
- [ ] `backend/tools/web_search_tool.py` (占位,Phase 5 实现)

### Step 4: 实现 Assets Upload API
- [ ] 创建 `backend/api/assets.py`

### Step 5: 集成到 AgentManager
- [ ] 修改 `backend/graph/agent.py`
- [ ] 注册 6 个工具

### Step 6: 修改 Chat API
- [ ] 修改 `backend/api/chat.py`
- [ ] 集成 PromptBuilder → Agent → TraceWriter

### Step 7: 端到端测试
- [ ] 测试渐进式披露 (LLM 主动读取文件)
- [ ] 测试数据分析 (python_repl)
- [ ] 测试溯源 (assets 路径)

---

## 六、验收标准

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **PromptBuilder** | 能构建包含 Memory Map 的 System Prompt | ⏳ |
| **❌ 无 ContextOrchestrator** | 不预选文件,完全由 LLM 决策 | ⏳ |
| **6 个核心工具** | 全部使用 LangChain 原生工具 | ⏳ |
| **渐进式披露** | LLM 能主动使用 read_file 读取文件 | ⏳ |
| **Assets 溯源** | Memory 文件包含 assets 路径 | ⏳ |
| **端到端测试** | 数据分析场景测试通过 | ⏳ |

---

## 七、关键设计决策

### 决策 1: ❌ 不实现 ContextOrchestrator

**理由**:
- 完全遵循 Tool-Driven 理念
- LLM 自主决策读取哪些文件
- 符合渐进式披露原则

### 决策 2: 使用 LangChain 原生工具

**理由**:
- PRD 明确要求
- 减少自定义代码
- 更好的维护性

### 决策 3: Phase 4 只实现 4 个工具,2 个占位

**理由**:
- read_file/terminal/python_repl/fetch_url 是核心
- search_knowledge_base 和 web_search 在 Phase 5 实现
- 保持最小 MVP

---

**准备开始开发!**
