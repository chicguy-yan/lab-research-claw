# Step 5：面试题库

---

## 一、基础题（20 题）

### B01. 一句话介绍这个项目是做什么的？
- 考察能力：产品抽象
- 项目证据：PRD §一、项目最终实现效果.md
- 避坑：不要说"科研版 ChatGPT"。要强调"本地化工作台 + 文件即记忆 + 证据链交付"三个差异点。

### B02. 你的目标用户是谁？他们的核心痛点是什么？
- 考察能力：场景拆解
- 项目证据：PRD §4.1 记忆压力源、Demo 剧本中的用户人格设定
- 避坑：不要泛泛说"科研人员"。要具体到"材料/化学/环境等实验学科的硕博生"，痛点要落到"180 天记忆断裂 + 证据链脱钩 + 被 challenge 后缺排查框架"。

### B03. 项目的技术栈是什么？为什么选这些？
- 考察能力：技术理解
- 项目证据：PRD §一.2、architecture-summary.md 附录 A
- 避坑：不要只列技术名词。要说清选型理由——FastAPI（异步 SSE）、LangChain create_agent（LangGraph runtime，非旧版 AgentExecutor）、本地文件系统（非向量数据库，因为科研用户需要可读可改）。

### B04. 为什么用文件系统而不是向量数据库做记忆？
- 考察能力：产品抽象 + 技术理解
- 项目证据：PRD §一 File-first Memory 定位、SOUL.md 证据标准
- 避坑：不要说"向量数据库不好"。要说"科研场景需要记忆可读、可改、可追溯，向量数据库是黑盒，用户无法直接查看和修正 AI 记住了什么"。

### B05. 三层记忆（Layer1/2/3）分别是什么？为什么要分三层？
- 考察能力：产品抽象
- 项目证据：PRD §4.2、architecture-summary.md §2.3
- 避坑：不要只描述目录结构。要说清分层逻辑——按"可变性"分层（L1 几乎不变 / L2 中频更新 / L3 高频创建），这决定了 ContextOrchestrator 的注入优先级。

### B06. Concept、Task、Pack 三个对象分别是什么？
- 考察能力：产品抽象
- 项目证据：PRD §4.2 Layer3、项目最终实现效果.md 的落盘示例
- 避坑：不要抽象地解释。用具体例子——Concept 是"Co(IV) 的存在性验证"，Task 是"PMSO 探针实验（含 Claim + Protocol + 3 次 Run）"，Pack 是"第 6 次阶段汇报 PPT 素材包"。

### B07. 什么是"三卡落盘"？
- 考察能力：产品抽象
- 项目证据：项目最终实现效果.md 的 Evidence/Task/Result 卡示例
- 避坑：不要只说"结构化输出"。关键区别是每张卡都有 trace 回指——Evidence 卡锚定用户原话和文件路径，Task 卡区分事实区/推断区，Result 卡的每条结论可追溯到证据来源。

### B08. Control Plane 和 Data Plane 的区别是什么？
- 考察能力：技术理解 + 产品抽象
- 项目证据：PRD §4.4.0、architecture-summary.md §5.1
- 避坑：不要只说"一个管规则一个管数据"。要说清优先级——Control Plane（SOUL.md 等）优先级最高，与 Data Plane（memory 三层）冲突时以 Control Plane 为准。这是为了确保 LLM 行为被硬约束控制。

### B09. ContextOrchestrator 做了什么？
- 考察能力：技术理解
- 项目证据：graph/context_orchestrator.py、PRD §4.4.3
- 避坑：不要说"选文件注入 Prompt"就完了。要说清选择逻辑——意图识别（关键词匹配）→ 按"稳定→变化→本轮相关"排序 → 降级策略（识别失败时全量默认注入）→ trace 记录选择原因。

### B10. PromptBuilder 的 System Prompt 结构是什么？
- 考察能力：技术理解
- 项目证据：graph/prompt_builder.py、architecture-summary.md §5.3
- 避坑：不要笼统说"拼接 Prompt"。要能说出 7 个 Block 的顺序和设计理由——Identity → Tooling → Workspace → Metadata → Control Plane → Skills Snapshot → Memory Map，稳定信息在前、变化信息在后。

### B11. 为什么选 SSE 而不是 WebSocket？
- 考察能力：技术理解
- 项目证据：PRD §5.1、api/chat.py
- 避坑：不要说"SSE 更简单"。要说"Agent 对话是单向推送场景，SSE 基于 HTTP 天然兼容代理/CDN/负载均衡，不需要维护长连接状态。WebSocket 在这个场景下是过度设计"。

### B12. SSE 事件流有哪些事件类型？
- 考察能力：技术理解
- 项目证据：architecture-summary.md §3.2
- 避坑：要能列出 token/tool_start/tool_end/new_response/done/error，并说清 done 事件在 trace 写入完成后才发送（解决竞态条件）。

### B13. Skills 系统是怎么工作的？
- 考察能力：技术理解 + 产品抽象
- 项目证据：PRD §三、graph/skill_loader.py
- 避坑：不要说"调用预置函数"。Skill 是 Markdown 说明书，不是代码。渐进式披露——菜单摘要注入 Prompt，Agent 自主决策是否 read_file 读取完整说明书，然后按说明书调用核心工具执行。

### B14. 项目有哪些核心工具？
- 考察能力：技术理解
- 项目证据：tools/ 目录、PRD §二
- 避坑：5 个已实现的工具（terminal/python_repl/read_file/write_file/fetch_url），不要把 PRD 中规划但未实现的 search_knowledge_base 和 web_search 说成已完成。

### B15. 路径安全是怎么做的？
- 考察能力：技术理解
- 项目证据：graph/path_utils.py、CLAUDE.md 代码规范
- 避坑：要说清用 `Path.relative_to()` 做边界检查，明确禁止 `str.startswith()`（可被 Unicode 路径绕过）。不要只说"做了路径检查"。

### B16. Session 和 Trace 的存储关系是什么？
- 考察能力：技术理解
- 项目证据：architecture-summary.md §6.2（已解决）
- 避坑：同一个文件，Envelope Schema `{"messages": [], "traces": [], "prompt": {}}`。SessionManager 管 messages，TraceWriter 管 traces，互不污染。不要说成两个文件。

### B17. 项目经历了几个 Phase？每个 Phase 做了什么？
- 考察能力：推进与 debug
- 项目证据：CLAUDE.md Phase 状态表
- 避坑：要能清晰说出依赖关系——Phase 1（SSE chat 基础）→ Phase 2（文件系统 + 路径安全）→ Phase 3+4（Orchestrator + Tools）→ Phase 5（Skills）→ Phase 5.3（Workspace 隔离）。不是按重要性排序，是按依赖关系排序。

### B18. Phase 5.3 做了什么？为什么需要这次重构？
- 考察能力：推进与 debug
- 项目证据：docs/phase5.3-dev-plan.md、runtime/workspace_registry.py
- 避坑：不要说"优化代码结构"。要说"产品需要多 workspace 支持（科研用户同时推进多个课题），全局单例 SessionManager 无法隔离不同课题的记忆和工具，所以重构为 WorkspaceRuntimeRegistry"。

### B19. 你们的开发流程是什么样的？
- 考察能力：推进与 debug + AI-native 协作
- 项目证据：CLAUDE.md Phase 开发前置检查流程
- 避坑：不要只说"敏捷开发"。要说清 CLAUDE.md 驱动的流程——每个 Phase 必须执行"扫描进度 → 写开发日志 → 生成架构 HTML"三步，AI 编码助手按规范自主推进。

### B20. 项目目前的状态是什么？还有什么没做完？
- 考察能力：推进与 debug
- 项目证据：CLAUDE.md Phase 状态表、architecture-summary.md 实现状态声明
- 避坑：诚实说 Phase 6（前端三栏 UI）未完成，RAG 检索（KnowledgeIndexer）未实现，web_search 工具未实现。不要把目标态说成现状。

---

## 二、中等深挖题（15 题）

### M01. 你怎么从用户访谈中提炼出"DDL 型"和"认知流动型"两种模式的？
- 考察能力：场景拆解
- 项目证据：项目最终实现效果.md 的场景设定、Demo 剧本
- 避坑：不要说"我觉得用户有两种需求"。要说清访谈中的关键发现——用户说"我要先活过今晚"（DDL 型）vs "我想知道到底是哪种问题"（认知流动型），这两句话背后是完全不同的上下文选择策略和输出结构。

### M02. ContextOrchestrator 的意图识别如果失败了怎么办？
- 考察能力：技术理解 + 评测设计
- 项目证据：architecture-summary.md §5.2 降级策略
- 避坑：不要说"不会失败"。要说清降级策略——关键词匹配失败时，使用默认全量注入顺序（workspace → skills → L1 → L2 → L3 → uploads）。这是有意为之的安全降级，确保不漏关键上下文。后续可引入 LLM 意图分类替代关键词匹配。

### M03. 如果用户的记忆文件有几百个，上下文窗口装不下怎么办？
- 考察能力：技术理解
- 项目证据：PRD §4.4.4 裁剪与预算、memory/identity/context_budget.md
- 避坑：不要说"用 RAG 检索"。要说清裁剪策略——单文件 20,000 字符上限（超出追加 truncated）、总预算按层分配（workspace 固定 → L1 固定 → L2 近邻 → L3 Top-K → uploads 最小化）、任何裁剪都记录到 trace（why + policy）。

### M04. "事实区"和"推断区"的分离在技术上是怎么实现的？
- 考察能力：技术理解 + 产品抽象
- 项目证据：SOUL.md 证据标准、项目最终实现效果.md 的 Result 卡示例
- 避坑：坦诚说这主要靠 Prompt 约束（SOUL.md 的硬规则），不是靠代码逻辑。SOUL.md 要求"所有结论必须带证据类型 + 数据路径 + 对照 + 判据"，LLM 在这个约束下会自然区分事实和推断。但 LLM 的遵循率不是 100%，这是已知局限。

### M05. Workspace 隔离的粒度是什么？共享什么、隔离什么？
- 考察能力：技术理解
- 项目证据：runtime/workspace_registry.py 的 SharedAgentResources + WorkspaceRuntime
- 避坑：要说清共享/隔离边界——共享 LLM 实例和 FetchURLTool（无状态），隔离 SessionManager、terminal/python_repl/read_file/write_file（CWD 绑定到 workspace 目录）。共享 LLM 是因为它无状态且创建成本高，隔离工具是因为文件操作必须限定在 workspace 范围内。

### M06. 你怎么保证 SOUL.md 的约束真的被 LLM 遵循了？
- 考察能力：评测设计
- 项目证据：SOUL.md、tests/test_system_prompt_contract.py
- 避坑：坦诚说没有 100% 保证。当前的保障是：1) SOUL.md 在 Prompt 最高优先级位置注入；2) System Prompt 契约测试验证结构完整性；3) Golden Test 剧本验证输出结构。但语义层面的遵循率需要人工审查，这是 LLM 产品的通用挑战。

### M07. 三类科研闭环（文献/实验/写作）是怎么定义的？
- 考察能力：场景拆解 + 评测设计
- 项目证据：skill_mapping_for_research_loops.md、数据集构建提示词
- 避坑：不要只列名字。要说清每类闭环的链路——文献闭环（主题文献→研究问题→假设/证据链）、实验闭环（实验目标→SOP/Protocol→原始数据→结果解释→下一步）、写作闭环（阶段目标→结果汇总→汇报/Paper 结构）。

### M08. 如果让你重新设计，你会改什么？
- 考察能力：产品抽象 + 推进与 debug
- 项目证据：architecture-summary.md §6 风险分析
- 避坑：不要说"没什么要改的"。可以说的改进点：1) Bootstrap 冷启动体验需要优化（当前依赖用户填写 project.md）；2) 意图识别应该从关键词匹配升级为 LLM 分类；3) 前端应该更早启动开发，与后端并行。

### M09. 你怎么处理 LLM 调用失败的情况？
- 考察能力：技术理解
- 项目证据：architecture-summary.md §6.7
- 避坑：坦诚说 MVP 阶段的降级策略比较简单——重试 2 次（间隔 1s/3s），超时 60s，失败后发送 SSE error 事件。没有做复杂的熔断或降级到小模型。这是有意的取舍——MVP 阶段优先保证核心链路跑通。

### M10. Trace 回放在产品层面的价值是什么？
- 考察能力：产品抽象
- 项目证据：PRD §4.3、项目最终实现效果.md
- 避坑：不要说"方便 debug"。Trace 的产品价值是建立用户信任——科研用户需要理解"AI 为什么给出这个建议"才敢用它的输出去面对导师。Trace 让用户看到"系统读了你的 project.md 判据 + 上周实验日志 + XRD csv，基于这些得出结论"，而不是"AI 说的"。

### M11. Skills 系统为什么用 Markdown 说明书而不是代码插件？
- 考察能力：产品抽象 + 技术理解
- 项目证据：PRD §三 Skills 范式
- 避坑：不要只说"更灵活"。三个具体原因：1) 用户（科研人员）可以自己写 Skill，不需要编程能力；2) Skill 的行为可以被审计（因为就是一段文本）；3) Agent 的能力扩展不需要改代码、不需要重启服务。这是 Anthropic Agent Skills 范式的实现。

### M12. 你怎么决定哪些信息放 Control Plane、哪些放 Data Plane？
- 考察能力：产品抽象
- 项目证据：PRD §4.4.0
- 避坑：判断标准是"可变性 + 权威性"。Control Plane 放的是低频变更、最高权威的硬协议（Agent 如何工作）。Data Plane 放的是允许缓慢演进的事实数据（Agent 知道什么）。如果一条信息"与任何记忆冲突时应该以它为准"，那它属于 Control Plane。

### M13. 双文件依赖策略（requirements.txt + requirements.lock）解决什么问题？
- 考察能力：技术理解
- 项目证据：CLAUDE.md 代码规范、backend/requirements.txt + requirements.lock
- 避坑：不要只说"锁版本"。要说清两个文件的分工——requirements.txt 用范围约束（如 `langchain>=1.1.1,<1.2`）保证开发灵活性，requirements.lock 用精确版本（如 `langchain==1.1.3`）保证部署可复现。解决的是"在我机器上能跑"问题。

### M14. 你怎么处理 LangChain v1.1.0 的 create_agent API 消失问题？
- 考察能力：推进与 debug
- 项目证据：architecture-summary.md §6.1
- 避坑：要说清定位过程——通过 LangChain 论坛发现 v1.1.0 的 `__init__.py` 导出缺失，锁定 >=1.1.1 版本，并在 CLAUDE.md 中记录决策。不要说"换了个版本就好了"，要体现排查过程。

### M15. 这个项目和市面上的 AI 科研助手（如 Elicit、Consensus）有什么区别？
- 考察能力：产品抽象
- 项目证据：PRD §一 核心差异化定位
- 避坑：不要贬低竞品。区别在定位——Elicit/Consensus 聚焦文献检索和摘要，是"搜索增强"产品。OpenClaw 聚焦实验全周期管理，是"工作台"产品。它们解决的是"找到信息"，我们解决的是"把信息组织成可交付的东西"。而且我们是本地化部署，数据不出本地。

---

## 三、高压挑战题（10 题）

### H01. 你这个项目本质上不就是给 ChatGPT 套了个文件系统吗？
- 考察能力：产品抽象
- 项目证据：ContextOrchestrator + PromptBuilder + TraceWriter 的完整链路
- 避坑：不要急着否认。承认底层确实是 LLM，但关键差异在于"确定性外壳"——ContextOrchestrator 的智能上下文选择、PromptBuilder 的 7-Block 结构化拼接、TraceWriter 的全链路审计，这些不是"套壳"，而是把不确定的 LLM 行为包进确定的工程系统里。类比：数据库引擎也是"套了个文件系统"，但 B+ 树索引和事务管理才是价值所在。

### H02. 前端都没做完，你怎么证明这个产品有用？
- 考察能力：推进与 debug + 评测设计
- 项目证据：Golden Test 剧本、Phase 验收矩阵、8 个单元测试
- 避坑：不要回避。坦诚说前端未完成是事实，但后端的核心链路已经通过 API 测试和 Golden Test 验证。两条 Demo 剧本证明了"三卡落盘"的可行性，Phase 验收矩阵证明了每个模块的功能完整性。前端是体验层，不是价值层——价值在于记忆架构和证据链机制，这些已经验证了。

### H03. 三层记忆听起来很复杂，用户真的需要这么复杂的系统吗？
- 考察能力：场景拆解 + 产品抽象
- 项目证据：PRD §4.1 记忆压力源
- 避坑：不要为复杂性辩护。要说清"复杂性对用户是透明的"——用户不需要理解三层架构，他们只需要正常对话。ContextOrchestrator 自动选择注入哪些文件，用户感知到的是"系统记住了我 3 个月前的实验"，而不是"系统有三层记忆"。复杂性在后端，简单性在前端。

### H04. 你的意图识别只是关键词匹配，这也太简陋了吧？
- 考察能力：技术理解 + 推进与 debug
- 项目证据：architecture-summary.md §6.3
- 避坑：不要否认简陋。要说清这是有意的 MVP 决策——关键词匹配覆盖 80% 高频场景，失败时安全降级为全量注入。在 MVP 阶段，"不出错"比"更智能"重要。后续迭代可以引入 LLM 意图分类，但前提是先验证核心链路的价值。过早引入复杂的意图识别是过度工程。

### H05. 你说"证据回指"，但 LLM 生成的 trace 本身可能是错的，怎么办？
- 考察能力：评测设计 + 产品抽象
- 项目证据：TraceWriter 的实现、SOUL.md 的证据标准
- 避坑：要区分两种 trace——系统级 trace（ContextOrchestrator 读了哪些文件、工具调用了什么）是确定性的，由代码生成，不会错。LLM 级 trace（Result 卡中的证据回指）确实可能出错，因为依赖 LLM 的指令遵循。当前的缓解是 SOUL.md 的硬约束 + Golden Test 验证结构，但语义准确性需要人工审查。这是诚实的局限。

### H06. 180 天的记忆文件会越来越多，系统性能怎么保证？
- 考察能力：技术理解
- 项目证据：PRD §4.4.4 裁剪与预算、context_budget.md
- 避坑：不要说"文件系统很快"。要说清两层保障：1) ContextOrchestrator 不是全量扫描，而是按意图选择性读取（阶段汇报只读 time_range 内的文件）；2) context_budget.md 定义了按层分配的预算策略，确保总注入量可控。但如果文件数量达到数千级别，目录扫描确实会变慢，这是后续需要优化的点（可以加索引文件或缓存）。

### H07. 你这个项目只有你和另一个人做，怎么证明你的个人贡献？
- 考察能力：推进与 debug
- 项目证据：zly工作文档.md、CLAUDE.md、Phase dev-log
- 避坑：不要模糊化。要能清晰说出自己负责的部分——比如"我负责产品设计（PRD/TAD）+ 后端架构设计 + Phase 开发流程定义 + Prompt 工程（SOUL.md/IDENTITY.md 等 workspace 模板）"，用 dev-log 中的具体 Step 作为证据。

### H08. 如果导师说"我不信 AI 的输出"，你的产品怎么应对？
- 考察能力：产品抽象
- 项目证据：Trace Plane 设计、三卡落盘的事实/推断分离
- 避坑：不要说"AI 很准"。要说"我们的设计就是基于'不信 AI'这个前提的"——三卡落盘强制区分事实和推断，每条结论挂证据回指，Trace 可以回放完整决策过程。用户拿着 Result 卡去面对导师时，说的不是"AI 说的"，而是"基于这个 csv 数据和这次实验记录，得出的结论是..."。系统的价值不是"替你思考"，而是"帮你组织证据"。

### H09. 你的 Skills 系统和 MCP（Model Context Protocol）有什么区别？
- 考察能力：技术理解 + 产品抽象
- 项目证据：PRD §三 Skills 范式
- 避坑：不要说"差不多"。MCP 是工具协议（定义 AI 如何调用外部工具），Skills 是指令协议（定义 AI 如何组合已有工具完成复杂任务）。Skill 是 Markdown 说明书，教 Agent "先 read_file 读数据，再 python_repl 画图，最后 write_file 保存"。MCP 解决的是"连接什么工具"，Skills 解决的是"怎么用这些工具完成科研任务"。

### H10. 这个项目对你申请 AI PM 岗位的价值是什么？你从中学到了什么？
- 考察能力：全局反思
- 项目证据：整个项目
- 避坑：不要说"学到了很多技术"。要从 PM 视角总结：1) 学会了从用户痛点倒推产品抽象（三卡落盘不是技术设计，是从"用户拿到输出后要做什么"倒推的）；2) 学会了在 AI 产品中平衡"智能"和"确定性"（LLM 越智能越不可控，所以需要 Control Plane 的硬约束）；3) 学会了 AI-native 的开发协作模式（CLAUDE.md 驱动开发，人定义规范、AI 按规范执行）。
