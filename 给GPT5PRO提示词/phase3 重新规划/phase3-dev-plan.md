# Phase 3 开发计划：Context Orchestrator + PromptBuilder + TraceWriter

> 基于 PRD v0.2 + TAD v0.2 + architecture-summary.md + phase3-index.md (spec)
> **前置**：Phase 1 (SSE chat + 会话 CRUD) + Phase 2 (文件系统 API + Agent CRUD) 均已完成
> **目标**: `POST /api/chat` 时自动选择上下文、组装 Prompt、写入 trace；`GET /api/traces` 可回放
> **最后更新**: 2026-03-08

---

## Phase 2 → Phase 3 衔接

| Phase 2 提供 | Phase 3 如何使用 |
|-------------|-------------|
| `GET /api/files/tree` | ContextOrchestrator 发现 workspace 中的 memory / assets 文件 |
| `GET /api/files` 读文件 | PromptBuilder 读取 Prompt 组件和 memory 文件注入 system prompt |
| `POST /api/files` 写文件 | TraceWriter 和 memory 写入（白名单内：`memory/`、`context_trace/`） |
| `resolve_safe_path()` | 全局路径安全工具 |
| `SessionManager._read_envelope` / `_write_envelope` | TraceWriter 向 envelope 的 `traces` 字段追加 trace 记录 |
| `app.py` 路由注册模式 | 新增 `traces_router` |

| Phase 3 产出 | Phase 4+ 依赖方 | 可靠性 |
|-------------|-------------|--------|
| `ContextOrchestrator.select_context()` | Phase 4 tools 注入时可复用上下文选择 | 本 Phase 交付 |
| `PromptBuilder.build()` | Phase 4/5 扩展 tools/RAG 注入块 | 本 Phase 交付 |
| `TraceWriter.write_trace()` | Phase 6 前端 trace 回放 | 本 Phase 交付 |
| `GET /api/traces` | Phase 6 前端回放视图 | 本 Phase 交付 |
| `chat.py` 集成三模块 | 后续 Phase 在此基础上扩展 | 本 Phase 修改 |

---

## 关键决策

1. **ContextOrchestrator 直接读文件系统** — 不通过 HTTP API，直接用 `Path` 读取 workspace 文件。这是内部模块，不需要经过 API 层。读取时使用 `resolve_safe_path()` 做安全检查。

2. **Intent hint 实现方式** — MVP 阶段使用关键词匹配 + 降级为默认排序。5 类 intent：`stage_progress` / `experiment_closure` / `mechanism_closure` / `writing_closure` / `general_consult`。不做重型 Router。

3. **Trace 写入 envelope** — trace 写入 `context_trace/{session_id}.json` 的 `traces` 字段（Phase 1 已预留），与 `messages` 互不污染。TraceWriter 直接操作 SessionManager 的 envelope。

4. **单文件字符上限** — 20,000 字符，超出追加 `...[truncated]`。总预算由 `context_budget.md` 控制。

5. **done 时机不变** — `done` 事件仍由 `api/chat.py` 统一发送，但需保证 trace 写入完成后才发 done（同步写入）。

6. **不修改 Phase 1/2 核心模块** — `session_manager.py`、`agent.py`、`files.py`、`agents.py`、`path_utils.py` 不做修改。仅修改 `chat.py` 和 `app.py` 做集成。

7. **无新依赖** — Phase 3 不引入新的 Python 包。

---

## 新建/修改文件清单

### 新建（4 个）

```
backend/
├── graph/
│   ├── context_orchestrator.py   # ContextOrchestrator — 上下文选择 + intent hint
│   ├── prompt_builder.py         # PromptBuilder — system/user prompt 组装
│   └── trace_writer.py           # TraceWriter — trace 落盘到 envelope
└── api/
    └── traces.py                 # Trace 查询 API（2 个端点）
```

### 修改（2 个）

```
backend/
├── api/chat.py                   # 集成 ContextOrchestrator + PromptBuilder + TraceWriter
└── app.py                        # 注册 traces_router + 初始化新模块
```

共 6 个文件变更。

---

## API 端点（2 个新增）

### Traces API

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/traces?session_id=...&limit=20` | 查询某 session 的 trace 列表（按时间倒序） |
| GET | `/api/traces/{session_id}/latest` | 获取某 session 最近一条 trace |

---

## 核心模块详细设计

### 1. `graph/context_orchestrator.py` — ContextOrchestrator

**职责**：读取控制平面 → 形成 intent hint → 选择 context → 管理预算

```python
class ContextOrchestrator:
    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    def select_context(
        self,
        message: str,
        selected_files: list[str] | None = None,
    ) -> ContextResult:
        """
        返回:
          - intent_hint: str (5 类之一)
          - context_files: list[ContextFile] (按优先级排序)
          - budget_report: dict (预算使用情况)
        """
```

**Memory md 文件溯源约定**：

memory 层的 md 文件是对 assets 原始文件（PDF、图片、数据文件等）的结构化沉淀，
目的是节省上下文（md 比原始文件小得多）。每个 memory md 文件**必须**在头部包含
`source_assets` 字段，记录其对应的原始 assets 文件路径，方便用户需要溯源时可以
追溯到原始材料：

```markdown
---
source_assets:
  - assets/uploads/XRD_sample_03.pdf
  - assets/uploads/SEM_image_03.png
created_at: 2026-03-08
---
# TASK_exp_003: XRD + SEM 联合表征
...
```

ContextOrchestrator 读取 memory 文件时，解析 `source_assets` 字段并记录到
`ContextFile.asset_sources` 中，供 trace 溯源和前端展示使用。

**ContextFile 新增字段**：

```python
@dataclass
class ContextFile:
    path: str           # 相对路径
    layer: str          # workspace | skills | memory_identity | memory_timeline | memory_concepts | memory_tasks | memory_packs | uploads
    why: str            # 选择原因
    status: str         # full | truncated | skipped
    content: str        # 文件内容（可能已截断）
    char_count: int     # 原始字符数
    asset_sources: list[str]  # 该 memory 文件对应的原始 assets 路径（非 memory 层文件为空列表）
```

**ContextResult 数据结构**：

```python
@dataclass
class ContextResult:
    intent_hint: str
    context_files: list[ContextFile]
    budget_report: dict
    control_context: list[str]  # 本轮使用的控制平面文件路径列表
```

**上下文选择逻辑**：

1. **固定脊梁 — 控制平面六大 md**（every turn always inject，缺一不可）：
   - `AGENTS.md` — 技能协议 + 记忆协议
   - `SOUL.md` — 人格与行为边界
   - `IDENTITY.md` — Agent 身份
   - `USER.md` — 用户画像与偏好
   - `SKILLS_SNAPSHOT.md` — 可用技能清单
   - `memory/identity/project.md` — 项目北极星与判据
   - *(预算控制用)* `memory/identity/context_budget.md` — 仅用于预算计算，不注入 prompt 正文

2. **默认注入**（按优先级）：
   - Layer1：`memory/identity/user.md`, `memory/identity/lab_context.md`
   - Layer2：`memory/timeline/180d_index.md`

3. **Intent 扩展**（根据 intent_hint 追加）：
   - `stage_progress` → `memory/timeline/180d_index.md`, 相关 `memory/timeline/weeks/`, 上一期 `memory/timeline/stage_reports/`, 最近 `memory/timeline/days/<YYYY-MM-DD>.md`
   - `experiment_closure` → `memory/identity/lab_context.md`, today `memory/timeline/days/<YYYY-MM-DD>.md`, active `memory/tasks/TASK_*`
   - `mechanism_closure` → project 判据, `memory/tasks/TASK_mechanism_*`, `memory/packs/PACK_mechanism_*`, `memory/concepts/CONCEPT_*`
   - `writing_closure` → project 北极星, `memory/packs/PACK_writing_*`, `memory/packs/PACK_figure_*`
   - `general_consult` → 仅默认注入

4. **用户指定文件**（`selected_files` 参数）直接注入

**Intent 识别规则**（关键词匹配）：

| Intent | 匹配关键词 |
|--------|-----------|
| `stage_progress` | `阶段汇报`, `进度`, `milestone`, `Rxx`, `ppt_pack`, `第N次` |
| `experiment_closure` | `实验`, `合成`, `表征`, `XRD`, `SEM`, `BET`, `kobs`, `淬灭` |
| `mechanism_closure` | `机理`, `Co(IV)`, `ClO₂`, `PMSO`, `DPD`, `自由基`, `证据链` |
| `writing_closure` | `论文`, `写作`, `摘要`, `introduction`, `图`, `figure`, `manuscript` |
| `general_consult` | 降级默认 |

**预算控制**：
- 读取 `context_budget.md` 获取总预算（默认 80,000 字符）
- 单文件上限 20,000 字符
- 超预算时按优先级从后向前 skip
- 被截断/skip 的文件记录 `status` 和 `why`

---

### 2. `graph/prompt_builder.py` — PromptBuilder

**职责**：将 ContextResult 按六块结构拼装 system/user prompt

```python
class PromptBuilder:
    def build(
        self,
        context_result: ContextResult,
        user_message: str,
        metadata: dict | None = None,
    ) -> tuple[str, str]:
        """
        返回 (system_prompt, user_prompt)
        """
```

**System Prompt 六块结构**：

```
Block 1: 身份行（固定常量）
  "You are a personal assistant running inside OpenClaw."

Block 2: ## Tooling
  列出可用工具摘要（Phase 3 为空，Phase 4 填充）

Block 3: ## Workspace
  工作目录声明 + 规则：
  - Project Context 文件是本轮事实来源
  - 信息不足必须列 Missing checklist，禁止脑补

Block 4: ## Inbound Context (trusted metadata)
  JSON: 平台/时区/语言/会话类型/当前日期/intent_hint

Block 5: # Memory Map（三层文件索引）
  列出三层 memory 中当前存在的所有 md 文件路径，让通用 Agent 自主决定
  本轮是否需要额外读取某些文件：
  ```
  ## Layer 1 — identity/
  - memory/identity/project.md        ← 已注入
  - memory/identity/user.md           ← 已注入
  - memory/identity/lab_context.md    ← 已注入
  - memory/identity/context_budget.md ← 仅预算

  ## Layer 2 — timeline/
  - memory/timeline/180d_index.md     ← 已注入
  - memory/timeline/phases/P01_bootstrap.md
  - memory/timeline/phases/P02_material_screening.md
  - memory/timeline/weeks/_WEEK_TEMPLATE.md
  - memory/timeline/days/2026-03-08.md
  - memory/timeline/stage_reports/_STAGE_REPORT_TEMPLATE.md
  ...

  ## Layer 3 — concepts/ + tasks/ + packs/
  - memory/concepts/CONCEPT_chlorite_activation.md
  - memory/tasks/TASK_baseline_activity.md
  - memory/tasks/TASK_exp_003.md
  - memory/packs/PACK_stage_report_R01.md
  - memory/packs/PACK_mechanism_coiv.md
  ...
  ```
  每个路径后标注 `← 已注入` 或不标（表示本轮未注入但可按需读取）。
  Agent 若判断需要某文件，可通过 tool 读取（Phase 4）或在回复中列出 Missing checklist。

Block 6: # Project Context
  逐文件注入：
  ## <path>
  <file_content>
```

**User Prompt 结构**：

```
[可选] <untrusted> JSON 代码块（上传文件路径等）
用户正文
```

**PromptBuilder 不负责**：
- 研究判断
- memory 决策
- trace 决策

---

### 3. `graph/trace_writer.py` — TraceWriter

**职责**：每轮对话完成后，将审计信息写入 envelope 的 `traces` 字段

```python
class TraceWriter:
    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    def write_trace(
        self,
        session_id: str,
        context_result: ContextResult,
        tool_calls: list[dict],
        memory_decision: dict,
        output_refs: list[str],
    ) -> dict:
        """
        写入 trace 到 envelope.traces[]，返回 trace 对象
        """
```

**Trace 结构**（推荐字段）：

```json
{
  "trace_id": "uuid",
  "timestamp": "ISO 8601",
  "intent_hint": "general_consult",
  "control_context": ["AGENTS.md"],
  "context_read": [
    {
      "path": "memory/identity/project.md",
      "layer": "memory_identity",
      "why": "项目北极星与判据，每轮必读",
      "status": "full",
      "asset_sources": []
    },
    {
      "path": "memory/tasks/TASK_exp_003.md",
      "layer": "memory_tasks",
      "why": "intent=experiment_closure, 匹配当前实验任务",
      "status": "full",
      "asset_sources": ["assets/uploads/XRD_sample_03.pdf", "assets/uploads/SEM_image_03.png"]
    }
  ],
  "asset_refs": ["assets/uploads/XRD_sample_03.pdf", "assets/uploads/SEM_image_03.png"],
  "budget_report": {
    "total_budget": 80000,
    "total_used": 12345,
    "files_injected": 5,
    "files_skipped": 0,
    "files_truncated": 1
  },
  "tool_calls": [],
  "memory_decision": {
    "action": "skip",
    "target_layer": null,
    "target_path": null,
    "reason": "本轮为通用咨询，无需写入 memory"
  },
  "missing_fields": [],
  "output_refs": []
}
```

**写入机制**：
- 读取 `context_trace/{session_id}.json` envelope
- 向 `traces` 数组追加新 trace
- 写回文件
- 返回 trace 对象（供 `done` 事件携带 trace_id）

---

### 4. `api/traces.py` — Trace 查询 API

```python
@router.get("")
async def list_traces(session_id: str, limit: int = 20):
    """GET /api/traces?session_id=...&limit=20"""
    # 读取 envelope → 返回 traces 数组（按时间倒序，截取 limit）

@router.get("/{session_id}/latest")
async def latest_trace(session_id: str):
    """GET /api/traces/{session_id}/latest"""
    # 返回最近一条 trace
```

---

### 5. `api/chat.py` 集成修改

Phase 3 的核心集成点。修改后的流程：

```
Step 1. SessionManager.load_session_for_agent(session_id)
Step 2. ContextOrchestrator.select_context(message)          ← NEW
Step 3. PromptBuilder.build(context_result, message)         ← NEW (替换硬编码 SYSTEM_PROMPT)
Step 4. AgentManager.astream(message, history, system_prompt)
Step 5. SessionManager.save_message(...)
Step 6. TraceWriter.write_trace(...)                         ← NEW
Step 7. yield SSE done (含 trace_id)                         ← MODIFIED (附带 trace_id)
```

**关键变更**：
- 删除 `SYSTEM_PROMPT` 硬编码常量
- `done` 事件数据中增加 `trace_id` 字段
- 异常处理：ContextOrchestrator/PromptBuilder 失败时降级为硬编码 prompt，仍然能对话

---

### 6. `app.py` 修改

```python
# 新增 import
from api.traces import router as traces_router
from graph.context_orchestrator import ContextOrchestrator
from graph.prompt_builder import PromptBuilder
from graph.trace_writer import TraceWriter

# startup 中初始化
context_orchestrator = ContextOrchestrator(cfg.DEFAULT_WORKSPACE_DIR)
prompt_builder = PromptBuilder()
trace_writer = TraceWriter(cfg.DEFAULT_WORKSPACE_DIR)

app.state.context_orchestrator = context_orchestrator
app.state.prompt_builder = prompt_builder
app.state.trace_writer = trace_writer

# 注册路由
app.include_router(traces_router, prefix="/api")
```

---

## 实现顺序

| Step | 内容 | 文件 |
|------|------|------|
| 1 | 创建 ContextOrchestrator | `graph/context_orchestrator.py` |
| 2 | 创建 PromptBuilder | `graph/prompt_builder.py` |
| 3 | 创建 TraceWriter | `graph/trace_writer.py` |
| 4 | 创建 Traces API | `api/traces.py` |
| 5 | 修改 chat.py 集成三模块 | `api/chat.py` |
| 6 | 修改 app.py 注册路由+初始化 | `app.py` |
| 7 | 启动 + curl 验证全部端点 | — |
| 8 | 输出文档 | `phase3-dev-log.md` + `phase3-architecture.html` |

---

## 验证方式

### 测试 1：服务启动
```bash
cd backend && python3 -m uvicorn app:app --port 8002 --reload
# 预期：无报错，Phase 1 + Phase 2 + Phase 3 路由全部注册
```

### 测试 2：对话带 trace
```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我梳理一下当前项目进度","session_id":"p3test","stream":true}'
# 预期：SSE token 流 + done 事件含 trace_id
```

### 测试 3：Trace 落盘
```bash
cat backend/.openclaw/workspace-default/context_trace/p3test.json | python3 -m json.tool
# 预期：envelope 中 traces 数组非空，包含 context_read / intent_hint / memory_decision
```

### 测试 4：Trace API 查询
```bash
curl "http://localhost:8002/api/traces?session_id=p3test"
# 预期：返回 trace 列表
```

### 测试 5：Trace 最近一条
```bash
curl "http://localhost:8002/api/traces/p3test/latest"
# 预期：返回最近一条 trace，含 context_read[] 详情
```

### 测试 6：Intent 识别验证
```bash
# 阶段汇报意图
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"准备第3次阶段汇报","session_id":"p3intent","stream":true}'
# 预期：trace 中 intent_hint 为 stage_progress

# 机理意图
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"分析Co(IV)中间体的证据链","session_id":"p3mech","stream":true}'
# 预期：trace 中 intent_hint 为 mechanism_closure
```

### 测试 7：预算截断验证
```bash
# 手动在 memory/identity/project.md 写入超过 20000 字符
# POST /api/chat 后检查 trace 中对应文件 status 为 truncated
```

### 测试 8：Phase 1/2 功能回归
```bash
# 会话 CRUD 正常
curl http://localhost:8002/api/sessions
# 文件 API 正常
curl "http://localhost:8002/api/files/tree"
# 路径安全正常
curl "http://localhost:8002/api/files?path=../../etc/passwd"
# 预期：403
```

---

## 验收标准（对齐 phase3-index §12）

| # | 验收项 | 验证方式 |
|---|--------|---------|
| 1 | Control Plane 真的参与了行为约束 | trace.control_context 非空，AGENTS.md 出现在 context_read |
| 2 | assets → memory 沉淀链成立 | memory_decision 字段清楚记录写了什么或为什么 skip |
| 3 | write-or-skip 清楚 | trace.memory_decision.action 为 `write` 或 `skip`，有 reason |
| 4 | trace 能回放 | GET /api/traces 返回完整 trace，含 context_read / asset_refs / memory_decision |

---

## Phase 3 不做的事（明确边界）

- subagent / 多 agent（后续 Phase）
- RAG / GraphRAG（Phase 5）
- tools 执行框架（Phase 4）
- 真上传链路闭环（Phase 5）
- 多 workspace 激活（Phase 6）
- 前端大改（Phase 6，但本次附带一个可测试前端）
- 自动 skill mining
- LLM 驱动的 memory 写入决策（本阶段 memory_decision 由规则判断，后续可接入 LLM）
