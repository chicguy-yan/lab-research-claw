# Phase 3 + Phase 4 合并方案 — Tool-Driven Memory Access

## 开发文档

**版本**: v1.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw
**方案**: Tool-Driven Memory Access (工具驱动的按需记忆访问)

---

## 1. 架构概览

### 1.1 核心理念

这个新架构采用 **Tool-Driven** 方式,让 LLM 通过工具主动访问 memory,而不是预先注入所有可能需要的内容。

**核心原则**:
- System Prompt 极简化: 只包含控制层的六大 md 文件
- Memory 三层只提供目录结构 (文件路径列表)
- LLM 通过 `read_file` 工具按需读取 memory 文件
- LLM 通过 `write_file` 工具直接写入 memory
- 工具调用本身就是决策,不需要额外的 `memory_decision` 结构化输出

### 1.2 与原 Phase 3 的对比

| 维度 | 原 Phase 3 | 新方案 (Phase 3+4 合并) |
|------|-----------|----------------------|
| **System Prompt** | 控制层 + 选中的 memory 文件内容 | 仅控制层 + memory 目录列表 |
| **Memory 读取** | ContextOrchestrator 预先选择并注入 | LLM 通过 `read_file` 工具按需读取 |
| **Memory 写入** | `memory_decision` 结构化输出 | 直接通过 `write_file` 工具 |
| **Context 大小** | 大 (预先注入) | 小 (按需读取) |
| **灵活性** | 低 (依赖预测) | 高 (LLM 自主决策) |
| **架构复杂度** | 需要 ContextOrchestrator 的复杂选择逻辑 | 简化,移除 ContextOrchestrator |

### 1.3 为什么这个方案更优雅

1. **Context 更小**: 不预先注入可能用不到的 memory 内容,节省 token
2. **更灵活**: LLM 根据实际需要决定读取哪些文件,而不是依赖预测
3. **更符合 Agent 理念**: 主动工具使用,而不是被动接收
4. **简化架构**: 移除 ContextOrchestrator 的复杂选择逻辑
5. **审计更清晰**: 工具调用本身就是 memory 访问的审计记录

---

## 2. Phase 3+4 合并后的核心模块

### 2.1 Phase 3 部分 (简化)

#### PromptBuilder (简化版)

**职责**: 构建 System Prompt,包含:
- Block 1-6: 控制层六大 md (完整内容)
- Block 7: Memory Map (仅目录结构,不注入内容)
- Block 8: Tools 说明 (read_file, write_file, list_directory)

**关键变化**:
- 不再需要 ContextOrchestrator 预先选择 memory
- 只注入 memory 目录结构,不注入文件内容
- 添加工具使用说明

#### TraceWriter (保持不变)

**职责**: 记录每轮对话的审计信息

**记录内容**:
- 工具调用 (read_file/write_file 就是 memory 访问的 trace)
- 不再需要 `memory_decision` 字段 (工具调用本身就是决策)

### 2.2 Phase 4 部分 (核心工具)

#### read_file 工具

```python
def read_file(path: str) -> str:
    """
    读取文件内容

    Args:
        path: 相对于 workspace 的路径

    Returns:
        文件内容 (自动截断超过 20000 字符)
    """
```

#### write_file 工具

```python
def write_file(path: str, content: str) -> str:
    """
    写入文件 (创建或覆盖)

    Args:
        path: 相对于 workspace 的路径 (必须在 memory/ 目录下)
        content: 文件内容

    Returns:
        成功消息
    """
```

#### list_directory 工具

```python
def list_directory(path: str) -> list[str]:
    """
    列出目录内容

    Args:
        path: 相对于 workspace 的路径

    Returns:
        文件和目录列表
    """
```

#### 工具执行框架

- 使用 LangChain 的 tools 机制
- 在 AgentManager 中注册工具
- 路径安全检查 (复用 Phase 2 的 `resolve_safe_path`)

---

## 3. System Prompt 设计

### 3.1 完整结构

```markdown
# Block 1: Identity
You are a personal assistant running inside OpenClaw.

# Block 2: Tooling
Available tools:
- read_file(path): 读取文件内容
- write_file(path, content): 写入文件
- list_directory(path): 列出目录内容

# Block 3: Workspace
工作目录: /workspace

规则:
- 信息不足时,使用 read_file 读取 memory 文件
- 需要沉淀时,使用 write_file 写入 memory
- 禁止脑补,必须基于实际文件内容

# Block 4: Inbound Context
{
  "platform": "darwin",
  "timezone": "Asia/Shanghai",
  "language": "zh-CN",
  "session_type": "research",
  "current_date": "2026-03-09"
}

# Block 5: Control Plane Files

## AGENTS.md
{完整内容}

## SOUL.md
{完整内容}

## IDENTITY.md
{完整内容}

## USER.md
{完整内容}

## SKILLS_SNAPSHOT.md
{完整内容}

## memory/identity/project.md
{完整内容}

# Block 6: Memory Map (仅目录结构，这里只是例子，这个目录结构是程序运行中获取的)

## Layer 1 — identity/
- memory/identity/user.md
- memory/identity/lab_context.md
- memory/identity/context_budget.md

## Layer 2 — timeline/
- memory/timeline/180d_index.md
- memory/timeline/phases/P01_bootstrap.md
- memory/timeline/weeks/WEEK_01.md
- memory/timeline/days/2026-03-08.md

## Layer 3 — concepts/ + tasks/ + packs/
- memory/concepts/CONCEPT_chlorite_activation.md
- memory/tasks/TASK_baseline_activity.md
- memory/tasks/TASK_exp_003.md
- memory/packs/PACK_stage_report_R01.md

**提示**: 如果需要了解某个文件的内容,使用 read_file(path) 工具。
```

### 3.2 关键设计点

1. **Block 1-5**: 控制层完整注入 (与原 Phase 3 相同)
2. **Block 6**: 只提供 memory 目录结构,不注入内容
3. **工具提示**: 明确告诉 LLM 如何使用工具访问 memory

---

## 4. 对话流程示例

### 4.1 场景 1: 实验闭环

**用户**: "XRD 数据显示 Co(IV) 特征峰在 2θ=31.2°"

**LLM 思考**:
1. 这是实验数据,需要更新实验任务
2. 先读取当前的实验任务文件

**LLM 调用**: `read_file("memory/tasks/TASK_exp_005.md")`

**系统返回**: `{当前任务内容}`

**LLM 思考**:
3. 需要在任务中添加 XRD 表征结果

**LLM 调用**: `write_file("memory/tasks/TASK_exp_005.md", {更新后的内容})`

**系统返回**: "文件写入成功"

**LLM 回答**: "根据 XRD 数据,Co(IV) 特征峰确认...我已更新实验任务记录。"

### 4.2 场景 2: 阶段汇报

**用户**: "准备第3次阶段汇报"

**LLM 思考**:
1. 需要了解当前进度
2. 先读取 180d_index 和最近的 stage_report

**LLM 调用**: `read_file("memory/timeline/180d_index.md")`
**LLM 调用**: `read_file("memory/timeline/stage_reports/R02.md")`

**LLM 思考**:
3. 基于当前进度,创建新的 stage_report

**LLM 调用**: `write_file("memory/timeline/stage_reports/R03.md", {汇报内容})`

**LLM 回答**: "已为您准备第3次阶段汇报..."

---

## 5. Trace 记录

### 5.1 Trace 结构

```json
{
  "trace_id": "uuid",
  "tool_calls": [
    {
      "tool": "read_file",
      "args": {"path": "memory/tasks/TASK_exp_005.md"},
      "result": "...",
      "timestamp": "..."
    },
    {
      "tool": "write_file",
      "args": {
        "path": "memory/tasks/TASK_exp_005.md",
        "content": "..."
      },
      "result": "success",
      "timestamp": "..."
    }
  ]
}
```

### 5.2 关键点

- 工具调用本身就是 memory 访问的审计记录
- 不需要单独的 `memory_decision` 字段
- 所有 read_file/write_file 调用都记录在 trace 中

---

## 6. 实施步骤

### Step 1: 简化 PromptBuilder

**任务**:
- 移除 ContextOrchestrator (不再需要预先选择 memory)
- 修改 PromptBuilder,只注入控制层 + memory 目录列表
- 添加工具使用说明到 System Prompt

**文件**:
- `backend/graph/prompt_builder.py` (修改)
- 删除 `backend/graph/context_orchestrator.py` (不再需要)

### Step 2: 实现核心工具

**任务**:
- 实现 `read_file` 工具 (带路径安全检查)
- 实现 `write_file` 工具 (限制在 memory/ 目录)
- 实现 `list_directory` 工具

**文件**:
- `backend/tools/read_file_tool.py` (新建)
- `backend/tools/write_file_tool.py` (新建)
- `backend/tools/list_directory_tool.py` (新建)

**安全检查**:
- 复用 Phase 2 的 `resolve_safe_path`
- write_file 限制在 `memory/` 目录
- 自动截断超过 20000 字符的文件

### Step 3: 集成工具到 Agent

**任务**:
- 使用 LangChain 的 tools 机制
- 修改 AgentManager,注册工具

**文件**:
- `backend/graph/agent.py` (修改)

### Step 4: 修改 TraceWriter

**任务**:
- 记录工具调用 (read_file/write_file)
- 移除 `memory_decision` 字段

**文件**:
- `backend/graph/trace_writer.py` (修改)

### Step 5: 端到端测试

**测试项**:
1. 测试 LLM 能否正确使用工具读取 memory
2. 测试 LLM 能否正确使用工具写入 memory
3. 测试 trace 记录完整性
4. 测试路径安全检查

---

## 7. 优势与挑战

### 7.1 优势

1. **Context 更小**: 不预先注入可能用不到的 memory 内容,节省大量 token
2. **更灵活**: LLM 根据实际需要决定读取哪些文件,而不是依赖预测
3. **更符合 Agent 理念**: 主动工具使用,体现真正的 Agent 能力
4. **简化架构**: 移除 ContextOrchestrator 的复杂选择逻辑
5. **工具调用即审计**: 不需要额外的 `memory_decision` 字段,工具调用本身就是决策记录
6. **更好的可扩展性**: 添加新的 memory 文件不需要修改选择逻辑

### 7.2 挑战

1. **多次工具调用可能增加延迟**: 每次 read_file 都是一次 LLM 调用
2. **需要 LLM 有良好的工具使用能力**: 依赖模型正确判断需要读取哪些文件
3. **需要设计好 memory 目录结构的展示**: 让 LLM 能快速定位需要的文件
4. **可能增加 token 消耗**: 虽然 context 更小,但多次调用可能总消耗更多

### 7.3 缓解策略

1. **优化目录结构展示**: 使用清晰的层级和命名规范
2. **提供文件描述**: 在目录列表中添加简短的文件用途说明
3. **缓存机制**: 对频繁访问的文件进行缓存
4. **批量读取**: 允许一次读取多个相关文件

---

## 8. 与原 Phase 3 验收标准的对应

| 原验收标准 | 新方案如何满足 |
|-----------|--------------|
| **Control Plane 参与行为约束** | ✓ 控制层完整注入到 System Prompt (Block 1-5) |
| **assets → memory 沉淀链成立** | ✓ 通过 write_file 工具实现沉淀 |
| **write-or-skip 清楚** | ✓ 工具调用本身就是决策,trace 中清晰记录 |
| **trace 能回放** | ✓ 记录所有工具调用 (read_file/write_file) |

---

## 9. 文件清单

### 9.1 新建文件

```
backend/
├── tools/
│   ├── read_file_tool.py          # 新建: 读取文件工具
│   ├── write_file_tool.py         # 新建: 写入文件工具
│   └── list_directory_tool.py     # 新建: 列出目录工具
```

### 9.2 修改文件

```
backend/
├── graph/
│   ├── agent.py                   # 修改: 注册工具
│   ├── prompt_builder.py          # 修改: 简化,只注入控制层+目录列表
│   └── trace_writer.py            # 修改: 记录工具调用
```

### 9.3 删除文件

```
backend/
├── graph/
│   └── context_orchestrator.py    # 删除: 不再需要预先选择 memory
```

---

## 10. 工具设计详解

### 10.1 read_file 工具

**功能**: 读取 workspace 中的文件内容

**参数**:
- `path` (str): 相对于 workspace 的路径

**返回**:
- 文件内容 (str),自动截断超过 20000 字符

**安全检查**:
- 使用 `resolve_safe_path` 防止路径遍历
- 只能读取 workspace 内的文件

**实现示例**:

```python
from langchain.tools import Tool
from backend.graph.path_utils import resolve_safe_path

def read_file_impl(path: str) -> str:
    """读取文件内容"""
    workspace_dir = get_current_workspace()
    safe_path = resolve_safe_path(workspace_dir, path)

    content = safe_path.read_text(encoding='utf-8')

    # 自动截断
    if len(content) > 20000:
        content = content[:20000] + "\n\n...[truncated]"

    return content

read_file_tool = Tool(
    name="read_file",
    description="读取文件内容。参数: path (相对于 workspace 的路径)",
    func=read_file_impl
)
```

### 10.2 write_file 工具

**功能**: 写入文件到 memory 目录

**参数**:
- `path` (str): 相对于 workspace 的路径 (必须在 memory/ 目录下)
- `content` (str): 文件内容

**返回**:
- 成功消息 (str)

**安全检查**:
- 使用 `resolve_safe_path` 防止路径遍历
- 限制只能写入 `memory/` 目录
- 自动创建父目录

**实现示例**:

```python
def write_file_impl(path: str, content: str) -> str:
    """写入文件"""
    workspace_dir = get_current_workspace()

    # 检查路径必须在 memory/ 目录下
    if not path.startswith("memory/"):
        raise ValueError("只能写入 memory/ 目录")

    safe_path = resolve_safe_path(
        workspace_dir,
        path,
        require_writable=True
    )

    # 自动创建父目录
    safe_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    safe_path.write_text(content, encoding='utf-8')

    return f"文件写入成功: {path}"

write_file_tool = Tool(
    name="write_file",
    description="写入文件到 memory 目录。参数: path, content",
    func=write_file_impl
)
```

### 10.3 list_directory 工具

**功能**: 列出目录内容

**参数**:
- `path` (str): 相对于 workspace 的路径

**返回**:
- 文件和目录列表 (list[str])

**实现示例**:

```python
def list_directory_impl(path: str) -> list[str]:
    """列出目录内容"""
    workspace_dir = get_current_workspace()
    safe_path = resolve_safe_path(workspace_dir, path)

    if not safe_path.is_dir():
        raise ValueError(f"不是目录: {path}")

    items = []
    for item in safe_path.iterdir():
        # 跳过隐藏文件
        if item.name.startswith('.') or item.name.startswith('_'):
            continue

        if item.is_dir():
            items.append(f"{item.name}/")
        else:
            items.append(item.name)

    return sorted(items)

list_directory_tool = Tool(
    name="list_directory",
    description="列出目录内容。参数: path",
    func=list_directory_impl
)
```

---

## 11. 测试计划

### 11.1 单元测试

**测试 read_file 工具**:
- ✓ 读取存在的文件
- ✓ 读取不存在的文件 (应报错)
- ✓ 路径遍历攻击 (应拦截)
- ✓ 超长文件自动截断

**测试 write_file 工具**:
- ✓ 写入 memory/ 目录
- ✓ 写入非 memory/ 目录 (应拦截)
- ✓ 自动创建父目录
- ✓ 覆盖已存在文件

**测试 list_directory 工具**:
- ✓ 列出目录内容
- ✓ 过滤隐藏文件
- ✓ 目录排序

### 11.2 集成测试

**场景 1: 实验数据更新**:
1. 用户发送实验数据
2. LLM 调用 read_file 读取当前任务
3. LLM 调用 write_file 更新任务
4. 验证 trace 记录完整

**场景 2: 阶段汇报准备**:
1. 用户请求准备汇报
2. LLM 调用 read_file 读取多个文件
3. LLM 调用 write_file 创建新汇报
4. 验证文件正确创建

**场景 3: 信息不足场景**:
1. 用户提问需要查阅 memory
2. LLM 调用 list_directory 浏览目录
3. LLM 调用 read_file 读取相关文件
4. LLM 基于文件内容回答

---

## 12. Phase 路线图

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 后端基础骨架: SSE chat + 会话 CRUD | ✅ DONE |
| Phase 2 | 文件系统 API + Agent CRUD + 路径安全 | ✅ DONE |
| **Phase 3+4 (合并)** | **Tool-Driven Memory Access** | 🔄 **Next** |
| Phase 5 | RAG (KnowledgeIndexer) + 资产上传 | ⏳ Later |
| Phase 6 | 前端三栏 UI + 集成 | ⏳ Later |

---

## 13. Phase 2 → Phase 3+4 衔接表

| Phase 2 产出 | Phase 3+4 如何使用 |
|-------------|------------------|
| `resolve_safe_path()` | 工具中复用,确保路径安全 |
| `GET /api/files` | 可选: 前端直接读取文件 |
| `POST /api/files` | 可选: 前端直接保存文件 |
| workspace 目录结构 | 工具操作的基础 |

---

## 14. 关键决策记录

### 决策 1: 移除 ContextOrchestrator

**原因**:
- 预先选择 memory 依赖复杂的意图识别
- 可能选择错误或遗漏重要文件
- 增加架构复杂度

**新方案**:
- LLM 通过工具按需读取
- 更灵活,更符合 Agent 理念

### 决策 2: 工具调用即决策

**原因**:
- 不需要额外的 `memory_decision` 结构化输出
- 工具调用本身就清晰表达了 LLM 的决策
- 简化 trace 结构

### 决策 3: 限制 write_file 到 memory/ 目录

**原因**:
- 防止 LLM 误写控制层文件 (SOUL.md, IDENTITY.md 等)
- 保持控制层的稳定性
- 符合 "Control Plane 优先级最高" 的原则

---

## 15. 实施时间估算

| 步骤 | 预计时间 | 依赖 |
|------|---------|------|
| Step 1: 简化 PromptBuilder | 2-3 小时 | Phase 2 |
| Step 2: 实现核心工具 | 3-4 小时 | Phase 2 |
| Step 3: 集成工具到 Agent | 2-3 小时 | Step 2 |
| Step 4: 修改 TraceWriter | 1-2 小时 | Step 3 |
| Step 5: 端到端测试 | 2-3 小时 | Step 4 |
| **总计** | **10-15 小时** | |

---

## 16. 风险与缓解

### 风险 1: LLM 不会正确使用工具

**缓解**:
- 在 System Prompt 中提供清晰的工具使用说明
- 提供示例
- 使用支持工具调用的强模型 (如 Claude 3.5+)

### 风险 2: 多次工具调用增加延迟

**缓解**:
- 优化 memory 目录结构展示
- 考虑实现批量读取功能
- 对频繁访问的文件进行缓存

### 风险 3: Token 消耗可能增加

**缓解**:
- 监控实际 token 使用情况
- 优化工具调用策略
- 必要时回退到部分预注入方案

---

## 17. 后续优化方向

### 17.1 短期优化 (Phase 3+4 完成后)

1. **批量读取**: 允许一次读取多个文件
2. **文件缓存**: 对频繁访问的文件进行缓存
3. **智能提示**: 根据用户问题推荐可能需要的文件

### 17.2 长期优化 (Phase 5+)

1. **混合方案**: 核心文件预注入 + 其他文件按需读取
2. **RAG 集成**: 结合 RAG 进行语义检索
3. **工具链优化**: 实现更复杂的工具组合

---

## 18. 总结

### 18.1 核心价值

这个 Tool-Driven Memory Access 方案的核心价值在于:

1. **简化架构**: 移除复杂的 ContextOrchestrator
2. **提升灵活性**: LLM 自主决策读取内容
3. **降低 Context**: 不预先注入可能用不到的内容
4. **更符合 Agent 理念**: 主动工具使用

### 18.2 实施建议

1. **先实现 MVP**: 基础的 read_file/write_file 工具
2. **充分测试**: 确保工具调用正确性
3. **监控性能**: 关注 token 消耗和延迟
4. **迭代优化**: 根据实际使用情况优化

### 18.3 验收标准

Phase 3+4 合并方案的验收标准:

- ✓ LLM 能正确使用 read_file 工具读取 memory
- ✓ LLM 能正确使用 write_file 工具写入 memory
- ✓ 工具调用记录在 trace 中
- ✓ 路径安全检查有效
- ✓ 端到端场景测试通过

---

**文档完成** | 2026-03-09
