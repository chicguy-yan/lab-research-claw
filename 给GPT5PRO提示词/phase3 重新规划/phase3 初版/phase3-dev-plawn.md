# Phase 3 开发计划 — Context Orchestrator + PromptBuilder + TraceWriter

> 目标：让 `/api/chat` 从"硬编码 system prompt"升级为"动态读取 workspace 文件 → 组装 system prompt → 追踪上下文"，实现 PRD §4 的三层记忆注入与 Trace 落盘。

---

## 0. 前置条件

- Phase 1 ✅：SSE chat + 会话 CRUD（`agent.py` / `chat.py` / `session_manager.py`）
- Phase 2 ✅：文件 API + Agent CRUD + 路径安全（`files.py` / `agents.py` / `path_utils.py`）
- 当前 `chat.py` 使用硬编码 `SYSTEM_PROMPT = "You are a personal assistant running inside OpenClaw."`

---

## 1. Phase 3 要交付的 3 个核心模块

### 1.1 ContextOrchestrator (`graph/context_orchestrator.py`)

**职责**：根据用户消息，决定本轮注入哪些 workspace 文件到 system prompt。

**输入**：
- `workspace_dir: Path` — 当前 workspace 根目录
- `user_message: str` — 用户本轮消息文本
- `today: str` — 当前日期 `YYYY-MM-DD`

**输出**：
```python
@dataclass
class SelectedFile:
    path: str          # 相对于 workspace 的路径，如 "SOUL.md"
    layer: str         # workspace | skills | memory_identity | memory_timeline | memory_atom | uploads
    why: str           # 选择原因（短句）
    status: str        # full | truncated | skipped | not_found

@dataclass
class SelectionResult:
    files: list[SelectedFile]      # 按注入顺序排列
    budget_report: dict            # {"total_chars": int, "budget_limit": int, "truncated": [...], "skipped": [...]}
```

**选择规则（与 PRD §4.4.3 对齐，Architecture §5.2 排序）**：

1. **Workspace 控制层（每轮必读，layer=`workspace`）**：
   - `AGENTS.md` — 工作区总纲（技能协议 + 记忆协议）
   - `SOUL.md` — 行为准则
   - `IDENTITY.md` — Agent 身份
   - `USER.md` — 用户偏好
2. **Skills 快照（layer=`skills`）**：
   - `SKILLS_SNAPSHOT.md` — 可用技能清单（Phase 4 生成；Phase 3 跳过，status="not_found"）
3. **Layer1（身份与规则，每轮必读，layer=`memory_identity`）**：
   - `memory/identity/user.md`
   - `memory/identity/project.md`
   - `memory/identity/lab_context.md`
   - `memory/identity/context_budget.md` — **仅供 Orchestrator 读取预算配置，不注入 system prompt**
4. **Layer2（时间轴，按需选择，layer=`memory_timeline`）**：
   - `memory/timeline/180d_index.md`（总读）
   - 当前 phase 文件（解析 `180d_index.md` 的 `current_phase` 字段）
   - 若消息包含"今天/最近/日志"关键词 → 追加 `memory/timeline/days/{today}.md`
   - 若消息包含"阶段汇报/Rxx"关键词 → 追加最近的 `stage_reports/` 文件
5. **Layer3（原子资产，按需选择，layer=`memory_atom`）**：
   - 若消息包含 `concept/task/pack` 或匹配的关键词 → 扫描 `memory/concepts/` `memory/tasks/` `memory/packs/` 中最近修改的 top-3 文件
   - 意图匹配（简单关键词匹配 MVP）：
     - "机理/证据/Co(IV)/ClO₂/PMSO/DPD/淬灭" → mechanism 相关 task/concept
     - "合成/checklist/SOP" → synthesis 相关 task
     - "汇报/PPT/ppt_pack/Rxx" → stage_report pack
     - "写作/论文/R&D/discussion" → writing pack

**预算策略（读 `context_budget.md`）**：
- `totalMaxChars`：默认 120,000
- `perFileMaxChars`：默认 20,000
- 超出 perFileMaxChars 的文件追加 `...[truncated]`
- 总量超出 totalMaxChars 时，从 Layer3 → Layer2（非 always_full）→ 按优先级跳过
- 被截断/跳过的文件记录到 `budget_report`

**关键方法**：
```python
def select_files(self, user_message: str, today: str, session_id: str = "") -> SelectionResult: ...
    # session_id 预留用于后续取最近对话摘要（Architecture §3.1 Step 2），Phase 3 MVP 不使用
def _read_budget_config(self) -> dict: ...
def _detect_intent(self, user_message: str) -> list[str]: ...
def _collect_layer3_files(self, intents: list[str]) -> list[SelectedFile]: ...
```

---

### 1.2 PromptBuilder (`graph/prompt_builder.py`)

**职责**：将 ContextOrchestrator 选出的文件组装成 OpenClaw 风格的 system prompt（PRD §4.4.1 两条消息模型的 system 部分）。

> **两条消息模型范围说明（PRD §4.4.1）**：PRD 定义 system + user 两条消息。Phase 3 仅实现 system prompt 动态组装；user message 的 untrusted 块拼接延迟到 Phase 6（前端上传后生成）。当前 user message 仍由 `api/chat.py` 直接传入 AgentManager（保持 Phase 1 行为不变）。

**输入**（对齐 TAD §PromptBuilder）：
- `workspace_dir: Path`
- `selected_files: list[SelectedFile]` — 已排序的文件列表（来自 Orchestrator）
- `user_message: str` — 用户本轮消息（Phase 3 不转换，仅用于元数据注入）
- `tools_summary: str` — 工具摘要（Phase 4 提供，Phase 3 传空字符串）
- `metadata: dict` — 可信元数据，如 `{"platform": "openclaw", "timezone": "Asia/Shanghai", "language": "zh-CN", "date": "2026-03-08"}`

**输出**：
- `system_prompt: str` — 拼接好的 system prompt

**system prompt 五块结构（PRD §4.4.2，Architecture §5.3）**：

```text
You are a personal assistant running inside OpenClaw.

## Tooling

{tools_summary 或 "No tools available yet."}

## Workspace

Your working directory is: {workspace_dir}
Today's date: {metadata.date}

Important rules:
- The "# Project Context" section below is your primary source of truth for this session.
- If information is missing, output a "Missing info checklist" instead of guessing.
- Never fabricate data, evidence, or conclusions.

## Inbound Context (trusted metadata)

```json
{"platform": "openclaw", "timezone": "Asia/Shanghai", "language": "zh-CN", "session_type": "main", "date": "2026-03-08"}
```

# Project Context

## AGENTS.md

{file content}

## SOUL.md

{file content}

...（按 selected_files 顺序逐文件注入，context_budget.md 不注入）
```

**裁剪逻辑**：
- 每个文件读取后，若超过 `perFileMaxChars` → 截断 + 追加 `\n...[truncated at {perFileMaxChars} chars]`
- 文件不存在 → 跳过，SelectedFile.status = "not_found"
- `context_budget.md` 不注入 Project Context（仅由 Orchestrator 读取用于预算计算）

**关键方法**：
```python
def build(
    self,
    workspace_dir: Path,
    selected_files: list[SelectedFile],
    user_message: str,
    tools_summary: str,
    metadata: dict,
) -> str: ...
```

---

### 1.3 TraceWriter (`graph/trace_writer.py`)

**职责**：在每轮 `/api/chat` 完成后，将上下文选择记录追加到 session envelope 的 `traces` 字段。

**Trace 条目 schema**：

```python
@dataclass
class TraceEntry:
    trace_id: str            # 自动生成：T{序号} 或 uuid hex[:8]
    timestamp: str           # ISO 8601
    context_read: list[dict] # [{"path", "layer", "why", "status"}] 来自 SelectedFile
    budget_report: dict      # 来自 SelectionResult
    tool_calls: list[dict]   # 本轮的 tool_call 列表（从 SSE 事件收集）
    assistant_summary: str   # assistant 最终回复的前 200 字符（截断摘要）
```

**落盘位置**：`context_trace/{session_id}.json` 的 `"traces"` 数组（与 SessionManager 共用同一文件）。

**关键方法**：
```python
class TraceWriter:
    def __init__(self, workspace_dir: Path): ...

    def write_trace(
        self,
        session_id: str,
        context_read: list[dict],
        budget_report: dict,
        tool_calls: list[dict],
        assistant_summary: str,
    ) -> str:
        """追加一条 trace 到 envelope.traces[]。返回 trace_id。"""
        ...
```

**与 SessionManager 的协作**：
- 读取 envelope → 追加到 `traces` → 写回
- 使用 `SessionManager._read_envelope()` 和 `SessionManager._write_envelope()` 方法
- 为避免循环依赖，TraceWriter 直接操作 JSON 文件（与 SessionManager 共享路径约定但不依赖其实例）

---

## 2. 修改已有文件

### 2.1 `api/chat.py` — 集成三个模块

**改动要点**：

1. 删除 `SYSTEM_PROMPT = "You are a personal assistant running inside OpenClaw."` 硬编码
2. 在 `event_generator()` 中，调用顺序：
   ```python
   # 1. 加载历史
   history = sm.load_session_for_agent(body.session_id)

   # 2. ContextOrchestrator 选文件（对齐 Architecture §3.1 Step 2）
   today = _today()
   orchestrator = ContextOrchestrator(workspace_dir)
   selection = orchestrator.select_files(
       body.message, today=today, session_id=body.session_id
   )

   # 3. PromptBuilder 组装 system prompt（对齐 TAD §PromptBuilder + PRD §4.4.2 五块结构）
   builder = PromptBuilder()
   metadata = {"platform": "openclaw", "timezone": "Asia/Shanghai",
                "language": "zh-CN", "session_type": "main", "date": today}
   system_prompt = builder.build(
       workspace_dir=workspace_dir,
       selected_files=selection.files,
       user_message=body.message,
       tools_summary="",   # Phase 4 will fill
       metadata=metadata,
   )

   # 4. 流式调用 AgentManager（不变）
   tool_calls_collected = []
   async for event in am.astream(body.message, history, system_prompt):
       # 收集 tool_calls
       if event["event"] == "tool_start":
           tool_calls_collected.append(event["data"])
       ...

   # 5. 持久化消息（不变）
   sm.save_message(...)

   # 6. TraceWriter 落盘
   trace_writer = TraceWriter(workspace_dir)
   trace_id = trace_writer.write_trace(
       session_id=body.session_id,
       context_read=[f.__dict__ for f in selection.files],
       budget_report=selection.budget_report,
       tool_calls=tool_calls_collected,
       assistant_summary=assistant_text[:200],
   )

   # 7. done 事件（增加 trace_path 字段，对齐 Architecture §3.1 Step 9）
   # trace_path 格式 = "{session_id}/{trace_id}"，前端可用 GET /api/traces/{trace_path} 获取
   trace_path = f"{body.session_id}/{trace_id}"
   done_data = {"session_id": body.session_id, "trace_path": trace_path}
   yield f"event: done\ndata: {json.dumps(done_data)}\n\n"
   ```
3. `workspace_dir` 获取方式：`request.app.state.session_manager._workspace_dir`

### 2.2 `app.py` — 注册新路由

- 新增 `from api.traces import router as traces_router`
- 新增 `app.include_router(traces_router, prefix="/api")`

---

## 3. 新增 API 端点

### 3.1 `api/traces.py` — Trace 查询（对齐 Architecture §4 #12-#13）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/traces?session_id=&limit=` | GET | 列出某 session 的所有 trace 条目（可选 limit 参数） |
| `/api/traces/{trace_path:path}` | GET | 获取单条 trace 详情。`trace_path` 格式为 `{session_id}/{trace_id}`，与 done 事件返回的 `trace_path` 字段一致 |

**实现**：读取 `context_trace/{session_id}.json` 的 `"traces"` 数组。

---

## 4. 文件清单（Phase 3 交付物）

| # | 文件 | 操作 | 说明 |
|---|------|------|------|
| 1 | `backend/graph/context_orchestrator.py` | 新建 | 上下文选择器 |
| 2 | `backend/graph/prompt_builder.py` | 新建 | system prompt 组装器 |
| 3 | `backend/graph/trace_writer.py` | 新建 | trace 落盘器 |
| 4 | `backend/api/traces.py` | 新建 | trace 查询 API |
| 5 | `backend/api/chat.py` | 修改 | 集成 Orchestrator → Builder → TraceWriter |
| 6 | `backend/app.py` | 修改 | 注册 traces 路由 |

**Phase 3 不新增依赖**：全部使用 stdlib（`pathlib`, `json`, `dataclasses`, `datetime`, `re`）+ Phase 1 已有依赖。`tiktoken` 已在 requirements.txt，Phase 3 可用于 token 估算但 MVP 阶段先用字符数估算（1 token ≈ 3-4 中文字符）。

---

## 5. 关键设计决策

| # | 决策 | 理由 |
|---|------|------|
| D1 | Orchestrator 用关键词匹配做意图检测（不用 LLM 推理） | Phase 3 MVP 优先简单可测；Phase 6 可升级为 embedding 相似度 |
| D2 | 每个文件 status 分 full / truncated / skipped / not_found | 对齐 PRD §4.4.5 trace 字段要求 |
| D3 | TraceWriter 直接操作 JSON 文件（不依赖 SessionManager 实例） | 避免循环依赖；二者共享 `context_trace/` 路径约定 |
| D4 | system prompt 身份行由 PromptBuilder 内置常量生成 | PRD §4.4.2 明确"身份行不从 workspace 读取" |
| D5 | tools_summary 参数在 Phase 3 传空字符串 | 工具注册在 Phase 4 实现 |
| D6 | budget 先用字符数（非 token 数）控制 | 避免每次请求都调 tiktoken 的性能开销；后续可切换 |
| D7 | done 事件增加 `trace_path` 字段（格式 `{session_id}/{trace_id}`），不破坏已有 SSE 协议 | PRD §5.1 约束"仅允许增加字段，不破坏既有解析器"；字段名对齐 Architecture §3.1 Step 9 |
| D8 | done 事件在 trace 同步写入完成后才发送 | 解决 Architecture §6.8 竞态风险：前端收到 done 后立即 GET trace，必须保证 trace 已落盘。采用方案 A（同步写入），trace 数据量小，延迟可忽略 |
| D9 | `context_budget.md` 仅供 Orchestrator 读取预算配置，不作为 Project Context 注入 system prompt | 该文件是内部配置而非 Agent 需要的上下文信息 |
| D10 | Phase 3 仅实现 system prompt 动态组装；user message 的 untrusted 块拼接（PRD §4.4.1）延迟到 Phase 6 | Phase 3 无前端上传，user message 保持 Phase 1 行为直接传入 |

---

## 6. 验证测试计划

| # | 测试项 | 命令 / 方法 | 预期结果 |
|---|--------|------------|----------|
| T1 | 服务启动正常 | `curl http://localhost:8002/` | `{"status":"ok", ...}` |
| T2 | Phase 1/2 接口不回归 | 分别 curl sessions CRUD / files tree / agents list | 返回正常 |
| T3 | chat 响应使用动态 system prompt | `curl -N POST /api/chat {...}` | SSE token 流正常返回，且回复内容体现"读到了 SOUL.md / project.md 的人格与项目信息" |
| T4 | IDENTITY.md 人格注入生效 | 在 IDENTITY.md 写入 Name=小克 → chat 中问"你叫什么" | 回复提及"小克" |
| T5 | project.md 项目信息注入生效 | 在 project.md 写入 North Star → chat 中问"我的项目是什么" | 回复包含 project.md 中的北极星信息 |
| T6 | trace 落盘 | chat 后读 `context_trace/{session_id}.json` | `traces` 数组有新条目，包含 `context_read[]` / `budget_report` / `tool_calls` / `assistant_summary` |
| T7 | trace API 查询 | `GET /api/traces?session_id=xxx` | 返回 trace 列表 |
| T8 | 单条 trace 查询 | `GET /api/traces/{session_id}/{trace_id}`（trace_path 格式） | 返回完整 trace 条目 |
| T9 | 文件不存在不崩溃 | 删除 `memory/identity/lab_context.md` 后 chat | 正常返回，该文件在 trace 中 status="not_found" |
| T10 | 预算截断生效 | 在 context_budget.md 设 perFileMaxChars=500 → 写一个超大文件 → chat | trace 中对应文件 status="truncated"，system prompt 中文件内容被截断 |
| T11 | done 事件包含 trace_path | 观察 SSE done 事件 | `{"session_id":"...","trace_path":"{session_id}/{trace_id}"}` |

---

## 7. 开发步骤（建议顺序）

### Step 1：创建 `context_orchestrator.py`
- 实现 `SelectedFile` / `SelectionResult` 数据类
- 实现 `select_files()` 核心方法
- 实现 `_read_budget_config()` 解析 context_budget.md
- 实现 `_detect_intent()` 关键词意图检测
- 实现 `_collect_layer3_files()` 原子资产选择

### Step 2：创建 `prompt_builder.py`
- 实现 `build()` 方法
- 实现文件读取 + 截断逻辑
- 实现 system prompt 五块拼接（PRD §4.4.2）：身份行 → Tooling → Workspace → Inbound Context → Project Context
- `context_budget.md` 跳过不注入

### Step 3：创建 `trace_writer.py`
- 实现 `write_trace()` 方法
- 直接操作 `context_trace/{session_id}.json`

### Step 4：创建 `api/traces.py`
- 实现 `GET /api/traces?session_id=&limit=`
- 实现 `GET /api/traces/{trace_path:path}`（trace_path 格式 `{session_id}/{trace_id}`）

### Step 5：修改 `api/chat.py`
- 集成 ContextOrchestrator → PromptBuilder → TraceWriter
- 修改 `event_generator()` 流程
- 收集 tool_calls 用于 trace
- done 事件增加 trace_path（格式 `{session_id}/{trace_id}`）
- 确保 trace 同步写入完成后才发送 done 事件（Architecture §6.8 方案 A）

### Step 6：修改 `app.py`
- 注册 traces 路由

### Step 7：验证 & 写日志
- 执行 T1-T11 测试
- 创建 `docs/phase3-dev-log.md`
- 创建 `docs/phase3-architecture.html`

---

## 8. Phase 3 → Phase 4 衔接

| Phase 3 产出 | Phase 4 依赖 |
|-------------|-------------|
| `PromptBuilder.build(tools_summary=...)` | Phase 4 传入工具摘要字符串 |
| `AgentManager.tools = []` | Phase 4 注册 6 个核心工具 |
| `ContextOrchestrator._detect_intent()` | Phase 4 的 skill 匹配可复用意图检测 |
| Trace 中 `tool_calls[]` | Phase 4 有实际工具调用后 trace 数据更丰富 |

---

## 9. 风险与缓解

| 风险 | 概率 | 缓解 | 引用 |
|------|------|------|------|
| system prompt 过长超出模型上下文窗口 | 中 | context_budget.md 预算控制 + 截断 + budget_report | PRD §4.4.4 |
| 关键词意图检测准确率不足 | 低 | MVP 阶段可接受；降级为全量默认注入；Phase 6 升级为 embedding 相似度 | Architecture §6.3 |
| Trace 写入与前端读取竞态 | 低 | 采用方案 A：done 在 trace 同步写入完成后才发送 | Architecture §6.8 |
| TraceWriter 与 SessionManager 同时写同一文件 | 低 | 当前单线程单用户场景不会并发；后续可加文件锁 | Architecture §6.2 |
| workspace 文件编码非 UTF-8 导致读取异常 | 低 | 统一使用 `encoding="utf-8"` + try/except fallback | — |
