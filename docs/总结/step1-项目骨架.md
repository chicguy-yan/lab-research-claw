# Step 1：项目骨架

## 一句话定义

Experimental-Research-OpenClaw 是一个面向实验学科的本地化科研 AI Agent 系统，通过"文件即记忆 + 技能即插件 + 全链路可追溯"三大机制，将 180 天实验周期中的文献、实验、机理验证、阶段汇报等高频场景编排为可闭环、可回放、可沉淀的工作流。

## 它解决的真实问题

科研人员（尤其是硕博生）在长周期实验中面临三重压力：

1. **记忆断裂**：实验跨度 180 天，阶段汇报 10+ 次，每次都要从头翻记录、找数据、拼 PPT。导师追问"上次那个对照做了没"时答不上来。
2. **证据链断裂**：结论和数据之间缺乏可追溯的锚点。"Ce 加多了峰不稳定"这句话背后到底对应哪个 csv、哪张照片、哪次实验条件？说不清就会被 challenge。
3. **认知负担过重**：被导师 challenge 后容易陷入自我怀疑，分不清"是我不行"还是"变量没控好"。缺乏结构化的排查框架把不确定性收敛为可验证的步骤。

以上三个痛点来自项目中的真实用户访谈（见 `项目最终实现效果.md` 中的"小路"人格设定），并直接驱动了产品的核心设计决策。

## 与普通 AI 助手的核心区别

| 维度 | 普通 AI 助手 | OpenClaw |
|------|-------------|----------|
| 记忆 | 单次对话窗口，关掉就忘 | 三层文件记忆（Identity/Timeline/AtomNotes），180 天持久化 |
| 证据 | 回答基于训练数据，无法引用用户的实验文件 | 每条结论挂 trace 回指（文件路径 + 用户原话 + 证据类型） |
| 透明度 | Prompt 拼接是黑盒 | 全链路可回放：读了什么文件、为什么读、有没有被裁剪 |
| 技能 | 固定能力，不可扩展 | Skills 即 Markdown 说明书，拖入文件夹即用，Agent 自主决策调用 |
| 交付物 | 纯文本回复 | 结构化三卡落盘（Evidence/Task/Result），事实区与推断区分离 |

## 最核心的产品抽象

**"三卡落盘"模型**（见 `项目最终实现效果.md` 的 golden test 剧本）：

- **Evidence 卡**（`memory/evidence/EVD-*.md`）：证据锚点——用户原话 + 文件路径 + 数据摘要，只记录事实
- **Task 卡**（`memory/tasks/TSK-*.md`）：任务结构——Claim + Protocol + Run + 事实区/推断区，把模糊需求拆成可执行步骤
- **Result 卡**（`memory/results/RES-*.md`）：交付物——PPT 大纲/SOP/证据链，每条结论挂 trace 回指和 assumptions 声明

本质：**把不确定的 LLM 行为包进确定的"证据采集 → 结构化输出 → 可追溯落盘"外壳里**。

---

## 100 字摘要

面向实验学科的本地化科研 AI Agent。三层文件记忆（Identity/Timeline/AtomNotes）管理 180 天实验周期；ContextOrchestrator 智能选择上下文，PromptBuilder 7-Block 结构化拼接，TraceWriter 全链路审计；输出为 Evidence→Task→Result 三卡闭环，事实与推断强制分离，每条结论挂证据回指。Skills 系统支持 Markdown 说明书即插即用。

---

## 3 个最关键关键词

1. **File-first Memory**（文件即记忆）—— 三层 Markdown 文件系统替代向量数据库，人类可读可改可追溯
2. **Evidence-traced Delivery**（证据链交付）—— 每条输出挂 trace 回指，事实与推断强制分离
3. **Skills-as-Instructions**（技能即说明书）—— Skill 是教 Agent 如何用工具的 Markdown，非预置函数，拖入即用

---

## 3 个最大亮点

### 亮点 1：三层记忆架构解决长周期科研的"记忆断裂"

不是简单的 RAG 检索，而是按"可变性"分层：
- Layer1（Identity）：项目北极星、判据、实验室约束 —— 几乎不变，每轮必读
- Layer2（Timeline）：180 天总览 → 阶段 → 周 → 日 —— 中频更新，按意图选择性注入
- Layer3（AtomNotes）：Concept/Task/Pack 原子资产 —— 高频创建，按相关性 Top-K 注入

ContextOrchestrator（`graph/context_orchestrator.py`）按"稳定→变化→本轮相关"的优先级自动选择注入哪些文件，并在 trace 的 `context_read[]` 中记录每个文件的选择原因和裁剪状态。系统能在第 150 天的对话中自动关联第 30 天的实验记录，而不需要用户手动翻找。

### 亮点 2：全链路透明可回放

从 Prompt 拼接到工具调用到记忆读写，每一步都有 trace（`context_trace/{session_id}.json`）：
- `context_read[]`：本轮读了哪些文件、为什么读、是否被裁剪（path/layer/why/status）
- `tool_calls[]`：调用了什么工具、输入输出是什么
- `prompt` 元数据：System Prompt 的 7-Block 完整结构

这不是"为了合规做的日志"，而是产品核心功能。Demo 剧本中明确设计了"证据回指"机制——用户拿着 Result 卡去面对导师时，每条结论后面都挂着 `(trace:EVD-20260204-001)` 这样的锚点，可以追溯到原始数据文件和用户原话。

### 亮点 3：从"回答问题"到"工作台交付"的产品范式转变

OpenClaw 的交互模式不是 Q&A，而是"工作台"：
- 输入不是"问题"，而是"证据材料"（实验本照片、XRD csv、文献 pdf、口头描述）
- 输出不是"回答"，而是"结构化交付物"（PPT 大纲 + 每页中心句、实验 SOP + 验收标准、机理证据链 + 事实/推断分离）
- 过程不是"一次性生成"，而是"A/B 轻量试探 → 证据锚点采集 → 三卡落盘 → 沉淀为可复用技能"

这个范式转变体现在 Demo 剧本的设计中：系统不装读心（只问一次 A/B 选择），不急着解释（先把可上台的输出做出来），每条建议有 trace 回指（不是"AI 说的"，是"数据说的"）。

---

## 3 个最大风险

### 风险 1：冷启动成本高，用户可能在 Bootstrap 阶段流失

三层记忆系统的威力建立在"Identity 层被正确填充"的前提上。如果 `project.md`（项目北极星、判据、术语表）没有被认真填写，后续所有的上下文选择和证据链都会失准。

**现状**：设计了 `BOOTSTRAP.md` 协议（`workspace-templates/BOOTSTRAP.md`）引导首次初始化——识别语义边界、引导初始 assets、生成最小 memory 骨架。协议采用"轻量试探"策略（A/B 选择而非开放式提问）。
**局限**：Bootstrap 协议的实际完成率未经真实用户验证。

### 风险 2：前端未完成，产品体验无法闭环验证

Phase 1-5.3 后端已完成（92 个 Python 文件、8 个单元测试、5 个 Phase 的 dev-log），但 Phase 6（前端三栏 UI）尚未开发。

**影响**：三层记忆的"可视化浏览"（MemoryPanel）、Trace 的"点击回放"（ThoughtChain）、Skills 的"面板选择"等核心体验无法展示。当前只能通过 API 调用（curl/httpie）验证功能。
**缓解**：有基础的 `frontend/index.html` 三栏原型（workspace 选择器 + chat + file viewer），Phase 6 的 dev-plan 已就绪。

### 风险 3：LLM 能力边界导致"三卡落盘"质量不稳定

三卡落盘的质量高度依赖 LLM 的指令遵循能力：
- Evidence 卡的"证据锚点"提取准确率取决于用户输入的模糊程度
- Task 卡的"Protocol"生成需要领域知识，通用模型可能给出不够专业的实验方案
- Result 卡的"事实区 vs 推断区"分离需要精确的逻辑推理

**现状**：通过 SOUL.md 中的硬约束（"所有结论必须带证据类型 + 数据路径 + 对照 + 判据"）和 PromptBuilder 的 7-Block 结构化注入来约束 LLM 行为。`tests/test_system_prompt_contract.py` 验证 Prompt 结构完整性。
**局限**：设计了两条 golden test 剧本（DDL 型 10 轮 + 认知流动型 12 轮）作为回归测试基线，但覆盖面有限，语义层面的输出质量仍需人工审查。
