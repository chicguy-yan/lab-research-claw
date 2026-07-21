# ResearchLoop-OpenClaw 面试材料包

> 说明：
> 1. 本材料优先基于 `PRD / 各 Phase 开发计划与日志 / workspace 控制平面模板 / benchmark JSON / 当前代码` 交叉整理。
> 2. 凡“规划文档”和“当前代码”冲突处，默认以“当前仓库实际可见状态”优先，并在 Part 6 单独提示面试风险。
> 3. 所有无法稳定确认的数字均标记为“待确认”。

---

# Part 1. 项目一句话定位

1. 简历标题版  
`ResearchLoop-OpenClaw：面向科研闭环的 AI-native File-first Research Agent OS，用 Concept / Task / Pack 把文献、实验与阶段汇报串成可追溯工作流。`

2. 面试开场版  
`这不是一个做科研问答的聊天工具，而是一个把“文献调研-实验推进-阶段汇报/论文写作”连接起来的 File-first 科研工作系统，核心是让每轮工作都沉淀到可回放的 Concept、Task、Pack。`

3. 飞书项目介绍版  
`我们参考 OpenClaw 的 File-first 思路，但把重点放在科研场景的闭环推进上：用控制平面约束 Agent 行为，用 Concept / Task / Pack 承接长期资产，用 trace 让每次读写和判断都能回溯。`

---

# Part 2. 项目能力生态地图

## 1. 需求洞察

- 能力名称：从“科研问答”重定义为“科研闭环推进”
- 在本项目中的具体体现：不是解决“AI能不能回答问题”，而是解决科研信息分散在文献、原始数据、PPT、论文草稿之间，导致上下文反复丢失、任务难持续推进的问题；因此产品目标被重定义为“管理科研任务流”。
- 最核心的 1 个证据锚点：`yyq工作文档` 中明确把问题从“如何让 AI 回答科研问题”改写为“如何让 AI 管理科研任务流”，并强调核心压力来自文献、实验、写作三条闭环。
- 可以对齐的 JD 能力关键词：用户洞察、需求抽象、场景定义、问题重述、北极星定义
- 面试官可能如何追问：你为什么认为科研场景的核心问题不是检索能力不足，而是上下文断裂；如果只做一个科研问答助手为什么不够

## 2. 场景拆解

- 能力名称：把复杂科研流程拆成三条可验收闭环
- 在本项目中的具体体现：将科研高频任务拆为文献机理闭环、实验证据闭环、阶段汇报/写作闭环，并要求三条闭环收敛在同一 workspace 下运行，而不是做松散功能拼盘。
- 最核心的 1 个证据锚点：`docs/phase5.1-index.md` 将闭环 A/B/C 分别定义为 `mechanism_closure`、`experiment_closure`、`stage_progress / writing_closure`，并写出每条闭环的最小 assets、必需 skills 与验收项。
- 可以对齐的 JD 能力关键词：用户旅程拆解、流程设计、最小闭环、场景优先级
- 面试官可能如何追问：为什么先做这三条闭环；三条闭环之间的依赖关系是什么；为什么闭环 C 要排在最后验收

## 3. 产品抽象

- 能力名称：找到科研场景的 sweet point 抽象层
- 在本项目中的具体体现：没有停留在“Paper/文件管理”或“聊天记忆”层，而是把科研长期资产抽象为 Layer3 的 `Concept / Task / Pack`，分别承接研究主题、验证任务和阶段性交付。
- 最核心的 1 个证据锚点：`docs/phase3—index.md` 明确写出“assets 是原始材料层，memory 是 md 化沉淀层，Layer3 则是 Concept / Task / Pack 三类原子资产”；`PRD` 中把 Layer3 作为跨周期证据链与可复用对象。
- 可以对齐的 JD 能力关键词：信息架构、对象模型、领域建模、抽象能力
- 面试官可能如何追问：为什么是三类对象，不是普通 note / tag / folder；为什么 Task 是闭环推进核心；Pack 为什么不能被普通总结替代

## 4. AI / Agent 技术理解

- 能力名称：把 OpenClaw 的通用 Agent 思路改造成科研工作系统
- 在本项目中的具体体现：参考 OpenClaw 的 File-first 与 skills 范式，但没有照搬其“技术目录”语义，而是引入 `Control Plane / Data Plane / Trace Plane` 以及 `ContextOrchestrator / PromptBuilder / SkillLoader / TraceWriter` 这条主链，强调“协议先行、上下文渐进披露、技能按需读取”。
- 最核心的 1 个证据锚点：`yyq工作文档` 明确写出“控制平面先定义科研工作协议，再由 ContextOrchestrator / PromptBuilder / TraceWriter / SkillLoader 去执行”；`backend/api/chat.py` 已把这几个模块串起来。
- 可以对齐的 JD 能力关键词：Agent 架构理解、Prompt engineering、context engineering、技能系统、工作流编排
- 面试官可能如何追问：为什么不把 intent 做成重 Router；为什么 route 不参与后端强匹配；为什么选择 snapshot + read_file，而不是全量注入技能

## 5. 记忆系统设计

- 能力名称：区分控制协议、事实沉淀和审计回放
- 在本项目中的具体体现：把 workspace 根目录大写 MD 文件定义为 Control Plane，用于约束 Agent 行为；把 `assets/ + memory/` 作为 Data Plane，用于原始材料和 md 化沉淀；把 `context_trace/` 作为 Trace Plane，用于解释本轮为什么这样读写。
- 最核心的 1 个证据锚点：`docs/phase3—index.md` 和 `backend/workspace-templates/AGENTS.md` 都强调“文件即记忆、证据优先、透明可控”，且 `SOUL / USER / TOOLS / MEMORY / BOOTSTRAP` 都被拆成独立协议文件。
- 可以对齐的 JD 能力关键词：memory system、knowledge lifecycle、traceability、data modeling、protocol design
- 面试官可能如何追问：为什么控制平面不能和 memory/identity 混写；为什么 memory 统一使用 Markdown；为什么 trace 不直接等于聊天记录

## 6. 数据与评测体系

- 能力名称：不用公开 benchmark，而是自己构建贴近真实科研生命周期的数据集
- 在本项目中的具体体现：以真实实验室研究记录、文献、阶段汇报材料和长期科研记忆为底，构建 180 天科研生命周期 JSON benchmark，并辅以三类闭环场景做功能验收。
- 最核心的 1 个证据锚点：`yyq_chlorite_full_lifecycle_180d_300turns.json` 实际包含 300 轮对话，时间从 `2025-08-27` 到 `2026-02-22`，跨度 179 天，含 317 个上传记录与 129 个唯一资产路径。
- 可以对齐的 JD 能力关键词：evaluation、benchmark construction、offline dataset、acceptance criteria、evidence-based iteration
- 面试官可能如何追问：为什么不用公开 benchmark；这个 benchmark 如何保证代表性；你如何定义“系统做错了”

## 7. 开发推进与 debug

- 能力名称：AI-native 但有工程验收意识的推进方式
- 在本项目中的具体体现：用 CC 做架构设计与复杂度收敛，用 Codex 做代码审查与 debug，并在每个阶段通过前端真实试用和日志复盘来定位“流程 bug”和“架构复杂度失控”。
- 最核心的 1 个证据锚点：`yyq工作文档` 明确写出“CC 负责架构设计与复杂度收敛，Codex 负责代码审查与 debug，本人通过前端真实试用驱动迭代”；`trace_collection_fix_log.md` 记录了因工具调用聚合错误而导致 trace 失真的修正过程。
- 可以对齐的 JD 能力关键词：AI-native development、debug、问题归因、迭代推进、工程协同
- 面试官可能如何追问：你如何判断是 prompt 问题、代码问题还是架构问题；为什么让 CC 和 Codex 分工而不是混用；真实试用具体发现过什么问题

## 8. 跨角色协作方式

- 能力名称：把“独立开发者 + AI 编程搭子”组织成明确分工
- 在本项目中的具体体现：由本人负责场景抽象、闭环验收、产品取舍和最终交付口径；CC 侧重架构研究、复杂度控制、生成学习资料；Codex 侧重读代码、查 drift、修 bug、补验证。
- 最核心的 1 个证据锚点：`docs/phase3—index.md` 明确这份文档“供 Claude Code、Codex 和人工审查共用”；`yyq工作文档` 进一步把三者分工写成可复用开发方法。
- 可以对齐的 JD 能力关键词：跨角色协作、owner 意识、需求对齐、技术沟通、AI 协同
- 面试官可能如何追问：你本人在其中真正做了什么；如果没有 AI 工具你是否还能讲清楚核心判断；你如何防止 AI 把项目带偏

---

# Part 3. 简历表述

- 需求洞察：基于真实生化环材科研工作流，发现科研效率瓶颈并非单点信息不足，而是文献、原始数据、阶段汇报与论文草稿分散在不同媒介中，导致“文献调研-实验推进-汇报写作”之间反复断链；据此将问题从“AI 回答科研问题”重定义为“AI 管理科研任务流”，目标是构建可追溯、可持续推进的科研闭环工作系统。
- 功能设计：参考 OpenClaw 的 File-first 思路，设计 `Control Plane / Data Plane / Trace Plane` 三平面结构，并将科研长期资产抽象为 `Concept / Task / Pack` 三类 Layer3 对象；系统以 `assets/` 为事实入口，通过控制平面协议、上下文编排、技能按需读取和 memory 写入，把 PDF 文献、CSV/图片实验数据与阶段性结论持续沉淀为可回放的研究资产，而非停留在聊天问答层。
- 评测体系：基于真实实验室研究记录构建 `180 天 / 300 轮` 科研生命周期 JSON benchmark，时间跨度 `2025-08-27` 至 `2026-02-22`，包含 `317` 个附件上传记录和 `129` 个唯一资产路径；同时围绕文献机理、实验证据、阶段汇报/写作三类闭环定义验收场景，并采用 `CC 负责架构设计与复杂度收敛 + Codex 负责代码审查与 debug + 前端真实试用` 的 AI-native 迭代方式推进产品验证。

---

# Part 4. 面试题库

## A. 项目开场题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 1. 你用一句话怎么介绍这个项目？ | 基础 | 规划文档 | 项目表达 |
| 2. 你为什么会想到做这个项目？ | 基础 | 规划文档 | 需求洞察 |
| 3. 这个项目和普通科研聊天助手最大的区别是什么？ | 基础 | 规划文档 | 产品定位 |
| 4. 为什么你坚持把它定义成 Research Agent OS，而不是 AI 工具箱？ | 中等 | 规划文档 | 抽象能力 |
| 5. 为什么项目里要强调“科研闭环”，而不是“科研效率提升”？ | 中等 | 规划文档 | 北极星定义 |
| 6. 如果面试官说这看起来还是一个带记忆的聊天系统，你会怎么反驳？ | 深挖 | 控制平面 | 差异化阐述 |
| 7. 你如何向非科研背景的面试官解释这个项目的业务价值？ | 中等 | 规划文档 | 跨领域沟通 |

## B. 场景与需求题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 8. 真实科研场景里最核心的断裂点是什么？ | 基础 | 规划文档 | 用户洞察 |
| 9. 为什么你把科研高频任务拆成文献、实验、汇报/写作三条闭环？ | 中等 | 规划文档 | 场景拆解 |
| 10. 三条闭环之间的依赖关系是什么？ | 中等 | 规划文档 | 流程设计 |
| 11. 为什么闭环 C 不是先做，而是依赖前两个闭环的产物？ | 中等 | 开发计划 | 优先级判断 |
| 12. 为什么一个 workspace 里最好收敛成同一研究主题下的三个闭环？ | 深挖 | 规划文档 | 范围定义 |
| 13. 你如何判断一轮用户请求更像 `mechanism_closure` 还是 `experiment_closure`？ | 深挖 | 控制平面 | 场景判断 |
| 14. 如果用户只是泛泛提问，不具备闭环条件，系统应该怎么处理？ | 中等 | 控制平面 | 边界意识 |

## C. 产品设计题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 15. 为什么 Layer3 只保留 `Concept / Task / Pack` 三类对象？ | 中等 | 规划文档 | 对象抽象 |
| 16. `Concept` 在科研闭环里解决的具体问题是什么？ | 基础 | 规划文档 | 信息架构 |
| 17. 为什么 `Task` 是闭环推进的核心执行单元？ | 中等 | 规划文档 | 任务建模 |
| 18. `Pack` 为什么不能简单等价于“总结”或“报告”？ | 中等 | 规划文档 | 交付物抽象 |
| 19. 为什么 Layer3 会被你称为项目的 sweet point？ | 深挖 | 规划文档 | 关键产品判断 |
| 20. 为什么 memory 不直接存原始文件，而是强调 md 化沉淀？ | 中等 | 控制平面 | 信息压缩与长期记忆 |
| 21. 为什么要把控制协议和 `memory/identity` 分开？ | 深挖 | 规划文档 | 权限与语义分层 |

## D. Agent / 架构题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 22. 为什么选择 File-first，而不是先做向量库/RAG-first？ | 中等 | 规划文档 | 架构取舍 |
| 23. OpenClaw 对你最大的启发是什么，你又改了什么？ | 中等 | 规划文档 | 技术迁移能力 |
| 24. `Control Plane / Data Plane / Trace Plane` 分别解决什么问题？ | 基础 | 规划文档 | 架构表达 |
| 25. 为什么 route 只作为工作语境，而不参与后端技能强匹配？ | 深挖 | 开发计划 | Agent 决策边界 |
| 26. 为什么要用 `SKILLS_SNAPSHOT + read_file` 做渐进式披露？ | 中等 | 代码架构 | context engineering |
| 27. `ContextOrchestrator / PromptBuilder / SkillLoader / TraceWriter` 这四个模块如何串起来？ | 中等 | 代码架构 | 系统设计 |
| 28. 为什么 bootstrap 被定义成 first-run 初始化协议，而不是模板生成器？ | 深挖 | 规划文档 | 产品语义设计 |

## E. 评测体系题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 29. 为什么这个项目不用公开 benchmark，而是自己构建 benchmark？ | 中等 | benchmark | 评测设计 |
| 30. 180 天 benchmark 是怎么构建出来的？ | 中等 | benchmark | 数据构建能力 |
| 31. 这个 benchmark 目前有哪些可量化特征？ | 基础 | benchmark | 数据理解 |
| 32. 为什么你认为三类闭环场景比单轮问答更能验证产品价值？ | 中等 | 规划文档 | 验收设计 |
| 33. 你定义过哪些评测指标，它们分别对应什么产品目标？ | 深挖 | 规划文档 | 指标设计 |
| 34. 你如何判断系统“做错了”，是读错上下文、写错对象还是证据链断裂？ | 深挖 | benchmark | 错误归因 |
| 35. 如果 benchmark 和真实代码状态不一致，你在面试里应该怎么说？ | 深挖 | 开发日志 | 证据意识 |

## F. 推进与协作题

| 问题 | 难度 | 证据来源类型 | 主要考察能力 |
|---|---|---|---|
| 36. 你为什么采用 CC / Codex / 本人三方协作，而不是自己单线程推进？ | 中等 | 开发日志 | 协作设计 |
| 37. CC 和 Codex 在这个项目里各自负责什么？ | 基础 | 开发日志 | 分工意识 |
| 38. 你如何区分“需要改 prompt”“需要改代码”“需要改架构”这三类问题？ | 深挖 | 开发日志 | debug 方法 |
| 39. 你通过前端真实试用发现过哪些典型问题？ | 中等 | 开发日志 | 用户验证 |
| 40. 为什么 trace 对这个项目不是普通日志，而是闭环审计器？ | 中等 | 控制平面 | 可解释性设计 |
| 41. 目前这个项目最真实的工程短板是什么？ | 深挖 | 代码架构 | 诚实评估 |
| 42. 如果面试官质疑你过度依赖 AI 工具，你怎么回答？ | 深挖 | 开发日志 | owner 意识 |

---

# Part 5. 证据锚点表

| 结论/能力点 | 证据类型 | 对应文档/模块 | 可量化指标 | 面试时如何一句话讲清楚 |
|---|---|---|---|---|
| 项目不是聊天助手，而是科研闭环工作系统 | 规划文档 | `yyq工作文档`、`experimental-research-openclaw-PRD.md`、`workspace-templates/AGENTS.md` | 最小闭环被明确写成 `Ingest → Plan → Close → Pack` | “我不是在优化科研问答，而是在把文献、实验、汇报三段断裂流程变成可沉淀的工作系统。” |
| Layer3 是项目 sweet point | 规划文档 | `docs/phase3—index.md`、`PRD` Layer3 小节 | Layer3 明确只有 `Concept / Task / Pack` 三类对象 | “这个项目真正的产品抽象不在聊天，而在 Layer3：用 Concept、Task、Pack 承接研究主题、验证任务和阶段交付。” |
| File-first 是主动取舍，不是能力不足 | 规划文档 | `PRD`、`phase3—index.md`、`学习笔记：workspace 语义` | 当前仓库长期资产全部落在 Markdown/JSON | “我故意不把向量库当主记忆源，因为科研更需要人类可读、可编辑、可回放的文件资产。” |
| benchmark 是重要亮点 | benchmark | `yyq_chlorite_full_lifecycle_180d_300turns.json` | `300` 轮、`179` 天、`317` 上传项、`129` 唯一路径 | “我没有拿公开题库凑评测，而是直接用真实实验室材料构了一个 180 天科研生命周期 benchmark。” |
| 三类闭环是产品验收主线 | 规划文档 | `docs/phase5.1-index.md`、`docs/phase5.1-dev-plan.md` | 闭环 A/B/C 各有最小 assets、skills、验收条件 | “我把科研需求收敛成三条闭环，每条闭环都能追到输入、技能、输出和验收项。” |
| AI-native 协作是推进亮点 | 开发日志 | `yyq工作文档`、`phase3—index.md` | 当前仓库保留多轮架构/审查文档与日志 | “我把 AI 工具当成协作角色来分工：CC 控架构，Codex 抓代码和 debug，我自己负责场景、验收和取舍。” |
| Control Plane 是合理产品判断 | 控制平面 | `workspace-templates/AGENTS.md`、`SOUL.md`、`TOOLS.md`、`BOOTSTRAP.md` | 控制平面模板至少 7 份常驻/初始化文件 | “我把协议先写进控制平面，而不是把科研规则硬编码进 if-else，这样产品行为更透明、更可迭代。” |
| Trace Plane 有明确价值 | 规划文档 + 代码架构 | `trace_collection_fix_log.md`、`context-trace-prompt-provenance-improvement-plan.md`、`backend/api/chat.py` | 当前 `chat.py` 已记录 `tool_start/tool_end`，但 provenance 仍在升级 | “trace 在这里不是普通日志，而是用来回答‘本轮读了什么、为什么写到这里、哪里还缺证据’的审计层。” |
| workspace 被重定义成业务容器 | 规划文档 | `学习笔记：workspace 语义`、`bootstrap-protocol-design.md`、`phase5.3-dev-log.md` | 已实现多 workspace runtime；bootstrap 状态机已进入 manifest | “我把 workspace 从技术目录升级成研究容器，因为科研输入是持续变化的材料流，不是一次性 prompt。” |
| assets / memory / trace 分层是合理的 | 规划文档 + 代码架构 | `phase3—index.md`、`phase5.2-dev-plan.md`、`backend/api/assets.py`、`backend/tools/write_file_tool.py` | 当前 assets 上传支持自动分类与 SHA8 去重；memory 写入支持 `source_assets` | “原始材料只进 assets，加工沉淀进 memory，运行过程写 trace，这样来源、结论和过程能彻底拆开。” |
| 现实世界验证不是停留在 demo 级 | benchmark + 开发计划 | `phase5.1-index.md`、benchmark JSON、`yyq工作文档` | benchmark 横跨 179 天；真实上传记录覆盖 PDF/CSV/图片 | “我不是只做单轮 demo，而是拿真实材料跑一个长期科研周期，看系统能不能持续推进。” |
| 当前实现与规划存在 drift，能体现你的证据意识 | 开发日志 + 代码架构 | `phase5.1-dev-plan.md`、当前 `backend/skills/registry.json`、本地测试结果 | 文档曾写 19 个 skill；当前 registry 实际 12 个；本地回归 `31/34` 通过 | “我会区分设计目标和当前实现，不把计划态当成已落地能力，这是我在面试里会主动说明的地方。” |

---

# Part 6. 风险与短板

## 6.1 目前哪些地方是已实现的

| 模块/判断 | 当前状态 | 稳妥表述建议 |
|---|---|---|
| File-first 基础架构 | 已实现主骨架 | “我已经把科研工作台的文件骨架、三层 memory、assets 与多 workspace runtime 搭起来了。” |
| Control Plane 模板 | 已实现 | “控制平面文件已拆成独立协议文件，并真实参与 prompt 组装。” |
| `ContextOrchestrator + PromptBuilder + SkillLoader + chat.py` 主链 | 已有代码落地 | “主链已经能把控制平面、Memory Map、Skills Snapshot 和对话运行串起来。” |
| assets 上传与轻量摘要 | 已实现 | “附件上传、自动分类、SHA8 去重和 quick summary 已经打通。” |
| memory 溯源注入 | 已实现工具层入口 | “基于资产生成 memory 文件时，write_file 已支持 `source_assets` 注入。” |
| benchmark 数据集文件 | 已存在并可量化 | “180 天 benchmark 数据已经构出来，当前主版本是 300 轮 JSON。” |
| 多 workspace runtime | 已实现基本运行时 | “workspace 已经从全局默认目录改成请求级 runtime 作用域。” |

## 6.2 哪些地方是设计明确但未完整落地的

| 模块/判断 | 当前真实情况 | 稳妥表述建议 |
|---|---|---|
| bootstrap runner 全流程 | `phase5.3` 日志已写明当前只完成状态流转，未执行完整初始化正文 | “bootstrap 的协议和状态机已经设计清楚，但 runner 的完整执行链还没全部闭环。” |
| trace provenance 审计 | 有基础 trace，但 `context_read / selection_reason / skipped/truncated` 等高级 provenance 仍在改进计划中 | “trace 已能记录工具调用和 prompt 载荷，但更细的上下文来源审计还在补。” |
| route 驱动上下文与 trace | `phase5-dev-log` 明确指出 route 目前只进入 metadata，尚未真正进入 ContextOrchestrator/TraceWriter | “route 作为工作语境的产品定义已明确，但代码里还没把它完全打透到上下文选择和审计层。” |
| 三条闭环端到端真实跑通 | 计划和手动验收场景定义得很清楚，但当前仓库里并不能把 3 条闭环都说成已经稳定产品化 | “我已经把三条闭环的输入、技能和验收方式定义清楚，并完成了部分链路落地，但不会说三条闭环都已完全产品化。” |
| skill 全景 | `phase5.1` 文档曾规划/记录 19 个 skill，但当前 `backend/skills/registry.json` 实际是 12 个 | “skills 体系经历过多轮重构，当前仓库保留的是更收敛的一版，不宜直接引用历史文档里的最大数字。” |
| 前端真实验证体系 | 有真实试用方法和前端页面，但没有稳定可回溯的用户实验统计指标 | “我会说我通过前端真实试用驱动迭代，而不会说已经建立了系统化的用户研究样本库。” |

## 6.3 哪些地方在面试里不宜夸大

| 不宜夸大的点 | 原因 | 更稳妥的说法 |
|---|---|---|
| “项目已完整实现 3 条科研闭环” | 目前更接近“闭环定义明确 + 部分链路落地 + 验收框架已建” | “我已经围绕三条闭环完成产品抽象和关键基础设施，并在部分场景上验证链路可行。” |
| “trace 已完整可回放每一轮上下文选择原因” | 当前 `TraceWriter` 仍较简化，改进计划单独存在 | “trace 已具备基础审计能力，但更细的 provenance 仍在补齐。” |
| “bootstrap 已经 fully automated” | 当前日志明确 runner 尚未完成初始化正文执行 | “bootstrap 协议和生命周期已经设计清楚，runner 还在继续落地。” |
| “skills 体系已完全覆盖科研闭环” | 当前 registry 仅 12 个条目，且部分历史计划 skill 未保留 | “skills 体系已经能覆盖一批核心科研场景，但还在持续收敛和替换。” |
| “所有测试都已通过” | 我本地重跑 `backend/.venv/bin/python -m unittest discover -s backend/tests -v`，结果为 `34` 项中 `31` 项通过、`3` 项报错 | “历史日志里有过全绿记录，但按当前仓库重跑仍有 3 个 chat flow 测试需要修复。” |

## 6.4 面试官可能质疑“是否过度依赖 AI 工具”的点

| 可能质疑 | 为什么会被质疑 | 更稳妥的回答方式 |
|---|---|---|
| 架构是不是 AI 帮你想的 | 文档中明确有 CC/Codex 参与 | “AI 帮我加速了架构研究和代码审查，但场景抽象、闭环定义、对象模型、验收标准和是否采纳方案，都是我自己拍板。” |
| 代码问题是不是都靠 Codex 修 | 有大量 debug 协作记录 | “我会用 Codex 做读代码和问题归因，但我自己先定义复现路径、判断是 prompt 还是代码还是架构问题，再让它协助修复。” |
| benchmark 是不是 AI 生成的伪数据 | 项目强调 AI-native | “benchmark 的底座是我真实实验室材料和长期记录，AI 参与的是整理和结构化，不是凭空编数据。” |
| 你本人是否真正理解 Agent 架构 | 文档多、AI工具多，容易显得像拼装 | “我能讲清楚为什么是 File-first、为什么是 Concept/Task/Pack、为什么 route 不是硬 Router、为什么 trace 要单独成平面，这些判断不是 AI 代替我完成的。” |
| AI 会不会让你过度设计 | 项目文档较多、规划跨度大 | “这也是我把 CC 的职责限定为复杂度收敛的原因，我会主动区分‘规划态’和‘已实现态’，避免把大图景直接包装成已落地能力。” |

## 6.5 面试时最稳妥的总口径

- 可以强调：你最强的亮点不是“我把一个 Agent 系统做全了”，而是“我把科研场景下真正值得做的产品抽象、评测口径和 AI-native 推进方式找出来了”。
- 可以强调：你最有辨识度的判断有三件事，分别是“把科研问题重定义成闭环推进”“找到 Layer3 的 sweet point”“用真实科研生命周期 benchmark 做评测”。
- 不要说满：闭环全量产品化、完整 trace provenance、bootstrap 完全自动化、全部 skills 已稳定可用。
- 最稳妥的一句话是：`这是一个已经搭起核心骨架、并用真实科研材料持续校验的 Research Agent OS，而不是一个只会聊天的科研 demo。`

