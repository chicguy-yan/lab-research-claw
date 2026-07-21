# Step 3：能力地图

> 从 AI 产品经理 / AI Agent 面试视角，抽取本项目体现的六项核心能力。

---

## 能力 1：场景拆解

### 证据

1. **用户访谈 → 场景分类**：从真实科研用户（"小路"人格）的访谈中提炼出两类托管模式——DDL 型（"今晚组会要交付"）和认知流动型（"被 challenge 到不自信，先搞清楚为什么"）。不是拍脑袋分的，而是从用户原话中抽象出来的。

2. **高频场景 → 读写策略映射**：PRD §4.6 定义了 7 个典型高频场景（合成 checklist、实验矩阵、机理证据链审计、表征审计、阶段汇报、写作结构、CSV 作图），每个场景都有明确的"读什么文件 → 写什么文件"策略，而不是笼统的"AI 帮你做"。

3. **180 天周期 → 时间粒度拆解**：把科研周期拆成"阶段→周→日"三级粒度，对应 Layer2 的 phases/weeks/days 目录结构。这不是技术设计驱动的，而是从"导师问你这两周做了什么"这个真实场景倒推出来的。

### 简历表达

> 基于用户访谈提炼 2 类托管模式（DDL 交付型 / 认知探索型）和 7 个高频科研场景，将 180 天实验周期拆解为"阶段→周→日"三级粒度，每个场景定义明确的上下文读写策略，驱动 ContextOrchestrator 的意图识别与文件选择逻辑。

### 面试追问点

- "你怎么确定这 7 个场景是高频的？有没有遗漏？"
  → 来自用户访谈 + 科研工作流分析，不是穷举而是覆盖 80% 高频操作。意图识别失败时降级为全量默认注入，确保不漏。
- "DDL 型和认知流动型的区别在产品层面意味着什么？"
  → 不同的上下文选择策略和输出结构。DDL 型优先产出交付物（PPT 大纲 + SOP），认知流动型优先产出原因桶 + 验证步骤。系统通过 A/B 轻量试探让用户自己选，而不是 AI 猜。
- "如果用户的需求不属于这 7 个场景怎么办？"
  → 降级为通用模式，按默认排序注入上下文。这是有意为之的——MVP 阶段不追求 100% 覆盖，而是确保核心场景体验好，边缘场景不崩。

---

## 能力 2：产品抽象

### 证据

1. **三卡落盘模型**：将科研交互的输出抽象为 Evidence/Task/Result 三张卡片，每张卡片有明确的 schema（事实区/推断区/trace 回指/assumptions）。这个抽象不是从技术角度设计的，而是从"用户拿到输出后要做什么"倒推的——Evidence 卡用于存档，Task 卡用于执行，Result 卡用于汇报。

2. **Concept/Task/Pack 三对象模型**：Layer3 的三个原子对象不是随意命名的，而是对科研工作流的精确建模——Concept（你在验证什么）驱动 Task（你怎么验证的），Task 的结果汇聚成 Pack（你验证出了什么）。这个抽象覆盖了从文献综述到实验执行到论文写作的完整链路。

3. **Control Plane / Data Plane 分离**：借鉴网络架构的控制面/数据面分离思想，将"Agent 如何工作"（SOUL/IDENTITY/AGENTS）和"Agent 知道什么"（memory 三层）解耦。这意味着可以在不改变记忆数据的情况下调整 Agent 行为，反之亦然。

### 简历表达

> 设计"Evidence→Task→Result"三卡落盘模型与 Concept/Task/Pack 三对象体系，将科研工作流抽象为可结构化、可追溯、可复用的原子资产。采用 Control Plane / Data Plane 分离架构，实现 Agent 行为规则与记忆数据的解耦，支持独立迭代。

### 面试追问点

- "三卡落盘和普通的结构化输出有什么区别？"
  → 区别在于 trace 回指。每条结论不是 AI 生成的文本，而是"带证据锚点的断言"。用户可以点击 trace 回溯到原始数据文件，这在科研场景中是刚需。
- "Concept/Task/Pack 这个抽象是怎么来的？"
  → 从科研工作流倒推。科研的本质是"提出假设→设计实验验证→汇总成果"。Concept 对应假设，Task 对应验证，Pack 对应成果。我们没有发明新概念，而是把散落在 Excel/Word/PPT 里的隐式结构显式化了。
- "Control Plane 和 Data Plane 分离在实际开发中带来了什么好处？"
  → 最直接的好处是 SOUL.md 的迭代不影响用户的记忆数据。我们在 Phase 3-5 中多次修改 SOUL.md 的证据标准，但用户的 project.md 和实验日志完全不受影响。

---

## 能力 3：技术理解

### 证据

1. **LangChain create_agent + LangGraph runtime**：选型时明确拒绝了旧版 AgentExecutor 和 langgraph.prebuilt.create_react_agent，选择 LangChain v1.x 的 create_agent（底层 LangGraph runtime）。在 v1.1.0 出现 API 消失问题时，锁定 >=1.1.1 版本并在 CLAUDE.md 中记录决策。

2. **SSE 流式架构**：POST /api/chat 返回 SSE 事件流（token/tool_start/tool_end/new_response/done），而不是 WebSocket。选择 SSE 的原因是：单向推送足够、HTTP 兼容性好、不需要维护长连接状态。done 事件在 trace 写入完成后才发送，解决了竞态条件。

3. **Envelope Schema 解决存储冲突**：Session 历史消息和 Trace 审计日志共用同一个 JSON 文件（`{"messages": [], "traces": [], "prompt": {}}`），SessionManager 和 TraceWriter 各管各的字段。这避免了两个文件的同步问题，同时保持了数据的原子性。

4. **路径安全实现**：使用 `Path.relative_to()` 做边界检查，明确禁止 `str.startswith()`（可被 Unicode 路径绕过）。这不是"加了个安全检查"，而是理解了路径穿越攻击的原理后做的防御。

5. **双文件依赖策略**：`requirements.txt`（范围约束如 `langchain>=1.1.1,<1.2`）+ `requirements.lock`（精确版本如 `langchain==1.1.3`）。开发时用范围约束保持灵活，部署时用精确锁保证可复现。

### 简历表达

> 基于 LangChain v1.x create_agent（LangGraph runtime）构建 Agent 编排引擎，SSE 流式推送实现实时工具调用展示。设计 Envelope Schema 统一 Session 消息与 Trace 审计存储，解决读写竞态。实现 Path.relative_to() 路径安全检查防御穿越攻击，双文件依赖策略（范围约束 + 精确锁）保证环境可复现。

### 面试追问点

- "为什么选 SSE 而不是 WebSocket？"
  → Agent 对话是单向推送场景（服务端→客户端），不需要双向通信。SSE 基于 HTTP，天然兼容代理/CDN/负载均衡，不需要额外的连接管理。WebSocket 在这个场景下是过度设计。
- "Envelope Schema 的 messages 和 traces 会不会有并发写入冲突？"
  → 不会。单次对话的流程是串行的：Agent 执行完 → SessionManager 写 messages → TraceWriter 写 traces → 发送 done。没有并发写入的场景。
- "create_agent 和 create_react_agent 的区别是什么？"
  → create_agent 是 LangChain v1.0 官方推荐的 Agent 构建方式，底层基于 LangGraph runtime，支持更灵活的状态管理和流式执行。create_react_agent 是 langgraph.prebuilt 的便捷函数，封装度更高但定制性差。我们需要控制 SSE 事件的精确时序，所以选择了 create_agent。

---

## 能力 4：评测设计

### 证据

1. **Golden Test 剧本**：设计了两条端到端的 Demo 剧本（DDL 型 10 轮对话 + 认知流动型 12 轮对话），每轮都有明确的输入和期望输出。这不是"写了个 demo"，而是可以作为回归测试基线的 golden test——输入同样的用户话术，系统必须产出同样结构的三卡。

2. **三类闭环测试数据集**：设计了从 1.45GB 真实科研资料中构建测试数据集的完整方法论（见用户选中的提示词文档），定义了 literature_closure / experiment_closure / writing_closure 三类闭环的测试标准，以及 context_hit_test / object_landing_test / trace_replay_test / writing_organization_test 四类能力标签。

3. **Phase 开发验收矩阵**：每个 Phase 都有明确的验收标准（docs/phase{N}-dev-log.md 中的测试结果表），包括 API 端点测试、功能集成测试、边界条件测试。不是"跑通了就行"，而是有 PASS/FAIL 状态的结构化验收。

4. **8 个单元测试文件**：覆盖 SkillLoader、Chat+WriteFile 流程、System Prompt 契约、5 个核心工具，确保核心模块的行为可预测。

### 简历表达

> 设计 2 条 Golden Test 剧本（DDL 交付型 / 认知探索型）作为端到端回归测试基线，定义三类科研闭环（文献/实验/写作）的结构化测试标准与 4 类能力标签。每个开发 Phase 配备验收矩阵（PASS/FAIL），8 个单元测试覆盖核心模块契约。

### 面试追问点

- "Golden Test 的覆盖率够吗？只有两条剧本。"
  → 两条剧本覆盖的是两种最典型的用户模式（DDL 型和探索型），不是追求覆盖率，而是追求"最小可验证集"。后续可以从三类闭环测试数据集中扩展更多样例，但 MVP 阶段这两条足够验证核心链路。
- "你怎么评估三卡落盘的质量？"
  → 目前是结构化检查：Evidence 卡是否包含 source + user_sentence，Task 卡是否区分事实区/推断区，Result 卡是否有 trace 回指。内容质量的评估依赖人工审查，这是已知的局限——LLM 输出的语义质量很难自动化评测。
- "如果 LLM 换了模型，测试还能用吗？"
  → Golden Test 验证的是输出结构（三卡 schema），不是输出内容。换模型后结构应该一致（因为 SOUL.md 的硬约束），但内容质量可能变化。这也是为什么我们把行为约束放在 Control Plane 而不是依赖模型能力。

---

## 能力 5：推进与 debug

### 证据

1. **6 个 Phase 的迭代推进**：从 Phase 1（SSE chat + Session CRUD）到 Phase 5.3（Workspace 运行时切换），每个 Phase 都有 dev-plan → dev-log → architecture.html 三件套。不是一次性设计完再开发，而是"最小可用 → 逐步增强"的迭代策略。

2. **Phase 5.3 的架构重构**：从全局单例 SessionManager 重构为 WorkspaceRuntimeRegistry，涉及 app.py、chat.py、sessions.py、files.py 等多个文件的改造。这不是"加个功能"，而是"改变系统的运行时模型"。重构过程中保持了 API 兼容性（通过 X-Workspace-Id header 或 body 字段），没有破坏已有功能。

3. **Bug 修复记入日志**：CLAUDE.md 明确要求"代码审查发现的 bug 修复需追加到对应 Phase 的 dev-log"。比如 Phase 1 Step 10 发现 Session Schema 冲突，立即修正为 Envelope Schema 并记录决策过程。

4. **已知限制显式标注**：architecture-summary.md 开头就声明"本文档描述的是目标架构，而非当前实现状态"，并用表格列出每个模块的实现状态。这不是"文档写得好"，而是"对项目状态有清醒认知"。

5. **依赖版本问题的快速定位**：LangChain v1.1.0 的 create_agent API 消失问题，通过论坛讨论定位后锁定 >=1.1.1，并在 CLAUDE.md 中记录。

### 简历表达

> 主导 6 个 Phase 的迭代开发（Phase 1→5.3），每个 Phase 配备 dev-plan/dev-log/architecture.html 三件套。Phase 5.3 完成从全局单例到 WorkspaceRuntimeRegistry 的架构重构，保持 API 兼容性。建立"Bug 修复记入日志 + 已知限制显式标注"的工程纪律。

### 面试追问点

- "Phase 5.3 重构的最大风险是什么？你怎么控制的？"
  → 最大风险是破坏已有的 chat 和 session 功能。控制方式：1) 共享资源（LLM/FetchURLTool）抽到 SharedAgentResources，不改变行为；2) workspace-scoped tools 的 CWD 绑定到 workspace 目录，隔离副作用；3) 默认 workspace 的行为与重构前完全一致，新功能通过 X-Workspace-Id header 触发。
- "你怎么决定什么时候该重构、什么时候该打补丁？"
  → Phase 5.3 的重构是因为"多 workspace"是产品核心需求，不是技术债。如果只是"代码不够优雅"，我会打补丁。但如果是"当前架构无法支撑下一个产品需求"，就必须重构。判断标准是"这个改动是为了产品还是为了代码"。
- "6 个 Phase 的开发顺序是怎么定的？"
  → 基于依赖关系。Phase 1（SSE chat）是一切的基础；Phase 2（文件系统）是记忆系统的前提；Phase 3+4（Orchestrator + Tools）是核心能力；Phase 5（Skills）是扩展性；Phase 6（前端）可以与 3-5 并行。不是按"哪个最重要"排序，而是按"哪个先做了后面才能做"排序。

---

## 能力 6：AI-native 开发协作

### 证据

1. **CLAUDE.md 驱动的开发流程**：项目有两层 CLAUDE.md——仓库级（study_ai/CLAUDE.md）和项目级（ResearchAgentPrivateWorkspace/CLAUDE.md）。项目级 CLAUDE.md 定义了 Phase 开发前置检查流程（扫描进度 → 写开发日志 → 生成架构 HTML），这意味着 AI 编码助手（Claude Code）不是"被动执行指令"，而是"按照规范自主推进开发"。

2. **给 GPT5PRO 提示词工程**：项目中有完整的提示词工程文件夹（给GPT5PRO提示词/），包含 Codex 交互提示词、Phase 规划提示词、workspace 生成提示词、数据集构建提示词等。这说明开发者不是"用 AI 写代码"，而是"设计 AI 的工作流程"。

3. **科研三闭环测试数据集构建提示词**：用户选中的文档展示了一个精心设计的提示词，将 AI 定位为"科研三闭环测试数据集构建助手"，定义了明确的任务边界、执行原则、验收条件。这是"AI-native 开发"的典型范式——不是让 AI 做所有事，而是设计 AI 的角色和约束。

4. **双人协作模式**：项目有 zly工作文档.md 和 yyq工作文档.md 两份工作进度记录，说明是多人协作开发。结合 CLAUDE.md 的规范，形成了"人定义规范 → AI 按规范执行 → 人审查结果"的协作模式。

5. **Workspace 模板即 Prompt 工程**：workspace-templates/ 中的 SOUL.md、IDENTITY.md、BOOTSTRAP.md 等文件，本质上是"给 Agent 的 Prompt 组件"。这些文件的设计过程就是 Prompt Engineering——不是写一段提示词，而是设计一套可组合、可维护的 Prompt 架构。

### 简历表达

> 建立 CLAUDE.md 驱动的 AI-native 开发流程（Phase 前置检查 → 开发日志 → 架构 HTML 自动生成），设计多层提示词工程体系（Codex 交互 / Phase 规划 / 数据集构建），实现"人定义规范 → AI 按规范执行 → 人审查结果"的协作模式。

### 面试追问点

- "CLAUDE.md 驱动开发和普通的 AI 辅助编码有什么区别？"
  → 普通的 AI 辅助编码是"我告诉 AI 写什么代码"。CLAUDE.md 驱动开发是"我定义 AI 的工作规范，AI 按规范自主推进"。区别在于：AI 不是工具，而是有明确角色和约束的协作者。CLAUDE.md 就是它的"岗位说明书"。
- "你怎么保证 AI 生成的代码质量？"
  → 三层保障：1) CLAUDE.md 定义代码规范（Pydantic v2、resolve_safe_path、双文件依赖等）；2) 每个 Phase 有验收矩阵；3) 人工 code review。AI 生成的代码不是直接合入的，而是经过规范约束 + 验收测试 + 人工审查的。
- "提示词工程在这个项目中的 ROI 是什么？"
  → 最大的 ROI 是"可复现性"。比如科研三闭环测试数据集的构建提示词，定义了完整的执行步骤和验收条件。换一个人（或换一个 AI）来执行，只要按照这个提示词，产出的质量是可预期的。这比"口头交代任务"的效率高一个数量级。
