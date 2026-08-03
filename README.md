<div align="center">

# Experimental-Research-OpenClaw

**把 180 天实验周期跑成可追溯、可验证、可回放的 AI 工作台**

一个面向实验学科（材料/化学/环境/生物）的透明 AI Agent 系统，<br/>
用文件系统替代黑盒向量库，让每一次对话、每一条建议都有据可查。

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.x-green.svg)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Why — 需求洞察

生化环材科研存在"执行重"与"信息散"的双重困境：

- 一方面，实验体系复杂、长链路且试错成本高，极度消耗研究者的物理执行力
- 另一方面，跨周期迭代产生的数据碎片化散落于笔记、仪器与临时文件中

这种割裂导致研究者极易在长周期推进中坠入细节海洋，丧失全局视野，难以维持围绕核心研究主线的多线程闭环任务推进。

基于这一真实场景痛点，本项目结合 OpenClaw 记忆系统设计与本地 Markdown 文件记忆管理系统，提出 **"用 AI 串联并沉淀科研任务流"**：系统可双向关联实验、文献与阶段成果，将零散研究过程转化为可持续推进的科研闭环。

| 痛点 | 表现 | 本项目的解法 |
|------|------|-------------|
| **记忆黑盒** | 向量数据库不透明，无法审计 Agent "记住"了什么 | File-first Memory — 三层 Markdown 文件系统，Obsidian/VSCode 可直接查看 |
| **证据断链** | AI 建议无法追溯到原始实验数据或文献 | Context Trace — 每回合落盘读/写/缺口/产物，支持前端回放 |
| **上下文失控** | 长周期项目（180 天）的上下文管理混乱 | Context Orchestrator — 显式文件选择策略，按 Identity → Timeline → Atom Notes 分层注入 |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│  ┌──────────────┬────────────────────────┬───────────────────┐  │
│  │  Left Panel  │     Chat Panel         │   Right Panel     │  │
│  │  L1: Identity│  SSE Streaming Chat    │   L3: Atom Notes  │  │
│  │  L2: Timeline│  ThoughtChain + Trace  │   Concepts/Tasks/ │  │
│  │              │                        │   Packs           │  │
│  └──────────────┴────────────────────────┴───────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ SSE (token/tool_start/tool_end/done)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI + LangChain)                │
│                                                                 │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │   API Layer  │  │   Agent Engine   │  │   Core Tools (6)  │  │
│  │  chat (SSE)  │  │  create_agent()  │  │  terminal         │  │
│  │  sessions    │→ │  LangGraph       │→ │  python_repl      │  │
│  │  files/tree  │  │  runtime         │  │  fetch_url        │  │
│  │  assets      │  │                  │  │  read_file        │  │
│  │  traces      │  │                  │  │  search_knowledge │  │
│  │  agents      │  │                  │  │  web_search       │  │
│  └─────────────┘  └──────────────────┘  └───────────────────┘  │
│                            │                                    │
│           ┌────────────────┼────────────────┐                   │
│           ▼                ▼                ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐        │
│  │   Context    │ │   Prompt     │ │   Trace          │        │
│  │ Orchestrator │ │   Builder    │ │   Writer         │        │
│  │ (选文件+预算) │ │ (两条消息拼接)│ │ (审计日志落盘)    │        │
│  └──────────────┘ └──────────────┘ └──────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Workspace (.openclaw/workspace-{agent_id}/)        │
│                                                                 │
│  Layer 1: Identity        Layer 2: Timeline     Layer 3: Atoms  │
│  ├── user.md              ├── 180d_index.md     ├── CONCEPT_*   │
│  ├── project.md           ├── phases/P01-P05    ├── TASK_*      │
│  ├── lab_context.md       ├── weeks/            └── PACK_*      │
│  └── context_budget.md    ├── days/                             │
│                           └── stage_reports/                    │
│                                                                 │
│  + assets/ (uploads/data/figures/ppt_pack)                      │
│  + context_trace/ (session JSON with audit metadata)            │
│  + skills/ (Markdown instruction plugins)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Core Features

### 1. 三层 Markdown 文件记忆系统

基于高频科研场景设计，用文件系统替代黑盒向量库：

| 层级 | 定位 | 内容 |
|------|------|------|
| Layer 1: Identity | 长期稳定的基础设施 | 实验室约束 (`lab_context.md`)、用户偏好 (`user.md`)、项目北极星与判据 (`project.md`) |
| Layer 2: Timeline | 阶段推进与执行记录 | 180 天总览 → 阶段计划 (P01-P05) → 周报 → 每日实验记录，自动汇总阶段汇报 |
| Layer 3: Atom Notes | 高频科研场景的原子资产 | **Concept** — 文献调研形成研究假设；**Task** — 实验设计与执行的可持续推进单元；**Pack** — 组会汇报/论文写作的证据链交付物 |

三层记忆围绕"读文献 → 做实验 → 写汇报"的科研闭环设计：Concept 沉淀假设，Task 推进验证，Pack 组织交付。

### 2. 面向研究主线的上下文可视化 Workspace

研究者通过自然语言交互和上传多来源、非结构化的原始科研材料，Workspace 即可按需调度生成实验建议、证据链摘要或汇报结构，并同步更新对应的 Concept / Task / Pack 记忆层文件。

- **Context Orchestrator** — 每轮对话显式选择注入哪些文件，按 stable → recent → relevant 排序，预算可控
- **Workspace 隔离** — 多 Agent 多工作区，每个 Agent 拥有独立的记忆空间和上下文
- **Skills as Plugins** — 技能是 Markdown 说明书而非硬编码函数，拖入 `skills/` 目录即生效
- **SSE 流式对话** — token / tool_start / tool_end / new_response / done 实时推送
- **6 个内置工具** — terminal、python_repl、fetch_url、read_file、search_knowledge_base、web_search

### 3. 面向交付结果可信度的溯源机制

- **双向关联**：通过代码强约束实现原始文件/学术搜索结果与 AI 生成结果的双向关联
- **Trace 回放**：Workspace 内可视化的 Agent 工作日志、tools/skills 调用轨迹，每回合记录 `context_read[] / context_write[] / missing[] / artifacts[]`
- **事实/推断分区**：AI 输出中事实、推断、观点的分区表达与置信度提示，帮助用户快速判断哪些内容可直接使用、哪些仍需补充证据

## Tech Stack

| 层级 | 技术 | 说明 |
|------|------|------|
| Agent 引擎 | LangChain 1.x `create_agent` + LangGraph | 现代 Agent 构建方式，严禁旧版 AgentExecutor |
| 后端框架 | FastAPI + Uvicorn | 异步 HTTP + SSE 流式推送 |
| 数据验证 | Pydantic v2 | 请求/响应模型 |
| LLM 接入 | OpenAI-compatible API | 支持 DeepSeek / OpenRouter / Claude 等 |
| RAG（可选） | LlamaIndex Core | Hybrid Search (BM25 + Vector)，仅作知识库外挂 |
| Embedding | BAAI/bge-m3 | 中文优化 |
| Token 计数 | tiktoken cl100k_base | 精确统计 |
| 前端 | React + Vite + TypeScript | 三栏 IDE 风格布局 |
| 存储 | 本地文件系统 | Markdown + JSON + assets，零外部数据库依赖 |

## Quick Start

```bash
# 1. 克隆项目
git clone <repo-url>
cd ResearchAgentPrivateWorkspace

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env，填入 LLM API Key：
#   OPENAI_API_KEY=your-key
#   OPENAI_BASE_URL=https://api.your-provider.com/v1
#   OPENAI_MODEL=your-model

# 3. 启动后端 (端口 8002)
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002 --reload

# 4. 启动前端 (端口 3000)
cd ../frontend
pnpm install
pnpm dev
```

> 最小可用：只需配置 `OPENAI_API_KEY` 即可运行。`BRAVE_API_KEY`（Web 搜索）和 Embedding 配置为可选。

## Project Structure

```
ResearchAgentPrivateWorkspace/
├── backend/
│   ├── app.py                      # FastAPI 入口，初始化 WorkspaceRuntimeRegistry
│   ├── config.py                   # 全局配置
│   ├── requirements.txt
│   ├── api/                        # API 路由层
│   │   ├── chat.py                 #   POST /api/chat (SSE 流式对话)
│   │   ├── sessions.py             #   会话 CRUD + 标题生成
│   │   ├── files.py                #   文件读写 + 目录树 + 预览
│   │   ├── assets.py               #   实验资产上传
│   │   └── traces.py               #   Trace 回放接口
│   ├── graph/                      # Agent 核心逻辑
│   │   ├── agent.py                #   AgentManager — create_agent + 流式调用
│   │   ├── context_orchestrator.py #   文件选择 + 预算管理
│   │   ├── prompt_builder.py       #   OpenClaw 风格两条消息拼接
│   │   ├── session_manager.py      #   会话持久化
│   │   └── trace_writer.py         #   审计日志落盘
│   ├── runtime/                    # Workspace 运行时
│   │   └── workspace_registry.py   #   多工作区隔离管理
│   ├── tools/                      # 6 个核心工具
│   ├── skills/                     # Skills 插件目录 (所有 Agent 共享)
│   └── workspace-templates/        # 新 Workspace 初始化模板
│       ├── memory/                 #   三层记忆骨架
│       ├── assets/                 #   实验资产目录
│       └── context_trace/          #   Trace 模板
├── frontend/                       # React + Vite 前端
│   └── src/
│       ├── app/                    #   三栏布局入口
│       └── components/             #   MemoryPanel / ChatPanel / AtomPanel
└── docs/                           # 项目文档
    ├── 架构/                       #   PRD v0.2 + TAD v0.2
    ├── 阶段/                       #   Phase 1-6 计划/日志/架构 HTML
    ├── 启动协议/                   #   Bootstrap Protocol 设计
    ├── 分析/                       #   安全分析 + Trace 分析
    └── 总结/                       #   项目总结 + 面试题库
```

## API Endpoints

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | SSE 流式对话（核心） |
| `/api/sessions` | GET/POST | 会话列表 / 创建 |
| `/api/sessions/{id}` | PUT/DELETE | 重命名 / 删除 |
| `/api/sessions/{id}/history` | GET | 对话历史（含 tool_calls） |
| `/api/files` | GET/POST | 文件读取 / 保存 |
| `/api/files/tree` | GET | 目录树（面板渲染用） |
| `/api/files/preview` | GET | 文件预览 |
| `/api/assets/upload` | POST | 实验资产上传（multipart） |
| `/api/traces` | GET | Trace 列表与回放 |
| `/api/agents` | GET/POST | Agent 列表 / 创建 |
| `/api/skills` | GET | 技能列表 |

## Design Decisions

| 决策 | 理由 |
|------|------|
| `create_agent()` 而非 AgentExecutor | LangChain v1.0 现代范式，底层 LangGraph runtime，原生支持流式 |
| 每次请求重建 Agent | workspace/skills 文件可随时编辑，重建确保即时生效 |
| File-first 三层记忆 | 研究过程可追溯，可用 Obsidian/VSCode 直接审计，拒绝黑盒 |
| Context Orchestrator 显式选文件 | "选哪些文件进上下文"变成可测试、可回放的确定性逻辑 |
| Session 与 Trace 共用一个 JSON | 避免两份文件的冗余与同步问题 |
| Skills 是 Markdown 而非 Python | 降低扩展门槛，用户写说明书即可教会 Agent 新技能 |
| RAG 仅作知识库外挂 | 记忆源必须在文件系统中，向量库只用于 knowledge/ 检索 |

## Evaluation — 评测体系

### 业务洞察与基建

基于课题组内研究者与 AI 真实工作流，构建 **180 天 / 300 轮生命周期提问数据集**。精准界定三大高频场景（文献-假设、实验-结果、汇报-论文），奠定产品记忆系统与可视化前端的架构基础。

### 评测体系搭建

针对三类高频科研闭环构建专项非结构化原始材料测试集，定义并量化两个北极星指标：

| 北极星指标 | 定义 | 评测方式 |
|-----------|------|---------|
| 科研闭环推进成功率 | Concept → Task → Pack 链路的完整度与准确度 | 专项测试集 + 人工评审 |
| 成果交付可信度 | 输出中事实/推断分区的准确性、证据链完整性 | Trace 回放审计 + 置信度校验 |

### 数据驱动迭代

建立基于数据的产品迭代 SOP：通过剖析 5 类核心 Badcase，借助 AI Coding 工具协作定位问题并优化 Prompt、交互和产品架构，驱动北极星指标优化提升。

## Development Phases

本项目采用分阶段迭代开发，每个 Phase 有独立的计划、日志和架构 HTML：

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 后端基础骨架：SSE chat + 会话 CRUD | ✅ Done |
| Phase 2 | 文件系统 API + Agent CRUD + 路径安全 | ✅ Done |
| Phase 3+4 | Context Orchestrator + PromptBuilder + TraceWriter + 核心工具 + Assets | ✅ Done |
| Phase 5 | Skills 系统：SkillLoader + Bootstrap Protocol + 渐进式披露 | ✅ Done |
| Phase 6 | 前端三栏 UI (React+Vite) + Bootstrap Gate + 技能面板 | 🚧 Next |

> 详细的开发日志和架构图见 [docs/阶段/](docs/阶段/) 目录。

## Documentation

项目文档体系完整，核心文档：

- [PRD v0.2](docs/架构/experimental-research-openclaw-PRD.md) — 产品需求文档，定义三层记忆、Skills 系统、API 规范
- [TAD v0.2](docs/架构/experimental-research-openclaw-TAD.md) — 技术架构文档，详述后端模块职责与数据流
- [Architecture Summary](docs/架构/architecture-summary.md) — 架构总览（目标态 + 实现状态标注）
- [Phase Dev Logs](docs/阶段/) — 每个 Phase 的开发日志与验收记录

## Related Projects

本仓库还包含 Researchloop-v1 — 一个更早期的"可追溯闭环 Demo"原型，将科研卡点转化为证据卡 + 任务卡 + 结果卡的三卡体系。OpenClaw 在此基础上演进为完整的 Workspace 架构。

## License

MIT
