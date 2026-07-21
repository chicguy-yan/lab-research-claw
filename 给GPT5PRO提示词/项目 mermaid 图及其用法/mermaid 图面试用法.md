下面给你一套**“节点级面试追问卡”**，直接对齐你 3 张 Mermaid 图里的每个节点。你可以把它当成：面试官问什么 → 你怎么答 → 你怎么反问把对话拉回你擅长的“产品判断 + 可落地的工程约束 + 可复盘的透明性”。

---

## 通用答题骨架（所有节点通用）

每个节点你都用这 6 句话兜底，基本不会翻车：

1. **它是什么**：一句话定义节点职责（模块边界）。
2. **为什么必须要它**：对齐实验研究场景的“记忆压力源 / 可追溯 / 可回放”。
3. **输入输出是什么**：输入来自哪里，输出落到哪个文件/API 字段。
4. **确定性在哪里**：哪些是 deterministic（选文件、裁剪、落盘、trace），哪些是模型生成（解释、建议）。
5. **失败会怎样 + 怎么定位**：失败模式 + 你会去看哪个 trace 字段/哪个目录。
6. **下一步演进**：基于 PRD/TAD 的 v0.2 规划，讲“先最小闭环，再扩展”。

---

# 1) Workspace 生命周期节点卡片（Create → Run → Evolve → Archive → Clone）

> 这一组的核心卖点：**把 LLM 的不确定性，装进一个可回放的工作台生命周期里**。

### Create

**面试官可能问**

* 你说的 workspace “创建”具体做了什么？为什么不是数据库建表？
* 初始化要哪些文件？如果模板变了，旧 workspace 怎么兼容？
* 你怎么保证首次启动是幂等的，不会把用户文件覆盖？

**你答题要点**

* Create = **从 `workspace-templates/` 初始化到 `.openclaw/workspace/` 或 `workspace-{agent_id}/`**，这是 file-first 的“工作台骨架”。
* 同时做 **Skills 扫描并生成 `SKILLS_SNAPSHOT.md`**，保证后续 prompt 注入可控。
* 兼容策略：模板是“默认骨架”，workspace 是“实例”。旧实例不强刷，避免破坏用户真实历史。

**你可以反问**

* “你们团队在 agent 产品里更看重可追溯性，还是更看重自动化程度？我这个设计是优先可追溯。”

---

### Run

**面试官可能问**

* Run 阶段的关键接口是什么？为什么用 SSE？
* 怎么保证前端解析不被破坏？你增加字段会不会影响旧渲染？
* 一次 Run 里模型到底拿到了哪些上下文？

**你答题要点**

* Run 核心是 **POST `/api/chat` + SSE 事件流**，事件类型保持兼容，只允许“加字段不破坏解析”。
* “模型拿到哪些上下文”不是猜，是在 trace 的 **`context_read[]`** 里显式记录。
* done 事件附带 `turn_id` / `trace_path`，让前端立刻跳回放。

**你可以反问**

* “如果要在你们现有产品里接入 trace 回放，你们更偏日志系统还是 file-based replay？我这边是 file-first。”

---

### Evolve

**面试官可能问**

* 你怎么定义“演进”？是写记忆？写任务？写 pack？
* 记忆写错了怎么办？怎么避免模型瞎写污染？
* 你怎么让演进对 debug 有用？

**你答题要点**

* Evolve = **落盘 trace + 可选 memory patch + 产出/更新 Layer3 资产（Concept/Task/Pack）+ Skill Mining 触发**。
* 防污染：PRD 明确 **Project Context 是事实来源，信息不足必须 missing checklist，禁止脑补**。写入也有白名单与安全模式（只允许 memory/ assets）。
* 对 debug 有用的关键：trace 记录 **读了什么、写了什么、为什么裁剪、缺哪些字段、调用了哪些工具**。

**你可以反问**

* “你们做过被模型写坏配置/知识库的事故吗？我这里用白名单 + trace 可回放来控风险。”

---

### Archive

**面试官可能问**

* 为什么要 Archive？什么触发归档？
* 归档是压缩对话，还是冻结 workspace？
* 归档后还能复盘吗？

**你答题要点**

* Archive 的目标是：阶段结束后减少噪声，让工作台进入“只读可复盘”状态。
* 实现路径：会话压缩（compress）+ workspace 保留 packs/traces/memory，做到“可回放但不再频繁变动”。

**你可以反问**

* “你们实验研究类用户更希望保留全量 trace 还是只保留 pack？我现在倾向两者都保留但 pack 优先。”

---

### Clone

**面试官可能问**

* Clone 和新建 session 的区别？
* 你怎么处理分支带来的记忆分叉？
* Clone 的价值是什么？

**你答题要点**

* Clone = 复用一个已验证的 workspace 骨架和资产，把它当成**研究分支**（比如新一轮 Rxx 或新方向）。
* 风险是记忆分叉，所以 trace 很关键：每个分支都有自己 `context_trace/`，可回放差异。

**你可以反问**

* “你们内部更像 git 分支模型，还是像 timeline 线性推进？我这个 Clone 是偏分支复用。”

---

# 2) 单次对话闭环 + 上下文拼接节点卡片（Ingest → Plan → Close → Pack → Skill Mining）

> 这一组的核心卖点：**一次对话不仅回答，还要产出可复用资产**。

## A. Context Assembly（SessionManager / ContextOrchestrator / PromptBuilder）

### SessionManager

**面试官可能问**

* session 保存什么？为什么不直接把所有消息塞进 prompt？
* 压缩策略怎么做？会不会丢信息？

**你答题要点**

* SessionManager 做“会话持久化与读取”，给 Orchestrator 提供必要的最近状态，但不是无限塞进上下文。
* 压缩是为控制 token 与噪声，真正可复盘靠 trace + file-first 记忆层。

**反问**

* “你们更担心 token 成本，还是更担心信息丢失？我这里是用 trace 来兜底信息可回放。”

---

### ContextOrchestrator

**面试官可能问**

* 你怎么选文件？为什么要显式选择？
* 默认注入顺序是什么？为什么这样排？
* 预算裁剪怎么做？截断如何解释？

**你答题要点**

* 它是实验版关键模块：输出 `selected_files[]`（带 why）、`budget_report`、`trace_seed`。
* 默认注入顺序：**workspace → skills_snapshot → Layer1 → Layer2 → Layer3 → uploads**，理由是“稳定 → 变化 → 本轮相关”。
* 单文件字符上限 20,000，截断/跳过必须进 trace，带 why + policy。

**反问**

* “你们在 RAG/文件注入里有没有遇到过‘模型看错版本’？我这里用固定排序 + trace 来降风险。”

---

### PromptBuilder

**面试官可能问**

* 你为什么强调 OpenClaw 风格两条消息？
* system 里为什么要把文件全文注入？
* untrusted 块是干嘛的？

**你答题要点**

* 两条消息把边界说清：system 固定运行规则 + Project Context 文件全文；user 是 untrusted（可选）+ 用户正文。
* system 块顺序固定（身份行、Tooling、Workspace 规则、Inbound metadata、Project Context）。
* untrusted 让平台元数据或不确定信息显式标注，不混入事实来源。

**反问**

* “你们更偏好把检索结果当事实，还是把文件当事实？我这里明确 Project Context 是事实来源。”

---

## B. Runtime Loop（Ingest / Plan / Close / Pack / Skill Mining）

### Ingest

**面试官可能问**

* 你怎么识别用户意图？为什么不直接让模型自由发挥？
* 缺口字段怎么处理？

**你答题要点**

* Ingest 识别意图类型（阶段汇报/实验矩阵/机理审计/写作/作图等），并产出 missing checklist。
* 价值：让研究任务从“聊天”变成“可执行闭环”。

**反问**

* “你们会在产品里显式展示 missing checklist 吗？我认为这对科研场景能显著降幻觉。”

---

### Plan

**面试官可能问**

* 计划输出什么算合格？怎么避免变成空泛建议？
* 你怎么定义最小验证集？

**你答题要点**

* Plan 输出下一步最小验证集：对照、空白、判据，能直接进入实验或数据处理动作。
* 它对齐你 PRD 的目标：研究闭环驱动，而不是知识问答。

**反问**

* “你们评估 agent 输出质量更看重可执行性还是解释性？我这边优先可执行。”

---

### Close

**面试官可能问**

* Close 为什么必要？聊天不就结束了吗？
* Close 写进哪里？怎么帮助下一轮？

**你答题要点**

* Close 把本轮 run 的 `raw_data_paths / quick_results / verdict` 写入 Task（或提示用户补齐）。
* 好处：下一轮不是从 0 开始，Layer3 的 Task 就是“研究进度条”。

**反问**

* “你们的研究类产品会把结论和证据链绑定存储吗？我这里 Close 就是把证据入口固定下来。”

---

### Pack

**面试官可能问**

* Pack 和 Task 区别？为什么要多一层？
* Pack 的典型交付是什么？

**你答题要点**

* Pack 是多个 Task 的组织层，用来产出阶段交付：PPT、机理证据链、写作段落、图集等。
* 它是科研用户真正需要的“可交付物”，不是聊天记录。

**反问**

* “你们觉得科研用户的北极星是论文，还是阶段汇报？我这里用 Pack 适配两者。”

---

### Skill Mining

**面试官可能问**

* 什么时候触发 Skill Mining？怎么判断“高重复交付”？
* Skill 的价值是什么？会不会把系统搞得越来越复杂？

**你答题要点**

* 触发条件：高频重复交付，如阶段汇报 PPT 提示词，沉淀为技能模板，减少重复劳动。
* 风险是复杂度，所以 Skill 以目录化管理，且通过 `SKILLS_SNAPSHOT.md` 控制注入范围。

**反问**

* “你们会担心技能库膨胀吗？我这里用 snapshot 做‘可用技能集合’收敛。”

---

## C. TraceWriter / Trace 文件（你的“面试护身符”）

**面试官可能问**

* 你怎么做到可回放？trace 里具体记录什么？
* Memory patch 怎么安全应用？防止写坏系统？

**你答题要点**

* 每回合落盘 `.openclaw/context_trace/Txxxx.json`，最小 schema 里有 `context_read / context_write / missing / skills_selected / tool_calls / artifacts`。
* Memory patch 可选，提取 `## Memory patch (proposed)` JSON，校验白名单与冲突策略，成功失败都写入 `context_write[]`。
* 这是你“透明可控”的核心论据：面试官问任何细节，你都能说“我会去 trace 里验证”。

**反问**

* “你们现在调试 agent 的主要手段是什么？我这里用 trace 把 agent 行为变成可审计资产。”

---

# 3) 前后端 + 记忆系统 + Workspace 架构节点卡片（图 3 全覆盖）

## Frontend 三栏（MemoryPanel / ChatPanel / ThoughtChain / AtomPanel / MonacoDock）

**面试官可能问**

* 为什么做三栏？用户心智是什么？
* Monaco 编辑器为什么要嵌？不会太重吗？
* ThoughtChain 为什么要保留？展示 tool_start/tool_end 的价值是什么？

**你答题要点**

* 三栏对应三层记忆：左侧长期规则与时间轴，中间对话闭环，右侧原子资产工作台。
* Monaco 让“记忆是文件”这个理念落地，用户能直接编辑可控。
* ThoughtChain 沿用 SSE 解析，核心价值是透明：用户看到模型在读什么、做什么、工具调用发生了什么。

**反问**

* “你们产品里更强调‘自动’，还是更强调‘可控’？我这里为了科研场景优先可控。”

---

## Backend API（chat/sessions/files/assets/traces/tokens/compress/config_api）

**面试官可能问**

* API 为什么这样拆？哪个是核心路径？
* 上传 assets 为什么是必需？和实验场景如何对齐？
* traces API 给谁用？前端怎么消费？

**你答题要点**

* 核心路径是 `/api/chat`，其余是让工作台可用：files 提供 tree/preview/skills list，assets 让数据与图进入工作区，traces 支持回放。
* tokens/compress/config_api 是工程治理与模式开关（比如 RAG）。

**反问**

* “你们更倾向把 trace 当内部日志，还是用户可见功能？我这里是用户可见来提升信任。”

---

## Core graph（AgentManager / ContextOrchestrator / PromptBuilder / SessionManager / TraceWriter / KnowledgeIndexer）

**面试官可能问**

* 你怎么划分 deterministic 与 LLM？
* 为什么 KnowledgeIndexer 是可选外挂？
* 工具调用如何被记录并回放？

**你答题要点**

* deterministic：选文件、裁剪、拼 prompt、写 trace、白名单写入。LLM：推理、解释、生成 plan/pack。
* KnowledgeIndexer 可选是为了先跑通 file-first 闭环，RAG 作为增强，不让系统依赖外部检索才能工作。
* 工具调用通过流式事件汇总进 trace 的 tool_calls。

**反问**

* “你们团队更偏 agent-first 还是 retrieval-first？我这边是 file-first，然后外挂 RAG。”

---

## tools/ 六大核心工具

**面试官可能问**

* 为什么这 6 个是核心？科研场景最常用哪个？
* web_search 为什么是条件启用？

**你答题要点**

* 终端 + python_repl + read_file 是科研工作台最常见动作组合，fetch/search_knowledge_base 是补信息。
* web_search 条件启用是为了控制事实来源与可复盘性，避免外部噪声破坏“本轮事实来源是 Project Context”。

**反问**

* “你们对外部搜索的可信度怎么做治理？我这里把它定位成可选工具，不当事实来源。”

---

## FS（workspace / memory / skills / context_trace / sessions / assets / knowledge）

**面试官可能问**

* 为什么坚持 file-first？扩展性如何？
* 记忆三层怎么避免混乱？
* trace 为什么不放进 memory？

**你答题要点**

* file-first 的好处：透明、可版本管理、可 diff、可回放，符合科研用户习惯。
* L1 稳定规则，L2 时间推进，L3 原子资产。上下文注入顺序固定，降低混乱。
* trace 是 debug log，不是记忆。它服务“复盘与定位”，不应该污染长期记忆。

**反问**

* “你们更倾向把知识沉淀成数据库，还是文档资产？我这里把文档当第一公民。”

---

## 最后给你一招“面试官追问到细节时的收束句”

当对方开始抠细节，你可以用这句把话题拉回优势：

> “这个点我会用 trace 的 `context_read/context_write/missing/tool_calls` 去验证，确保可回放可审计。模型负责生成建议，但系统负责保证确定性与可追溯。”

如果你希望我再帮你做一版更狠的：把每个节点都压成 **“15 秒口播版”**（适合面试时快速说清楚），我也能按同一套节点顺序输出。
