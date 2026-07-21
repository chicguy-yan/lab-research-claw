# Phase 3 开发计划：Router × Context × Prompt × Trace 显式中枢层

> 基于 `docs/phase3_index.md`（Spec v2）+ `docs/architecture-summary.md` + Phase 1/2 实际交付
> **前置**：Phase 1（SSE chat + 会话 CRUD）+ Phase 2（Files API + Agent CRUD + 路径安全）已完成
> **目标**：`POST /api/chat` 从硬编码 system prompt 升级为"显式路由 → 最少上下文选择 → prompt 组装 → 写入建议 → trace 落盘"；`GET /api/traces` 可回放任意一轮的决策链路
> **最后更新**：2026-03-08

---

## 0. Phase 3 的唯一目标

> 让一次科研请求在单 workspace、单代理下，稳定形成：
> **主意图识别 → 最少上下文选择 → prompt 组装 → 写入建议生成 → trace 落盘。**

Phase 3 不是"新能力层"，而是整个科研工作台第一次出现的 **显式中枢层**。
它第一次回答"为什么这轮这样答，它建议写到哪里"。

**关键边界**：Phase 3 **不执行任何 memory 文件写入**。写入由 Phase 4 的 LLM 通过内生工具自主执行。
Phase 3 的 `atom_decision` 只是写入 trace 的**建议标签**，指导后续 Phase 4 的 LLM 工具调用行为。

---

## 1. Phase 1 → Phase 2 → Phase 3 衔接

### 已交付基线

| Phase | 模块 | Phase 3 如何使用 |
|-------|------|-----------------|
| P1 | `api/chat.py` — SSE 流式对话 | Phase 3 在其中插入 Orchestrator → Builder → TraceWriter 流程 |
| P1 | `graph/agent.py` — `AgentManager.astream()` | 不变，Phase 3 只替换传入的 `system_prompt` |
| P1 | `graph/session_manager.py` — envelope `{"messages":[], "traces":[]}` | TraceWriter 追加 `traces[]`；新增 traces helper + per-session lock |
| P2 | `api/files.py` — 文件读写 + tree | ContextOrchestrator 扫描 `memory/` 文件；PromptBuilder 读取文件内容 |
| P2 | `graph/path_utils.py` — `resolve_safe_path()` | trace 路径安全边界 |
| P2 | `app.py` — workspace 初始化 + 路由注册 | 新增 `traces_router` 注册 |

### Phase 3 产出 → 后续 Phase 依赖

| Phase 3 产出 | 后续依赖方 | 可靠性 |
|-------------|-----------|--------|
| `route` + `context_read[]` + `budget_report` | Phase 4 tools 接入后复用 trace 审计结构 | 可直接复用 |
| `PromptBuilder.build()` | Phase 4 注入 `tools_summary` 到 `## Tooling` | 可直接扩展 |
| `api/traces.py` | Phase 6 前端 trace 回放入口 | 可直接复用 |
| `atom_decision.write_mode` | Phase 4 LLM 工具调用时读取建议，自主决定写入 | ⚠️ Phase 3 只产建议，Phase 4 执行 |
| 更新后的 `AGENTS.md` 模板 | Phase 4+ 每轮 prompt 注入时不再有指令冲突 | 必须在 Phase 3 完成 |

---

## 2. 关键决策（对齐 phase3_index 硬约束）

1. **顶层 intent 固定为 `4+1`**
   `stage_progress` / `experiment_closure` / `mechanism_closure` / `writing_closure` / `general_consult`。
   不做复杂多层 Router。`input_tags` / `exec_tags` 只是标签，不升级成新路由层。

2. **Layer3 绑定是硬约束**
   - `stage_progress` → Pack-first
   - `experiment_closure` → Task-first
   - `mechanism_closure` → Task + Pack
   - `writing_closure` → Pack-first
   - `general_consult` → trace-only

3. **固定脊梁只保留轻量最小集**
   默认每轮固定：`AGENTS.md` + `memory/identity/project.md`。
   `context_budget.md` 只参与预算计算，**不**注入 prompt 正文。
   不把 `SOUL.md` / `IDENTITY.md` / `USER.md` / `MEMORY.md` / `TOOLS.md` / 全量 `identity/*` 升级成每轮必读。

4. **Trace 薄而硬**
   Trace 只回答 4 个问题：本轮属于哪个闭环、读了哪些文件为什么、主要操作了哪个原子对象、有没有因信息不足停住。
   不写长篇解释、不替代 Layer3 文档、不替代开发日志。

5. **Trace 采用 envelope 追加**
   不新增独立 trace 文件，统一追加到 `context_trace/{session_id}.json` 的 `traces[]`。

6. **`done` 只在 trace 落盘后发送**
   沿用 Phase 1 约束，由 `api/chat.py` 统一发 `done`，新增 `trace_path` 字段。

7. **Router 先内聚在 ContextOrchestrator 中**
   Phase 3 不单独建 `router.py`，Router 作为 orchestrator 的内部规则层实现，保留后续抽离自由度。

8. **预算先按字符数**
   避免引入复杂 token 计数依赖。`totalMaxChars` 默认 `120_000`，`perFileMaxChars` 默认 `20_000`。

9. **Phase 3 不执行文件写入，只记录写入建议**
   `atom_decision` 是写入 trace 的**建议标签**，告诉"这轮建议写什么"。
   真实写入由 Phase 4 的 LLM 通过内生工具（read_file / terminal 等）自主执行。
   这样设计的原因是：用户数据在 `assets/` 中，LLM 需要自己调用工具处理数据并写入 `memory/`，
   由确定性模块代劳会丧失大模型的泛化能力。
   Phase 3 的 `output_refs` 始终为空，Phase 4 tools 接入后由 trace 记录实际工具写入路径。

10. **Envelope 并发安全：per-session lock**
    `SessionManager` 的 read-modify-write 在 `append_trace()` 加入后有竞态风险。
    Phase 3 在 `session_manager.py` 新增 per-session `threading.Lock`，保护所有 envelope 读写。

11. **AGENTS.md 模板必须与 Phase 3 运行时行为对齐**
    AGENTS.md 是固定注入到每轮 prompt 的文件。当前模板内容与 Phase 3 设计有多处冲突（见 §14），
    必须在 Phase 3 完成时更新模板，否则模型会收到矛盾指令。

---

## 3. 边界：Phase 3 不做什么

- subagent / 多 agent 协作
- RAG / GraphRAG / hybrid retrieval
- tools 执行框架（Phase 4）
- 真上传链路（Phase 5）
- 多 workspace 激活依赖
- 前端大改（Phase 6）
- 复杂 planner
- 自动 skill mining
- **不执行 memory 文件写入**（Phase 4 LLM 工具自主执行）

---

## 4. 运行链路

Phase 3 的单轮闭环：

```text
User Request
  ↓
Router (intent + input_tags + exec_tags)
  ↓
Context Orchestrator (select files + budget trim + atom_decision suggestion)
  ↓
Prompt Builder (assemble system prompt)
  ↓
AgentManager.astream() (LLM response)
  ↓
Trace Writer (落盘 trace，含 atom_decision 建议)
  ↓
done event (含 trace_path)
```

### done 事件发送条件

`done` 必须在以下全部完成后再发：
1. assistant 输出已形成
2. trace 已成功写入 `context_trace/{session_id}.json`

---

## 5. 四段核心设计

### 5.1 Router

**硬约束**：顶层只有 5 个 intent，直接对应 PRD 四大记忆压力源。

| Intent | 面向场景 | Layer3 绑定 |
|--------|---------|------------|
| `stage_progress` | 阶段推进、汇报、Rxx 整理、近期成果汇总 | Pack-first |
| `experiment_closure` | 实验动作、对照缺口、参数矩阵、表征证明力 | Task-first |
| `mechanism_closure` | Co(IV) / ClO₂ 等机理证据链审计 | Task + Pack |
| `writing_closure` | R&D 目录树、中心句、主文/SI 图文策略 | Pack-first |
| `general_consult` | 兜底，不把普通咨询硬塞进长期结构 | trace-only |

**轻标签**（标签，不是新路由层）：

- `input_tags`：`has_asset_path` / `has_pdf` / `has_image` / `has_csv` / `has_time_range` / `text_only`
- `exec_tags`：`needs_more_info` / `pack_first` / `task_first` / `task_plus_pack` / `trace_only`

**实现策略**：MVP 用关键词匹配 + 降级为 `general_consult`。具体检测规则（纯关键词、规则表、可配置映射）留给实现自由。

### 5.2 Context Orchestrator

#### 固定脊梁（每轮至少考虑）

- `AGENTS.md`
- `memory/identity/project.md`
- `memory/identity/context_budget.md`（仅预算使用，不注入正文）

#### 意图扩展

| Intent | 优先考虑的文件 |
|--------|--------------|
| `stage_progress` | `180d_index.md` → time range 内 `weeks/` → 必要时最近 `days/` → 上一期 `stage_report` → `PACK_stage_report_*` |
| `experiment_closure` | `lab_context.md` → today `day` → active `TASK_*` → 必要时 `CONCEPT_*` |
| `mechanism_closure` | `project.md` 判据 → `TASK_mechanism_*` → `PACK_mechanism_*` → paper path / 摘要 |
| `writing_closure` | `project.md` 北极星 → `PACK_writing_*` → `PACK_figure_*` → supporting `TASK_*` |
| `general_consult` | 只拿最小必要上下文 |

#### 预算裁剪

- 来源：`memory/identity/context_budget.md`
- 默认值：`totalMaxChars=120_000`，`perFileMaxChars=20_000`
- 裁剪顺序：截断长文件 → 跳过低优先级 Layer3 → 跳过 Layer2 补充文件 → 不跳过 `AGENTS.md` 和 `project.md`
- 任何被截断/跳过必须记录到 trace（why + status）

#### 按需 Skill 说明

- 只有主意图命中后，才读对应 `SKILL.md`
- 不允许默认全量注入所有 skill 说明

### 5.3 Prompt Builder

PromptBuilder 只负责拼接，不负责业务判断。

**固定骨架**：

```text
You are a personal assistant running inside OpenClaw.

## Tooling
{tools_summary — Phase 3 留空，Phase 4 填充}

## Workspace
{工作目录声明 + 规则}

## Inbound Context
{JSON: 平台/时区/语言/会话类型/当前日期}

# Project Context
## {path_1}
{file_content_1}

## {path_2}
{file_content_2}
...
```

**约束**：
- `context_budget.md` 不进入 `# Project Context`
- `selected_files` 顺序由 Orchestrator 决定
- Builder 只读取 `status != skipped` 的文件
- 不把 prompt 组装逻辑散落到 `api/chat.py`

**实现自由度**：
- `build()` 返回字符串还是结构化对象后转字符串，由实现决定
- 截断逻辑在 orchestrator 做还是 builder 做，由实现决定

### 5.4 Trace Writer

**Trace 最小回答 4 个问题**：
1. 本轮被判成哪个闭环
2. 读了哪些文件，为什么
3. 最后主要建议操作哪个原子对象
4. 有没有因为信息不足而停在 Missing

**Trace 硬字段**：

```python
TraceEntry = {
    "trace_id": str,           # e.g. "T0001"
    "timestamp": str,          # ISO 8601
    "route": {
        "intent": str,         # 5 选 1
        "input_tags": list[str],
        "exec_tags": list[str],
    },
    "context_read": [
        {
            "path": str,       # 文件相对路径
            "layer": str,      # workspace | skills | memory_identity | memory_timeline | memory_atom | uploads
            "why": str,        # 选择原因（短句）
            "status": str,     # full | truncated | skipped
        }
    ],
    "budget_report": {
        "total_budget": int,
        "used_chars": int,
        "truncated_paths": list[str],
        "skipped_paths": list[str],
    },
    "atom_decision": {
        "concept_ref": str | None,
        "task_refs": list[str],
        "pack_refs": list[str],
        "write_mode": list[str],   # e.g. ["trace_only"] 或 ["suggest_update_task", "suggest_update_pack"]
    },
    "missing_fields": list[str],
    "output_refs": list[str],      # Phase 3 始终为 []，Phase 4 由工具填充
    "tool_calls": list[dict],
    "assistant_summary": str,      # 保持简短
}
```

**`write_mode` 枚举值**（`list[str]` 类型，可组合）：
- `trace_only` — 只记 trace，不建议写文件
- `suggest_create_task` — 建议新建 TASK
- `suggest_update_task` — 建议更新已有 TASK
- `suggest_create_pack` — 建议新建 PACK
- `suggest_update_pack` — 建议更新已有 PACK
- `skip` — 不操作

**为什么用 `list[str]`**：`mechanism_closure` 绑定 Task + Pack，需要表达 `["suggest_update_task", "suggest_update_pack"]`。单字符串 `str` 无法表达双写建议。

**落盘**：追加到 `context_trace/{session_id}.json` 的 `traces[]`。

**不建议做太重的**：很长的 response_summary、大量主观解释、复杂 trace analytics、trace 替代开发日志/Layer3 文档。

---

## 6. atom_decision 建议规则

Phase 3 **不执行文件写入**。`atom_decision` 是写入 trace 的建议，指导 Phase 4 LLM 工具调用行为。
真实写入由 Phase 4 的 LLM 通过内生工具（read_file / terminal 等）自主决定和执行，这样才能保证大模型的泛化能力。

### 6.1 默认建议规则（对应 Layer3 绑定）

| Intent | 建议 write_mode | 降级策略 |
|--------|----------------|---------|
| `stage_progress` | `["suggest_update_pack"]` | 找不到明确 pack → `["trace_only"]` |
| `experiment_closure` | `["suggest_update_task"]` | 无明确 task → `["suggest_create_task"]` |
| `mechanism_closure` | `["suggest_update_task", "suggest_update_pack"]` | Phase 3 MVP 实际降级为 `["trace_only"]`，仅给出 `task_refs` + `pack_refs` 建议 |
| `writing_closure` | `["suggest_update_pack"]` | 找不到明确 pack → `["trace_only"]` |
| `general_consult` | `["trace_only"]` | — |

### 6.2 Phase 3 vs Phase 4 的分工

| 阶段 | 职责 |
|------|------|
| Phase 3 | 生成 `atom_decision`（建议标签 + refs），写入 trace。`output_refs` 始终为空。 |
| Phase 4 | LLM 通过 read_file / terminal 等工具读取 assets/ 数据，自主写入 memory/ 文件。trace 记录实际写入路径到 `output_refs`。 |

---

## 7. 新建/修改文件清单

### 新建（4 个）

```text
backend/
├── graph/
│   ├── context_orchestrator.py   # Router + 上下文选择 + 预算裁剪 + atom_decision
│   ├── prompt_builder.py         # 五块 system prompt 组装
│   └── trace_writer.py           # trace entry 构造 + envelope 追加
└── api/
    └── traces.py                 # trace 列表 + 详情查询（2 个端点）
```

### 修改（6 个）

```text
backend/
├── api/
│   └── chat.py                                         # 接入 Orchestrator → Builder → TraceWriter 流程
├── graph/
│   └── session_manager.py                              # traces helper + per-session lock
├── app.py                                              # 注册 traces_router
└── workspace-templates/
    ├── AGENTS.md                                       # 对齐 Phase 3 运行时行为（见 §14）
    ├── context_trace/README.md                         # trace 存储说明对齐
    └── context_trace/TRACE_TEMPLATE.json               # 更新为 trace entry schema
```

共 10 个文件变更。Phase 3 不新增第三方依赖。

---

## 8. API 端点

### 新增 Traces API（2 个）

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/traces?session_id=&limit=` | 列出某 session 的 trace 列表 |
| GET | `/api/traces/{session_id}/{trace_id}` | 返回单条 trace 详情 |

### `done` 事件变更

```json
{
  "session_id": "xxx",
  "trace_path": "xxx/T0001"
}
```

### 兼容性要求

- 不破坏现有 `/api/chat` SSE 协议
- `done` 事件只允许增加字段，不移除已有字段

---

## 9. 核心模块说明

### 9.1 `graph/context_orchestrator.py`

**职责**：路由判定 + 上下文选择 + 预算裁剪 + atom_decision 建议生成

**推荐数据类**：

```python
@dataclass
class RouteDecision:
    intent: str            # 5 选 1
    input_tags: list[str]
    exec_tags: list[str]

@dataclass
class ContextRead:
    path: str
    layer: str             # workspace | skills | memory_identity | memory_timeline | memory_atom | uploads
    why: str
    status: str            # full | truncated | skipped

@dataclass
class AtomDecision:
    concept_ref: str | None
    task_refs: list[str]
    pack_refs: list[str]
    write_mode: list[str]  # e.g. ["trace_only"] 或 ["suggest_update_task", "suggest_update_pack"]

@dataclass
class SelectionResult:
    route: RouteDecision
    context_read: list[ContextRead]
    budget_report: dict
    atom_decision: AtomDecision
    missing_fields: list[str]
```

**核心方法**：

```python
class ContextOrchestrator:
    def __init__(self, workspace_dir: Path): ...
    def select(self, message: str, session_id: str) -> SelectionResult: ...
```

**内部分步**：
1. `_detect_intent(message)` → `RouteDecision`
2. `_collect_candidates(route)` → 候选文件列表
3. `_apply_budget(candidates, budget)` → `context_read[]` + `budget_report`
4. `_resolve_atom_decision(route, context_read)` → `AtomDecision`

### 9.2 `graph/prompt_builder.py`

**职责**：把 Orchestrator 的选择结果拼成 system prompt

**核心方法**：

```python
class PromptBuilder:
    def __init__(self, workspace_dir: Path): ...
    def build(self, selection: SelectionResult, metadata: dict | None = None) -> str: ...
```

**输入**：`SelectionResult` + 可选 metadata
**输出**：拼接好的 `system_prompt: str`

### 9.3 `graph/trace_writer.py`

**职责**：构造 trace entry + 写入 envelope

**核心方法**：

```python
class TraceWriter:
    def __init__(self, session_manager: SessionManager): ...
    def write_trace(
        self,
        session_id: str,
        selection: SelectionResult,
        tool_calls: list[dict],
        assistant_summary: str,
    ) -> str: ...  # 返回 trace_id
```

注意：`output_refs` 在 Phase 3 始终为 `[]`，由 TraceWriter 内部硬编码。Phase 4 tools 接入后由调用方传入。

### 9.4 `api/traces.py`

**职责**：暴露 trace 查询端点

```python
GET /api/traces?session_id=&limit=   → {"traces": [...]}
GET /api/traces/{session_id}/{trace_id} → single trace entry
```

### 9.5 `graph/session_manager.py` 修改

保持现有 envelope schema 不变，新增两部分：

**A. traces 操作方法**：

```python
def append_trace(self, session_id: str, trace_entry: dict) -> None: ...
def list_traces(self, session_id: str, limit: int | None = None) -> list[dict]: ...
def get_trace(self, session_id: str, trace_id: str) -> dict | None: ...
```

**B. per-session lock**（并发安全）：

```python
import threading

class SessionManager:
    def __init__(self, workspace_dir: Path) -> None:
        ...
        self._locks: dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()  # 保护 _locks dict 本身

    def _session_lock(self, session_id: str) -> threading.Lock:
        with self._locks_lock:
            if session_id not in self._locks:
                self._locks[session_id] = threading.Lock()
            return self._locks[session_id]
```

`save_message()` 和 `append_trace()` 内部使用 `with self._session_lock(session_id):` 保护 read-modify-write。

### 9.6 `api/chat.py` 接入流程

现状：硬编码 `SYSTEM_PROMPT`，流结束后只持久化消息。

Phase 3 接入顺序：

```python
# 1. ensure session + load history（不变）
# 2. ContextOrchestrator.select(message, session_id) → SelectionResult
#    （包含 route、context_read、budget_report、atom_decision 建议）
# 3. PromptBuilder.build(selection, metadata) → system_prompt
# 4. AgentManager.astream(message, history, system_prompt)（不变）
# 5. 汇总 assistant_text + tool_calls
# 6. 持久化 messages（不变）
# 7. TraceWriter.write_trace(session_id, selection, tool_calls, assistant_summary)
#    （atom_decision 建议已在 selection 中，Phase 3 不执行写入）
# 8. yield done event（含 trace_path）
```

### 9.7 `app.py` 变更

- 注册 `traces_router`
- 保持现有 startup 结构不变

---

## 10. 实现顺序

1. **`graph/context_orchestrator.py`**
   - 数据类：`RouteDecision`、`ContextRead`、`AtomDecision`、`SelectionResult`
   - `_detect_intent()` — 关键词匹配 + 降级
   - `_collect_candidates()` — 固定脊梁 + 意图扩展
   - `_apply_budget()` — 预算裁剪
   - `_resolve_atom_decision()` — Layer3 绑定规则
   - `select()` — 组合以上步骤

2. **`graph/prompt_builder.py`**
   - 五块骨架拼接
   - 读取文件内容（`status != skipped` 的）
   - 跳过 `context_budget.md` 正文注入

3. **`graph/session_manager.py` 修改**
   - 新增 per-session lock（`_session_lock()`）
   - 新增 `append_trace()` / `list_traces()` / `get_trace()`
   - 现有 `save_message()` 加锁保护
   - 不改 envelope schema

4. **`graph/trace_writer.py`**
   - trace entry 构造（trace_id 生成、timestamp）
   - 调用 `session_manager.append_trace()` 落盘
   - `output_refs` 硬编码为 `[]`

5. **`api/traces.py`**
   - 2 个查询端点

6. **`api/chat.py` 修改**
   - 接入完整链路
   - `done` 晚于 trace 写入，新增 `trace_path`

7. **`app.py` 修改**
   - 注册 `traces_router`

8. **模板迁移**（见 §14）
   - 更新 `workspace-templates/AGENTS.md`
   - 更新 `workspace-templates/context_trace/README.md`
   - 更新 `workspace-templates/context_trace/TRACE_TEMPLATE.json`
   - `_migrate_workspace()` 已有机制自动同步已有 workspace

9. **验证回归 + gold cases**

10. **输出文档**
    - `docs/phase3-dev-log.md`
    - `docs/phase3-architecture.html`

---

## 11. 验证方式

### 11.1 Phase 1/2 回归

```bash
curl http://localhost:8002/
curl http://localhost:8002/api/sessions
curl http://localhost:8002/api/files/tree
curl http://localhost:8002/api/agents
```

### 11.2 Phase 3 Gold Cases（5 类）

#### Case 1: `stage_progress`

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请总结最近的阶段推进重点，准备 R06 汇报","session_id":"gold-stage","stream":true}'
```

预期：
- `route.intent == "stage_progress"`
- `exec_tags` 含 `pack_first`
- `context_read` 含 `180d_index.md`、相关 `weeks/`
- `atom_decision.write_mode == ["suggest_update_pack"]` 或 `["trace_only"]`

#### Case 2: `experiment_closure`

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"今天做了 PMSO 实验，对照组缺少一个空白样，需要记录","session_id":"gold-exp","stream":true}'
```

预期：
- `route.intent == "experiment_closure"`
- `exec_tags` 含 `task_first`
- `context_read` 含 `lab_context.md`、today `day`
- `atom_decision.write_mode == ["suggest_update_task"]` 或 `["suggest_create_task"]`

#### Case 3: `mechanism_closure`

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Co(IV) 的证据链现在能闭环吗？ClO₂ 那条线还缺什么？","session_id":"gold-mech","stream":true}'
```

预期：
- `route.intent == "mechanism_closure"`
- `exec_tags` 含 `task_plus_pack`
- `context_read` 含 `project.md` 判据、`TASK_mechanism_*`
- `atom_decision.write_mode == ["trace_only"]`（MVP 降级），但 `task_refs` + `pack_refs` 有值

#### Case 4: `writing_closure`

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我整理一下论文的 Results 目录树和图文策略","session_id":"gold-write","stream":true}'
```

预期：
- `route.intent == "writing_closure"`
- `exec_tags` 含 `pack_first`
- `context_read` 含 `project.md`
- `atom_decision.write_mode == ["suggest_update_pack"]` 或 `["trace_only"]`

#### Case 5: `general_consult`

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Python 里怎么用 pandas 读 csv？","session_id":"gold-general","stream":true}'
```

预期：
- `route.intent == "general_consult"`
- `exec_tags` 含 `trace_only`
- `atom_decision.write_mode == ["trace_only"]`
- `context_read` 最少

### 11.3 每类 Gold Case 必检项

| 检查项 | 说明 |
|--------|------|
| Router | intent / input_tags / exec_tags 是否合理 |
| Context | 是否读到该读的，是否没有明显过读 |
| Budget | 被截断/跳过是否可解释 |
| Layer3 | atom_decision 建议是否符合绑定规则 |
| Trace | 是否完整落盘、`context_read[]` 满足最小字段 |
| done | 是否晚于 trace 写入、是否含 `trace_path` |
| output_refs | Phase 3 必须为 `[]` |

### 11.4 Trace API 验证

```bash
# 列出 traces
curl "http://localhost:8002/api/traces?session_id=gold-stage"

# 单条 trace
curl "http://localhost:8002/api/traces/gold-stage/T0001"
```

### 11.5 异常测试

| 场景 | 预期行为 |
|------|---------|
| `lab_context.md` 不存在 | 跳过，`context_read` 中 `status: skipped`，不崩溃 |
| `context_budget.md` 配置过小 | 部分文件被 `truncated`/`skipped`，trace 有记录 |
| 未命中任何 `TASK_*` / `PACK_*` | `atom_decision.write_mode` 降级为 `["trace_only"]` |
| 指定文件不存在 | 优雅降级，trace 记录缺口 |
| assistant 回复为空 | `trace.assistant_summary` 为空，trace 仍然落盘 |

---

## 12. Phase 3 完成判据

满足以下条件即可判定 Phase 3 成立：

- `/api/chat` 不再依赖硬编码固定 system prompt
- 每轮都有显式 route / context_read / budget_report / atom_decision
- trace 能回答"为什么读这些文件、建议打到哪个 Task/Pack"
- `done` 一定晚于 trace 写入
- 5 类 gold case 均能跑通
- Phase 1/2 接口不回归
- **Phase 3 不执行任何 memory 文件写入**（`output_refs` 始终为 `[]`）
- **AGENTS.md 模板与 Phase 3 运行时行为对齐**（无指令冲突）

真正的通过标准：

> 你能拿任意一轮请求，清楚解释它为什么被路由成这样、为什么读这些文件、建议写什么原子资产。

---

## 13. Phase 3 不做的事

- 不做多 agent / subagent
- 不做 tools 执行框架
- 不做 RAG / GraphRAG / hybrid retrieval
- 不做真实上传链路
- 不做前端大改
- 不做依赖 Agent 切换
- 不做复杂 planner
- 不做自动 skill mining
- 不把 skill 名重新抬成顶层业务意图
- 不把 input_tags / exec_tags 膨胀成复杂多层路由
- 不把固定上下文做重
- 不把 Trace 写成超长日志
- **不执行 memory 文件的 create/update**（Phase 4 LLM 工具自主执行）

---

## 14. 模板迁移清单

AGENTS.md 是固定注入到每轮 prompt 的文件。以下是当前模板与 Phase 3 设计的冲突点，必须在 Phase 3 中修复。

### 14.1 `workspace-templates/AGENTS.md`

| 位置 | 当前内容 | 冲突 | 修改为 |
|------|---------|------|--------|
| §0 第 29 行 | `写入：.openclaw/context_trace/TXXXX.json` | Phase 3 trace 追加到 envelope `traces[]`，不写独立文件 | `写入：追加到 context_trace/{session_id}.json 的 traces[] 数组` |
| §1 第 35-41 行 | 默认读 `SOUL.md` / `USER.md` / `IDENTITY.md` / 全量 Layer1 / `skills/registry.json` | Phase 3 固定脊梁只有 `AGENTS.md` + `project.md`，其余按 intent 扩展 | 改为"由 ContextOrchestrator 按主意图决定本轮读取范围，固定读取本文件 + project.md" |
| §2 第 43-49 行 | 写入规则直接指导 Agent 写文件 | Phase 3 不执行写入，Phase 4 LLM 工具自主写入 | 改为"Phase 4 工具可用后，Agent 可通过工具自主写入以下位置；当前阶段只生成建议" |

### 14.2 `workspace-templates/context_trace/README.md`

| 当前内容 | 修改为 |
|---------|--------|
| `命名：T0001.json / T0002.json / ...`（独立文件） | `Trace 追加到 {session_id}.json 的 traces[] 数组，trace_id 格式为 T0001/T0002/...` |

### 14.3 `workspace-templates/context_trace/TRACE_TEMPLATE.json`

当前内容是 OpenAI messages 示例（user/assistant/tool），不是 trace schema。
替换为 Phase 3 的 trace entry schema（与 §5.4 一致）。

### 14.4 迁移机制

- 模板更新后，`app.py` 的 `_migrate_workspace()` 会在启动时自动将新增文件同步到已有 workspace
- 但 `_migrate_workspace()` 不覆盖已有文件，所以对于 AGENTS.md 等已存在的文件，需要额外处理：
  - 方案：Phase 3 启动时检查 AGENTS.md 是否包含旧版标记（如 `TXXXX.json`），如果是则用模板覆盖
  - 或：手动更新 workspace-default 中的对应文件（单用户 MVP 可接受）
