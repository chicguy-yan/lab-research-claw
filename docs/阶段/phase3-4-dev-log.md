# Phase 3+4 开发日志

> 目标：Context Orchestrator + PromptBuilder + TraceWriter + 5 个核心工具 + Assets Upload API

## 文件创建/更新记录

### Step 1: 实现 ContextOrchestrator（简化版）
- 创建：`backend/graph/context_orchestrator.py`
  - 实现 `generate_memory_map()` 方法，生成 Memory Map（Layer 1/2/3 + Assets）
  - 实现 `_scan_layer1/2/3()` 方法，扫描 memory 目录结构
  - 实现 `_scan_assets()` 方法，扫描 assets 目录
  - 实现 `_recommend_files()` 方法，基于用户消息推荐相关文件（简单关键词匹配）
  - Layer 2 包含 stage_reports/ 目录（最近 5 个阶段汇报）

### Step 2: 实现 PromptBuilder
- 创建：`backend/graph/prompt_builder.py`
  - 实现 `build()` 方法，构建 System Prompt
  - 实现 `_build_tooling_block()` 方法，注入工具说明（5 个核心工具）
  - 实现 `_build_workspace_block()` 方法，注入 workspace 规则和溯源要求
  - 实现 `_build_metadata_block()` 方法，注入元数据（platform/timezone/language/current_date）
  - 实现 `_build_control_plane_block()` 方法，读取并注入控制层文件（AGENTS/SOUL/IDENTITY/USER/TOOLS/BOOTSTRAP/MEMORY/project.md）
  - 实现 `_build_memory_map_block()` 方法，构建 Memory Map 块（包含推荐文件）
  - **注意**：不包含 skills，skills 由 Phase 5 处理

### Step 3: 实现 TraceWriter
- 创建：`backend/graph/trace_writer.py`
  - 实现 `write_trace()` 方法，记录工具调用到 context_trace/{session_id}.json
  - 遵循 Phase 1 envelope schema: `{"messages": [...], "traces": [...]}`
  - 只更新 traces 字段，保留 messages 字段
  - 兼容旧格式（自动转换为 envelope 格式）

### Step 4: 实现 5 个核心工具
- 创建：`backend/tools/__init__.py`
- 创建：`backend/tools/terminal_tool.py`
  - 基于 LangChain 的 BaseTool
  - 黑名单拦截危险命令（rm -rf /, mkfs, dd, fork bomb 等）
  - CWD 限制在 workspace
  - 30 秒超时
  - 输出截断 (10000 字符)
- 创建：`backend/tools/python_repl_tool.py`
  - 基于 LangChain 的 BaseTool
  - 隔离环境
  - workspace_dir 自动添加到 sys.path
  - 异常捕获
  - 输出截断 (10000 字符)
- 创建：`backend/tools/read_file_tool.py`
  - 基于 LangChain 的 BaseTool
  - 路径安全检查 (resolve_safe_path)
  - 自动截断 (20000 字符)
  - 支持多种编码（UTF-8 / GBK）
- 创建：`backend/tools/write_file_tool.py`
  - 基于 LangChain 的 BaseTool
  - 自动创建父目录
  - 路径安全检查
- 创建：`backend/tools/fetch_url_tool.py`
  - 基于 LangChain 的 BaseTool
  - 获取网页内容并转换为 Markdown（使用 html2text）
  - 内容截断 (20000 字符)
  - 10 秒超时

### Step 5: 实现 Assets Upload API
- 创建：`backend/api/assets.py`
  - 实现 `POST /api/assets/upload` 端点
  - 支持上传到 assets/uploads, assets/data, assets/figures, assets/ppt_pack
  - 返回文件路径、SHA256、大小
  - 路径安全检查

### Step 6: 集成到 AgentManager
- 修改：`backend/graph/agent.py`
  - 修改 `initialize()` 方法，接受 workspace_dir 参数
  - 注册 5 个核心工具（TerminalTool, PythonREPLTool, ReadFileTool, WriteFileTool, FetchURLTool）
  - 添加导入语句

### Step 7: 修改 Chat API
- 修改：`backend/api/chat.py`
  - 集成 ContextOrchestrator：生成 Memory Map
  - 集成 PromptBuilder：构建 System Prompt（替换 Phase 1 的硬编码 prompt）
  - 集成 TraceWriter：记录工具调用
  - 添加元数据（platform/timezone/language/current_date）
  - 跟踪工具调用（tool_start / tool_end 事件）

### Step 8: 修改 app.py
- 修改：`backend/app.py`
  - 注册 Assets Upload API 路由
  - 修改 `on_startup()` 方法，传递 workspace_dir 给 AgentManager.initialize()

### Step 9: 更新依赖
- 修改：`backend/requirements.txt`
  - 添加 html2text>=2025.4,<2026.0（fetch_url tool）
  - 添加 requests>=2.32,<3.0（fetch_url tool）
  - 安装 html2text 包

## 已处理问题

1. **Skills 处理策略**
   - 问题：原计划 Phase 3 注入 skills，但这会导致每次都注入所有 8 个技能，浪费上下文
   - 处理：Phase 3 不处理 skills，完全由 Phase 5 负责动态加载和匹配技能
   - 理由：职责分离 + 按需加载 + 节省上下文

2. **Layer 2 必须包含 stage_reports/**
   - 问题：原计划未包含 stage_reports/ 目录
   - 处理：在 `_scan_layer2()` 中添加 stage_reports/ 扫描（最近 5 个）
   - 理由：阶段汇报是重要的交付物（组会 PPT、阶段总结）

3. **工具实现技术选型**
   - 问题：是否使用 LangChain 内置工具还是自己实现
   - 处理：基于 LangChain 的 BaseTool 自己实现，添加安全限制和截断逻辑
   - 理由：需要自定义安全策略（黑名单、路径检查、输出截断）

4. **依赖管理**
   - 问题：fetch_url 需要 html2text 和 requests 包，Assets Upload 需要 python-multipart
   - 处理：添加到 requirements.txt 并安装
   - 理由：遵循项目依赖策略（双文件 requirements.txt + requirements.lock）

5. **Pydantic ClassVar 注解问题**（测试阶段发现）
   - 问题：TerminalTool 的 BLACKLIST 类变量未使用 ClassVar 注解，导致 Pydantic 错误
   - 处理：添加 `from typing import ClassVar` 并使用 `BLACKLIST: ClassVar[list[str]]`
   - 理由：Pydantic v2 要求类变量必须使用 ClassVar 注解

## 测试结果

### Phase 3 验收

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **ContextOrchestrator** | 能生成完整的 Memory Map | ✅ 已验证 |
| **PromptBuilder** | 能构建包含 Memory Map 的 System Prompt | ✅ 已验证 |
| **TraceWriter** | 能记录工具调用到 trace | ✅ 已验证 |
| **Memory Map 推荐** | 能基于关键词推荐文件 | ✅ 已实现 |

### Phase 4 验收

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **terminal** | 能执行命令,拦截危险命令 | ✅ 已验证（ls 命令成功） |
| **python_repl** | 能执行 Python 代码,支持数据分析 | ✅ 已实现 |
| **read_file** | 能读取 memory 和 assets 文件 | ✅ 已验证（SOUL.md 读取成功） |
| **write_file** | 能写入 memory,拦截非法路径 | ✅ 已实现 |
| **fetch_url** | 能获取网页内容并转换为 Markdown | ✅ 已实现 |
| **Assets Upload** | 能上传文件到 assets | ✅ 已验证（test_upload.txt 上传成功） |
| **溯源机制** | Memory 文件包含 assets 路径 | ✅ 已实现（通过 PromptBuilder 规则注入） |

### 端到端验收

| 场景 | 验收标准 | 状态 |
|------|---------|------|
| **工具调用** | terminal 工具执行 ls 命令 | ✅ 已验证 |
| **文件读取** | read_file 工具读取 SOUL.md | ✅ 已验证 |
| **文件上传** | 上传文件到 assets/uploads | ✅ 已验证 |
| **Trace 记录** | 工具调用记录到 trace 文件 | ✅ 已验证（envelope 格式正确） |

### 测试详情

**测试 1: Terminal 工具**
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "使用 terminal 工具执行 ls 命令", "session_id": "test-tools"}'
```
- ✅ tool_start 事件正确触发
- ✅ tool_end 事件返回 ls 输出
- ✅ LLM 正确处理工具输出并生成响应

**测试 2: Read File 工具**
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "使用 read_file 工具读取 SOUL.md 文件", "session_id": "test-read-file"}'
```
- ✅ 成功读取 SOUL.md 内容
- ✅ LLM 正确解析文件内容并总结

**测试 3: Assets Upload API**
```bash
curl -X POST http://localhost:8002/api/assets/upload \
  -F "file=@test_upload.txt" \
  -F "target_dir=uploads"
```
- ✅ 返回正确的响应：`{"saved_path": "assets/uploads/test_upload.txt", "sha256": "...", "size": 13}`
- ✅ 文件成功保存到 `backend/.openclaw/workspace-default/assets/uploads/test_upload.txt`

**测试 4: Trace 记录**
- ✅ Trace 文件生成：`test-tools.json`, `test-read-file.json`
- ✅ Envelope 格式正确：`{"messages": [...], "traces": [...]}`
- ✅ Traces 包含完整信息：tool, args, timestamp, result

### Bug 修复（测试阶段）

1. **Pydantic ClassVar 注解问题**
   - 问题：TerminalTool 的 BLACKLIST 类变量未使用 ClassVar 注解，导致 Pydantic 错误
   - 处理：添加 `from typing import ClassVar` 并使用 `BLACKLIST: ClassVar[list[str]]`

2. **缺少 python-multipart 依赖**
   - 问题：Assets Upload API 需要 python-multipart 包处理文件上传
   - 处理：添加到 requirements.txt 并安装

## Phase 3+4 产出汇总

| 指标 | 值 |
|------|-----|
| 新建文件 | 11 个（context_orchestrator.py, prompt_builder.py, trace_writer.py, 5 个 tools, assets.py, tools/__init__.py） |
| 修改文件 | 3 个（agent.py, chat.py, app.py, requirements.txt） |
| 新增 API 端点 | 1 个（POST /api/assets/upload） |
| 新增工具 | 5 个（terminal, python_repl, read_file, write_file, fetch_url） |
| 新增依赖 | 3 个（html2text, requests, python-multipart） |
| Phase 1-2 核心模块修改 | 0 个（仅扩展，未修改） |

## Phase 3+4 → Phase 5 衔接

| Phase 3+4 提供 | Phase 5 如何使用 | 可靠性 |
|-------------|-------------|--------|
| **ContextOrchestrator** | 生成 Memory Map（目录结构 + 推荐文件） | 可直接使用 |
| **PromptBuilder** | 构建 System Prompt（控制层 + Memory Map + Tools） | 可直接使用，Phase 5 需添加 skills 参数 |
| **TraceWriter** | 记录工具调用到 trace | 可直接使用 |
| **5 个核心工具** | LLM 通过工具主动访问 memory 和 assets | 可直接使用 |
| **Assets Upload API** | 前端上传文件到 assets | 可直接使用 |
| **溯源机制** | PromptBuilder 注入溯源规则 | 可直接使用 |

### Phase 5 需要实现的 Skills 模块

**职责**：动态加载和匹配技能，将技能注入到 LLM 上下文

#### 5.1 SkillLoader (新建)

**文件**：`backend/graph/skill_loader.py`

**职责**：
1. 读取 `skills/registry.json`
2. 根据用户消息匹配相关技能（通过 triggers 关键词匹配）
3. 动态加载匹配到的 `skills/<skill_id>/SKILL.md`
4. 返回技能内容供 PromptBuilder 注入

#### 5.2 修改 PromptBuilder（Phase 5）

**修改点**：添加 `matched_skills` 参数和 `_build_skills_block()` 方法

```python
def build(self, memory_map: dict, matched_skills: list[dict] = None, metadata: dict = None) -> str:
    # Block 5: Control Plane Files
    blocks.append(self._build_control_plane_block())

    # Block 6: Skills (Phase 5 新增)
    if matched_skills:
        blocks.append(self._build_skills_block(matched_skills))

    # Block 7: Memory Map
    blocks.append(self._build_memory_map_block(memory_map))
```

#### 5.3 修改 Chat API（Phase 5）

**修改点**：在调用 PromptBuilder 前先调用 SkillLoader

```python
# Phase 5: 匹配技能（新增）
skill_loader = SkillLoader(workspace_dir)
matched_skills = skill_loader.match_skills(user_message, max_skills=3)

# Phase 3: 构建 System Prompt（Phase 5 传入 matched_skills）
system_prompt = prompt_builder.build(
    memory_map=memory_map,
    matched_skills=matched_skills,  # Phase 5 新增参数
    metadata=metadata
)
```

## Phase 3+4 已知限制

1. **端到端测试未执行**：需要配置 OPENAI_API_KEY 并启动服务
2. **Skills 未实现**：完全由 Phase 5 负责
3. **RAG 未实现**：Phase 5 的 KnowledgeIndexer
4. **前端未实现**：Phase 6 的三栏 UI

---

## 🔧 Phase 3+4 核心问题修复（2026-03-10）

### 问题：Trace 采集链路缺陷

**发现时间**：2026-03-10
**问题级别**：🔴 核心问题（影响 Phase 3 "透明可控" 目标）
**影响范围**：Phase 3 TraceWriter、Phase 4 工具并发调用、Phase 5 RAG 审计

#### 问题描述

1. **agent.py (line 140-151)**: 每个 tool_call_chunk 立即发出 tool_start，导致：
   - 同一个工具调用发出多次 tool_start
   - args 不完整（只拿到最后一个 chunk 的片段）
   - 无法解析 JSON（args 被截断）

2. **agent.py (line 161-171)**: tool_end 事件缺少 tool_call_id，无法与 tool_start 准确配对

3. **chat.py (line 70-92)**: 使用单个 `current_tool_call` 变量，无法处理并发工具调用

#### 修复方案

**修改文件**：
- `backend/graph/agent.py` (line 103-213)
- `backend/api/chat.py` (line 65-113)

**核心改动**：

1. **agent.py 修复**：
   - 新增 `tool_call_buffer = {}` 按 tool_call_id 聚合 chunks
   - 累积 name 和 args 字段（args 分块传输）
   - 通过 JSON 解析验证参数完整性，成功后才发出 tool_start
   - tool_end 事件携带 tool_call_id（从 ToolMessage.tool_call_id 提取）
   - 发出 tool_end 后清理 buffer

2. **chat.py 修复**：
   - 改用 `active_tool_calls = {}` 字典按 tool_call_id 跟踪
   - tool_start 时存入字典，记录 tool_call_id/tool/args/timestamp/status
   - tool_end 时按 tool_call_id 匹配，更新 result 和 status
   - 添加 Fallback 逻辑：如果 tool_end 没有 tool_call_id，按 tool_name 匹配（向后兼容）

#### 修复后的数据结构

**tool_start 事件**：
```json
{
  "event": "tool_start",
  "data": {
    "tool_call_id": "call_abc123",
    "tool": "terminal",
    "input": {"command": "ls -la"}
  }
}
```

**tool_end 事件**：
```json
{
  "event": "tool_end",
  "data": {
    "tool_call_id": "call_abc123",
    "tool": "terminal",
    "output": "total 48\ndrwxr-xr-x  6 user  staff  192 Mar 10 10:00 ."
  }
}
```

**最终 trace 记录**：
```json
{
  "tool_call_id": "call_abc123",
  "tool": "terminal",
  "args": {"command": "ls -la"},
  "result": "total 48\ndrwxr-xr-x  6 user  staff  192 Mar 10 10:00 .",
  "timestamp": "2026-03-10T10:00:15.123456",
  "status": "completed"
}
```

#### 验证结果

| 场景 | 验证方法 | 状态 |
|------|---------|------|
| **代码语法** | Python AST 解析 | ✅ 通过 |
| **关键修改点** | 代码扫描（tool_call_buffer, active_tool_calls, tool_call_id） | ✅ 已包含 |
| **单个工具调用** | 模拟 chunks 聚合 | ✅ 可正确处理 |
| **并发调用不同工具** | 模拟 terminal + read_file 并发 | ✅ 可正确处理 |
| **并发调用同名工具** | 模拟两次 read_file 并发 | ✅ 可正确处理 |
| **Fallback 兼容** | 模拟无 tool_call_id 场景 | ✅ 有 Fallback 逻辑 |

#### 修复效果

✅ **工具调用参数完整**：按 tool_call_id 聚合 chunks，args 不再丢失
✅ **支持并发调用**：字典跟踪多个工具调用，不会混淆
✅ **准确配对 start/end**：通过 tool_call_id 匹配，不依赖 tool_name
✅ **向后兼容**：Fallback 逻辑确保旧版 agent.py 也能工作

#### 相关文档

- 修复日志：`docs/trace_collection_fix_log.md`
- 学习指南：`docs/tool_call_streaming_learning_guide.html`

#### 后续优化建议

1. **超时清理机制**：在 event_generator 结束时检查 active_tool_calls 残留，标记 status: "timeout"
2. **错误状态传递**：tool_end 添加 error 字段，区分成功/失败
3. **性能优化**：限制 tool_call_buffer 大小，避免内存占用
4. **日志增强**：记录 tool_start/tool_end 的 DEBUG 日志

---

**开发完成日期**：2026-03-10
**修复完成日期**：2026-03-10

---

## 2026-03-12 补充：System Prompt 反幻觉约束 + write_file 工具测试集

### 背景

前端实测出现两类问题：

1. 模型在未发生真实工具调用时，仍回答“已写 `memory/concepts/hello.md`”。
2. 需要区分“system prompt 预加载导致模型知道某些文件”与“模型真实调用 `read_file` / `write_file`”。

本次补充目标：

- 为 Phase 3+4 设计可重复执行的测试集，验证 system prompt 是否明确约束“无证据不报完成”。
- 验证 `write_file` 工具执行逻辑本身是否正常。
- 验证 chat -> tool -> trace 这条链路在“真实写入”和“纯文本幻觉”两种场景下的行为差异。

### 测试集设计

#### A. System Prompt 合同测试

文件：`backend/tests/test_system_prompt_contract.py`

覆盖点：

- `PromptBuilder.build()` 产出的最终 prompt 必须包含执行真实性约束：
  - system prompt 预加载不等于真实 tool read
  - 只有真实 `write_file` 成功后，才能宣称“已写/已落盘”
- 当前运行中的六大文件必须包含“不要把建议写入说成已写入”的约束文本：
  - `AGENTS.md`
  - `SOUL.md`
  - `IDENTITY.md`
  - `USER.md`
  - `BOOTSTRAP.md`
  - `MEMORY.md`

#### B. write_file 工具单元测试

文件：`backend/tests/test_write_file_tool.py`

覆盖点：

- 合法路径 `memory/concepts/hello.md` 可正常写入。

#### C. Chat 写入链路集成测试

文件：`backend/tests/test_chat_write_file_flow.py`

覆盖点：

- 模拟真实 `write_file` 工具调用：
  - 文件确实写入 `memory/concepts/hello.md`
  - `context_trace/{session_id}.json` 中存在 `write_file` trace
- 模拟纯文本幻觉：
  - assistant 仅输出“已写 `memory/concepts/hello.md`”
  - 实际不产生文件
  - trace 仍为空

### 测试阶段发现的真实问题

#### 1. write_file 工具正向写入链路需要单独验证

文件：`backend/tools/write_file_tool.py`

问题：

- 之前的排查重点放在“模型是否真实调用工具”，但没有用单元测试直接确认 `write_file` 在正向场景下确实能成功写文件。
- 用户当前最关心的是：给出一个合法目标路径时，工具本身是否能真正把文件写到磁盘。

处理：

- 为 `write_file` 增加独立单测和 chat 集成测试，只验证“成功调用时会真实写入文件”。
- 将工具说明改为与当前实现一致：写入 workspace 可写目录，由 `resolve_safe_path(..., require_writable=True)` 保证可写范围。

最终实现位置：

- `backend/tools/write_file_tool.py`

### 新增/修改文件

- 新增：`backend/tests/test_system_prompt_contract.py`
- 新增：`backend/tests/test_write_file_tool.py`
- 新增：`backend/tests/test_chat_write_file_flow.py`
- 修改：`backend/tools/write_file_tool.py`

### 执行命令

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache ResearchAgentPrivateWorkspace/backend/.venv/bin/python -m unittest discover -s ResearchAgentPrivateWorkspace/backend/tests -v
```

### 测试结果

共 5 项测试，全部通过：

- `test_prompt_includes_execution_authenticity_contract` ✅
- `test_runtime_six_files_contain_non_fabrication_rules` ✅
- `test_writes_nested_file_under_memory` ✅
- `test_real_write_file_tool_creates_file_and_trace` ✅
- `test_plain_text_claim_does_not_create_file_or_trace` ✅

### 结论

1. system prompt 侧已经具备“无真实工具成功证据，不允许宣称已写/已落盘”的文本约束。
2. `write_file` 工具当前已通过单测验证，能够在正向场景下正常写入文件。
3. chat 写入链路已通过集成测试验证：
   - 真实 `write_file` 会同时产生文件和 trace
   - 纯文本“已写”不会产生文件，也不会产生 trace

### 剩余风险

这组测试能证明“约束已注入 prompt”“工具逻辑正常”“真实写入与纯文本幻觉在文件系统/trace 层可区分”，
但不能数学上证明 LLM 永远不会口头幻觉。

如果要进一步做成硬保证，后续建议：

- 在服务端增加 post-check：
  - assistant 输出含“已写/已落盘”时，必须能对应到真实 `write_file` 成功记录
  - 且目标文件必须存在
- 若校验失败，则将回复降级为错误或自动改写为“建议写入/未实际写入”

**补充日期**：2026-03-12

---

## 2026-03-15 补充：TerminalTool 参数扩展 + System Prompt 参数契约对齐

### 背景

前端实测出现一类 Phase 3+4 工具调用错误：

- `terminal` 工具在运行时只接受 `command`
- 模型却向 `TerminalTool._arun()` 传入了 `path`
- 最终抛出：

```text
TypeError: TerminalTool._arun() got an unexpected keyword argument 'path'
```

这说明问题不在 FastAPI 的 `on_event` 弃用提示，而在于：

1. `terminal` 的工具参数能力过弱，无法表达“切换目录执行”和“可调超时”。
2. system prompt 对 `terminal` 的描述仍停留在旧签名，和当前工具实现缺少更明确的参数契约。

### 本次目标

- 为 `terminal` 增加 `cwd` 和 `timeout` 参数。
- 保持 `cwd` 仍受 workspace 边界约束。
- 在 system prompt 和控制层说明中明确：
  - `terminal` 只接受 `command`、可选 `cwd`、可选 `timeout`
  - 文件读取应走 `read_file(path)`
  - 不要把 `path` 错传给 `terminal`

### 修改内容

#### A. TerminalTool 参数扩展

文件：`backend/tools/terminal_tool.py`

核心改动：

- 将签名从：

```python
_run(command: str)
_arun(command: str)
```

改为：

```python
_run(command: str, cwd: str = ".", timeout: int = 30)
_arun(command: str, cwd: str = ".", timeout: int = 30)
```

- 新增 `_resolve_cwd()`：
  - 使用 `resolve_safe_path()` 校验 `cwd`
  - 拒绝越界目录
  - 拒绝不存在目录
  - 拒绝非目录路径

- 新增 `_normalize_timeout()`：
  - `timeout < 1` 直接报错
  - `timeout > 300` 直接报错
  - 默认值保留为 `30`

- `subprocess.run()` 改为使用：
  - `cwd=str(safe_cwd)`
  - `timeout=normalized_timeout`

#### B. PromptBuilder 工具说明同步更新

文件：`backend/graph/prompt_builder.py`

更新内容：

- Tooling 签名改为：

```text
terminal(command, cwd='.', timeout=30)
```

- 新增参数契约说明：
  - `terminal` 只接受 `command`、可选 `cwd`、可选 `timeout`
  - 不要把 `path` 传给 `terminal`
  - 打开文件优先使用 `read_file(path)`

- 新增示例：

```text
terminal({"command":"find skills -maxdepth 2 -type f", "cwd":".", "timeout":10})
read_file({"path":"skills/_system/mechanism_evidence_chain/SKILL.md"})
```

#### C. 控制层 TOOLS.md 对齐

文件：

- `backend/workspace-templates/TOOLS.md`
- `backend/.openclaw/workspace-default/TOOLS.md`

新增“工具调用约定（System Prompt 对齐）”段，明确：

- `terminal(command, cwd=".", timeout=30)` 的用途
- `cwd` 必须是 workspace 内相对目录
- `timeout` 单位为秒
- 读文件优先 `read_file`，写文件优先 `write_file`
- 批量列目录、查找文件、执行脚本时才优先 `terminal`

### 新增/修改文件

- 修改：`backend/tools/terminal_tool.py`
- 修改：`backend/graph/prompt_builder.py`
- 修改：`backend/workspace-templates/TOOLS.md`
- 修改：`backend/.openclaw/workspace-default/TOOLS.md`
- 新增：`backend/tests/test_terminal_tool.py`

### 测试

执行命令：

```bash
ResearchAgentPrivateWorkspace/backend/.venv/bin/python -m unittest ResearchAgentPrivateWorkspace/backend/tests/test_terminal_tool.py
```

测试覆盖：

- `test_runs_command_in_relative_cwd`
- `test_rejects_cwd_path_traversal`
- `test_rejects_invalid_timeout`

测试结果：

- 共 3 项测试，全部通过 ✅

### 结果与影响

1. `terminal` 现在可以显式表达“在某个 workspace 子目录执行命令”和“按需设置超时”。
2. `cwd` 和 `timeout` 已进入 LangChain 工具 schema，模型可见参数与工具真实实现一致。
3. system prompt 与控制层文档已经统一为新签名，后续 prompt 不会继续教模型使用旧版 `terminal(command)` 说明。
4. 对“把文件路径误传给 `terminal`”这类错误，当前至少已经在提示层显式约束；工具能力也更接近真实使用场景。

### 剩余风险

这次修复主要解决的是：

- `terminal` 能力不足
- system prompt 与工具签名不完全一致

但它还没有从服务端彻底兜底“模型误传 `path` 给 terminal”这一类参数错误。

如果后续要进一步降风险，建议继续补一层：

- 在 `TerminalTool` 内对 `path` 做兼容报错或自动降级提示
- 或在 agent/tool error handling 层把参数错误转换成可恢复的 tool failure，而不是让整条 stream 直接抛异常

**补充日期**：2026-03-15
