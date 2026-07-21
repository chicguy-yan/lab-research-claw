可以。下面这版我直接按你刚刚收敛出来的方向，给你一份 **可直接放进仓库使用** 的新版 `BOOTSTRAP.md`。

这版明确做了几件事：

* 保留 **first-run only** 和“点火不巡航”定位，沿用你现有控制层思路。 
* 不再默认每个 workspace 都是“完整 180 天科研主线”，因为旧版确实默认生成 `180d_index.md`、首个 `Concept` 和 bootstrap task。 
* 保持 **file-first**，坚持 `assets` 是事实源、`memory` 是 md 化沉淀、`trace` 是回放审计层。 
* 把“引导用户先上传少量初始 assets”纳入协议，但解析动作交给你已有的 skill，不让 `BOOTSTRAP` 自己变成解析器。你现有设计也已经把 skill 定位成按需读、按 route 使用，而不是把所有能力全塞进控制层。 

---

````md
---
title: "BOOTSTRAP.md — Workspace Initialization Protocol"
read_when:
  - first-run only
not_injected_after: init
status: active
---

# BOOTSTRAP.md — Workspace 初始化协议

> 本文件只在 workspace 首次启动时使用。
> 它的职责不是默认生成一套完整科研项目模板，而是：
>
> 1. 帮助识别并确认当前 workspace 的最小语义边界  
> 2. 引导用户提供少量代表性初始 assets 辅助初始化  
> 3. 将 scope 判断桥接为首批文件生成计划  
> 4. 生成与该 workspace 相称的最小骨架文件  
> 5. 完成后退出，不参与后续常驻控制层注入
>
> 一句话：
> **BOOTSTRAP 只负责点火，不负责巡航。**

---

# 0. 角色与退出规则

## 0.1 本文件是什么
本文件是 **workspace 首次启动协议**。

它负责：
- 识别 workspace 的最小语义边界
- 将用户意图与初始材料转化为初始化计划
- 生成首批最小 memory 骨架
- 将控制权交回常驻控制层

它不是：
- 常驻控制层
- 长期项目调度器
- 多 agent 编排器
- 完整 ingest 系统
- 资产解析器
- 默认完整科研项目模板器

---

## 0.2 本文件与系统三平面的边界

### Control Plane
负责定义 Agent 如何工作。  
本文件初始化完成后，应由以下文件接管长期运行：

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `TOOLS.md`
- `MEMORY.md`
- `SKILLS_SNAPSHOT.md`

### Data Plane
- `assets/` 存放原始材料
- `memory/` 存放 md 化沉淀

### Trace Plane
- `context_trace/` 存放本轮如何发生的回放记录

---

## 0.3 退出规则
当初始化完成且 completion summary 已输出后：

- 本文件不再进入后续 system prompt 正文
- 后续上下文获取由常驻控制层负责
- 后续研究推进不再依赖本文件二次拍板

---

# 1. 初始化总原则

## 1.1 workspace 的双重含义
在本系统中，workspace 同时是：

### A. 技术作用域
- agent 的工作目录
- tools 的默认作用域
- session / store / trace 的隔离边界

### B. 语义作用域
- 一个由用户定义边界的研究容器

这个研究容器 **不一定** 是完整 180 天科研主线。  
它也可能是：

- 一个完整科研主线
- 当前某个阶段
- 一个机制验证分支
- 一个文献调研容器
- 一个写作 / 汇报容器
- 其他用户自定义工作边界

---

## 1.2 初始化成功标准
初始化完成，不以“生成文件越多越好”为标准，而以以下问题能否被后续控制层快速回答为标准：

1. 这个 workspace 是什么语义容器  
2. 它不包含什么  
3. 它是否需要 timeline  
4. 它更适合从 `Concept / Task / Pack` 的哪一类起手  
5. 首批 memory 是否已尽量与初始 assets 建立来源关系  
6. 哪些文件被有意跳过，而不是漏做

---

## 1.3 初始化最小复杂度要求
初始化阶段明确不做：

- 多 agent 编排
- 重型 Router
- 数据库初始化
- 复杂审批流
- 完整 RAG / hybrid retrieval
- 全量 assets 导入
- skill proposal 自动上线

---

# 2. 初始化流程总览

初始化按以下顺序进行：

1. Scope Discovery  
2. Initial Asset Intake  
3. Asset Parse Handoff  
4. Scope Confirmation  
5. Generation Plan  
6. Minimal Identity Generation  
7. Timeline Generation（Conditional）  
8. Layer3 Seed Generation（Conditional）  
9. Completion Summary and Handoff  

任何一步都应遵守：
- file-first
- 最小必要
- 不默认完整主线
- 不用口头描述替代事实材料
- 解析动作通过已有 skill 完成

---

# 3. Phase A · Scope Discovery

## 3.1 目标
先做轻量归纳，不急着生成文件。  
本阶段要回答：

> 这个 workspace 想被当成什么样的研究容器？

---

## 3.2 需要识别的最小 scope 信息

### A. semantic_scope
从下列类型中选择最接近的一类：

- `mainline`：完整科研主线容器
- `stage`：阶段推进容器
- `branch`：单个机制 / 方案验证分支
- `literature`：文献调研容器
- `writing`：写作 / 汇报容器
- `custom`：用户自定义容器

### B. time_mode
从下列类型中选择：

- `long_horizon`
- `current_stage`
- `short_sprint`
- `no_timeline`

### C. primary_object
从下列类型中选择：

- `concept_first`
- `task_first`
- `pack_first`
- `mixed`
- `undecided`

### D. exclusions
至少说明 1 到 3 条本 workspace **不负责** 的内容。

---

## 3.3 scope discovery 的输出
本阶段先形成内部草案：

```yaml
scope_draft:
  semantic_scope: ""
  time_mode: ""
  primary_object: ""
  exclusions: []
  confidence: low|medium|high
  basis:
    - user_statement
````

此时只允许形成草案，不得直接视为最终确认结果。

---

# 4. Phase B · Initial Asset Intake

## 4.1 目标

引导用户先提供少量代表性初始 assets，辅助初始化。
这里的目标不是完整导入，而是让系统在首次启动时，不只依赖口头描述。

---

## 4.2 引导语

如用户尚未提供初始材料，应要求其优先上传 **1 到 5 个最能代表当前 workspace 边界或当前工作焦点的材料**。

可接受的材料包括但不限于：

* 核心 pdf / 综述
* 当前组会 PPT
* csv / xlsx / txt 实验数据
* 图谱 / 图片
* 原始实验记录
* 写作草稿 / md 笔记
* 机制图 / figure 草稿

---

## 4.3 intake 只做轻分类

本阶段不做深解析，只做：

### A. 是否存在初始 assets

* `present`
* `missing`

### B. 初始 assets 是否足以辅助初始化

* `sufficient`
* `partial`
* `insufficient`

### C. 初始 assets 类型倾向

* `literature_heavy`
* `experiment_heavy`
* `writing_heavy`
* `mixed`

---

## 4.4 输出

形成以下记录：

```yaml
initial_asset_status:
  presence: present|missing
  sufficiency: sufficient|partial|insufficient
  tendency: literature_heavy|experiment_heavy|writing_heavy|mixed|unknown
  asset_paths: []
  notes: []
```

---

## 4.5 边界

* 没有初始 assets，也允许轻量初始化
* 但必须显式记录缺口
* 不允许把“用户未上传材料”静默当成“没有事实源”
* 不允许把本阶段扩展成完整 ingest 流程

---

# 5. Phase C · Asset Parse Handoff

## 5.1 目标

若用户已提供初始 assets，则在必要时调用已有 parsing skill，获取 **可被初始化消费的轻量解析结果**。

---

## 5.2 边界

`BOOTSTRAP` 本身不负责：

* pdf 深度解析
* csv 内容抽取
* 图谱判读
* 来源锚点写入实现
* asset-to-memory 映射实现

这些动作统一由 **已有 skill** 负责。

---

## 5.3 `BOOTSTRAP` 只负责三件事

1. 判断是否需要触发 parsing skill
2. 将初始 assets 交给对应 skill
3. 接收解析结果并用于初始化判断

---

## 5.4 允许消费的 parsing 结果

解析结果应尽量轻，只需包含以下信息：

```yaml
parse_handoff_result:
  used: true|false
  parsed_assets:
    - asset_path: ""
      asset_type: ""
      likely_role: ""
      scope_signal: ""
      source_summary: ""
  overall_notes:
    - ""
```

其中：

* `likely_role` 用于判断该 asset 更像支撑 `Concept / Task / Pack` 的哪一类
* `scope_signal` 用于修正 scope
* `source_summary` 用于初始化阶段的来源说明

---

## 5.5 若未触发 parsing skill

也必须明确写出：

```yaml
parse_handoff_result:
  used: false
  reason: "..."
```

---

# 6. Phase D · Scope Confirmation

## 6.1 目标

结合：

* 用户初始表述
* 初始 assets
* parsing skill 返回的轻量结果

正式确认 workspace 的最小边界。

---

## 6.2 必须确认的内容

```yaml
confirmed_scope:
  semantic_scope: ""
  time_mode: ""
  primary_object: ""
  exclusions: []
  evidence_basis:
    - user_statement
    - initial_assets
    - parse_handoff
```

---

## 6.3 生成文件

本阶段必须生成：

# `memory/identity/workspace_scope.md`

---

## 6.4 `workspace_scope.md` 最小内容要求

该文件至少应包含以下块：

### A. Workspace Purpose

一句话说明本 workspace 是什么研究容器。

### B. Semantic Scope

明确其属于：

* 主线 / 阶段 / 分支 / 文献 / 写作 / 自定义

### C. Time Mode

明确其时间语义。

### D. Primary Work Object

明确其初始化后更偏：

* `Concept`
* `Task`
* `Pack`
* 或 mixed

### E. Exclusions

明确其不负责什么。

### F. Initialization Evidence Basis

说明 scope 判断来自：

* 用户表述
* 哪些初始 assets
* 是否用了 parsing skill

---

# 7. Phase E · Generation Plan

## 7.1 目标

在 confirmed scope 基础上，决定：

* 必须生成什么
* 条件生成什么
* 明确跳过什么

---

## 7.2 必须形成 generation plan

```yaml
bootstrap_plan:
  confirmed_scope:
    semantic_scope: ""
    time_mode: ""
    primary_object: ""
  initial_asset_status:
    presence: ""
    sufficiency: ""
  parse_handoff_used: true|false

  must_generate: []
  conditional_generate: []
  skip_by_design: []

  seed_strategy: ""
  rationale: []
```

---

## 7.3 generation plan 的判断原则

### 必须生成

只保留最小骨架文件。

### 条件生成

只有在 scope 明确需要时才生成。

### skip by design

如果某些旧版默认文件不适合本 workspace，必须显式写为“有意跳过”。

---

## 7.4 旧版默认行为的废除规则

除非 generation plan 明确要求，否则不得默认生成：

* `memory/timeline/180d_index.md`
* `memory/concepts/CONCEPT_<topic>.md`
* `memory/tasks/TASK_bootstrap_initial_questions.md`
* `memory/identity/lab_context.md`

---

# 8. Phase F · Minimal Identity Generation

## 8.1 目标

生成后续控制层能快速拿上下文所需的最小 identity 骨架。

---

## 8.2 默认必须生成

以下文件默认必须生成：

### A. `memory/identity/workspace_scope.md`

由 Phase D 生成。

### B. 轻量 identity 文件

默认生成以下二选一之一：

* `memory/identity/project.md`
* 或 `memory/identity/workspace_profile.md`

推荐默认使用：`memory/identity/project.md`

---

## 8.3 `project.md` 的新版职责

该文件不再默认写成“完整科研主线宣言”，而应写成：

* 当前 workspace 的目的
* 当前容器与整体研究主线的关系（若存在）
* 当前近期交付或当前工作焦点
* 当前主要不确定性
* 当前工作对象偏向

---

## 8.4 `context_budget.md`

若系统仍沿用统一的上下文预算规则，则默认生成：

* `memory/identity/context_budget.md`

其内容可继续保持全 workspace 通用模板。

---

## 8.5 `lab_context.md` 改为条件生成

仅当 confirmed scope 明显包含实验推进语义时，才允许生成：

* `memory/identity/lab_context.md`

例如：

* `mainline`
* `stage`
* `branch` 且包含实验验证

如果 workspace 是：

* `writing`
* `literature`
* 或不依赖实验上下文的 `custom`

则默认跳过，或使用更轻的替代文件：

* `memory/identity/work_context.md`

---

# 9. Phase G · Timeline Generation（Conditional）

## 9.1 目标

timeline 不再是默认产物，而是 scope 驱动的条件产物。

---

## 9.2 条件分支

### 若 `time_mode = long_horizon`

生成：

* `memory/timeline/180d_index.md`

### 若 `time_mode = current_stage`

生成：

* `memory/timeline/current_stage.md`

### 若 `time_mode = short_sprint`

生成：

* `memory/timeline/current_sprint.md`

### 若 `time_mode = no_timeline`

不生成 timeline 文件。

---

## 9.3 timeline 文件的最低要求

只需足够支持后续控制层理解：

* 当前处于哪个时间框架
* 最近要推进什么
* 时间推进如何影响 context selection

不得为了“显得完整”而硬写长期路线图。

---

# 10. Phase H · Layer3 Seed Generation（Conditional）

## 10.1 目标

根据 confirmed scope 和 generation plan，决定初始化后是否 seed Layer3，以及从哪类对象起手。

---

## 10.2 seed_strategy 允许值

* `concept_first`
* `task_first`
* `pack_first`
* `mixed_seed`
* `no_seed`

---

## 10.3 条件分支

### A. `concept_first`

适用于：

* `mainline`
* 部分以研究主题为核心的 `literature`

允许生成：

* 首个 `Concept`

---

### B. `task_first`

适用于：

* `stage`
* `branch`
* 实验推进型 workspace

允许生成：

* kickoff `Task`

---

### C. `pack_first`

适用于：

* `writing`
* 汇报导向 workspace
* 文献整合型 workspace

允许生成：

* kickoff `Pack`

---

### D. `mixed_seed`

适用于少数确有必要的情况。
仅在 generation plan 明确说明原因时使用。

---

### E. `no_seed`

适用于：

* 边界尚不稳定
* 初始材料不足
* 当前仅完成 scope 初始化

此时只允许：

* 生成 identity
* 记录 trace
* 等待后续正式工作流触发 Layer3 沉淀

---

## 10.4 来源要求

若存在初始 assets 且 parse handoff 已产出结果，则首批 Layer3 seed 应尽量带：

* source refs
* 初始化依据说明
* 对应的 asset path 或来源摘要

不得生成“无来源、无依据”的空心 seed。

---

# 11. Phase I · Completion Summary and Handoff

## 11.1 目标

初始化结束时，输出的不只是文件列表，还应包括初始化结论。

---

## 11.2 completion summary 必须包含

```yaml
bootstrap_completion_summary:
  confirmed_scope:
    semantic_scope: ""
    time_mode: ""
    primary_object: ""

  initial_asset_status:
    presence: ""
    sufficiency: ""

  parse_handoff_status:
    used: true|false

  generated_files: []
  skipped_by_design: []

  default_context_priority: []
  seed_strategy: ""

  handoff_target:
    - AGENTS.md
    - SOUL.md
    - IDENTITY.md
    - USER.md
    - TOOLS.md
    - MEMORY.md
    - SKILLS_SNAPSHOT.md
```

---

## 11.3 `default_context_priority` 的生成要求

completion summary 中必须明确，后续控制层默认先看什么。

例如：

* 固定脊梁优先
* 若写作型则优先 Pack
* 若实验阶段型则优先 active Task + lab context
* 若文献型则优先 project / relevant Pack / literature-derived Concept

---

## 11.4 完成时的标准提示语

当初始化完成后，应输出类似确认信息：

> Workspace 初始化完成。
> BOOTSTRAP.md 已完成使命，后续对话将由常驻控制层接管。
> 当前 workspace 已确认其语义边界；后续上下文选择将优先依据 `workspace_scope.md`、相关 identity 文件、匹配 route 和按需 skill 读取进行。

---

# 12. Guardrails

以下规则为红线，不得违反。

## 12.1 关于 workspace

* 不要默认每个 workspace 都是完整科研主线
* 不要将 workspace type、route、skill category 混为一谈

## 12.2 关于初始化复杂度

* 不要把 scope discovery 做成长问卷
* 不要引入多 agent、数据库、复杂审批流
* 不要把初始化扩展成完整 ingest 系统

## 12.3 关于文件生成

* 不要默认每个 workspace 都生成 `180d_index.md`
* 不要默认每个 workspace 都 seed `Concept`
* 不要默认每个 workspace 都生成 bootstrap task
* 不要默认每个 workspace 都生成 `lab_context.md`

## 12.4 关于 assets

* bootstrap 可以请求少量初始 assets 辅助初始化
* 但不得把自己扩展为完整资产解析器
* 资产解析必须通过已有 skill 完成
* 若无初始 assets，允许轻量初始化，但必须显式记录缺口

## 12.5 关于用户主导权

* bootstrap 可以帮助归纳和确认 workspace scope
* 但不得完全替用户拍板研究边界
* 当用户表述与初始材料冲突时，应显式提示并请求确认，而不是静默覆盖

## 12.6 关于 handoff

* 初始化完成后，`BOOTSTRAP.md` 不再参与常驻控制层注入
* 后续行为应由 Control Plane + Data Plane + Trace Plane 共同驱动

---

# 13. 实施约束

* 所有生成文件必须通过正式写文件工具落盘后才算完成
* 所有条件生成文件，必须有 generation plan 中的理由
* 所有 skip 都应在 completion summary 中显式说明
* 本文件只定义初始化协议，不定义后续常驻运行策略细节

---

# 14. 最终一句话

> **BOOTSTRAP 的职责不是根据用户口头描述生成一套完整科研项目模板，而是帮助用户用“意图 + 初始材料”共同定义 workspace 的最小边界，再生成与之相称的初始化骨架。**

```

