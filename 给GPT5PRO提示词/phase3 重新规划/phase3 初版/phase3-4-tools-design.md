# Phase 3-4: 完整工具集设计 (含 terminal 和 python_repl)

**版本**: v1.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## 一、工具集概述

### 1.1 完整工具列表

根据 PRD 要求,Phase 3-4 必须实现以下工具:

| # | 工具名称 | 功能 | Phase | 优先级 |
|---|---------|------|-------|--------|
| 1 | **read_file** | 读取文件内容 | Phase 3 | P0 |
| 2 | **write_file** | 写入文件 | Phase 3 | P0 |
| 3 | **list_directory** | 列出目录内容 | Phase 3 | P0 |
| 4 | **terminal** | 执行 Shell 命令 | Phase 4 | P0 |
| 5 | **python_repl** | 执行 Python 代码 | Phase 4 | P0 |
| 6 | **fetch_url** | 抓取网页内容 | Phase 5 | P1 |
| 7 | **web_search** | 网络搜索 | Phase 5 | P1 |
| 8 | **search_knowledge_base** | RAG 检索 | Phase 5 | P1 |

**本文档重点**: Phase 3-4 的 5 个核心工具 (1-5)

---

## 二、Phase 3 工具: Memory 操作

### 2.1 read_file 工具

**功能**: 读取 workspace 中的文件内容

**实现**: `backend/tools/read_file_tool.py`

```python
from langchain.tools import Tool
from pathlib import Path
from backend.graph.path_utils import resolve_safe_path

def read_file_impl(path: str, workspace_dir: Path) -> str:
    """
    读取文件内容

    Args:
        path: 相对于 workspace 的路径
        workspace_dir: workspace 根目录

    Returns:
        文件内容 (自动截断超过 20000 字符)

    Raises:
        ValueError: 路径不安全或文件不存在
    """
    # 安全检查
    safe_path = resolve_safe_path(workspace_dir, path)

    if not safe_path.exists():
        raise ValueError(f"文件不存在: {path}")

    if not safe_path.is_file():
        raise ValueError(f"不是文件: {path}")

    # 读取内容
    try:
        content = safe_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # 尝试其他编码
        content = safe_path.read_text(encoding='gbk')

    # 自动截断
    if len(content) > 20000:
        content = content[:20000] + "\n\n...[truncated]"

    return content


def create_read_file_tool(workspace_dir: Path) -> Tool:
    """创建 read_file 工具"""

    def _read_file(path: str) -> str:
        return read_file_impl(path, workspace_dir)

    return Tool(
        name="read_file",
        description=(
            "读取文件内容。"
            "参数: path (相对于 workspace 的路径,如 'memory/identity/project.md')"
            "返回: 文件内容 (自动截断超过 20000 字符)"
        ),
        func=_read_file
    )
```

**安全措施**:
- ✅ 路径安全检查 (resolve_safe_path)
- ✅ 只能读取 workspace 内的文件
- ✅ 自动截断超大文件
- ✅ 支持多种编码

**使用示例**:
```python
# Agent 调用
content = read_file("memory/identity/project.md")
```

---

### 2.2 write_file 工具

**功能**: 写入文件到 memory 目录

**实现**: `backend/tools/write_file_tool.py`

```python
from langchain.tools import Tool
from pathlib import Path
from backend.graph.path_utils import resolve_safe_path

def write_file_impl(path: str, content: str, workspace_dir: Path) -> str:
    """
    写入文件 (创建或覆盖)

    Args:
        path: 相对于 workspace 的路径 (必须在 memory/ 目录下)
        content: 文件内容
        workspace_dir: workspace 根目录

    Returns:
        成功消息

    Raises:
        ValueError: 路径不安全或不在 memory/ 目录下
    """
    # 检查路径必须在 memory/ 目录下
    if not path.startswith("memory/"):
        raise ValueError(f"只能写入 memory/ 目录,当前路径: {path}")

    # 安全检查
    safe_path = resolve_safe_path(
        workspace_dir,
        path,
        require_writable=True
    )

    # 自动创建父目录
    safe_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    safe_path.write_text(content, encoding='utf-8')

    return f"✅ 文件写入成功: {path}"


def create_write_file_tool(workspace_dir: Path) -> Tool:
    """创建 write_file 工具"""

    def _write_file(path: str, content: str) -> str:
        return write_file_impl(path, content, workspace_dir)

    return Tool(
        name="write_file",
        description=(
            "写入文件到 memory 目录。"
            "参数: path (相对路径,必须在 memory/ 下), content (文件内容)"
            "返回: 成功消息"
        ),
        func=_write_file
    )
```

**安全措施**:
- ✅ 限制只能写入 memory/ 目录
- ✅ 路径安全检查
- ✅ 自动创建父目录
- ✅ 防止覆盖控制层文件

**使用示例**:
```python
# Agent 调用
result = write_file(
    "memory/tasks/TASK_exp_005.md",
    "## 实验 005\n\n### 数据\n..."
)
```

---

### 2.3 list_directory 工具

**功能**: 列出目录内容

**实现**: `backend/tools/list_directory_tool.py`

```python
from langchain.tools import Tool
from pathlib import Path
from backend.graph.path_utils import resolve_safe_path

def list_directory_impl(path: str, workspace_dir: Path) -> str:
    """
    列出目录内容

    Args:
        path: 相对于 workspace 的路径
        workspace_dir: workspace 根目录

    Returns:
        目录内容列表 (格式化字符串)

    Raises:
        ValueError: 路径不安全或不是目录
    """
    # 安全检查
    safe_path = resolve_safe_path(workspace_dir, path)

    if not safe_path.exists():
        raise ValueError(f"目录不存在: {path}")

    if not safe_path.is_dir():
        raise ValueError(f"不是目录: {path}")

    # 列出内容
    items = []
    for item in sorted(safe_path.iterdir()):
        # 跳过隐藏文件
        if item.name.startswith('.') or item.name.startswith('_'):
            continue

        if item.is_dir():
            items.append(f"📁 {item.name}/")
        else:
            # 显示文件大小
            size = item.stat().st_size
            size_str = _format_size(size)
            items.append(f"📄 {item.name} ({size_str})")

    if not items:
        return f"目录为空: {path}"

    return "\n".join([f"目录: {path}", ""] + items)


def _format_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"


def create_list_directory_tool(workspace_dir: Path) -> Tool:
    """创建 list_directory 工具"""

    def _list_directory(path: str) -> str:
        return list_directory_impl(path, workspace_dir)

    return Tool(
        name="list_directory",
        description=(
            "列出目录内容。"
            "参数: path (相对于 workspace 的路径,如 'memory/tasks')"
            "返回: 目录内容列表"
        ),
        func=_list_directory
    )
```

**安全措施**:
- ✅ 路径安全检查
- ✅ 过滤隐藏文件
- ✅ 显示文件大小

**使用示例**:
```python
# Agent 调用
content = list_directory("memory/tasks")
# 输出:
# 目录: memory/tasks
#
# 📄 TASK_exp_001.md (2.3KB)
# 📄 TASK_exp_002.md (1.8KB)
# 📄 TASK_exp_003.md (3.1KB)
```

---

## 三、Phase 4 工具: 代码执行

### 3.1 terminal 工具

**功能**: 执行 Shell 命令 (受限环境)

**实现**: `backend/tools/terminal_tool.py`

```python
from langchain_community.tools import ShellTool
from langchain.tools import Tool
from pathlib import Path
import subprocess
import shlex

# 黑名单: 危险命令
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "dd",
    "mkfs",
    "format",
    "> /dev/sda",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "chown -R",
]

def is_dangerous_command(command: str) -> bool:
    """检查是否是危险命令"""
    command_lower = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous.lower() in command_lower:
            return True
    return False


def terminal_impl(command: str, workspace_dir: Path) -> str:
    """
    执行 Shell 命令 (受限环境)

    Args:
        command: Shell 命令
        workspace_dir: workspace 根目录 (作为 CWD)

    Returns:
        命令输出 (stdout + stderr)

    Raises:
        ValueError: 危险命令被拦截
        subprocess.TimeoutExpired: 命令超时
    """
    # 黑名单检查
    if is_dangerous_command(command):
        raise ValueError(f"❌ 危险命令被拦截: {command}")

    # 执行命令
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(workspace_dir),
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            encoding='utf-8',
            errors='replace'
        )

        # 合并 stdout 和 stderr
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        # 截断超长输出
        if len(output) > 10000:
            output = output[:10000] + "\n\n...[truncated]"

        # 添加返回码
        if result.returncode != 0:
            output += f"\n\n[返回码: {result.returncode}]"

        return output

    except subprocess.TimeoutExpired:
        raise ValueError(f"❌ 命令超时 (30秒): {command}")


def create_terminal_tool(workspace_dir: Path) -> Tool:
    """创建 terminal 工具"""

    def _terminal(command: str) -> str:
        return terminal_impl(command, workspace_dir)

    return Tool(
        name="terminal",
        description=(
            "执行 Shell 命令 (受限环境)。"
            "参数: command (Shell 命令,如 'ls -la')"
            "返回: 命令输出 (stdout + stderr)"
            "注意: 危险命令会被拦截,超时时间 30 秒"
        ),
        func=_terminal
    )
```

**安全措施**:
- ✅ 黑名单拦截危险命令
- ✅ CWD 限制在 workspace
- ✅ 30 秒超时
- ✅ 输出截断 (10000 字符)

**使用示例**:
```python
# Agent 调用
output = terminal("ls -la memory/tasks")
# 输出:
# total 24
# drwxr-xr-x  5 user  staff   160 Mar  9 10:00 .
# drwxr-xr-x  8 user  staff   256 Mar  9 09:00 ..
# -rw-r--r--  1 user  staff  2345 Mar  9 10:00 TASK_exp_001.md
# -rw-r--r--  1 user  staff  1876 Mar  9 10:00 TASK_exp_002.md
```

---

### 3.2 python_repl 工具

**功能**: 执行 Python 代码 (隔离环境)

**实现**: `backend/tools/python_repl_tool.py`

```python
from langchain_experimental.tools import PythonREPLTool
from langchain.tools import Tool
from pathlib import Path
import sys
import io
import contextlib

def python_repl_impl(code: str, workspace_dir: Path) -> str:
    """
    执行 Python 代码 (隔离环境)

    Args:
        code: Python 代码
        workspace_dir: workspace 根目录 (添加到 sys.path)

    Returns:
        代码输出 (stdout + 返回值)

    Raises:
        Exception: 代码执行错误
    """
    # 创建隔离的 stdout
    stdout_buffer = io.StringIO()

    # 添加 workspace 到 sys.path
    workspace_str = str(workspace_dir)
    if workspace_str not in sys.path:
        sys.path.insert(0, workspace_str)

    try:
        # 捕获 stdout
        with contextlib.redirect_stdout(stdout_buffer):
            # 执行代码
            exec_globals = {
                '__builtins__': __builtins__,
                'workspace_dir': workspace_dir,
            }
            exec(code, exec_globals)

        # 获取输出
        output = stdout_buffer.getvalue()

        # 截断超长输出
        if len(output) > 10000:
            output = output[:10000] + "\n\n...[truncated]"

        return output if output else "✅ 代码执行成功 (无输出)"

    except Exception as e:
        return f"❌ 执行错误: {type(e).__name__}: {str(e)}"


def create_python_repl_tool(workspace_dir: Path) -> Tool:
    """创建 python_repl 工具"""

    def _python_repl(code: str) -> str:
        return python_repl_impl(code, workspace_dir)

    return Tool(
        name="python_repl",
        description=(
            "执行 Python 代码。"
            "参数: code (Python 代码字符串)"
            "返回: 代码输出 (stdout + 返回值)"
            "注意: 代码在隔离环境中执行,workspace_dir 变量可用"
        ),
        func=_python_repl
    )
```

**安全措施**:
- ✅ 隔离的 stdout
- ✅ workspace_dir 自动添加到 sys.path
- ✅ 异常捕获
- ✅ 输出截断

**使用示例**:
```python
# Agent 调用
output = python_repl("""
import pandas as pd

# 读取 CSV
df = pd.read_csv('assets/data/exp_005.csv')

# 统计
print(df.describe())
""")
```

---

## 四、工具注册与集成

### 4.1 在 AgentManager 中注册工具

**文件**: `backend/graph/agent.py`

```python
from tools.read_file_tool import create_read_file_tool
from tools.write_file_tool import create_write_file_tool
from tools.list_directory_tool import create_list_directory_tool
from tools.terminal_tool import create_terminal_tool
from tools.python_repl_tool import create_python_repl_tool

class AgentManager:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

        # 创建工具
        self.tools = [
            create_read_file_tool(workspace_dir),
            create_write_file_tool(workspace_dir),
            create_list_directory_tool(workspace_dir),
            create_terminal_tool(workspace_dir),
            create_python_repl_tool(workspace_dir),
        ]

    def _build_agent(self):
        """构建 Agent"""
        from langchain.agents import create_agent

        agent = create_agent(
            llm=self.llm,
            tools=self.tools,
            ...
        )

        return agent
```

### 4.2 在 PromptBuilder 中说明工具

**文件**: `backend/graph/prompt_builder.py`

```python
def _build_tooling_block(self) -> str:
    """构建 Tooling 块"""
    return """## Tooling

Available tools:
- **read_file(path)**: 读取文件内容
- **write_file(path, content)**: 写入文件到 memory/ 目录
- **list_directory(path)**: 列出目录内容
- **terminal(command)**: 执行 Shell 命令 (受限环境)
- **python_repl(code)**: 执行 Python 代码

Tool usage guidelines:
1. Use read_file to access memory and assets
2. Use write_file to persist insights to memory
3. Use python_repl for data analysis and visualization
4. Use terminal for system operations
5. Always check file existence before reading
"""
```

---

## 五、工具使用场景

### 5.1 场景 1: 数据分析

**用户**: "分析 exp_005.csv 的动力学数据,拟合 kobs"

**Agent 执行**:
```python
# Step 1: 读取数据
data = read_file("assets/data/exp_005.csv")

# Step 2: 分析数据
output = python_repl("""
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('assets/data/exp_005.csv')

# 定义一阶动力学模型
def first_order(t, C0, k):
    return C0 * np.exp(-k * t)

# 拟合
popt, pcov = curve_fit(first_order, df['time'], df['concentration'])
C0, k = popt

print(f"拟合结果: C0={C0:.2f}, kobs={k:.4f} min^-1")

# 作图
plt.figure(figsize=(8, 6))
plt.scatter(df['time'], df['concentration'], label='实验数据')
plt.plot(df['time'], first_order(df['time'], *popt), 'r-', label='拟合曲线')
plt.xlabel('Time (min)')
plt.ylabel('Concentration (mg/L)')
plt.legend()
plt.savefig('assets/figures/exp_005_kinetics.png', dpi=300)
print("图表已保存: assets/figures/exp_005_kinetics.png")
""")

# Step 3: 写入 Task
write_file("memory/tasks/TASK_exp_005.md", f"""
## 实验 005: 动力学分析

### 数据来源
[原始数据](assets/data/exp_005.csv)

### 分析结果
{output}

### 图表
[动力学曲线](assets/figures/exp_005_kinetics.png)
""")
```

---

### 5.2 场景 2: 合成 checklist

**用户**: "整理今天的合成流程"

**Agent 执行**:
```python
# Step 1: 读取实验室约束
lab_context = read_file("memory/identity/lab_context.md")

# Step 2: 读取今天的日志
today_log = read_file("memory/timeline/days/2025-11-23.md")

# Step 3: 生成 checklist
checklist = """
## 合成 Checklist (2025-11-23)

### 准备阶段 (9:00-9:30)
- [ ] 称量 Co(NO3)2·6H2O: 291mg (容器: 50mL烧杯, 标号: A1)
- [ ] 称量 Ce(NO3)3·6H2O: 93mg (容器: 50mL烧杯, 标号: A2)
- [ ] 量取乙二醇: 40mL (容器: 量筒)

⚠️ 注意: A1 和 A2 容器不要混淆

### 搅拌阶段 (9:30-9:40)
- [ ] 将 A1 和 A2 倒入水热釜内胆
- [ ] 加入搅拌子,600转搅拌 10min

### 水热阶段 (9:40-21:40)
- [ ] 转移到水热釜,180°C 水热 12h
- [ ] 标号: Ce-Co3O4-20251123

⚠️ 注意: 水热釜标号要清晰

### 洗涤阶段 (次日 9:00-10:00)
- [ ] 离心 8000rpm × 5min
- [ ] 乙醇洗涤 3 次
- [ ] 去离子水洗涤 2 次

### 煅烧阶段 (次日 10:00-14:00)
- [ ] 60°C 烘干 2h
- [ ] 350°C 煅烧 2h (升温速率: 5°C/min)
"""

# Step 4: 写入今天的日志
write_file("memory/timeline/days/2025-11-23.md", today_log + "\n\n" + checklist)
```

---

### 5.3 场景 3: 阶段汇报素材整理

**用户**: "整理 R06 的素材文件"

**Agent 执行**:
```python
# Step 1: 列出素材目录
files = list_directory("assets/ppt_pack/R06_20251123")

# Step 2: 分析图片尺寸
output = python_repl("""
from PIL import Image
import os

ppt_dir = 'assets/ppt_pack/R06_20251123'
files = os.listdir(ppt_dir)

print("素材清单:")
for f in sorted(files):
    path = os.path.join(ppt_dir, f)
    if f.endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(path)
        print(f"📷 {f}: {img.size[0]}x{img.size[1]}px")
    elif f.endswith('.csv'):
        import pandas as pd
        df = pd.read_csv(path)
        print(f"📊 {f}: {len(df)} 行 × {len(df.columns)} 列")
    else:
        size = os.path.getsize(path)
        print(f"📄 {f}: {size/1024:.1f}KB")
""")

# Step 3: 写入 Pack
write_file("memory/packs/PACK_stage_report_R06.md", f"""
## 第6次阶段汇报素材清单

### 素材目录
assets/ppt_pack/R06_20251123/

### 文件列表
{output}

### 使用建议
- 合成照片: 用于"本期工作-材料合成"页
- XRD谱图: 用于"关键数据-晶体结构"页
- DPD显色照片: 用于"关键数据-ClO2生成"页
""")
```

---

## 六、工具安全总结

### 6.1 安全措施汇总

| 工具 | 安全措施 |
|------|---------|
| **read_file** | 路径检查、workspace 限制、自动截断 |
| **write_file** | 路径检查、memory/ 限制、自动创建目录 |
| **list_directory** | 路径检查、过滤隐藏文件 |
| **terminal** | 黑名单拦截、CWD 限制、超时、输出截断 |
| **python_repl** | 隔离环境、异常捕获、输出截断 |

### 6.2 审计日志

所有工具调用都会记录到 Trace:

```json
{
  "tool_calls": [
    {
      "tool": "read_file",
      "args": {"path": "memory/identity/project.md"},
      "result": "...",
      "timestamp": "2025-11-23T10:00:00"
    },
    {
      "tool": "python_repl",
      "args": {"code": "import pandas as pd\n..."},
      "result": "拟合结果: kobs=0.0234 min^-1",
      "timestamp": "2025-11-23T10:01:00"
    },
    {
      "tool": "write_file",
      "args": {
        "path": "memory/tasks/TASK_exp_005.md",
        "content": "..."
      },
      "result": "✅ 文件写入成功",
      "timestamp": "2025-11-23T10:02:00"
    }
  ]
}
```

---

## 七、实施步骤

### Step 1: 实现 Phase 3 工具
- ✅ read_file_tool.py
- ✅ write_file_tool.py
- ✅ list_directory_tool.py

### Step 2: 实现 Phase 4 工具
- ⏳ terminal_tool.py
- ⏳ python_repl_tool.py

### Step 3: 集成到 AgentManager
- ⏳ 注册所有工具
- ⏳ 更新 PromptBuilder

### Step 4: 端到端测试
- ⏳ 测试数据分析场景
- ⏳ 测试合成 checklist 场景
- ⏳ 测试阶段汇报场景

---

## 八、验收标准

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **read_file** | 能正确读取 memory 和 assets 文件 | ⏳ |
| **write_file** | 能正确写入 memory 文件,拦截非法路径 | ⏳ |
| **list_directory** | 能正确列出目录内容 | ⏳ |
| **terminal** | 能执行命令,拦截危险命令 | ⏳ |
| **python_repl** | 能执行 Python 代码,支持数据分析 | ⏳ |
| **安全检查** | 所有工具通过安全测试 | ⏳ |
| **审计日志** | 所有工具调用记录到 Trace | ⏳ |

---

**文档完成** | 2026-03-09
