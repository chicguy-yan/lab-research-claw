# Experimental-Research-OpenClaw 架构总结文档

> **版本**: v1.0 | **基于**: PRD v0.2 + TAD v0.2
> **用途**: 开发 Checklist / 团队对齐 / 冲突预警
> **约定**: 中英混合；代码与路径使用英文；说明使用中文。

> **⚠️ 实现状态声明（2026-03-07 更新）**
>
> 本文档描述的是**目标架构（全部 6 个 Phase 完成后的终态）**，而非当前实现状态。
> 当前实际完成的模块仅包含 Phase 1 + Phase 2，具体如下：
>
> | 模块 | 状态 |
> |------|------|
> | `app.py`, `config.py` | ✅ 已实现 (Phase 1) |
> | `api/chat.py`, `api/sessions.py` | ✅ 已实现 (Phase 1) |
> | `graph/agent.py`, `graph/session_manager.py` | ✅ 已实现 (Phase 1) |
> | `api/files.py`, `api/agents.py`, `graph/path_utils.py` | ✅ 已实现 (Phase 2) |
> | `graph/context_orchestrator.py`, `graph/prompt_builder.py`, `graph/trace_writer.py` | ❌ 未实现 (Phase 3) |
> | `graph/knowledge_indexer.py` | ❌ 未实现 (Phase 5) |
> | `tools/*` (6 个核心工具) | ❌ 未实现 (Phase 4) |
> | `api/assets.py`, `api/traces.py`, `api/tokens.py`, `api/config_api.py` | ❌ 未实现 (Phase 3-5) |
> | `frontend/src/*` | ❌ 未实现 (Phase 6) |
>
> Prompt 组件（SOUL.md / IDENTITY.md 等）放在 workspace **根目录**（非 `workspace/` 子目录）。
> 会话文件使用 **envelope schema** `{"messages": [...], "traces": []}`。
>
> 请以各 Phase 的 `docs/phase{N}-dev-log.md` 为实际交付依据。

---

## 目录

1. [Workspace 生命周期状态机](#第-1-章workspace-生命周期状态机)
2. [系统架构总览](#第-2-章系统架构总览)
3. [用户单次对话完整流线](#第-3-章用户单次对话完整流线)
4. [前端行为 → API → 后端功能映射表](#第-4-章前端行为--api--后端功能映射表)
5. [记忆系统与 Prompt 拼接详解](#第-5-章记忆系统与-prompt-拼接详解)
6. [冲突/缺失/风险分析](#第-6-章冲突缺失风险分析)
7. [推荐开发优先级](#第-7-章推荐开发优先级)

---

## 第 1 章：Workspace 生命周期状态机

### 1.1 三态总览

```text
                POST /api/agents                       done event
  ┌──────────┐ ─────────────────→ ┌──────────┐ ─────────────────→ ┌──────────┐
  │  Create  │                    │   Run    │                    │  Evolve  │
  │ (初始化)  │                    │ (对话中)  │ ←──────────────── │ (沉淀中)  │
  └──────────┘                    └──────────┘   返回 Run         └──────────┘
       ↑                                                              │
       └───────────────── 重建 workspace（手动触发）──────────────────┘
```

### 1.2 状态详细定义

| 状态 | 触发条件 | 输入 | 输出（必须落盘） | 允许操作 |
|------|---------|------|-----------------|---------|
| **Create** | 创建 Agent（`POST /api/agents`） | `workspace-templates/` + `skills/` | `backend/.openclaw/workspace-{agent_id}/` 目录骨架（复制模板 + 创建 memory/assets/context_trace 子目录） | → 进入 Run |
| **Run** | `POST /api/chat`（单回合运行） | user message + uploads + history + selected_files | SSE 流式事件（token / tool_start / tool_end / new_response / done）+ `trace_seed` | → 可进入 Evolve |
| **Evolve** | 该回合 `done` 事件触发"沉淀动作" | trace_seed + tool_calls + assistant final text | 写入 trace JSON；提示模型更新 memory docs（days/tasks/packs 等） | → 返回 Run |

### 1.3 Create 的验收标准

当 `workspace-{agent_id}/` 不存在时，初始化必须创建以下骨架（从 `workspace-templates/` 复制）：

```text
backend/.openclaw/workspace-{agent_id}/
├── SOUL.md                  # Prompt 组件直接放在根目录（非 workspace/ 子目录）
├── IDENTITY.md
├── USER.md / AGENTS.md / BOOTSTRAP.md / MEMORY.md / TOOLS.md / README.md
├── memory/
│   ├── identity/            # user.md / project.md / lab_context.md / context_budget.md
│   ├── timeline/            # 180d_index.md + phases/ + weeks/ + days/ + stage_reports/
│   ├── concepts/            # CONCEPT_TEMPLATE.md
│   ├── tasks/               # TASK_TEMPLATE.md
│   └── packs/               # PACK_TEMPLATE.md
├── assets/
│   ├── uploads/
│   ├── data/
│   ├── figures/
│   └── ppt_pack/
└── context_trace/           # README.md + TRACE_TEMPLATE.json
```

> **验收**: 创建 session 后，前端三栏能通过 `GET /api/files/tree` 看到以上完整目录树。

---

## 第 2 章：系统架构总览

### 2.1 后端架构

**技术栈**: FastAPI (port 8002) + LangChain 1.x Agent + LlamaIndex Hybrid Search

```text
Experimental-Research-OpenClaw/backend/
├── app.py                          # FastAPI 入口：读配置 → 初始化工具/模块 → 注册路由
├── config.py                       # 全局配置（config.json 持久化）
├── requirements.txt
├── .env.example
│
├── api/                            # ── API 路由层 ──
│   ├── chat.py                     # POST /api/chat — SSE 流式对话（核心）
│   ├── sessions.py                 # 会话 CRUD + 标题生成
│   ├── files.py                    # 文件读写 + tree + preview + skills 列表
│   ├── assets.py                   # 上传到 assets/
│   ├── traces.py                   # trace 列表与读取
│   ├── tokens.py                   # Token 统计
│   └── config_api.py               # RAG 模式开关
│
├── graph/                          # ── Agent 核心逻辑 ──
│   ├── agent.py                    # AgentManager — 构建 & 流式调用
│   ├── session_manager.py          # SessionManager — JSON 会话持久化
│   ├── context_orchestrator.py     # ContextOrchestrator — 选文件/做预算/生成 trace
│   ├── prompt_builder.py           # PromptBuilder — OpenClaw 风格 system+user 拼接
│   ├── trace_writer.py             # TraceWriter — trace 落盘 + patch 应用记录
│   └── knowledge_indexer.py        # KnowledgeIndexer — knowledge/ 索引（RAG 外挂，可选）
│
├── tools/                          # 6 个核心工具
│   ├── terminal_tool.py            # Shell 命令（ShellTool + 黑名单 + CWD 限制）
│   ├── python_repl_tool.py         # Python REPL（PythonREPLTool）
│   ├── fetch_url_tool.py           # 抓取网页（RequestsGetTool + HTML→Markdown 清洗）
│   ├── read_file_tool.py           # 读文件（ReadFileTool + root_dir 限制）
│   ├── search_knowledge_tool.py    # knowledge/ 检索（LlamaIndex Hybrid）
│   └── web_search_tool.py          # Web 搜索（Brave/Tavily，条件启用）
│
├── workspace-templates/            # Agent workspace 初始化模板（Create 时复制）
├── skills/                         # Skills 目录（所有 agent 共用）
└── .openclaw/                      # 运行时 workspace 数据
    ├── workspace-default/          # 默认 agent 的工作区
    └── workspace-{agent_id}/       # 自定义 agent 的工作区
```

#### graph/ 核心模块职责速查

| 模块 | 文件 | 核心职责 |
|------|------|---------|
| **AgentManager** | `agent.py` | 调用 `create_agent(llm, tools, ...)`（LangGraph runtime）构建 Agent（每次请求重建）；`astream()` 流式执行并 yield SSE 事件 |
| **SessionManager** | `session_manager.py` | 会话 JSON 持久化；`load_session_for_agent()` 合并连续 assistant 消息 |
| **ContextOrchestrator** | `context_orchestrator.py` | 决定本轮注入哪些文件；输出 `selected_files[]` + `budget_report` |
| **PromptBuilder** | `prompt_builder.py` | OpenClaw 风格两条消息（system + user）拼接；注入 Project Context |
| **TraceWriter** | `trace_writer.py` | 每轮 `/api/chat` 完成后落盘 trace JSON（context_read + tool_calls） |
| **KnowledgeIndexer** | `knowledge_indexer.py` | 为 `knowledge/` 目录构建 LlamaIndex 混合检索索引（BM25 + Vector） |

### 2.2 前端架构

**技术栈**: Next.js 14 App Router + Tailwind CSS + Shadcn/UI + Monaco Editor

```text
frontend/src/
├── app/page.tsx                    # 三栏主布局入口
├── components/
│   ├── panels/
│   │   ├── MemoryPanel.tsx         # 左栏：Layer1 (Identity) + Layer2 (Timeline) 文件树
│   │   ├── ChatPanel.tsx           # 中栏：消息列表 + 输入框 + ThoughtChain + 回放入口
│   │   └── AtomPanel.tsx           # 右栏：Layer3 (Concepts / Tasks / Packs) 列表
│   ├── chat/
│   │   ├── ThoughtChain.tsx        # SSE 流式工具调用展示（沿用 mini-openclaw）
│   │   └── RetrievalCard.tsx       # RAG 检索结果展示卡片
│   └── editor/
│       └── MonacoDock.tsx          # Monaco 编辑器（Dock/Drawer 形式）
└── lib/
    └── api.ts                      # API 调用封装
```

#### 三栏布局示意

```text
┌───────────────────────────────────────────────────────────────────────┐
│  Navbar（Project / Session / Agent / RAG Toggle / Token Stats）       │
├─────────────────┬──────────────────────────────┬──────────────────────┤
│  Left Panel     │  Middle Panel                │  Right Panel         │
│  MemoryPanel    │  ChatPanel                   │  AtomPanel           │
│                 │                              │                      │
│  ┌─ Identity ─┐ │  ┌─ Messages ──────────────┐ │  ┌─ Concepts ─────┐ │
│  │ user.md    │ │  │ User: "帮我做R06..."    │ │  │ CONCEPT_001    │ │
│  │ project.md │ │  │ Assistant: (streaming)   │ │  │ CONCEPT_002    │ │
│  │ lab_ctx.md │ │  └────────────────────────┘ │  └────────────────┘ │
│  └────────────┘ │                              │  ┌─ Tasks ────────┐ │
│  ┌─ Timeline ─┐ │  ┌─ ThoughtChain ─────────┐ │  │ TASK_synth_01  │ │
│  │ 180d_index │ │  │ 🔧 terminal: ls data/  │ │  │ TASK_mech_02   │ │
│  │ phases/    │ │  │ ✅ result: [files...]    │ │  └────────────────┘ │
│  │ weeks/     │ │  └────────────────────────┘ │  ┌─ Packs ────────┐ │
│  │ days/      │ │                              │  │ PACK_R06_ppt   │ │
│  │ reports/   │ │  ┌─ Input ─────────────────┐ │  │ PACK_mech_co4  │ │
│  └────────────┘ │  │ [消息输入] [📎上传] [发送]│ │  └────────────────┘ │
│                 │  └────────────────────────┘ │                      │
├─────────────────┴──────────────────────────────┴──────────────────────┤
│  Monaco Editor Dock（点击文件时弹出，可关闭/拖拽）                     │
└───────────────────────────────────────────────────────────────────────┘
```

#### 状态管理（React Context — AppProvider）

| 状态 | 类型 | 说明 |
|------|------|------|
| `sessionId` | `string` | 当前活跃会话 ID |
| `sessions` | `Session[]` | 会话列表 |
| `messages` | `Message[]` | 当前会话消息（含 segments） |
| `streaming` | `boolean` | 是否正在流式接收 |
| `memoryTree` | `TreeNode` | 左栏目录树数据 |
| `atomIndex` | `AtomItem[]` | 右栏 Concept/Task/Pack 列表 |
| `activeFilePath` | `string \| null` | Monaco 编辑器当前打开文件 |
| `ragMode` | `boolean` | RAG 模式开关 |
| `tokenStats` | `TokenInfo` | Token 统计信息 |
| `lastTurnTrace` | `Trace \| null` | 最近一轮 trace（回放用） |

### 2.3 三层记忆系统

```text
backend/.openclaw/workspace-{agent_id}/memory/
│
├── identity/                    ← Layer1: 身份与规则（长期稳定）
│   ├── user.md                  # 用户偏好与输出约束
│   ├── project.md               # 主线假设、指标、术语表、判据（最关键）
│   ├── lab_context.md           # 实验室现实约束：仪器/表征/命名/污染风险
│   └── context_budget.md        # 单回合上下文预算与截断策略
│
├── timeline/                    ← Layer2: 时间轴（阶段→周→日）
│   ├── 180d_index.md            # 180天总览：阶段划分、里程碑、风险雷达
│   ├── phases/                  # 阶段文档
│   │   ├── P01_bootstrap.md
│   │   ├── P02_material_screening.md
│   │   ├── P03_parameter_optimization.md
│   │   ├── P04_mechanism_closure.md
│   │   └── P05_writing_submission.md
│   ├── weeks/                   # 周报
│   │   └── 2025-W39.md ...
│   ├── days/                    # 日志
│   │   └── 2025-12-31.md ...
│   └── stage_reports/           # 阶段汇报
│       └── R09_20260119.md ...
│
├── concepts/                    ← Layer3: Atom Notes — Concept
│   └── CONCEPT_*.md             # 一个研究主题容器（你在验证什么）
│
├── tasks/                       ← Layer3: Atom Notes — Task
│   └── TASK_*.md                # 一次验证任务（= Claim + Protocol + Run）
│
└── packs/                       ← Layer3: Atom Notes — Pack
    └── PACK_*.md                # 交付包（PPT/机理证据链/论文写作/图集）
```

**Layer 语义总结：**

| Layer | 目录 | 语义 | 可变性 | 典型内容 |
|-------|------|------|--------|---------|
| **L1** | `identity/` | 身份与规则 | 低频变更（长期稳定） | 项目北极星、用户偏好、实验室约束、预算策略 |
| **L2** | `timeline/` | 时间轴推进 | 中频更新（阶段→周→日） | 180天总览、阶段计划、周报、日志、阶段汇报 |
| **L3** | `concepts/` `tasks/` `packs/` | 原子资产 | 高频创建/更新 | 研究主题、验证任务、交付包 |

---

## 第 3 章：用户单次对话完整流线

### 3.1 端到端链路图（精确到模块级）

```text
[前端 ChatPanel]
  ├─ 用户输入消息 + 可选上传文件（POST /api/assets/upload → 获得 saved_path）
  ├─ streamChat(message, session_id) ──→ POST /api/chat
  │
[后端 chat.py — 请求入口]
  │
  ├─ Step 1. SessionManager.load_session_for_agent(session_id)
  │          → 获取历史消息数组（合并连续 assistant 消息）
  │
  ├─ Step 2. ContextOrchestrator.select_files(message, session_id)
  │          → selected_files[] + budget_report
  │          → 意图识别：阶段汇报 / 机理审计 / 作图拟合 / 通用
  │          → 按默认排序：workspace → skills → L1 → L2 → L3 → uploads
  │
  ├─ Step 3. PromptBuilder.build(selected_files, user_message, metadata)
  │          → system_msg（身份行 + Tooling + Workspace + Context + Project Context 全文）
  │          → user_msg（可选 untrusted 块 + 用户正文）
  │
  ├─ Step 4. [若 RAG 开启] KnowledgeIndexer.retrieve(query)
  │          → SSE event: retrieval {query, results}
  │          → 检索结果追加到 history 尾部（不持久化）
  │
  ├─ Step 5. AgentManager._build_agent()
  │          → 构建 LangChain Agent（每次请求重建，确保读取最新 workspace/skills 配置）
  │
  ├─ Step 6. agent.astream(messages)
  │          → 流式执行，依次 yield SSE 事件：
  │          │
  │          ├─ SSE: token        → 前端 ThoughtChain 追加文字
  │          ├─ SSE: tool_start   → 前端显示工具调用中 {tool, input}
  │          ├─ SSE: tool_end     → 前端显示工具结果 {tool, output}
  │          ├─ SSE: new_response → 前端创建新 assistant 气泡 {}
  │          └─ (Agent 流结束，不产出 done)
  │
  ├─ Step 7. SessionManager.save_message(session_id, user + assistant segments)
  │          → 追加消息到会话 JSON 文件（envelope schema: {"messages": [...], "traces": []}）
  │
  ├─ Step 8. TraceWriter.write(trace_seed + tool_calls + context_read)
  │          → 落盘 trace JSON 到 context_trace/{session_id}.json
  │
  ├─ Step 9. api/chat.py 统一发送 SSE: done {session_id, trace_path}
  │          → done 事件由 chat.py 在 Agent 流结束 + 消息落盘 + trace 写入完成后发送
  │          → 保证前端只收到一个 done，避免状态机冲突
  │
[前端 ChatPanel — done 回调]
  └─ done 收到 trace_path
     → GET /api/traces/{trace_path}
     → 渲染回放卡片（读了什么 / 写了什么 / 缺什么 / 产物路径）
```

### 3.2 SSE 事件序列

```text
普通模式:  token → [tool_start → tool_end → new_response → token]* → done
RAG 模式:  retrieval → token → [tool_start → tool_end → new_response → token]* → done
```

| SSE 事件 | 数据字段 | 前端行为 |
|----------|---------|---------|
| `token` | `{content}` | 追加文字到当前 assistant 气泡 |
| `tool_start` | `{tool, input}` | ThoughtChain 显示"正在调用 {tool}..." |
| `tool_end` | `{tool, output}` | ThoughtChain 显示工具执行结果 |
| `new_response` | `{}` | 创建新的 assistant 消息气泡 |
| `retrieval` | `{query, results}` | RetrievalCard 展示检索结果 |
| `done` | `{session_id, trace_path}` | 结束流式 → 请求 trace → 渲染回放卡片。**注意**：done 只由 `api/chat.py` 发送（Agent 流结束 + 消息落盘 + trace 写入完成后），AgentManager 不产出 done |
| `title` | `{session_id, title}` | 更新会话标题（首次对话自动生成） |
| `error` | `{error}` | 显示错误信息 |

---

## 第 4 章：前端行为 → API → 后端功能映射表

> 以下是完整的 18 项映射，覆盖 PRD/TAD 定义的所有接口。

| # | 用户行为 | 前端组件 | HTTP 方法 & 端点 | 后端文件 | 核心逻辑 |
|---|---------|---------|-----------------|---------|---------|
| 1 | 发送消息/对话 | ChatPanel | `POST /api/chat` | `api/chat.py` → `graph/agent.py` | SSE 流式: SessionManager → Orchestrator → PromptBuilder → Agent → TraceWriter |
| 2 | 查看会话列表 | Navbar | `GET /api/sessions` | `api/sessions.py` | 按 `updated_at` 倒序返回会话列表 |
| 3 | 创建新会话 | Navbar | `POST /api/sessions` | `api/sessions.py` | 新建 session JSON 文件 |
| 4 | 重命名会话 | Navbar | `PUT /api/sessions/{id}` | `api/sessions.py` | 更新 title 字段 |
| 5 | 删除会话 | Navbar | `DELETE /api/sessions/{id}` | `api/sessions.py` | 删除 JSON 文件 |
| 6 | 查看对话历史 | ChatPanel | `GET /api/sessions/{id}/history` | `api/sessions.py` | 读取消息数组（含 tool_calls） |
| 7 | 浏览左/右面板文件树 | MemoryPanel / AtomPanel | `GET /api/files/tree?path=...&max_depth=...` | `api/files.py` | 递归目录扫描，返回树形结构 |
| 8 | 读取文件内容 | Monaco Editor | `GET /api/files?path=...` | `api/files.py` | 读取文件返回 content |
| 9 | 保存文件 | Monaco Editor | `POST /api/files` | `api/files.py` | 写入 `{path, content}` |
| 10 | 预览文件 | MemoryPanel / AtomPanel (hover) | `GET /api/files/preview?path=...&max_chars=...` | `api/files.py` | 截取前 N 字符返回 |
| 11 | 上传实验数据/PDF | ChatPanel 输入框 | `POST /api/assets/upload` | `api/assets.py` | multipart → `assets/uploads/`；返回 `{saved_path, sha256, size}` |
| 12 | 查看 Trace 回放 | ThoughtChain 回放视图 | `GET /api/traces?session_id=...&limit=...` | `api/traces.py` | 读取 trace JSON 列表 |
| 13 | 读取单个 Trace | ThoughtChain 回放视图 | `GET /api/traces/{trace_path}` | `api/traces.py` | 读取指定 trace JSON |
| 14 | 查看技能列表 | 设置面板 | `GET /api/skills` | `api/files.py` | 扫描 `skills/` 目录 + SKILLS_SNAPSHOT |
| 15 | 重扫描技能 | 设置面板 | `POST /api/skills/rescan` | `api/files.py` | 重新扫描 `skills/` 并生成 `SKILLS_SNAPSHOT.md` |
| 16 | 切换 RAG 模式 | Navbar 开关 | `GET/PUT /api/config/rag-mode` | `api/config_api.py` | `config.json` 持久化 |
| 17 | 查看 Agent 列表 | Navbar 下拉 | `GET /api/agents` | `agents`（待建） | 扫描 `.openclaw/` 返回 agent 列表 |
| 18 | 创建新 Agent | Navbar → New Agent | `POST /api/agents` | `agents`（待建） | 复制 `workspace-templates/` → 写 IDENTITY.md |
| 19 | Token 统计 | Navbar 显示 | `GET /api/tokens`（可选） | `api/tokens.py` | tiktoken `cl100k_base` 统计 |

### API 接口速查

```text
# 核心对话
POST   /api/chat                         → SSE 流式（chat.py）

# 会话管理
GET    /api/sessions                     → 会话列表
POST   /api/sessions                     → 创建会话
PUT    /api/sessions/{id}                → 重命名
DELETE /api/sessions/{id}                → 删除
GET    /api/sessions/{id}/history        → 对话历史

# 文件操作
GET    /api/files?path=...               → 读文件
POST   /api/files                        → 保存文件
GET    /api/files/tree?path=...          → 目录树
GET    /api/files/preview?path=...       → 文件预览

# 资产上传
POST   /api/assets/upload                → multipart 上传

# Trace 回放
GET    /api/traces?session_id=...        → trace 列表
GET    /api/traces/{trace_path}          → 单个 trace

# Skills
GET    /api/skills                       → 技能列表
POST   /api/skills/rescan                → 重扫描

# Agent 管理
GET    /api/agents                       → agent 列表
POST   /api/agents                       → 创建 agent

# 配置
GET    /api/config/rag-mode              → 读取 RAG 模式
PUT    /api/config/rag-mode              → 设置 RAG 模式

# Token 统计
GET    /api/tokens                       → token 统计（可选）
```

---

## 第 5 章：记忆系统与 Prompt 拼接详解

### 5.1 Workspace 控制层 vs Memory 数据层

系统中存在两类看起来都像"身份信息"的文件，但语义边界清晰：

| 维度 | **Workspace 控制层 (Control Plane)** | **Layer1: memory/identity (Data Plane)** |
|------|-------------------------------------|----------------------------------------|
| **文件** | `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`（workspace 根目录） | `memory/identity/user.md`, `project.md`, `lab_context.md`, `context_budget.md` |
| **作用** | 定义"Agent 如何工作"的硬协议（工具边界、输出结构、禁止脑补、记忆/技能协议） | 存放长期稳定事实与约束数据（项目北极星与判据、实验室约束、用户偏好） |
| **权威性** | **最高**（与任何记忆冲突时，以 workspace 为准） | 服从 workspace 协议 |
| **可变性** | 低频变更（由开发者/用户手动维护） | 允许缓慢演进（可由模型"提议写入"，由后端落盘） |
| **写权限** | 允许写入 | 允许写入 |

> **冲突规则**：workspace 协议优先级最高；与记忆内容冲突时，以 workspace 为准。

### 5.2 Context Orchestrator 选文件规则

**默认排序（稳定 → 变化 → 本轮相关）：**

```text
 优先级   注入内容                                  来源
───────┼──────────────────────────────────────────┼─────────────
  1    │ AGENTS.md（技能协议 + 记忆协议）            │ workspace 根目录
  2    │ SOUL.md / IDENTITY.md / USER.md            │ workspace 根目录
  3    │ SKILLS_SNAPSHOT.md                         │ skills/
  4    │ memory/identity/user.md                    │ Layer1
  4    │ memory/identity/project.md                 │ Layer1
  4    │ memory/identity/lab_context.md              │ Layer1
  5    │ memory/timeline/180d_index.md + 当前 phase │ Layer2
  5+   │ [条件] days/YYYY-MM-DD.md                  │ Layer2（"最近/今天"问题）
  5+   │ [条件] weeks/ + 上一期 stage_report         │ Layer2（"阶段汇报"问题）
  6    │ 与本轮最相关的 CONCEPT/TASK/PACK            │ Layer3（active/最近更新）
  7    │ 本轮 uploads（文本直接注入；大文件仅路径+摘要）│ uploads
```

**意图识别规则（MVP 阶段简单关键词匹配）：**

| 意图 | 匹配关键词 | 额外注入 |
|------|-----------|---------|
| 阶段汇报 | `第 N 次阶段汇报` / `Rxx_YYYYMMDD` / `ppt_pack` | time_range 内的 weeks/ + days/ + 上一期 stage_report |
| 机理审计 | `Co(IV)` / `ClO₂` / `PMSO` / `DPD` / `淬灭` | mechanism 相关 TASK/PACK |
| 作图/拟合 | `kobs` / `csv` / `拟合` | 数据路径 + user 偏好 |
| 通用 | 其他 | 默认排序注入 |

> **降级策略**：意图识别不确定时，使用默认全量注入顺序。

### 5.3 Prompt Builder 的 system prompt 五块结构

```text
┌─────────────────────────────────────────────────────────────┐
│  Block 1: 身份行（固定常量）                                 │
│  "You are a personal assistant running inside OpenClaw."    │
├─────────────────────────────────────────────────────────────┤
│  Block 2: ## Tooling                                        │
│  列出可用工具摘要（terminal / python_repl / fetch_url /     │
│  read_file / search_knowledge_base / web_search）           │
├─────────────────────────────────────────────────────────────┤
│  Block 3: ## Workspace                                      │
│  工作目录声明 + 规则：                                       │
│  - Project Context 文件是本轮事实来源                        │
│  - 信息不足必须列 Missing checklist，禁止脑补                │
├─────────────────────────────────────────────────────────────┤
│  Block 4: ## Subagent Context（可选）                        │
│  ## Inbound Context (trusted metadata)                      │
│  JSON: 平台/时区/语言/会话类型/当前日期                      │
├─────────────────────────────────────────────────────────────┤
│  Block 5: # Project Context                                 │
│  逐文件注入：                                               │
│  ## <absolute_or_workspace_path>                            │
│  （空行）                                                   │
│  <file_content>                                             │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

**user message 结构：**

```text
┌─────────────────────────────────────────┐
│  [可选] untrusted 块（JSON 代码块）      │
│  用户正文                               │
│  （无正文但有媒体则使用占位符）           │
└─────────────────────────────────────────┘
```

### 5.4 裁剪策略

| 规则 | 说明 |
|------|------|
| 单文件字符上限 | 20,000 字符；超出追加 `...[truncated]` |
| 总上下文预算 | 由 `memory/identity/context_budget.md` 控制（推荐按层分配） |
| 预算分配建议 | workspace 固定 → L1 固定 → L2 近邻 → L3 Top-K → uploads 最小化 |
| 裁剪记录 | 任何被截断/跳过必须记录到 trace（`why` + `policy`） |

### 5.5 Trace 的 `context_read[]` 最小字段

每项至少包含：

```json
{
  "path": "memory/identity/project.md",
  "layer": "memory_identity",
  "why": "项目北极星与判据，每轮必读",
  "status": "full"
}
```

| 字段 | 类型 | 可选值 |
|------|------|-------|
| `path` | `string` | 文件相对路径 |
| `layer` | `string` | `workspace` \| `skills` \| `memory_identity` \| `memory_timeline` \| `memory_atom` \| `uploads` |
| `why` | `string` | 选择原因（短句） |
| `status` | `string` | `full` \| `truncated` \| `skipped` |

> **目的**：前端能"点一下回放"，开发者能快速定位"本轮读了什么、为什么读、有没有被裁掉"。

---

## 第 6 章：冲突/缺失/风险分析

> ⚠️ **以下问题必须在开发前解决或明确决策。**

### 6.1 ~~`create_agent` API 名称错误~~ ✅ 已解决

| 项目 | 详情 |
|------|------|
| **来源** | PRD §一.2 核心技术架构 |
| **原问题** | 怀疑 `from langchain.agents import create_agent` 不存在 |
| **决策** | LangChain v1.0 确实引入了 `create_agent`，底层基于 **LangGraph runtime**。参考：[LangChain & LangGraph 1.0 博客](https://blog.langchain.com/langchain-langgraph-1dot0/) 与 [v1 迁移指南](https://docs.langchain.com/oss/python/migrate/langchain-v1)。 |
| **版本锁定** | `langchain>=1.0,<1.2`。LangChain v1.1.0 曾报告 `create_agent` 从 `__init__.py` 消失（[论坛讨论](https://forum.langchain.com/t/create-agent-no-longer-exists-in-langchain-agents-v1-1-0/2350)），需关注兼容性。 |
| **禁令** | 严禁 `AgentExecutor`；严禁 `langgraph.prebuilt.create_react_agent`（除非临时降级并打 `TODO: migrate to create_agent`） |
| **风险等级** | ~~🔴 阻塞级~~ → ✅ 已解决 |

### 6.2 ~~Session 与 Trace 存储路径歧义~~ ✅ 已解决

| 项目 | 详情 |
|------|------|
| **来源** | PRD §4.3 + §5.2，TAD §session_manager.py + §trace_writer.py |
| **原问题** | Session 历史消息和 Trace 审计日志是同一个文件还是两个文件？ |
| **决策** | **同一个文件**：`context_trace/{session_id}.json`，使用 **envelope schema**：`{"messages": [...], "traces": []}`。`messages` 为 OpenAI messages 数组（SessionManager 读写），`traces` 为审计信息数组（TraceWriter 在 Phase 3 填充 `context_read[]` 等）。两个模块各管各的字段，互不污染。会话元数据（title/created_at/updated_at）存储在独立的 `context_trace/_sessions_index.json`。支持自动迁移旧版纯数组格式。 |
| **风险等级** | ~~🟡 需澄清~~ → ✅ 已解决 |

### 6.3 Context Orchestrator 意图识别规则不完整

| 项目 | 详情 |
|------|------|
| **来源** | PRD §4.4.3 + TAD §Context Orchestrator |
| **问题** | PRD 仅举例了几种关键词模式（阶段汇报/机理审计/作图拟合），未覆盖所有场景。匹配失败时的行为未定义。 |
| **建议** | MVP 阶段使用**简单关键词匹配 + 降级为全量默认注入**。后续迭代可引入 LLM 意图分类。 |
| **风险等级** | 🟢 **低风险** — 有合理降级策略 |

### 6.4 Monaco Editor 的触发位置与交互方式

| 项目 | 详情 |
|------|------|
| **来源** | TAD §前端架构：`Monaco 编辑器以 Dock/Drawer 形式出现（可由左右面板触发）` |
| **问题** | 未说明：覆盖哪一栏？是否可拖拽调整大小？是否支持全屏？打开多个文件时的行为？ |
| **建议** | MVP：底部 Dock 形式（覆盖底部 40% 高度），可折叠/展开，单文件模式（打开新文件替换当前）。 |
| **风险等级** | 🟢 **低风险** — 前端 UI 细节，可迭代调整 |

### 6.5 Skills rescan 时机

| 项目 | 详情 |
|------|------|
| **来源** | PRD §3.2.1：Bootstrap 时自动扫描生成 SKILLS_SNAPSHOT |
| **问题** | 运行时是否需要 watch 文件变化自动 rescan？ |
| **建议** | MVP 只做**手动 rescan**（`POST /api/skills/rescan`）。后续可加 fs.watch。 |
| **风险等级** | 🟢 **低风险** |

### 6.6 Agent 创建时 name 写入 IDENTITY.md 的格式

| 项目 | 详情 |
|------|------|
| **来源** | PRD §5.7：`name 会保存到 .openclaw/workspace-{agent_id}/IDENTITY.md` |
| **问题** | 未明确写入格式。是 YAML frontmatter？纯 Markdown heading？还是自由文本？ |
| **建议** | 使用简单 Markdown 格式：`# {name}` 作为文件第一行，后续内容从模板复制。 |
| **风险等级** | 🟢 **低风险** |

### 6.7 LLM 调用失败的降级策略

| 项目 | 详情 |
|------|------|
| **来源** | PRD/TAD 均未定义 |
| **问题** | API 层未定义 LLM 调用失败时的重试次数、超时时间、降级行为。网络不稳定或 API 限流时如何处理？ |
| **建议** | MVP：重试 2 次（间隔 1s/3s），超时 60s，失败后发送 SSE `error` 事件并保存部分结果。 |
| **风险等级** | 🟡 **中风险** — 影响用户体验 |

### 6.8 Trace 写入与前端读取的竞态条件

| 项目 | 详情 |
|------|------|
| **来源** | TAD §chat.py 流程：done → write trace → 前端 GET trace |
| **问题** | `done` 事件返回 `trace_path` 后前端立即 `GET`，但 trace 是异步写入，可能读到空文件或不完整文件。 |
| **建议** | 方案 A：`done` 事件在 trace 写入**完成后**才发送（同步写入）。<br>方案 B：前端 GET trace 时加 retry（最多 3 次，间隔 200ms）。<br>**推荐方案 A**，trace 数据量小，同步写入延迟可忽略。 |
| **风险等级** | 🟡 **中风险** — 可能导致前端回放功能异常 |

### 6.9 `/api/files` 的路径安全

| 项目 | 详情 |
|------|------|
| **来源** | TAD §files.py：`禁止 .. 路径穿越` |
| **问题** | TAD 提到了路径安全但未给出具体实现规范。需要防止 `../../etc/passwd` 等路径穿越攻击。 |
| **建议** | 实现 `resolve_safe_path(base_dir, user_path)` 工具函数：<br>① `os.path.realpath()` 解析符号链接<br>② 检查解析后路径是否在 `base_dir` 下<br>③ 拒绝包含 `..` 的路径<br>④ 白名单允许的根目录 |
| **风险等级** | 🔴 **高风险** — 安全漏洞 |

### 6.10 6 个核心工具的依赖安装与版本兼容

| 项目 | 详情 |
|------|------|
| **来源** | PRD §二 + TAD §tools/ |
| **问题** | 核心工具依赖分散在多个 LangChain 子包中，版本兼容性需要锁定：<br>- `langchain` (core)<br>- `langchain_community`（ShellTool, RequestsGetTool, ReadFileTool）<br>- `langchain_experimental`（PythonREPLTool）<br>- `langchain_openai`（ChatOpenAI）<br>- `llama_index`（Hybrid Search）<br>- `langchain-tavily-search` 或 Brave API |
| **建议** | 在 `requirements.txt` 中锁定具体版本号，并在 CI 中加版本兼容性测试。 |
| **风险等级** | ~~🟡 中风险~~ → ✅ 已解决（Phase 1 已提供 `requirements.lock` 精确版本锁 + 收窄范围约束） |

### 风险汇总

| 等级 | 编号 | 问题 |
|------|------|------|
| ✅ 已解决 | 6.1 | `create_agent` — LangChain v1.1.1+ `create_agent`（LangGraph runtime），锁定 >=1.1.1 避开 1.1.0 |
| ✅ 已解决 | 6.2 | Session/Trace — 同一文件，envelope schema `{"messages":[], "traces":[]}` |
| ✅ 已解决 | 6.10 | 依赖版本 — `requirements.lock` 精确锁 + `requirements.txt` 收窄范围 |
| 🔴 高风险 | 6.9 | `/api/files` 路径安全 |
| 🟡 中风险 | 6.7 | LLM 调用失败降级 |
| 🟡 中风险 | 6.8 | Trace 写入竞态 |
| 🟢 低风险 | 6.3 | 意图识别不完整（有降级） |
| 🟢 低风险 | 6.4 | Monaco 交互细节 |
| 🟢 低风险 | 6.5 | Skills rescan 时机 |
| 🟢 低风险 | 6.6 | IDENTITY.md 写入格式 |

---

## 第 7 章：推荐开发优先级

### 基于依赖关系的分层开发顺序

```text
Phase 0: 前置决策（开发前必须解决）
  └─ 确认 LangChain Agent API（6.1）
  └─ 确认 Session/Trace 存储方案（6.2）
  └─ 锁定依赖版本（6.10）

Phase 1: 基础骨架（Week 1）
  ├─ backend/config.py + .env + app.py 入口
  ├─ graph/agent.py — AgentManager 基础版（单工具测试）
  ├─ graph/session_manager.py — 会话 CRUD
  ├─ api/chat.py — SSE 流式（最小可用）
  ├─ api/sessions.py — 会话管理 5 个端点（含 history）
  └─ 验证：curl POST /api/chat → SSE token 流

Phase 2: 文件系统 + Workspace（Week 2）
  ├─ api/files.py — 文件读写 + tree + preview + 路径安全（6.9）
  ├─ workspace-templates/ — 完整模板目录
  ├─ api/agents.py — Agent CRUD（POST 触发 workspace 初始化）
  ├─ 前端 MemoryPanel + AtomPanel — 文件树展示
  └─ 验证：POST /api/agents → 目录骨架创建 → GET /api/files/tree 返回完整树

Phase 3: 记忆注入 + Prompt（Week 3）
  ├─ graph/context_orchestrator.py — 选文件逻辑 + 意图识别
  ├─ graph/prompt_builder.py — 五块 system prompt 拼接
  ├─ graph/trace_writer.py — trace 落盘
  ├─ api/traces.py — trace 读取端点
  └─ 验证：POST /api/chat → trace 落盘 → GET /api/traces 读取 context_read[]

Phase 4: 工具集 + Skills（Week 4）
  ├─ tools/ — 6 个核心工具实现
  ├─ skills/ — Skills 扫描 + SKILLS_SNAPSHOT 生成
  ├─ api/files.py — GET /api/skills + POST /api/skills/rescan
  └─ 验证：Agent 能调用 terminal/python_repl → tool_start/tool_end SSE 事件

Phase 5: RAG + 资产上传（Week 5）
  ├─ graph/knowledge_indexer.py — LlamaIndex Hybrid Search
  ├─ api/assets.py — 文件上传
  ├─ api/config_api.py — RAG 模式开关
  ├─ api/tokens.py — Token 统计
  └─ 验证：RAG 模式开 → SSE retrieval 事件 → RetrievalCard 展示

Phase 6: 前端完善 + 集成（Week 6）
  ├─ 前端 ChatPanel — 消息渲染 + 输入 + ThoughtChain
  ├─ 前端 MonacoDock — 文件编辑器
  ├─ 前端 Trace 回放视图
  ├─ Navbar — Agent 切换 / Session 管理 / RAG 开关
  └─ 验证：端到端流程跑通（创建 Agent → 发送消息 → 工具调用 → Trace 回放）
```

### Phase 依赖图

```text
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
                │                       │                       │
                └───────────────────────┴───────────────────────┴──→ Phase 6
```

> **说明**: Phase 6（前端完善）可与 Phase 3-5 并行开发，前端团队可基于 mock API 先行。

---

## 附录 A：关键技术选型速查

| 层级 | 技术 | 版本/说明 |
|------|------|----------|
| 后端框架 | FastAPI + Uvicorn | 异步 HTTP + SSE 流式推送 |
| Agent 引擎 | LangChain 1.x `create_agent` | `from langchain.agents import create_agent`，底层 LangGraph runtime |
| LLM | DeepSeek / OpenAI-compatible | 通过 OpenAI API 格式统一接入 |
| RAG | LlamaIndex Core | Hybrid Search（向量 + BM25） |
| Embedding | BAAI/bge-m3 | 中文优化 |
| Token 计数 | tiktoken cl100k_base | 精确 token 统计 |
| 前端框架 | Next.js 14 App Router | TypeScript + React 18 |
| UI | Tailwind CSS + Shadcn/UI | IDE 风格三栏 |
| 代码编辑器 | Monaco Editor | 在线编辑 Memory/Skill/Workspace 文件 |
| 状态管理 | React Context | 单一 AppProvider（不引入 Redux） |
| 存储 | 本地文件系统 | JSON + Markdown + assets/ |

## 附录 B：环境配置模板

```bash
# backend/.env

# 主模型（DeepSeek / OpenAI-compatible）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.xiaomimimo.com/v1
OPENAI_MODEL=mimo-v2-flash

# Embedding（RAG 用，可选）
EMBEDDING_API_KEY=your_embedding_key_here
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3

# Web Search（可选，缺少则不启用 web_search 工具）
BRAVE_API_KEY=your_brave_key_here
```

## 附录 C：文档溯源

| 本文章节 | 对应 PRD 章节 | 对应 TAD 章节 |
|---------|-------------|-------------|
| 第 1 章 状态机 | PRD §4.8.2 状态机定义 | TAD §后端架构详解 |
| 第 2 章 系统架构 | PRD §一.2 核心技术架构 | TAD §技术选型 + §项目结构 |
| 第 3 章 对话流线 | PRD §4.4 Prompt 拼接 + §5.1 核心对话接口 | TAD §chat.py + §核心数据流 |
| 第 4 章 API 映射 | PRD §五 后端 API 接口规范 | TAD §API 层 + §API 接口速查 |
| 第 5 章 记忆与 Prompt | PRD §4.2 三层记忆 + §4.4 Prompt 拼接 | TAD §Context Orchestrator + §Prompt Builder |
| 第 6 章 风险分析 | 综合 PRD/TAD 交叉对比 | 综合 PRD/TAD 交叉对比 |
| 第 7 章 开发优先级 | 基于依赖关系推导 | 基于依赖关系推导 |
