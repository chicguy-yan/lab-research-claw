可以。下面这版我会把它写成一份 **“可读、可约束、但不给实现绑死手脚”** 的 spec。

它基于你当前已经反复确认的四个核心点来写：

* Phase 3 的中枢目标是把 **上下文选择、prompt 组装、trace 落盘** 做成显式能力，而不是提前把工具、RAG、多 agent 一次做完。
* 研究用户的核心压力源就是 **阶段推进、实验闭环、机理证据链闭环、写作闭环**。
* 一次对话的 MVP 闭环是 **Ingest → Plan → Close → Pack**，并且高频场景已经对应到具体的读写策略。 
* 上下文选择必须显式，`context_read[]`、预算裁剪、trace 回放都是硬约束。

---

# Phase 3 Spec v2

## Router × Layer3 × Context × Trace

### 版本定位：**约束边界，不锁死实现**

---

## 目录

1. 这份 spec 是干什么的
2. Phase 3 的唯一目标
3. 设计原则：哪些必须定死，哪些留给实现自由
4. 架构总览：4 个核心块怎么分工
5. Router：主路由怎么设计
6. Layer3：Concept / Task / Pack 怎么接住路由结果
7. Context：上下文怎么选，怎么拼，但不做成重框架
8. Trace：怎么记，记到什么程度
9. 单轮最小闭环：一次请求如何真正结束
10. Phase 3 的边界：明确不做什么
11. 给 CC / Codex 的自由度说明
12. 验收标准：做到什么算 Phase 3 成立

---

## 1. 这份 spec 是干什么的

这不是 PRD，也不是 coding checklist。
它是 **Phase 3 的“设计边界文档”**。

它的作用只有三件事：

* 帮你自己建立脑内地图，不在 Router / Context / Trace 之间迷路
* 给 CC 和 Codex 一套共同遵守的主逻辑
* 约束方向，但不把实现写成“唯一答案”

所以这份 spec 会区分三种东西：

### A. 硬约束

这些必须守住，不能改偏。

### B. 默认建议

这些是当前最推荐的做法，但允许在不破坏主逻辑的前提下微调。

### C. 实现自由度

这些可以留给 CC / Codex 根据现有代码结构做具体取舍。

---

## 2. Phase 3 的唯一目标

Phase 3 的唯一目标不是新增更多能力，而是：

> **让一次科研请求在单 workspace、单代理下，稳定形成：
> 主意图识别 → 最少上下文选择 → prompt 组装 → write-or-skip 决策 → trace 落盘。**

这和你现有文档是对齐的。当前 Phase 3 本来就被定义成 `ContextOrchestrator`、`PromptBuilder`、`TraceWriter`、`api/traces.py` 这一组中枢模块。 

### 这句话翻译成人话就是：

* Phase 1 先把聊天跑起来
* Phase 2 先把文件、session、workspace 模板管起来
* **Phase 3 才第一次回答“为什么这轮这样答，它写到了哪里”**

---

## 3. 设计原则：哪些必须定死，哪些留给实现自由

## 3.1 必须定死的 4 件事

### 第一，顶层不要做复杂多层 Router

你已经反复讨论过，最合适的复杂度不是“再造一棵分类树”，而是 **4 个科研闭环 + 1 个兜底**。

### 第二，Layer3 必须和闭环绑定

Router 不能只是判“问题类型”，还要决定 **这轮主要打到哪个原子资产**。这也是你现在这套设计最值钱的地方。

### 第三，上下文要轻脊梁、按需扩展

不能把所有 identity / skills / memory 一次灌满。PRD 已经要求上下文选择显式、预算受控、裁剪可回放。

### 第四，Trace 要薄而硬

Trace 的目的不是写第二份大日志，而是回答：

* 本轮属于哪个闭环
* 读了哪些文件，为什么
* 主要操作了哪个原子对象
* 有没有因为信息不足而停住
  这个方向就是你们已经确认过的最终版本。 

---

## 3.2 可以留给实现自由的部分

下面这些不要在 spec 里写死：

* `_detect_intent()` 具体是纯关键词、规则表，还是一个轻量可配置映射
* `context_read` 的内部数据类命名
* `atom_decision` 是在 orchestrator 阶段生成，还是在 write 阶段补齐
* `PromptBuilder.build()` 返回字符串，还是返回 system/user 结构化对象后再转字符串
* `TraceWriter` 是直接操作 envelope 文件，还是通过一个共用 helper 间接写入

这些都是 **实现策略**，不是产品边界。

---

## 4. 架构总览：4 个核心块怎么分工

你可以把 Phase 3 想成一个很轻的四段链路：

### 1）Router

只回答：
**这轮请求属于哪个科研闭环。**

### 2）Context Orchestrator

只回答：
**为了这个闭环，本轮最少该读什么。**

### 3）Prompt Builder

只回答：
**把这些上下文按固定骨架拼成模型能用的输入。**

### 4）Trace Writer

只回答：
**把本轮为什么这么处理、最终打到了哪里，钉回文件系统。**

### 关系图

```text
User Request
   ↓
Router
   ↓
Context Orchestrator
   ↓
Prompt Builder
   ↓
LLM / Agent Response
   ↓
write-or-skip decision
   ↓
Trace Writer
```

### 一句理解

Phase 3 不是“新能力层”，而是你整个科研工作台第一次出现的 **显式中枢层**。

---

## 5. Router：主路由怎么设计

## 5.1 硬约束

顶层主路由只保留 5 个 intent：

* `stage_progress`
* `experiment_closure`
* `mechanism_closure`
* `writing_closure`
* `general_consult`

这个选择不是拍脑袋，而是直接对应 PRD 里的四大记忆压力源。

---

## 5.2 为什么不用复杂多层路由

因为你前面已经证明了一个问题：

* `file/image/pdf/csv` 是输入模态
* `needs_more_info` 是执行状态
* `graphrag` 是后续技术策略
* 它们都不该抢占“顶层业务意图”的位置

所以这版 spec 只保留：

### 主意图

决定闭环类型

### 轻标签

做补充，不升格成大路由

---

## 5.3 轻标签怎么理解

### input_tags

用于描述这轮输入材料：

* `has_asset_path`
* `has_pdf`
* `has_image`
* `has_csv`
* `has_time_range`
* `text_only`

### exec_tags

用于描述这轮主要处理方式：

* `needs_more_info`
* `pack_first`
* `task_first`
* `task_plus_pack`
* `trace_only`

### 这里的关键约束

**input_tags / exec_tags 是标签，不是新路由层。**

换句话说，CC / Codex 可以决定怎么存、怎么算、怎么命名，但不能把它们重新膨胀成“第二层 / 第三层大路由”。

---

## 5.4 Router 的默认解释

### `stage_progress`

面向阶段推进、阶段汇报、Rxx 整理、近期成果汇总。
典型输入会提到 `assets/ppt_pack/Rxx_YYYYMMDD/` 或时间范围。

### `experiment_closure`

面向实验动作、对照缺口、参数矩阵、表征能证明什么不能证明什么。

### `mechanism_closure`

面向 Co(IV) / ClO₂ 这类机理证据链审计。

### `writing_closure`

面向 R&D 目录树、中心句、主文/SI 图文策略。

### `general_consult`

兜底，不把普通咨询硬塞进长期结构。

---

## 6. Layer3：Concept / Task / Pack 怎么接住路由结果

这里是这版 spec 最重要的部分。

Router 不只是决定“怎么答”，还要决定：

> **本轮主要操作哪个原子资产。**

---

## 6.1 Concept 的角色

Concept 是 **研究主题容器**，不是每轮直接写入目标。
更准确的说法是：

> Router 决定闭环类型，Concept 决定这条闭环挂到哪条研究主线上。 

### 硬约束

* 不因为普通一轮对话自动新建 Concept
* 默认优先挂已有 Concept
* 只有明显出现新主线时，才建议新建

---

## 6.2 Task 的角色

Task 是 **最小可验证工作单元**。
实验闭环和机理闭环的主载体就是它。

### 默认用 Task 的情况

* 新的验证问题
* 新的对照建议
* 新的“能证明 / 不能证明”判断
* 新的 run / raw_data / verdict
* 新的 Missing checklist

### 硬约束

* 没证据可以建 Missing 状态 Task
* 不能为了“看起来闭环”伪造 Run

---

## 6.3 Pack 的角色

Pack 是 **交付型编排对象**。
阶段推进和写作闭环主要落它，机理闭环也会用它做证据链汇总。

### 默认用 Pack 的情况

* 阶段汇报结构
* 机理证据链整理
* 写作目录树
* 图集/图文策略
* 一段时期多个 Task 的汇总交付

---

## 6.4 Router 与 Layer3 的绑定规则

这是硬约束。

### `stage_progress` → Pack-first

默认主操作对象是 Pack。
因为它本质是“把一段时间内的 Task 重新编排成交付”。

### `experiment_closure` → Task-first

默认主操作对象是 Task。
因为它本质是“某项实验动作和证据是否闭环”。

### `mechanism_closure` → Task + Pack

既要把单条 claim/protocol/run 写进 Task，又要把整条证据链汇总成 Pack。

### `writing_closure` → Pack-first

主要是在组织已有结论，不是新建实验任务。

### `general_consult` → trace-only

默认不写 Layer3，只写 trace，必要时写 day。

---

## 7. Context：上下文怎么选，怎么拼，但不做成重框架

## 7.1 总原则

Context 采用三段式：

1. **固定脊梁**
2. **意图扩展**
3. **按需 skill 说明**

这是当前你们已经确认的最稳方案。

---

## 7.2 固定脊梁

默认建议每轮至少考虑：

* `AGENTS.md`
* `memory/identity/project.md`
* `memory/identity/context_budget.md` 仅预算使用，不注入正文

这和 PRD 的“workspace 协议优先、context 选择显式、预算可控”是一致的。 

### 硬约束

* `context_budget.md` 只用于预算，不注入 Project Context 正文。 
* 固定脊梁必须轻，不能默认把所有 identity/soul/user 文件升级成每轮必读

### 实现自由度

CC / Codex 可以决定是否把某些 workspace bootstrap 文件做成“条件固定层”，但不能把固定层做重。

---

## 7.3 意图扩展

由主意图决定往上加什么。

### `stage_progress`

默认优先考虑：

* `180d_index.md`
* time range 内 `weeks/`
* 必要时最近 `days/`
* 上一期 `stage_report`
* 关键 `PACK_stage_report_*`
  这和 PRD 的阶段汇报读写策略是对齐的。 

### `experiment_closure`

默认优先考虑：

* `lab_context.md`
* today `day`
* active `TASK_*`
* 必要时 `CONCEPT_*`
   

### `mechanism_closure`

默认优先考虑：

* `project` 判据
* `TASK_mechanism_*`
* `PACK_mechanism_*`
* 必要 paper path / 摘要
   

### `writing_closure`

默认优先考虑：

* project 北极星
* `PACK_writing_*`
* `PACK_figure_*`
* supporting `TASK_*`
   

### `general_consult`

只拿最小必要上下文，避免普通咨询被过度结构化。

---

## 7.4 按需 skill 说明

PRD 已经写得很明确：skills 可以有 snapshot，具体 skill 要按需读，不是每轮全灌。

### 硬约束

* 只有主意图命中后，才读对应 `SKILL.md`
* 不允许默认全量注入所有 skill 说明

### 实现自由度

* CC / Codex 可以决定用 registry、映射表、frontmatter 还是硬编码目录来找到 skill
* 但不能改变“按需读”这条原则

---

## 7.5 PromptBuilder 的职责边界

PromptBuilder 只负责拼接，不负责业务判断。
这点和当前 phase3-dev-plan 是一致的。

### 固定建议结构

1. 身份行
2. `## Tooling`
3. `## Workspace`
4. `## Inbound Context`
5. `# Project Context`


### 但不写死的地方

* CC / Codex 可以决定 `build()` 返回字符串还是结构化对象
* 可以决定 selected_files 的内部表示
* 可以决定截断逻辑在 orchestrator 做还是 builder 做
  只要不破坏上面这套骨架就行

---

## 8. Trace：怎么记，记到什么程度

## 8.1 总原则

Trace 是 **薄而硬的闭环审计记录**。
它服务的是回放、定位、失败归因，不是再写一层解释。

---

## 8.2 Trace 最小回答的 4 个问题

1. 本轮被判成哪个闭环
2. 读了哪些文件，为什么
3. 最后主要操作了哪个原子对象
4. 有没有因为信息不足而停在 Missing


---

## 8.3 Trace 的硬字段

### `route`

至少能看出：

* `intent`
* `input_tags`
* `exec_tags`

### `context_read`

至少包含：

* `path`
* `layer`
* `why`
* `status`
  这是 PRD 明写的最小要求。

### `budget_report`

至少能看出：

* 总预算
* 已使用
* 哪些路径被截断
* 哪些路径被跳过

### `atom_decision`

至少能看出：

* `concept_ref`
* `task_refs`
* `pack_refs`
* `write_mode`

### `missing_fields`

列缺口，不需要长篇发挥

### `output_refs`

记录本轮最终更新/产出的路径

---

## 8.4 不建议在 Phase 3 做得太重的部分

这些可以有，但不要当核心：

* 很长的 `response_summary`
* 大量主观解释
* 复杂 trace analytics
* trace 替代开发日志
* trace 替代正式 Layer3 文档

---

## 8.5 落盘位置与 done 时机

当前最合理的做法仍然是：

* trace 写入 `context_trace/{session_id}.json`
* 作为 envelope 的 `traces[]` 追加
  这与 TAD / phase3 plan 的方向一致。 

### 硬约束

`done` 必须在：

1. assistant 输出已形成
2. write-or-skip 决策已执行
3. trace 已成功写入
   之后再发。

---

## 9. 单轮最小闭环：一次请求如何真正结束

PRD 的 Runtime Loop 已经给了非常清楚的主线：
**Ingest → Plan → Close → Pack**。

把它映射到 Phase 3，你可以理解成：

### 1）Ingest

Router 判主意图，收集缺口

### 2）Plan

Context Orchestrator 选最少文件，PromptBuilder 组装输入

### 3）Close

模型产出结果后，系统决定：

* create
* update
* skip

### 4）Pack

如果这轮本来就是交付型闭环，就生成/更新 Pack；否则只更新 Task 或 trace

### 这轮结束的判据

不是“问题被完美解决”，而是：

> **这轮留下了一个可回放的状态变化。**

---

## 10. Phase 3 的边界：明确不做什么

这是硬约束。

Phase 3 不做：

* subagent / 多 agent 协作
* RAG / GraphRAG / hybrid retrieval
* tools 执行框架
* 真上传链路
* 多 workspace 激活依赖
* 前端大改
* 复杂 planner
* 自动 skill mining

原因很简单：
你现在最该追求的不是“把后面所有词都做出来”，而是先把 Phase 3 做成一个 **你能讲清楚、也能跑通的中枢**。

而且 Phase 2 的已知限制也明确写了：现在还不能依赖 agent 切换，Files API 也还不支持真正的二进制上传。

---

## 11. 给 CC / Codex 的自由度说明

这是你这次特别强调的点，我单独写出来。

### 11.1 可以自由发挥的地方

* 如何实现 intent 检测
* 如何组织数据类 / schema helper
* 如何组织 ContextOrchestrator 内部模块
* 如何组织 PromptBuilder 的输入输出形式
* 如何写 envelope 读写 helper
* 如何设计测试夹具和 gold case 结构
* 是否补充 html 图来帮助你理解

### 11.2 不应自由发挥的地方

* 不得把 skill 名重新抬成顶层业务意图
* 不得把 input_tags / exec_tags 扩展成复杂多层路由
* 不得破坏 Layer3 绑定关系
* 不得把固定上下文做得过重
* 不得把 Trace 写成超长日志
* 不得偷跑到 Phase 4 / 5

### 一句话

**实现可以自由，但主逻辑不能漂。**

---

## 12. 验收标准：做到什么算 Phase 3 成立

至少要有 5 类 gold case：

* `stage_progress`
* `experiment_closure`
* `mechanism_closure`
* `writing_closure`
* `general_consult`

每类至少验证：

### Router

* 主意图是否合理
* input_tags 是否合理
* exec_tags 是否合理

### Context

* 是否读到了该读的
* 是否没有明显过读
* 被截断/跳过是否可解释

### Layer3

* `atom_decision` 是否合理
* write-or-skip 是否符合闭环类型

### Trace

* 是否完整落盘
* `context_read[]` 是否满足最小字段
* 是否能看出本轮打到了哪个原子资产
* done 是否晚于 trace 写入

### 真正的通过标准

不是“系统看起来很聪明”，而是：

> **你能拿一轮请求，清楚说明它为什么被路由成这样、为什么读这些文件、为什么写到这个 Task/Pack/trace。**

---

## 最后一段，给你自己看的

这版 spec 的核心不是把 prompt 写死，而是把 **决策边界** 写清楚。

它给 CC / Codex 留的自由度足够大：

* 可以自己决定怎么写类
* 怎么拆 helper
* 怎么组织测试
* 怎么和现有代码拼起来

但它也把最重要的方向钉住了：

* 主路由轻
* Layer3 绑定稳
* Context 不重
* Trace 可回放

这就够了。

如果你要，我下一条可以直接把这版转成 **更像仓库文档风格的 md 成稿**，包括标题、注释风格、给 CC/Codex 的“阅读提示”。
