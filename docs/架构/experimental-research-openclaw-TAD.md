# Experimental-Research-OpenClaw 技术架构文档 (TAD) — v0.2

> 本 TAD 以 mini-openclaw 的实现为底座（FastAPI + SSE + LangChain create_agent + Next.js + Monaco），
> 按 PRD v0.2 改造为“实验学科研究版本”：三层记忆（Layer1/2/3）+ Context Orchestrator + Trace 回放 + 三栏前端。

---

## 目录

* 技术选型
* 项目结构（实验版）
* 环境配置
* 启动方式
* 后端架构详解
  * 应用入口 app.py
  * Agent 引擎 graph/
  * Context Orchestrator（新增）
  * Prompt Builder（OpenClaw 风格）
  * Session Manager（会话持久化）
  * Trace Writer（新增）
  * Knowledge Indexer（RAG，知识库外挂）
* 六大核心工具 tools/
  * API 层 api/
* 前端架构概览（三栏：L1/L2 | Chat | L3）
* 核心数据流（SSE 不变）
* 关键设计决策
* API 接口速查

---

## 技术选型（保持 mini-openclaw 选型不变）

层级 | 技术 | 说明
---|---|---
后端框架 | FastAPI + Uvicorn | 异步 HTTP + SSE 流式推送
Agent 引擎 | LangChain 1.x `create_agent` | `from langchain.agents import create_agent`，底层基于 LangGraph runtime；严禁 AgentExecutor 和 `langgraph.prebuilt.create_react_agent`
LLM | DeepSeek / OpenAI-compatible | 通过 OpenAI API 格式统一接入
RAG | LlamaIndex Core | Hybrid Search（向量 + BM25），用于 knowledge/ 知识库外挂
Embedding | BAAI/bge-m3 | 固定好embedding的中文路径
Token 计数 | tiktoken cl100k_base | 精确 token 统计
前端框架 | Next.js 14 App Router | TypeScript + React 18
UI | Tailwind CSS + Shadcn/UI | IDE 风格三栏 + 可拖拽分隔条
代码编辑器 | Monaco Editor | 在线编辑 Memory/Skill/Workspace 文件
状态管理 | React Context | 单一 AppProvider（不引入 Redux）
存储 | 本地文件系统 | JSON + Markdown + assets/

---

## 项目结构（实验版）

```text
Experimental-Research-OpenClaw/
├── backend/
│   ├── app.py                         # FastAPI 入口
│   ├── config.py                      # 全局配置（config.json 持久化）
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── api/                           # API 路由层
│   │   ├── chat.py                    # POST /api/chat — SSE 流式对话（不变）
│   │   ├── sessions.py                # 会话 CRUD + 标题生成
│   │   ├── files.py                   # 文件读写 + tree + preview + skills list
│   │   ├── assets.py                  # (新增) 上传到 assets/
│   │   ├── traces.py                  # (新增) trace 列表与读取
│   │   ├── tokens.py                  # Token 统计
│   │   └── config_api.py              # RAG 模式开关
│   │
│   ├── graph/                         # Agent 核心逻辑（LangChain create_agent）
│   │   ├── agent.py                   # AgentManager — 构建 & 流式调用
│   │   ├── session_manager.py         # SessionManager — JSON 会话持久化
│   │   ├── context_orchestrator.py    # (新增) 选文件/做预算/生成 trace
│   │   ├── prompt_builder.py          # (改造) OpenClaw 风格 system+user 拼接
│   │   ├── trace_writer.py            # (新增) trace 落盘 + patch 应用记录
│   │   └── knowledge_indexer.py       # (可选) knowledge/ 索引（RAG 外挂）
│   │
│   ├── tools/                         # 6 个核心工具（terminal/python/fetch/read_file/search_knowledge/web_search）
│   ├── workspace-templates/                     # System Prompt 组件（可编辑）
│   │   ├── SOUL.md
│   │   ├── IDENTITY.md
│   │   ├── USER.md
│   │   ├── AGENTS.md
│   │   ├── BOOTSTRAP.md
│   │   ├── MEMORY.md
│   │   ├── TOOLS.md
│   │   ├── README.md
│   │   ├── assets/
│   │   │   ├── data/README.md
│   │   │   ├── figures/README.md
│   │   │   └── ppt_pack/README.md
│   │   ├── context_trace/
│   │   │   ├── README.md
│   │   │   └── TRACE_TEMPLATE.json
│   │   └── memory/
│   │       ├── identity/
│   │       │   ├── context_budget.md
│   │       │   ├── lab_context.md
│   │       │   ├── project.md
│   │       │   └── user.md
│   │       ├── concepts/
│   │       │   └── CONCEPT_TEMPLATE.md
│   │       ├── packs/
│   │       │   └── PACK_TEMPLATE.md
│   │       ├── tasks/
│   │       │   └── TASK_TEMPLATE.md
│   │       └── timeline/
│   │           ├── 180d_index.md
│   │           ├── days/_DAY_TEMPLATE.md
│   │           ├── weeks/_WEEK_TEMPLATE.md
│   │           ├── stage_reports/_STAGE_REPORT_TEMPLATE.md
│   │           └── phases/
│   │               ├── P01_bootstrap.md
│   │               ├── P02_material_screening.md
│   │               ├── P03_parameter_optimization.md
│   │               ├── P04_mechanism_closure.md
│   │               └── P05_writing_submission.md
│   ├── skills/                        # Skills（每个技能一个目录），所有技能均在此管理，所有agent共用
│   │   └── stage_report_ppt/SKILL.md
│   └── .openclaw/
│       ├── workspace-default/                 # 默认的工作区，从workspace-templates初始化
│       └── workspace-{agent_id}/      # 定义了名字的agent的工作区，但是也是从workspace-templates初始化
│
└── frontend/
    └── src/
        ├── app/page.tsx               # 三栏：Layer1/2 | Chat | Layer3
        ├── components/
        │   ├── panels/
        │   │   ├── MemoryPanel.tsx
        │   │   ├── ChatPanel.tsx
        │   │   └── AtomPanel.tsx
        │   ├── chat/
        │   │   ├── ThoughtChain.tsx
        │   │   └── RetrievalCard.tsx
        │   └── editor/MonacoDock.tsx
        └── lib/api.ts
```

---

## 环境配置

### DeepSeek / OpenAI-compatible（主模型）

在 `backend/.env` 配置（示例）：

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.xiaomimimo.com/v1     
OPENAI_MODEL=mimo-v2-flash                   
```

### OpenAI Embedding（RAG 用）

```bash
EMBEDDING_API_KEY=...
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3
```

> 如不启用 RAG（仅使用 File-first 记忆 + 规则选文件），Embedding 可不配。

---

## 启动方式

### 后端（端口 8002）

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

### 前端（端口 3000）

```bash
cd frontend
pnpm install
pnpm dev
```

---

## 后端架构详解

### 应用入口 app.py

职责：

1) 读取配置（config.json / .env）
2) 初始化工具列表（tools.get_all_tools）
   - 条件启用 web_search：仅当检测到 `BRAVE_API_KEY`（本地 Brave API 配置）时注册该工具；否则跳过以保证最小 MVP
3) 初始化 AgentManager、SessionManager、KnowledgeIndexer（可选）
4) 注册 API 路由（chat/sessions/files/assets/traces/...）

---

### Agent 引擎 graph/

#### agent.py — AgentManager（流式）

> 使用 `from langchain.agents import create_agent`（LangGraph runtime）。严禁 `AgentExecutor` 和 `langgraph.prebuilt.create_react_agent`。

核心方法 | 职责
---|---
initialize(base_dir) | 创建 LLM、加载工具列表、初始化 Orchestrator/SessionManager
_build_agent() | **每次请求重建**，调用 `create_agent(llm, tools, ...)` 确保读取最新 workspace/skills 配置
astream(message, history, injected_context) | 核心流式方法：将 prompt 与 history 送入 create_agent，并依次 yield SSE 事件

流式事件序列（保持 mini-openclaw 不变）：

```text
[RAG 模式] retrieval → token → tool_start → tool_end → new_response → token → done
[普通模式]            token → tool_start → tool_end → new_response → token → done
```

> 多段响应：工具调用后 Agent 重新生成文本时 emit `new_response`，前端据此创建新助手气泡。

---

#### session_manager.py — SessionManager（会话持久化）
会话持久化主要是为了展示和debug使用，方便查看之前的开发
存储路径：`.openclaw/workspace-{agent_id}/context_trace/{session_id}.json`

> **澄清**：Session 历史消息与 Trace 审计日志共用此文件（OpenAI messages 数组格式）。SessionManager 负责读写对话消息，TraceWriter 负责在每轮 done 后追加 `context_read[]` 等审计元信息。不拆分两个文件。

核心方法 | 说明
---|---
load_session(id) | 返回原始消息数组
load_session_for_agent(id) | 合并连续 assistant 消息；注入 compressed_context（虚拟 assistant 摘要消息）
save_message(id, role, content, tool_calls) | 追加消息到会话文件

> 说明：会话用于“对话上下文”，不替代三层记忆（memory/）。这个核心是给人看的，方便显示在前端

---

### Context Orchestrator（新增）— context_orchestrator.py

> 这是实验版的关键模块：**决定本轮要注入哪些文件**，并为 Trace 生成结构化的 `context_read plan`。

输入：

- user message（文本 + uploads 路径）
- session_id（可选：用于取最近对话摘要）
- ui_hints（可选：today / active_concepts / active_tasks）

输出：

- `selected_files[]`：按最终注入顺序排列的文件列表（含 why）
- `budget_report`：哪些被截断、哪些被跳过、原因

最小规则（与 PRD 对齐）：

- 默认顺序：workspace → skills_snapshot → Layer1 → Layer2 → Layer3 → uploads
- “阶段汇报”意图识别：匹配 `第 N 次阶段汇报` / `Rxx_YYYYMMDD` / `ppt_pack`
- “机理审计”意图识别：匹配 `Co(IV)` / `ClO₂` / `PMSO` / `DPD` / `淬灭`
- “作图/拟合”意图识别：匹配 `kobs` / `csv` / `拟合`

---

### Prompt Builder（改造）— prompt_builder.py

> 从“拼接 6 个文件”升级为 **OpenClaw 风格两条消息（system + user）**，并在 system 末尾注入 Project Context 文件全文。

#### system prompt 结构

块顺序（块与块之间一个空行）：

1) 身份行：`You are a personal assistant running inside OpenClaw.`
2) `## Tooling`：工具摘要（从工具注册表生成）
3) `## Workspace`：工作目录、规则（Project Context 是事实来源；缺信息就列 checklist；禁止脑补）
4) `## Subagent Context`（含 `## Inbound Context (trusted metadata)` JSON）
5) `# Project Context`：逐文件注入
   - `## <path>`
   - 空行
   - `<file_content>`

#### user message 结构

1) 可选 untrusted 块（JSON 代码块，标注为 untrusted）
2) 用户正文（无正文但有媒体则使用占位符）

#### 裁剪策略

- 单文件上限 20,000 字符；超出追加 `...[truncated]`
- 总预算来自 `memory/identity/context_budget.md`（若存在）
- 裁剪结果写入 Orchestrator 的 `budget_report` 并进入 trace

---

### Trace Writer— trace_writer.py

职责：

1) 在每次 /api/chat 完成后，将本轮 `context_read[]`、tool_calls 等审计信息追加到 `./openclaw/workspace-{agent_id}/context_trace/{session_id}.json`（与 SessionManager 共用同一文件）
2) 汇总 tool_calls（来自 AgentManager 的流式事件记录）

> 建议实现“安全模式”：默认只落盘到 memory/ 与 assets/；禁止写入 backend 代码目录。

---

### Knowledge Indexer（可选）— knowledge_indexer.py（RAG 外挂）

目标：为 `backend/knowledge/` 构建混合检索索引（不是记忆源）。

方法 | 说明
---|---
rebuild_index() | 扫描 knowledge/ → 分块 → 建索引 → 持久化到 storage/knowledge_index/
retrieve(query, top_k=3) | 返回 [{text, score, source_path}]
maybe_rebuild() | MD5/mtime 检测变更，必要时重建

当开启 RAG 模式：

- 在调用 Agent 前执行 `retrieve(query)`
- 通过 SSE 发送 `retrieval` 事件（前端用 RetrievalCard 展示）
- 把检索结果拼成 `"[知识库检索结果]"` 临时上下文追加到 history 尾部（**不持久化**）

---

## 六大核心工具 tools/

工具 | 文件 | 功能 | 安全措施
---|---|---|---
terminal | terminal_tool.py | 执行 Shell 命令 | 黑名单（rm -rf / 等）；CWD 限制；超时；输出截断
python_repl | python_repl_tool.py | 执行 Python | 封装 LangChain PythonREPLTool
fetch_url | fetch_url_tool.py | 抓取网页 | JSON/HTML 识别；HTML→Markdown；超时；截断
read_file | read_file_tool.py | 读文件 | root_dir 限制；白名单；截断
search_knowledge_base | search_knowledge_tool.py | knowledge/ 检索 | 仅访问索引 + 白名单目录
web_search | web_search_tool.py | Web 搜索（Brave API/Tavily 兼容） | 条件启用；结果清洗与去重；请求节流

> 最小 MVP 说明：如果本地未配置 Brave API（缺少 `BRAVE_API_KEY`），则不启用 `web_search` 工具，系统以离线工具集运行以保证最小可用。

---

## API 层 api/

### chat.py — 流式对话（核心）

POST `/api/chat`

Request：

```json
{"message":"...","session_id":"abc123","stream":true}
```

Response：SSE（事件类型不变）

- token `{content}`
- tool_start `{tool,input}`
- tool_end `{tool,output}`
- new_response `{}`
- retrieval `{query,results}`（RAG 模式）
- done `{session_id, trace_path}`
- title `{session_id,title}`
- error `{error}`

内部流程（实验版）：

1) `SessionManager.load_session_for_agent()`
2) `ContextOrchestrator.select_files(...)` 得到 selected_files + trace_seed
3) `PromptBuilder.build(system_files=selected_files, user_message=..., metadata=...)`
4) `AgentManager._build_agent()` + `agent.astream()`
5) SSE 推送 token/tool_start/tool_end/new_response…
6) done：
   - 写会话消息（user + assistant segments）
   - `TraceWriter.write(...)`
   - 首次对话生成 title

---

### sessions.py — 会话管理（保持）


---

### files.py — 文件操作（扩展）

端点 | 方法 | 说明
---|---|---
`/api/files?path=...` | GET | 读取文件
`/api/files` | POST | 保存文件（编辑器用）
`/api/files/tree?path=...&max_depth=...` | GET | 列目录树（左/右面板）
`/api/files/preview?path=...&max_chars=...` | GET | 文件预览
`/api/skills` | GET | 列技能（从 skills/ 扫描 + SKILLS_SNAPSHOT）

路径白名单：

- 根目录白名单：SKILLS_SNAPSHOT.md
- 禁止 `..` 路径穿越

---

### assets.py — 上传（新增）

POST `/api/assets/upload`（multipart/form-data）

返回：

```json
{"saved_path":"assets/uploads/xxx.csv","sha256":"...","size":12345}
```

---

### traces.py — Trace（新增）

- GET `/api/traces?session_id=...&limit=...`
- GET `/api/traces/{trace_path}`

---


tokens：统计会话/system prompt tokens（可选）


config_api：RAG mode 开关（config.json 持久化）

---

## 前端架构概览（三栏：Layer1+Layer2 | Chat | Layer3）

布局：

```text
┌──────────────────────────────────────────────────────────┐
│ Navbar                                                    │
├──────────────┬──────────────────────────┬────────────────┤
│ MemoryPanel  │ ChatPanel                 │ AtomPanel       │
│ Layer1/2     │ 消息 + 输入 + ThoughtChain │ Layer3         │
│ Identity     │ RetrievalCard（可选）      │ Concepts/Tasks/ │
│ Timeline     │ Trace 回放入口             │ Packs          │
└──────────────┴──────────────────────────┴────────────────┘
```

关键点：

- Monaco 编辑器以 Dock/Drawer 形式出现（可由左右面板触发）
- ThoughtChain 组件沿用 mini-openclaw 的 SSE 解析与展示
- 每轮 done 后读取 trace_path，渲染“读/写/缺/产物”回放卡片

状态管理（store.tsx / AppProvider）建议包含：

- sessionId、sessions 列表
- messages（含 segments）
- streaming 状态（current token buffer、thoughtchain）
- memoryTree（左）、atomIndex（右）
- activeFilePath + editor state
- ragMode、tokenStats
- lastTurnTrace（回放）

---

## 核心数据流（SSE 不变）

### 用户发送消息（实验版）

```text
前端                                   后端
 │
 ├─ sendMessage(text, uiHints)
 │   └─ streamChat() ───────────────→ POST /api/chat
 │                                      │
 │                                      ├─ load_session_for_agent()
 │                                      ├─ context_orchestrator.select_files()
 │                                      ├─ prompt_builder.build(system+user)
 │                                      ├─ [RAG] knowledge_indexer.retrieve() → SSE retrieval
 │                                      ├─ create_agent() → agent.astream()
 │  ← SSE token/tool_start/tool_end/new_response/done ──────┤
 │                                      ├─ save session messages
 │                                      └─ write trace
 │
 └─ done 收到 trace_path → GET trace → 渲染回放
```

---

## 关键设计决策

决策 | 理由
---|---
使用 `create_agent()` 而非 AgentExecutor | LangChain v1.0 现代范式，底层 LangGraph runtime，原生流式
每次请求重建 Agent | workspace/skills 可编辑，确保即时生效
File-first 记忆（三层） | 研究过程可追溯，可用 Obsidian/VSCode 直接审计
新增 Context Orchestrator | 让“选哪些文件进上下文”变成显式且可测试的逻辑
Trace 每回合落盘 | 前端可回放，开发者可定位读写与缺口
RAG 只做知识库外挂 | 避免把“记忆源”交给不透明向量库；记忆仍在文件里

---

## API 接口速查（摘要）

- POST `/api/chat`（SSE）
- GET/POST/PUT/DELETE `/api/sessions...`
- GET/POST `/api/files`
- GET `/api/files/tree`，GET `/api/files/preview`
- POST `/api/assets/upload`
- GET `/api/traces`，GET `/api/traces/{trace_path}`
- GET/PUT `/api/config/rag-mode`

---
