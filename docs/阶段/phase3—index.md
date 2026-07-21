/Users/fenke/projects/study_ai/2-未完成项目存档/zly 规划-0219/ResearchAgentPrivateWorkspace/docs/phase3-dev-plan.md这个文件：1。每次 systemprompt 必须有控制平面的六大 md 笔记 2。上下文拼接其他就是要有一个告诉 llm 三层 memory 中分别有哪些文件的路径，方便让通用 agent 自己决定读取哪些上下文。3。memory 都是 md 文件是为了节省上下文的，中间一定要带 基于assets对应文件生成的那些文件的路径，方便用户需要溯源的时候可以溯源

* Phase 3 的核心模块仍然是 `ContextOrchestrator`、`PromptBuilder`、`TraceWriter`、`api/traces.py`，目标是把上下文选择、Prompt 组装和审计落盘做成显式能力。 
* Workspace 控制层和 memory/identity 在语义上是分开的。前者定义 Agent 如何工作，优先级最高；后者存放长期稳定事实，可由模型提议写入、后端落盘。 
* assets 是原始材料层，memory 是 md 化沉淀层，Layer3 则是 Concept / Task / Pack 三类原子资产。 
* 一次对话的 MVP 闭环仍然是 Ingest → Plan → Close → Pack，只是这一版不把“意图识别”实现成过重的独立 Router，而把它降级成控制平面下的软约束判断。

---

# `docs/phase3-spec.md`

## Experimental-Research-OpenClaw

## Phase 3 Spec

## 主题：Control Plane × Assets × Memory × Trace

### 文档状态

Frozen for implementation guidance

### 文档用途

这份文档用于约束 Phase 3 的主逻辑与边界，供 Claude Code、Codex 和人工审查共用。
它不是 PRD，不是 TAD，也不是逐文件 coding checklist。

---

## 目录

1. 目标与边界
2. 核心设计判断
3. 三个平面：Control Plane / Data Plane / Trace Plane
4. 关键对象分工
5. Phase 3 的运行闭环
6. “意图识别”在本阶段的定义
7. assets 与 memory 的关系
8. memory 写入规则
9. context 选择与 prompt 组装
10. trace 记录规则
11. 实现建议
12. 验收标准
13. 明确不做的内容

---

## 1. 目标与边界

### 1.1 Phase 3 的唯一目标

Phase 3 的唯一目标是：

**在 workspace 控制平面的软约束下，把用户请求和 assets 转成可追溯的 memory 更新或 skip 决策，并把全过程写入 trace。**

这意味着 Phase 3 解决的不是“更多功能”，而是三件事：

* 本轮该读什么
* 本轮该写什么
* 本轮为什么这样做

### 1.2 Phase 3 的成功标准

Phase 3 成立，不以“模型更聪明”为判断标准，而以以下问题能否清楚回答为标准：

* 为什么这轮读了这些文件
* 为什么这轮主要更新的是 Task / Pack / Timeline，或者为什么选择 skip
* 为什么这轮的输出可以被回放和审计
* 为什么这一轮没有依赖 RAG、复杂工具编排或多 agent 也能形成闭环

---

## 2. 核心设计判断

### 2.1 本阶段不把“意图识别”做成重型 Router

本阶段不追求多层 Router 树，也不把 `file/image/graphrag/additional` 这类混层概念做成中心模块。

本阶段对“意图”的定义是：

**LLM 在控制平面软约束下，对当前工作重心形成的轻量判断。**

它的作用只有两个：

* 帮助决定该优先读哪些上下文
* 帮助决定该优先写哪类 memory 对象，或只写 trace

### 2.2 本阶段优先做“记忆沉淀中枢”

Phase 3 更适合被理解为一个 **Memory Compiler**：

输入：

* 用户请求
* assets
* 现有 memory
* workspace 控制平面

输出：

* context 选择
* prompt 组装
* memory 写入或 skip
* trace 回放记录

### 2.3 本阶段坚持 File-first

* 原始事实首先存在于 `assets/`
* 长期工作状态存在于 `memory/`
* 运行过程存在于 `context_trace/`

memory 不是原始文件仓库，而是 md 化沉淀层。
trace 不是 memory，而是审计和回放层。
这些边界必须稳定。

---

## 3. 三个平面：Control Plane / Data Plane / Trace Plane

## 3.1 Control Plane

Control Plane 是 workspace 根目录下的一组大写 MD 文件，例如：

* `AGENTS.md`
* `SOUL.md`
* `IDENTITY.md`
* `USER.md`
* `SKILLS_SNAPSHOT.md`

它们的职责是定义 Agent 如何工作，包括但不限于：

* 输出边界
* 工具边界
* 记忆协议
* 技能协议
* 禁止脑补
* 读写原则

**Control Plane 优先级最高。**
与 memory 冲突时，以 workspace 控制层为准。 

### 结论

Control Plane 决定“怎么工作”。

---

## 3.2 Data Plane

Data Plane 分成两块：

### A. assets

原始材料层，例如：

* `assets/uploads/`
* `assets/data/`
* `assets/figures/`
* `assets/ppt_pack/`

这里放 pdf、csv、ppt、图像、原始 md 笔记等。

### B. memory

沉淀层，例如：

* `memory/identity/`
* `memory/timeline/`
* `memory/concepts/`
* `memory/tasks/`
* `memory/packs/`

这里放的是由 LLM 在控制平面约束下，对 assets 和上下文做出的 md 化沉淀。

### 结论

Data Plane 决定“事实与沉淀存在哪里”。

---

## 3.3 Trace Plane

Trace Plane 是运行时回放层，写在：

* `context_trace/{session_id}.json`

它负责记录本轮如何发生，而不替代长期记忆。
当前设计也已经明确 session 历史和 traces 共用同一个 envelope 文件。

### 结论

Trace Plane 决定“这轮是怎么发生的”。

---

## 4. 关键对象分工

## 4.1 assets

原始输入层，不承载长期推理结构。

## 4.2 Layer1: memory/identity

稳定事实层，存放：

* 项目北极星
* 主线判据
* 实验室现实约束
* 用户偏好
* 上下文预算规则

这层允许缓慢演进，但服从 Control Plane。

## 4.3 Layer2: memory/timeline

时间推进层，存放：

* 180d index
* phase / week / day
* stage reports

这层负责让系统知道“最近发生了什么、当前推进到哪里”。

## 4.4 Layer3: Atom Notes

原子资产层，存放：

* `Concept`
* `Task`
* `Pack`

这层不是原始材料堆，而是跨周期可复用的工作流资产。

## 4.5 trace

运行审计层，只记录本轮发生了什么，不代替 memory。

---

## 5. Phase 3 的运行闭环

本阶段默认采用以下闭环：

### Step 1. 读取控制平面

先读取 workspace 控制层的软约束，明确当前 Agent 的工作协议。

### Step 2. 选择最少必要上下文

结合当前请求、assets、已有 memory，选出本轮最少必要的上下文。

### Step 3. 组装 Prompt

将 Control Plane 与选中的上下文按固定骨架拼装给模型。

### Step 4. 生成回答与 memory 决策

模型生成回答，同时形成本轮的 memory 决策：

* 写 Layer1 / Layer2 / Layer3 的哪一层
* 写哪个对象
* 还是显式 skip

### Step 5. 执行写入

由文件系统 / 工具层执行实际落盘。

### Step 6. 写入 trace

把“为什么这样读、为什么这样写、最终写到了哪里”记录到 trace。

### Step 7. done

只有在回答、memory 决策、trace 都完成后，本轮才算真正结束。

---

## 6. “意图识别”在本阶段的定义

### 6.1 定义

本阶段保留闭环语义，但把它定义成 **intent hint**，不是重型独立 Router。

推荐的 intent hint 集合仍可沿用这 5 类：

* `stage_progress`
* `experiment_closure`
* `mechanism_closure`
* `writing_closure`
* `general_consult`

但这里的重点不是“分类器精度”，而是：

* 它是否帮助 context 选择
* 它是否帮助 memory 决策
* 它是否没有引入过重复杂度

### 6.2 允许的实现自由度

可以由 CC / Codex 自行决定：

* 用规则关键词
* 用轻量映射表
* 用 prompt 内软判断
* 或 hybrid 方式

### 6.3 不允许的方向

不允许把它实现成：

* 多层大 Router 树
* 独立复杂 Planner
* `file/image/graphrag/additional` 这种混层中心
* 一个吞掉 Context / Trace / Layer3 逻辑的超级分类器

---

## 7. assets 与 memory 的关系

## 7.1 assets 是原始材料层

assets 中的文件是用户上传或已有的原始材料，例如：

* 论文 pdf
* 实验 csv
* ppt 素材
* 图像
* 原始学习笔记

它们是第一事实源，但不是最终工作流资产。

## 7.2 memory 是沉淀层

memory 是 LLM 在控制平面软约束下，对原始材料和既有记忆做出的结构化沉淀。

因此：

* 不应无脑复制所有 assets 到 memory
* 不应把 memory 做成另一个 uploads 文件夹
* 不应每轮都强行写 Layer3

## 7.3 三层 memory 的职责

### Layer1

存稳定事实与约束

### Layer2

存时间推进与阶段脉络

### Layer3

存跨周期可复用原子资产

---

## 8. memory 写入规则

## 8.1 基本原则

### 原则 A

不是每轮都必须写 memory，允许只写 trace。

### 原则 B

memory 写的是 md 化结论，不是原始文件复制品。

### 原则 C

LLM 负责提出写入建议，文件系统 / 工具层负责执行写入。

这条原则既保留了“LLM 软约束下自进化”的味道，也避免失控。

---

## 8.2 Layer1 写入规则

只写稳定、慢变、长期影响后续判断的内容，例如：

* 新的主线判据
* 新的实验室硬约束
* 新的用户长期偏好
* 新的 context budget 策略

不写临时任务结果。

---

## 8.3 Layer2 写入规则

只写时间推进信息，例如：

* 今天做了什么
* 本周风险
* 某次阶段汇报索引更新
* 阶段里程碑

---

## 8.4 Layer3 写入规则

### 写 Concept

仅在明显出现一条新研究主线时。
默认优先挂已有 Concept，而不是新建。

### 写 Task

当本轮产出新的可验证工作单元时，例如：

* 新 claim
* 新 protocol
* 新 missing checklist
* 新 run
* 新的“能证明 / 不能证明”判断


### 写 Pack

当本轮主要产物是交付组织时，例如：

* 阶段汇报
* 机理证据链整理
* 写作目录树
* 图文策略


---

## 9. context 选择与 prompt 组装

## 9.1 默认 context 顺序

本阶段仍然沿用以下默认优先级：

1. workspace 控制层
2. skills snapshot
3. Layer1
4. Layer2
5. Layer3
6. uploads / assets 采样或路径

这是默认优先级，不是默认全量注入清单。

---

## 9.2 固定脊梁

建议至少稳定考虑：

* `AGENTS.md`
* `memory/identity/project.md`
* `memory/identity/context_budget.md`

其中 `context_budget.md` 只用于预算控制，不进入正文注入。 

---

## 9.3 意图扩展

可以根据 intent hint 追加 Layer2 / Layer3 内容，例如：

### `stage_progress`

* `180d_index.md`
* 相关 `weeks/`
* 上一期 `stage_report`
* 关键 `PACK_stage_report_*`
* 必要时最近 `days/`


### `experiment_closure`

* `lab_context.md`
* today `day`
* active `TASK_*`
* 必要时 `CONCEPT_*`


### `mechanism_closure`

* project 判据
* `TASK_mechanism_*`
* `PACK_mechanism_*`
* 必要 paper path / 摘要


### `writing_closure`

* project 北极星
* `PACK_writing_*`
* `PACK_figure_*`
* supporting `TASK_*`


---

## 9.4 按需 skill 说明

只在需要时读取对应 `SKILL.md`。
不允许每轮全量注入全部 skills。

---

## 9.5 PromptBuilder 的职责

PromptBuilder 只负责：

* 按固定骨架拼装 system / user
* 管理正文注入顺序
* 保证预算与可解释性

PromptBuilder 不负责：

* 研究判断
* memory 决策
* trace 决策

---

## 9.6 预算规则

必须保留这些硬约束：

* 单文件字符上限 20,000
* 总预算由 `context_budget.md` 控制
* 被截断 / 被跳过必须记录到 trace


---

## 10. trace 记录规则

## 10.1 trace 的职责

trace 是记忆沉淀过程的审计器。
它最少需要回答：

1. 本轮用了哪些控制平面文件
2. 本轮读了哪些上下文
3. 本轮引用了哪些 assets
4. 本轮决定写哪个 memory 对象，或 skip
5. 本轮缺了什么
6. 本轮最终产物路径是什么

---

## 10.2 推荐结构

本阶段不把 schema 完全写死，但推荐至少包含：

* `trace_id`
* `control_context`
* `context_read`
* `asset_refs`
* `memory_decision`
* `missing_fields`
* `output_refs`

其中 `context_read[]` 至少要保留：

* `path`
* `layer`
* `why`
* `status`
  这是当前 PRD 的硬要求。

---

## 10.3 trace 的关键新点

本阶段 trace 至少要能看出：

> **本轮最终打到了哪个 memory 对象，或者为什么选择 skip。**

这比“只是记录读了哪些文件”更重要。

---

## 10.4 done 时机

done 只能在以下动作完成后发出：

1. assistant 输出已形成
2. memory 写入或 skip 决策已完成
3. trace 已成功写入

这条不建议放松。

---

## 11. 实现建议

## 11.1 推荐模块

建议 Phase 3 围绕这些模块组织：

* `context_orchestrator.py`
* `prompt_builder.py`
* `trace_writer.py`
* `api/traces.py`
* `api/chat.py` 集成

这与现有 plan 保持一致。

## 11.2 模块职责建议

### `context_orchestrator.py`

负责：

* 读取控制平面
* 形成 intent hint
* 选择 context
* 管理预算
* 给出 memory 相关 hint

### `prompt_builder.py`

负责：

* system/user 组装
* Project Context 注入
* 截断处理

### `trace_writer.py`

负责：

* 统一写 trace
* 记录 control / context / assets / memory decision / outputs

### `api/traces.py`

负责：

* 查询 trace
* 支持前端回放

---

## 12. 验收标准

Phase 3 的通过标准，不再只看“分类是否正确”，而看这 4 件事：

### 1. Control Plane 真的参与了行为约束

也就是 workspace 大写 MD 不是摆设。

### 2. assets → memory 的沉淀链成立

原始材料没有被粗暴复制进 memory，而是形成了合理 md 化沉淀。

### 3. write-or-skip 清楚

这轮到底写了哪层 memory，或为什么 skip。

### 4. trace 能回放

至少能回答：

* 本轮读了什么
* 本轮用到了哪些 assets
* 本轮打到了哪个 memory 对象
* 为什么这样做

---

## 13. 明确不做的内容

Phase 3 不做：

* subagent / 多 agent
* RAG / GraphRAG
* tools 执行框架全量接入
* 真上传链路闭环
* 多 workspace 激活依赖
* 前端大改
* 自动 skill mining 落地

原因不是“不重要”，而是这些属于后续 phase。
当前阶段先把 **受控的记忆沉淀中枢** 做稳。

---

你要是愿意，我下一条就继续给你补两份和这版 spec 严格对齐的仓库文档：

* `docs/cc_workflow_prompts.md`
* `docs/codex_workflow_prompts.md`
