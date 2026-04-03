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

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│  ┌──────────────┬────────────────────────┬───────────────────┐  │
│  │  Left Panel  │     Chat Panel         │   Right Panel     │  │
│  │  File Tree   │  SSE Streaming Chat    │   Trace /         │  │
│  │  Workspaces  │  Audit Disclosure      │   Preview /       │  │
│  │  Bootstrap   │                        │   Atom Notes      │  │
│  └──────────────┴────────────────────────┴───────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ SSE (token/tool_start/tool_end/done)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI + LangChain)               │
│                                                                 │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │   API Layer │  │   Agent Engine   │  │   Core Tools (5)  │  │
│  │  chat (SSE) │  │  create_agent()  │  │  terminal         │  │
│  │  sessions   │→ │  LangGraph       │→ │  python_repl      │  │
│  │  files/tree │  │  runtime         │  │  fetch_url        │  │
│  │  assets     │  │                  │  │  read_file        │  │
│  │  workspaces │  │                  │  │  write_file       │  │
│  │  agents     │  │                  │  │                   │  │
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
│              Workspace (backend/.openclaw/workspace-*)          │
│                                                                 │
│  Layer 1: Identity        Layer 2: Timeline     Layer 3: Atoms  │
│  ├── user.md              ├── 180d_index.md     ├── CONCEPT_*   │
│  ├── project.md           ├── phases/           ├── TASK_*      │
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
| Layer 2: Timeline | 阶段推进与执行记录 | 180 天总览 → 阶段计划 → 周报 → 每日实验记录，自动汇总阶段汇报 |
| Layer 3: Atom Notes | 高频科研场景的原子资产 | **Concept** — 文献调研形成研究假设；**Task** — 实验设计与执行的可持续推进单元；**Pack** — 组会汇报/论文写作的证据链交付物 |

三层记忆围绕"读文献 → 做实验 → 写汇报"的科研闭环设计：Concept 沉淀假设，Task 推进验证，Pack 组织交付。

### 2. 面向研究主线的上下文可视化 Workspace

研究者通过自然语言交互和上传多来源、非结构化的原始科研材料，Workspace 即可按需调度生成实验建议、证据链摘要或汇报结构，并同步更新对应的 Concept / Task / Pack 记忆层文件。

- **Context Orchestrator** — 每轮对话显式选择注入哪些文件，按 stable → recent → relevant 排序，预算可控
- **Workspace 隔离** — 多工作区、多会话，每个 workspace 拥有独立的记忆空间和上下文
- **Skills as Plugins** — 技能是 Markdown 说明书而非硬编码函数，拖入 `skills/` 目录即生效
- **SSE 流式对话** — token / tool_start / tool_end / new_response / done 实时推送
- **5 个内置工具** — terminal、python_repl、fetch_url、read_file、write_file

### 3. 面向交付结果可信度的溯源机制

- **双向关联**：通过代码约束把上下文读取、工具调用与最终输出关联到同一轮会话
- **Trace 回放**：Workspace 内可视化 Agent 工作日志、tools/skills 调用轨迹，每回合记录 prompt 与 tool trace
- **事实/推断分区基础设施**：前端提供审计面板与 trace 展示，为后续更细粒度的可信表达留出接口

## Tech Stack

| 层级 | 技术 | 说明 |
|------|------|------|
| Agent 引擎 | LangChain 1.x `create_agent` + LangGraph | 现代 Agent 构建方式，避免旧版 AgentExecutor |
| 后端框架 | FastAPI + Uvicorn | 异步 HTTP + SSE 流式推送 |
| 数据验证 | Pydantic v2 | 请求/响应模型 |
| LLM 接入 | OpenAI-compatible API | 通过 `.env` 配置兼容 OpenAI 风格接口 |
| Token 计数 | tiktoken cl100k_base | 精确统计 |
| 前端 | React + Vite + TypeScript | 三栏 IDE 风格布局 |
| 测试 | unittest + Vitest + Playwright | 覆盖后端单测、前端单测和基础 smoke |
| 存储 | 本地文件系统 | Markdown + JSON + assets，零外部数据库依赖 |

## Quick Start

```bash
# 1. 克隆项目
git clone <repo-url>
cd Experimental-Research-OpenClaw

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env，填入 LLM API Key：
#   OPENAI_API_KEY=your-key
#   OPENAI_BASE_URL=https://api.your-provider.com/v1
#   OPENAI_MODEL=your-model

# 3. 启动后端 (端口 8002)
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002 --reload

# 4. 启动前端 (端口 5173)
cd ../frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

也可以直接在仓库根目录运行：

```bash
bash start_backend.sh
bash start_frontend.sh
```

> 最小可用：只需配置 `OPENAI_API_KEY` 即可运行。

## Project Structure

```text
Experimental-Research-OpenClaw/
├── backend/
│   ├── app.py                      # FastAPI 入口，初始化 WorkspaceRuntimeRegistry
│   ├── config.py                   # 全局配置
│   ├── requirements.txt
│   ├── api/                        # API 路由层
│   │   ├── chat.py                 #   POST /api/chat (SSE 流式对话)
│   │   ├── sessions.py             #   会话 CRUD + 历史记录
│   │   ├── files.py                #   文件读写 + 目录树 + 预览
│   │   ├── assets.py               #   上传 / 下载资产
│   │   ├── workspaces.py           #   Workspace CRUD + Bootstrap
│   │   └── agents.py               #   兼容层接口
│   ├── graph/                      # Agent 核心逻辑
│   │   ├── context_orchestrator.py #   文件选择 + 预算管理
│   │   ├── prompt_builder.py       #   系统提示词拼接
│   │   ├── session_manager.py      #   会话持久化
│   │   ├── skill_loader.py         #   技能快照加载
│   │   └── trace_writer.py         #   审计日志落盘
│   ├── runtime/                    # Workspace 运行时
│   │   ├── bootstrap_runner.py     #   首次引导流程
│   │   └── workspace_registry.py   #   多工作区隔离管理
│   ├── tools/                      # 5 个核心工具
│   ├── skills/                     # Skills 插件目录
│   ├── workspace-templates/        # 新 Workspace 初始化模板
│   └── tests/                      # 后端单元测试
├── frontend/                       # React + Vite 前端
│   ├── src/
│   │   ├── app/                    #   应用入口
│   │   ├── features/               #   chat/files/trace/workspace 视图
│   │   └── shared/                 #   API client、types、utils
│   └── tests/                      # Playwright smoke 测试
├── start_backend.sh
├── start_frontend.sh
├── LICENSE
└── README.md
```

## API Endpoints

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | SSE 流式对话（核心） |
| `/api/sessions` | GET/POST | 会话列表 / 创建 |
| `/api/sessions/{id}` | PUT/DELETE | 重命名 / 删除 |
| `/api/sessions/{id}/history` | GET | 对话历史（含 tool 调用记录） |
| `/api/files` | GET/POST | 文件读取 / 保存 |
| `/api/files/tree` | GET | 目录树 |
| `/api/files/preview` | GET | 文件预览 |
| `/api/assets/upload` | POST | 上传资产 |
| `/api/assets/download` | GET | 下载资产 |
| `/api/workspaces` | GET/POST | Workspace 列表 / 创建 |
| `/api/workspaces/{id}` | PUT | 重命名 Workspace |
| `/api/workspaces/{id}/manifest` | GET | 获取 Workspace manifest |
| `/api/workspaces/{id}/bootstrap/start` | POST | 启动首次引导 |
| `/api/agents` | GET/POST | 兼容旧接口的 Agent 列表 / 创建 |

## Design Decisions

| 决策 | 理由 |
|------|------|
| `create_agent()` 而非 AgentExecutor | LangChain v1.0 现代范式，底层 LangGraph runtime，原生支持流式 |
| 每次请求重建 Agent | workspace/skills 文件可随时编辑，重建确保即时生效 |
| File-first 三层记忆 | 研究过程可追溯，可用 Obsidian/VSCode 直接审计，拒绝黑盒 |
| Context Orchestrator 显式选文件 | "选哪些文件进上下文"变成可测试、可回放的确定性逻辑 |
| Session 与 Trace 共用一套本地持久化 | 降低会话历史和审计记录的同步复杂度 |
| Skills 是 Markdown 而非 Python | 降低扩展门槛，用户写说明书即可教会 Agent 新技能 |
| WorkspaceRuntimeRegistry | 把多工作区生命周期管理集中到统一入口，便于隔离与扩展 |

## Testing

后端基础单元测试可直接运行：

```bash
cd backend
python -m unittest discover -s tests -p 'test_*.py'
```

前端测试命令：

```bash
cd frontend
npm test
npm run test:e2e
```

## License

MIT
