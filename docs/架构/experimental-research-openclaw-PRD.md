# Experimental-Research-OpenClaw 开发需求文档 (PRD) — v0.2

> 本 PRD 在 mini-openclaw 的技术栈（FastAPI + SSE + LangChain create_agent + Next.js + Monaco）基础上，
> 面向 **实验学科研究**（材料/化学/环境/生物等）场景，强化“研究闭环”与“记忆系统”能力。

---

## 一、项目介绍

### 1. 功能与目标定位

Experimental-Research-OpenClaw 是一个基于 Python 重构的、轻量级且高度透明的 AI Agent 系统，旨在复刻并优化 OpenClaw（原名 Moltbot/Clawdbot）的核心体验。

本项目不追求构建庞大的 SaaS 平台，而是致力于打造一个运行在本地的、拥有“真实记忆”的数字副手。其核心差异化定位在于：

- **文件即记忆 (File-first Memory)**：摒弃不透明的向量数据库作为“记忆源”，回归最通用的 Markdown/JSON 文件系统。用户的每一次对话、Agent 的每一次复盘与沉淀，都以人类可读的文件形式存在并可追溯。
- **技能即插件 (Skills as Plugins)**：遵循 Anthropic 的 Agent Skills 范式，通过文件夹结构管理能力，实现“拖入即用”的技能扩展（Skill 是 Markdown 说明书，而非预置函数）。
- **透明可控**：System Prompt 拼接逻辑、工具调用、记忆读写与缺口追问全部可回放（Trace），拒绝黑盒。

### 2. 项目核心技术架构（保持 mini-openclaw 选型不变）

本项目要求完全采用 **前后端分离** 架构，后端作为纯 API 服务运行。

- 后端语言：Python 3.10+（强制使用 Type Hinting）。
- Web 框架：FastAPI（提供 RESTful 接口，支持异步处理）。
- Agent 编排引擎：LangChain 1.x（Stable Release）
  - **必须使用** `create_agent` API（`from langchain.agents import create_agent`）。
    - `create_agent` 底层基于 **LangGraph runtime**，是 LangChain v1.0 官方推荐的现代 Agent 构建方式。
    - 参考：[LangChain & LangGraph 1.0 博客](https://blog.langchain.com/langchain-langgraph-1dot0/) 与 [v1 迁移指南](https://docs.langchain.com/oss/python/migrate/langchain-v1)。
  - **严禁使用**旧版 `AgentExecutor`。
  - **严禁使用** `langgraph.prebuilt.create_react_agent`（除非作为"临时降级方案"并明确打 `TODO: migrate to create_agent`）。
- RAG 检索引擎：LlamaIndex Core（Hybrid Search：BM25 + Vector），用于“知识库外挂”，**不作为记忆源**。
- 模型接口：兼容 OpenAI API 格式（支持 OpenRouter / DeepSeek / Claude 等）。
- 数据存储：本地文件系统为主（Markdown/JSON），不引入 MySQL/Redis。

---

## 二、内置工具（Core Tools）

Experimental-Research-OpenClaw 在启动时，除了加载用户自定义的 Skills 外，必须内置以下 6 个核心基础工具（Core Tools）。根据“优先使用 LangChain 原生工具”的原则，技术选型更新如下：

### 1. 命令行操作工具 (Command Line Interface)

- 功能描述：允许 Agent 在受限的安全环境下执行 Shell 命令。
- 实现逻辑：
  - 直接使用 LangChain 内置工具：langchain_community.tools.ShellTool。
  - 配置要求：
    - 初始化时需配置 root_dir 限制操作范围（沙箱化），防止 Agent 修改系统关键文件。
    - 需预置黑名单拦截高危指令（如 rm -rf /）。
- 工具名称：terminal。

### 2. Python 代码解释器 (Python REPL)

- 功能描述：赋予 Agent 逻辑计算、数据处理和脚本执行的能力。
- 实现逻辑：
  - 直接使用 LangChain 内置工具：langchain_experimental.tools.PythonREPLTool。
  - 配置要求：
    - 该工具会自动创建一个临时的 Python 交互环境。
    - 注意：由于 PythonREPLTool 位于 experimental 包中，需确保依赖项安装正确。
- 工具名称：python_repl。

### 3. Fetch 网络信息获取

- 功能描述：用于获取指定 URL 的网页内容，Agent 联网的核心。
- 实现逻辑：
  - 直接使用 LangChain 内置工具：langchain_community.tools.RequestsGetTool。
  - 增强配置 (Wrapper)：
    - 原生 RequestsGetTool 返回的是原始 HTML，Token 消耗巨大。
    - 必须封装：建议继承该类或创建一个 Wrapper，在获取内容后使用 BeautifulSoup 或 html2text 库清洗数据，仅返回 Markdown 或纯文本内容。
- 工具名称：fetch_url。

### 4. 文件读取工具 (File Reader)

- 功能描述：用于精准读取本地指定文件的内容。这是 Agent Skills 机制的核心依赖，用于读取 SKILL.md 的详细说明。
- 实现逻辑：
  - 直接使用 LangChain 内置工具：langchain_community.tools.file_management.ReadFileTool。
  - 配置要求：
    - 必须设置 root_dir 为项目根目录，严禁 Agent 读取项目以外的系统文件。
- 工具名称：read_file。

### 5. RAG 检索工具 (Hybrid Retrieval)

- 功能描述：当用户询问具体的知识库内容（非对话历史）时，Agent 可调用此工具进行深度检索。
- 技术选型：LlamaIndex。
- 实现逻辑：
  - 索引构建：支持扫描指定目录（如 knowledge/）下的 PDF/MD/TXT 文件，构建本地索引。
  - 混合检索：必须实现 Hybrid Search（关键词检索 BM25 + 向量检索 Vector Search）。
  - 持久化：索引文件需持久化存储在本地（storage/）。
- 工具名称：search_knowledge_base。

### 6. 网络搜索（web_search）

- LangChain 官方专门为 Tavily 写了一个工具包（langchain-tavily-search），把它封装成了标准的 LangChain Tool 接口。因为 LangGraph 直接复用 LangChain 的 Tool 系统，所以调用起来就是一行代码的事。亦可接入 Brave API 作为搜索提供方。
- 数据格式契合：传统的搜索引擎返回的是杂乱的 HTML 或大段文本，而 Tavily/Brave 方案可返回更易消费的摘要/结构化信息。这对于 LangGraph 中的 LLM 节点来说，不仅消耗的 Token 少，而且信息提取的成功率较高。

> 最小 MVP 说明：若本地未配置 Brave API（缺少 `BRAVE_API_KEY`），则不启用 `web_search` 工具，系统保持离线工具集运行，确保最小可用。

> 说明：**记忆系统的“读/写”由后端 Orchestrator 通过文件系统完成**（见第四节），避免把“记忆落盘”交给不受控的向量库或隐式黑盒。

---

## 三、Experimental-Research-OpenClaw 的 Agent Skills 系统

### 1. Skills 范式

Skills 遵循 **Instruction-following**（指令遵循）范式：Skill 是教会 Agent 如何使用 Core Tools 的“说明书”，而不是预先写好的 Python 函数。

### 2. Skills 载入与执行流程

#### 2.1 Bootstrap：生成 SKILLS_SNAPSHOT

系统启动或会话开始时扫描 `backend/skills/`，读取每个 `SKILL.md` 的 Frontmatter 元数据，生成 `SKILLS_SNAPSHOT.md` 注入 System Prompt。

#### 2.2 Execution：使用 Skill 的硬协议

当 Agent 需要使用某个技能时：

1) 先用 `read_file` 读取该 Skill 的 `location`  
2) 按 Skill 说明书执行（调用 terminal/python_repl/fetch_url 等）  
3) 将产物路径写入输出（并在需要时进入记忆系统的 Pack/Task 资产）

> 注意：实验版建议提供一组默认技能模板：`stage_report_ppt`、`synthesis_checklist`、`experiment_matrix`、`mechanism_audit`、`characterization_audit`、`writing_outline`、`csv_kobs_fit`。

---

## 四、Experimental-Research-OpenClaw 对话记忆管理系统设计（核心改造）

> 本节以《research-openclaw-记忆系统设计.md》为准，目标是把 180 天实验周期跑成“可追溯、可验证、可回放、可沉淀”的工作台。

### 4.1 设计目标：解决实验研究用户的“记忆压力源”

**系统必须替用户记住：**

1) **阶段性推进**：比如每 2–3 周一次阶段汇报（R01…R10），用户会给 `assets/ppt_pack/Rxx_YYYYMMDD/` 素材路径，需要快速汇总。
2) **实验闭环**：比如每天做了什么、是否支撑主线、缺哪些对照/表征（合成 checklist、参数矩阵、XRD/SEM/XPS“能证明什么不能证明什么”）。
3) **机理证据链闭环**：比如Co(IV) / ClO₂ 的硬证据链（PMSO 探针 + DPD 显色 + 淬灭剂 + 必要空白/对照 + 判据）。
4) **写作闭环**：比如Results & Discussion 目录树、每节中心句、主文/SI 放图策略。

### 4.2 三层记忆（File-first）

记忆拆成三层文件系统（均位于 `.openclaw/workspace-{agent_id}/`）,记忆系统模板在`backend\workspace-templates`：

#### Layer1：Identity（身份与规则，长期稳定）

让系统长期知道“你是谁、项目是什么、输出应该长什么样”。

```text
memory/identity/
  user.md                # 用户偏好与输出约束
  project.md             # 主线假设、指标、术语表、判据（最关键）
  lab_context.md         # 实验室现实约束：仪器/表征/命名/污染风险
  context_budget.md      # 单回合上下文预算与截断策略（可选但推荐）
```

#### Layer2：Timeline（时间轴推进，阶段→周→日）

把 180 天从“阶段计划”落到“每天执行”，并能自动汇总成阶段汇报 pack。

```text
memory/timeline/
  180d_index.md                 # 180天总览：阶段划分、里程碑、风险雷达
  phases/
    P01_bootstrap.md
    P02_material_screening.md
    P03_parameter_optimization.md
    P04_mechanism_closure.md
    P05_writing_submission.md
  weeks/
    2025-W39.md
    ...
  days/
    2025-12-31.md
    ...
  stage_reports/
    R09_20260119.md
    ...
```

#### Layer3：Atom Notes（原子资产，跨周期证据链与可复用对象）

对外推荐三对象（更简洁、易用）：

- **Concept**：一个研究主题容器（你在验证什么）
- **Task**：一次验证任务（= Claim + Protocol + Run，可追加多次 run）
- **Pack**：把证据链写成最终交付物如论文和 ppt 等（阶段汇报/机理闭环证据链/论文写作文段/实验图片即便）

```text
memory/concepts/
  CONCEPT_*.md
memory/tasks/
  TASK_*.md              # 内含 Claim + Protocol + Run
memory/packs/
  PACK_*.md              # stage_report/mechanism/writing/figure 等交付包
```


> 建议：前端仍以 Concept/Task/Pack 展示

### 4.3 Context Trace（透明可控）

每回合必须落盘一份 trace，支持回放”读/写/缺/技能/工具/产物”，其实也就是 OpenAI 的对话历史。
落实在 `.openclaw/workspace-{agent_id}/context_trace/` 目录下。这个不在记忆中，仅仅是作为 debug 的 log 信息。

> **澄清（v0.2.1）**：Session 历史消息与 Trace 审计日志是**同一个文件**（`context_trace/{session_id}.json`），格式为 OpenAI messages 数组（`role: user / assistant / tool`）。SessionManager 负责读写对话消息，TraceWriter 负责在每轮 `done` 后将 `context_read[]` 等审计元信息追加到该数组中（可作为 `role: system` 或自定义字段）。不拆分两个文件，避免冗余与同步问题。

trace 最小 schema,这个trace就是最简单的：

```json
[
  {
    "role": "user",
    "content": "请帮我查一下今天上海的天气。"
  },
  {
    "role": "assistant",
    "content": null,
    "tool_calls": [
      {
        "id": "call_abc123def456",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"Shanghai\", \"unit\": \"celsius\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_abc123def456",
    "name": "get_weather",
    "content": "{\"temperature\": 25, \"condition\": \"Sunny\", \"location\": \"Shanghai\"}"
  }
]
```

### 4.4 用户单次对话 Prompt 拼接与上下文注入（OpenClaw 风格，两条消息）

> 目标：把不确定的 LLM 行为包进确定的“上下文选择 + 注入顺序 + 读写落盘 + trace 回放”外壳里，确保可迭代、可复盘、可定位。

#### 4.4.0 两类“身份信息”的语义与边界

系统内存在两类看起来都像“Identity”的文件，但语义不同：

A) **Workspace 控制层（Control Plane）**：`workspace/AGENTS.md`、`workspace/SOUL.md`、`workspace/IDENTITY.md`、`workspace/USER.md`
- 作用：定义“Agent 如何工作”的硬协议（工具边界、输出结构、禁止脑补、记忆/技能协议等）
- 权威性：最高（与任何记忆冲突时，以 workspace 为准）
- 可变性：低频变更（由开发者/用户维护为主）
- 写权限：允许写入

B) **Layer1: memory/identity（Data Plane, Stable Facts）**：`memory/identity/user.md`、`project.md`、`lab_context.md`、`context_budget.md`
- 作用：存放长期稳定事实与约束数据（项目北极星与判据、实验室现实约束、用户偏好、上下文预算策略）
- 权威性：服从 workspace 协议
- 可变性：允许缓慢演进（可由模型“提议写入”，由后端落盘）
- 写权限：允许写入


#### 4.4.1 两条消息模型

- **system**：框定运行环境 + 注入 Project Context（工作区文件全文）
- **user**：拼接“非可信上下文块（untrusted）”+“用户正文”

#### 4.4.2 system prompt 的固定块顺序（块与块之间空一行）

1) 身份行（固定）  
`You are a personal assistant running inside OpenClaw.`
身份行由 PromptBuilder 内置常量生成，不从 workspace/ 或 memory/ 文件读取；workspace/ 与 memory/ 内容仅通过 # Project Context 注入。

2) `## Tooling`：列出可用工具摘要（terminal/python_repl/fetch_url/read_file/search_knowledge_base/web_search）

3) `## Workspace`：声明工作目录与规则  
- 例如：`Your working directory is: /workspace`  
- 强制声明：**Project Context 文件是本轮事实来源**；信息不足必须列 Missing checklist，禁止脑补。

4) `## Subagent Context` / `## Group Chat Context`（可选）  
- `## Inbound Context (trusted metadata)` + JSON（平台/时区/语言/会话类型/当前日期等）

5) `# Project Context`：按顺序注入本轮在/memory 文件中选中的文件全文
- 格式：  
  - `## <absolute_or_workspace_path>`  
  - 空行  
  - `<file_content>`

#### 4.4.3 Project Context 注入文件的默认排序（稳定→变化→本轮相关）

默认按“稳定 → 变化 → 本轮输入相关”拼接（推荐）：

1. `workspace/AGENTS.md`（技能协议 + 记忆协议）
2. `workspace/SOUL.md` / `workspace/IDENTITY.md` / `workspace/USER.md`
3. `SKILLS_SNAPSHOT.md`（可用技能清单）
4. **Layer1**：`memory/identity/user.md`、`memory/identity/project.md`、`memory/identity/lab_context.md`
5. **Layer2**：`memory/timeline/180d_index.md` + 当前 `phase.md`  
   - 若是“最近/今天”问题：追加 `days/YYYY-MM-DD.md`
   - 若是“阶段汇报”：追加 time_range 内相关 `weeks/` 与 `stage_reports/上一期`
6. **Layer3**：与本轮最相关的 `CONCEPT/TASK/PACK`（优先 active/最近更新）
7. 本轮 `uploads`（若是文本类可直接注入；大文件仅注入路径 + 摘要/采样）

冲突规则（必须实现）：
- workspace 协议优先级最高；与记忆内容冲突时，以 workspace 为准。
- “上下文选择”必须显式，并写入 trace 的 `context_read[]`。

#### 4.4.4 裁剪与预算（必须实现）

- 单文件字符上限：20,000（与 mini-openclaw 保持一致）；超出追加 `...[truncated]`
- 总上下文预算：以 `context_budget.md` 为准（（推荐按层分配：workspace 固定、L1 固定、L2 近邻、L3 Top-K、uploads 最小化）
- 任何被截断/跳过必须记录到 trace（why + policy）

#### 4.4.5 Trace 最小字段（为回放与定位服务）

`context_read[]` 每项至少包含：
- `path`：文件路径
- `layer`：workspace | skills | memory_identity | memory_timeline | memory_atom | uploads
- `why`：选择原因（短句）
- `status`：full | truncated | skipped

> 目的：前端能“点一下回放”，开发者能快速定位“本轮读了什么、为什么读、有没有被裁掉”。

### 4.5 Runtime Loop：一次对话如何“读→做→写→沉淀”

一次对话最小闭环（MVP）：

1) **Ingest（摄取）**：识别意图（阶段汇报/实验矩阵/机理审计/写作/作图），收集缺口字段。
2) **Plan（计划）**：输出下一步最小验证集（对照/空白/判据）。
3) **Close（闭环）**：将 Run 的 raw_data_paths、quick_results、verdict 写入 Task（或建议用户补齐）。
4) **Pack（交付）**：把多个 Task 组织成 Pack（PPT/机理证据链/写作段落/图集）。
5) **Skill Mining（沉淀）**：检测高重复交付（如“阶段汇报 PPT 提示词”），提炼为新 Skill 模板（半自动）。


### 4.6 典型高频场景 → 读写策略（必须覆盖）

- **合成 checklist**：读 project 判据 + lab_context + today day；写 `days/YYYY-MM-DD.md` 的 planned_tasks + 新建/更新 `TASK_synthesis_*`
- **实验矩阵**：读 project 判据 + 已有 task/pack + today day；写 `TASK_experiment_matrix_*` + 更新 day
- **机理证据链审计（Co(IV)/ClO₂）**：读 project 判据 + mechanism tasks +（可选 papers）；写 `TASK_mechanism_*` + `PACK_mechanism_*`
- **表征审计（能证明/不能证明）**：读对应数据 task 的 evidence + project 判据；输出两列表格 + 最小补齐对照
- **阶段汇报（Rxx）**：读 time_range 内 days/weeks + 上一份 stage_report + 关键 packs；写新 stage_report + `PACK_stage_report_*` + 更新 `180d_index.md`
- **写作结构（R&D）**：读 project 北极星 + packs（图/结论）；写 `PACK_writing_*`
- **CSV 作图 + kobs 拟合**：读数据路径（assets/data）+ user 偏好；写 figure + `TASK_figure_kobs_*`

### 4.7 端到端例子：第 6 次阶段汇报（R06）

#### 用户输入（body）

> “帮我做第 6 次阶段汇报（R06），素材都放在 `assets/ppt_pack/R06_20251123/`。请给我 PPT 的页级结构 + 每页中心句 + WPS AI 提示词。我这两周主要做了材料合成和 DPD 显色。”

#### Orchestrator 选择文件（context_read plan，示意）

- `memory/identity/project.md`（北极星与判据）
- `memory/timeline/stage_reports/R05_20251105.md`（上一期）
- `memory/timeline/weeks/2025-W46.md` ~ `2025-W47.md`（time_range）
- `memory/timeline/days/2025-11-XX.md`（关键实验日，Top-N）
- `memory/packs/PACK_mechanism_*.md`（若本期涉及机理线）
- `skills/stage_report_ppt/SKILL.md`（若启用阶段汇报技能）
- `assets/ppt_pack/R06_20251123/` 下用户提供的素材清单（仅路径/文件名）


---

> Workspace 是 File-first 的工作台：memory/、assets/、context_trace/、workspace/*.md 的集合体。

### 4.8.1 核心对象关系（必须明确）

- Session：一次对话线程（messages + tool_calls），用于短期对话上下文，不替代三层记忆。

最小 MVP 绑定策略(当下建议)：
- `session_id` 绑定到一个 `agent_id`（默认 1:1）。
- Workspace 目录命名规则：
  - 默认：`backend/.openclaw/workspace-default/`（可视为 agent_id = "default"）
  - 其他：`backend/.openclaw/workspace-{agent_id}/`

> 约束：Context Orchestrator 的文件选择、TraceWriter 的落盘，都必须以 “本 session 绑定的 workspace_dir” 为根目录执行。

### 4.8.2 状态机定义（状态/触发/输入输出）

| 状态 | 触发条件 | 输入 | 输出（必须落盘） | 允许操作 |
|---|---|---|---|---|
| Create | 创建这个agent | workspace-templates/ + skills/ | 初始化 workspace_dir（复制模板 + 创建 memory/assets/context_trace 骨架） | 进入 Run |
| Run | POST /api/chat（单回合运行） | user message + uploads + history + selected_files | SSE token/tool_start/tool_end/new_response/done； | 可进入 Evolve |
| Evolve | 该回合 done 后执行“沉淀动作” | trace_seed + tool_calls + assistant final text | 写入 trace；提示模型更新各类文档 | 返回 Run |



### 4.8.3 Workspace 初始化内容（Create 的验收标准）

当 workspace_dir 不存在时，初始化必须创建以下骨架（空文件可用模板）这里直接把模板文件复制过来：

- `workspace/`（SOUL/IDENTITY/USER/AGENTS 等 prompt 组件）
- `memory/identity/`（user.md / project.md / lab_context.md / context_budget.md）
- `memory/timeline/`（180d_index.md + templates）
- `memory/concepts/` `memory/tasks/` `memory/packs/`
- `assets/uploads/` `assets/data/` `assets/figures/` `assets/ppt_pack/`
- `context_trace/`（README + TRACE_TEMPLATE.json + 运行时 Txxxx.json）

> 验收：用户创建 session 后，前端三栏能通过 /api/files/tree 看到以上目录树。



## 五、后端 API 接口规范 (FastAPI)（需适配三层记忆与三栏前端）

后端服务作为独立进程运行，负责 Agent 编排、Prompt 组装、文件读写、Trace 落盘与会话管理。

- 服务端口：8002
- Base URL：`http://localhost:8002`

### 5.1 核心对话接口（SSE，保持 mini-openclaw 协议）

**POST `/api/chat`**

- Request JSON：

```json
{
  "message": "帮我做第 6 次阶段汇报（R06）...",
  "session_id": "main_session",
  "stream": true
}
```

- Response：SSE 流式事件（事件类型保持兼容：`token/tool_start/tool_end/new_response/retrieval/done/title/error`）

用 SSE 的 event: 作为类型
```json
{"message":"...","session_id":"main_session","stream":true}
```

> 约束：SSE 事件类型与前端 ThoughtChain 的渲染方式保持不变，仅允许“增加字段”，不破坏既有解析器。

### 5.2 会话管理接口

- `GET  /api/sessions`：列出会话（按更新时间倒序）
- `POST /api/sessions`：创建会话
- `PUT  /api/sessions/{id}`：重命名
- `DELETE /api/sessions/{id}`：删除
- `GET  /api/sessions/{id}/history`：获取对话历史（含 tool_calls）

存储路径：`.openclaw/workspace-{agent_id}/context_trace/{session_id}.json`（SessionManager 持久化）

> **注意**：Session 历史消息与 Trace 审计日志共用此文件（见 §4.3 澄清）。

### 5.3 文件系统接口（支持三层记忆面板 ）


- `GET  /api/files?path=...`：读取文件内容
- `POST /api/files`：保存文件（body: `{path, content}`）
- `GET  /api/files/tree?path=...&max_depth=...`：列出目录树（用于左/右面板）
- `GET  /api/files/preview?path=...&max_chars=...`：返回文件预览（用于列表 hover/摘要）


### 5.4 资产上传（实验场景必需）

- `POST /api/assets/upload`（multipart/form-data）
  - fields：`file`, `target_dir`（默认 `assets/uploads/`）
  - 返回：`{saved_path, sha256, size}`

### 5.5 Trace 回放接口（建议新增，便于前端回放,方便用户完全理解大模型是如何工作的）

- `GET /api/traces?session_id=...&limit=...`：列出 trace



### 5.6 Skills 接口（保持 + 小增强）

- `GET  /api/skills`：列出技能（name/description/location）
- `POST /api/skills/rescan`：重新扫描 skills/ 并生成 SKILLS_SNAPSHOT.md（可选）

### 5.7 创建新agent的窗口, 在前端会有一个new_agent的按钮

- `GET  /api/agents`：

返回可选 agent 列表（Navbar 下拉用）

{
  "agents": [
    {"agent_id":"default","name":"Default","updated_at":"..."},
    {"agent_id":"cobalt_mech","name":"Co(IV) Mechanism","updated_at":"..."}
  ],
  "current":"default"
}
- `POST /api/agents`：

创建 agent（New Agent 提交,这里需要在前端让用户输入agent_id和name,但是会提供默认为default和ChemistryResearchAgent）
{
  "agent_id": "cobalt_mech",
  "name": "Co(IV) Mechanism"
}
name 会保存到  .openclaw\workspace-{agent_id}\IDENTITY.md
---

## 六、前端开发要求（适配实验版“三栏：L1/L2 | Chat | L3”）

> SSE 流式与 ThoughtChain 展示沿用 mini-openclaw，不修改解析逻辑。

### 6.1 总体布局

三栏 IDE 风格布局（支持拖拽分隔条、折叠）：

```text
┌───────────────────────────────────────────────────────────────────┐
│ Navbar（Project / Session / RAG / Token / Settings）               │
├───────────────┬──────────────────────────────┬────────────────────┤
│ Left Panel    │ Middle Panel                 │ Right Panel         │
│ Layer1+Layer2 │ Chatbot（消息 + 输入）        │ Layer3（Atom Notes）│
│ Identity      │ + ThoughtChain（SSE 工具流）  │ Concepts / Tasks /  │
│ Timeline      │ + RetrievalCard（可选）       │ Packs               │
└───────────────┴──────────────────────────────┴────────────────────┘
```

### 6.2 左侧面板：Layer1 + Layer2（长期规则 + 时间轴）

必须支持：

- **分区树**：Identity / Timeline 两大分组
- Identity 快捷入口：`user.md / project.md / lab_context.md / context_budget.md`
- Timeline 快捷入口：
  - `180d_index.md`
  - phases（P01–P05）
  - stage_reports（Rxx 列表，按时间倒序）
  - days / weeks（支持按日期范围加载，避免一次性渲染 180 个文件）
- 点击文件：右侧或弹出编辑器打开（Monaco），支持保存（调用 `/api/files`）

### 6.3 中间面板：Chatbot（研究闭环对话）

必须支持：

- Markdown 消息渲染（含表格/代码块）
- 输入框支持：
  - 多行输入
  - 上传文件（调用 `/api/assets/upload`，并把返回路径插入输入或作为 uploads 附件）
- Agent 流式输出：
  - token 流
  - tool_start/tool_end/new_response 触发 ThoughtChain 更新（与 mini-openclaw 一致）


### 6.4 右侧面板：Layer3（Concept / Task / Pack 工作台）

必须支持：

- Concepts 列表（读取 `memory/concepts/`）
- Tasks 列表（读取 `memory/tasks/`）
- Packs 列表（读取 `memory/packs/`）
- 列表项展示：标题/更新时间/状态（可从 Frontmatter 解析，也可后端提供 index API）
- 点击打开：展示全文 + back-links（通过引用字段或简单搜索实现）
- 推荐提供“快速新建”按钮：创建空模板文件（调用 `/api/files` create）

### 6.5 Trace 回放（实验版关键）

- 提供一个“回放”视图（可在 ThoughtChain 中集成），展示：
  - 读了哪些文件（context_read）
  - 写了哪些文件（context_write）
  - 缺口追问（missing）
  - 产物路径（artifacts）
这个就是对于message的直接展示,但是要有一个好的现实状态展示

---
