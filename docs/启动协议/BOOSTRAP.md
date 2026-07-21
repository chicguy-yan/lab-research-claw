---
title: "BOOTSTRAP.md"
role: "workspace first-run initialization protocol"
read_when:
  - first entry into a provisioned workspace
status: active
not_persistent_after_completion: true
---

# BOOTSTRAP.md

> 本文件只在某个 workspace 首次进入时使用。
>
> 它的职责不是根据用户口头描述生成一套默认完整科研项目模板，
> 而是帮助用户用“意图 + 初始材料”共同定义这个 workspace 的最小边界，
> 再生成与之相称的初始化骨架。
>
> 一句话：
>
> **BOOTSTRAP 只负责把一个已 provision 的技术 workspace 初始化成一个已确认边界的研究容器。**

---

# 0. Role and Boundaries

## 0.1 你现在在做什么

你正在执行一个 **first-run initialization protocol**。

你要做的事只有四件：

1. 识别并确认当前 workspace 的最小语义边界
2. 引导用户提供少量代表性初始 assets 辅助初始化
3. 生成与该 scope 相称的最小 memory 骨架
4. 输出 completion summary，并把控制权交回常驻控制层

## 0.2 你不负责什么

你不负责：

- 创建 workspace
- 直接更新 `workspace_manifest.json`
- 完整资产解析
- 多 agent 编排
- 把当前 workspace 默认当成完整 180 天科研主线

`workspace_manifest.json` 的生命周期更新由系统负责，不由你通过普通写文件工具直接回写。

## 0.3 你现在可以假定什么

本协议假定以下事实已经成立：

- 当前 workspace 已完成基础创建
- 当前请求已经明确定位到某个 `workspace_id`
- 当前读写、assets、sessions、trace 都已经具有 workspace 作用域
- 系统已经显式进入 bootstrap 初始化阶段

## 0.4 退出规则

当以下条件满足时，本协议结束：

1. `memory/identity/workspace_scope.md` 已生成
2. generation plan 已执行完毕
3. completion summary 已输出
4. 系统已将该 workspace 标记为完成初始化

结束后：

- 本文件不再进入后续常驻控制层 prompt
- 后续对话与文件操作全部交由正常 workspace runtime routing 处理

---

# 1. Core Principles

## 1.1 workspace 的双重含义

在本系统中，workspace 同时是：

### 技术作用域

- agent 的工作目录
- tools 的默认作用域
- session / trace / assets / memory 的隔离边界

### 语义作用域

- 一个由用户定义边界的研究容器

这个研究容器不一定是完整科研主线。
它也可能是：

- 一个完整主线
- 当前阶段
- 一个机制验证分支
- 一个文献调研容器
- 一个写作 / 汇报容器
- 其他用户自定义工作边界

## 1.2 初始化成功标准

初始化完成，不以“生成文件越多越好”为标准，而以以下问题能否被后续控制层快速回答为标准：

1. 这个 workspace 是什么语义容器
2. 它不包含什么
3. 它是否需要 timeline
4. 它更适合从 `Concept / Task / Pack` 的哪一类起手
5. 首批 memory 是否尽量与初始 assets 建立来源关系
6. 哪些文件是有意跳过，而不是漏做

## 1.3 初始化复杂度边界

初始化阶段不做：

- 多 agent 编排
- 数据库编排
- 跨 workspace 资产整合
- 完整 ingest
- 自动 skill proposal 上线
- 默认完整 180 天科研主线设定

---

# 2. Inputs You May Use

执行本协议时，你可以使用以下输入：

## 2.1 用户输入

- 用户对该 workspace 的口头描述
- 用户当前目标
- 用户对 workspace 边界的主观定义
- 用户补充的初始说明

## 2.2 manifest 输入

从 `workspace_manifest.json` 读取：

- `workspace_id`
- `display_name`
- `description`
- `bootstrap_status`

manifest 是机器侧输入锚点，但它不等于最终 scope。

## 2.3 初始 assets

用户在当前 workspace 下上传的少量代表性材料。

## 2.4 parsing skill 返回结果

若有调用已有解析 skill，则其轻量摘要可作为输入之一。

---

# 3. Phase A · Scope Discovery

## 3.1 目标

先形成一个 scope draft，但不立即拍板。

本阶段要回答：

> 当前这个已 provision 的 workspace，想被当成什么研究容器？

## 3.2 你必须判断的最小内容

至少判断这四件事：

1. `semantic_scope`
   可选方向：
   - `mainline`
   - `stage`
   - `branch`
   - `literature`
   - `writing`
   - `custom`
2. `time_mode`
   可选方向：
   - `long_horizon`
   - `current_stage`
   - `short_sprint`
   - `no_timeline`
3. `primary_object`
   当前更适合从：
   - `Concept`
   - `Task`
   - `Pack`
   - `mixed`
   起手
4. `exclusions`
   至少列出 1 到 3 条本 workspace 明显不负责的内容

## 3.3 依据

scope draft 可以参考：

- 用户表述
- `workspace_manifest.json.display_name`
- `workspace_manifest.json.description`

但不允许只凭 manifest 就认定最终 scope。

---

# 4. Phase B · Initial Asset Intake

## 4.1 目标

引导用户在当前 workspace 下先提供 **1 到 5 个最能代表当前工作边界或当前工作焦点的初始 assets**。

这一步的目标不是完整导入，而是让 bootstrap 不只依赖口头描述。

## 4.2 引导原则

若用户尚未提供初始材料，应优先请求其上传少量代表性材料，例如：

- 核心 pdf / 综述
- 当前组会 PPT
- 实验 csv / xlsx
- 实验记录 / md 笔记
- 写作草稿
- 图谱 / 机制图 / figure 草稿

引导要求：

- 材料数量尽量少
- 但足以辅助判断 workspace 边界
- 只处理当前 workspace 下的材料
- 不跨 workspace 借材料

## 4.3 你在本阶段只做轻分类

本阶段不做深解析，只判断：

- 当前是否已有初始 assets
- 这些材料是否足以辅助初始化
- 它们整体更偏 literature / experiment / writing / mixed

## 4.4 边界

- 没有初始 assets，也允许轻量初始化
- 但必须显式记录缺口
- 不得将本阶段扩展为完整 ingest

---

# 5. Phase C · Asset Parse Handoff

## 5.1 目标

如当前 workspace 已有代表性初始 assets，则在必要时调用已有 parsing skill，获取可供 bootstrap 使用的轻量解析结果。

## 5.2 你不负责

- pdf 深解析
- csv 内容抽取
- 图谱判读
- 结构化来源锚点实现
- asset-to-memory 映射实现

这些动作统一由已有 skill 负责。

## 5.3 你在这里只做三件事

1. 判断是否需要触发 parsing skill
2. 将当前 workspace 的初始 assets 交给对应 skill
3. 接收轻量结果并用于后续 scope confirmation 与 generation plan

## 5.4 你需要从解析结果里拿什么

只需要消费轻量信息：

- 该 asset 更像支撑 `Concept / Task / Pack` 中哪一类对象
- 它对当前 scope 有什么支持或修正信号
- 可用于初始化说明的来源摘要

若未触发 parsing skill，也要明确写出原因。

---

# 6. Phase D · Scope Confirmation

## 6.1 目标

结合：

- 用户表述
- manifest
- 初始 assets
- parsing skill 结果

正式确认当前 workspace 的最小语义边界。

## 6.2 本阶段必须生成

- `memory/identity/workspace_scope.md`

## 6.3 `workspace_scope.md` 至少要包含

1. `Workspace Purpose`
   一句话说明本 workspace 是什么研究容器
2. `Semantic Scope`
   明确它属于 mainline / stage / branch / literature / writing / custom 中哪一类
3. `Time Mode`
   明确其时间语义
4. `Primary Work Object`
   明确初始化后更偏向 `Concept / Task / Pack / mixed`
5. `Exclusions`
   明确它不负责什么
6. `Initialization Evidence Basis`
   说明判断来自：
   - 用户表述
   - manifest
   - 哪些初始 assets
   - 是否用了 parsing skill

---

# 7. Phase E · Generation Plan

## 7.1 目标

把 confirmed scope 翻译成初始化动作。

本阶段要回答：

- 哪些文件必须生成
- 哪些文件条件生成
- 哪些文件应显式跳过
- 首批 Layer3 应如何起手

## 7.2 生成原则

### must_generate

只保留最小骨架文件。

### conditional_generate

只有在 scope 明确需要时才生成。

### skip_by_design

若旧版默认文件不适合本 workspace，必须显式记为有意跳过。

## 7.3 默认废除的旧行为

除非 generation plan 明确要求，否则不得默认生成：

- `memory/timeline/180d_index.md`
- `memory/concepts/CONCEPT_<topic>.md`
- `memory/tasks/TASK_bootstrap_initial_questions.md`
- `memory/identity/lab_context.md`

---

# 8. Phase F · Minimal Identity Generation

## 8.1 目标

生成后续控制层快速拿上下文所需的最小 identity 骨架。

## 8.2 默认必须生成

### A. `memory/identity/workspace_scope.md`

由 Phase D 生成。

### B. 一个轻量 identity 文件

默认生成以下之一：

- `memory/identity/project.md`
- 或 `memory/identity/workspace_profile.md`

推荐默认使用：

- `memory/identity/project.md`

### C. `memory/identity/context_budget.md`

若系统仍沿用 context budget 规则，则应保留。

## 8.3 `project.md` 的职责

`project.md` 不再承担 workspace 命名元数据职责。
workspace 命名与生命周期状态由 `workspace_manifest.json` 承担。

`project.md` 只负责写 agent 可读内容，例如：

- 当前 workspace 的目的
- 它与整体研究主线的关系（若存在）
- 当前近期交付或当前工作焦点
- 当前主要不确定性
- 当前工作对象偏向

## 8.4 条件生成：`lab_context.md`

仅当 confirmed scope 明显包含实验推进语义时，才允许生成：

- `memory/identity/lab_context.md`

如果 workspace 是：

- `writing`
- `literature`
- 非实验导向 `custom`

则默认跳过，或改用更轻替代：

- `memory/identity/work_context.md`

---

# 9. Phase G · Timeline Generation（Conditional）

## 9.1 目标

timeline 是 scope 驱动的条件产物，不是 runtime 成立的前提。

## 9.2 条件分支

- 若 `time_mode = long_horizon`，生成 `memory/timeline/180d_index.md`
- 若 `time_mode = current_stage`，生成 `memory/timeline/current_stage.md`
- 若 `time_mode = short_sprint`，生成 `memory/timeline/current_sprint.md`
- 若 `time_mode = no_timeline`，不生成 timeline 文件

## 9.3 约束

- timeline 是否生成，不影响 workspace runtime 成立
- timeline 只影响后续 agent 如何理解时间推进
- 不得为了“显得完整”而硬写长期路线图

---

# 10. Phase H · Layer3 Seed Generation（Conditional）

## 10.1 目标

根据 confirmed scope 决定是否 seed Layer3，以及从哪类对象起手。

## 10.2 seed_strategy

允许值：

- `concept_first`
- `task_first`
- `pack_first`
- `mixed_seed`
- `no_seed`

## 10.3 条件分支

- `concept_first`
  适用于 `mainline` 及部分主题导向 `literature`
- `task_first`
  适用于 `stage`、`branch`、实验推进型 workspace
- `pack_first`
  适用于 `writing`、汇报导向 workspace、文献整合型 workspace
- `mixed_seed`
  仅在 generation plan 明确给出理由时使用
- `no_seed`
  适用于边界仍不稳定、初始材料不足、当前只完成 scope 初始化

Layer3 seed 的存在与否，不是 bootstrap 成功与否的硬前提。

## 10.4 来源要求

若当前 workspace 下存在初始 assets 且 parse handoff 已成功产出结果，则首批 Layer3 seed 应尽量带：

- source refs
- 初始化依据说明
- 对应 asset path 或来源摘要

不得生成无来源、无依据的空心 seed。

---

# 11. Phase I · Completion Summary and Handoff

## 11.1 目标

输出初始化结论，并把该 workspace 交回 active runtime。

## 11.2 completion summary 必须包含

至少包括：

- `workspace_id`
- `confirmed_scope`
- `initial_asset_status`
- `parse_handoff_status`
- `generated_files`
- `skipped_by_design`
- `default_context_priority`
- `seed_strategy`
- `handoff_target`

## 11.3 `default_context_priority` 要求

必须明确后续控制层默认优先读什么。

例如：

- 固定脊梁优先
- 写作型优先 Pack
- 实验阶段型优先 active Task + lab context
- 文献型优先 relevant Pack / Concept / literature-derived notes

## 11.4 handoff 条件

只有在以下条件全部满足时，才算 handoff 完成：

1. `workspace_scope.md` 已生成
2. generation plan 已执行完毕
3. completion summary 已输出
4. 系统已确认该 workspace 初始化完成

此后：

> 当前 workspace 进入 active 状态。
> 后续所有请求都按正常 workspace runtime 执行，而不再进入 bootstrap 主流程。

---

# 12. Failure Handling

## 12.1 失败时的原则

若初始化过程中出现问题：

- 应尽量保留已经成功生成的最小文件
- 应让系统能够记录初始化失败
- 必须显式记录失败原因
- 不得伪装为 completed
- 不得因为局部失败就删除整个 workspace provision 结果

## 12.2 允许的保守降级

即使以下情况发生，也允许 bootstrap 以较轻方式完成或部分完成：

- 没有初始 assets
- 初始 assets 不足
- parse skill 未触发
- parse skill 返回结果有限
- 当前不适合 seed Layer3

但这些都必须在 summary 中显式记录。

---

# 13. Guardrails

以下规则为红线，不得违反。

## 13.1 关于 workspace

- 不要默认每个 workspace 都是完整科研主线
- 不要将 workspace type、route、skill category 混为一谈

## 13.2 关于与 5.3 的边界

- 不要让 BOOTSTRAP 负责创建 workspace
- 不要让 BOOTSTRAP 负责切换工作作用域
- 不要让 BOOTSTRAP 接管请求级 routing
- 不要让 BOOTSTRAP 替代 `workspace_manifest.json` 的机器状态职责

## 13.3 关于初始化复杂度

- 不要把 scope discovery 做成长问卷
- 不要引入多 agent、数据库、复杂审批流
- 不要把初始化扩展成完整 ingest 系统

## 13.4 关于文件生成

- 不要默认每个 workspace 都生成 `180d_index.md`
- 不要默认每个 workspace 都 seed `Concept`
- 不要默认每个 workspace 都生成 bootstrap task
- 不要默认每个 workspace 都生成 `lab_context.md`

## 13.5 关于 assets

- bootstrap 可以请求少量初始 assets 辅助初始化
- 但不得把自己扩展为完整资产解析器
- 资产解析必须通过已有 skill 完成
- 若无初始 assets，允许轻量初始化，但必须显式记录缺口
- 资产读取、解析和写回必须严格限定在当前 workspace 范围内

## 13.6 关于用户主导权

- bootstrap 可以帮助归纳和确认 scope
- 但不得完全替用户拍板研究边界
- 当用户表述与初始材料冲突时，应显式提示并请求确认，而不是静默覆盖

## 13.7 关于退出

- 初始化完成后，`BOOTSTRAP.md` 不再参与常驻控制层注入
- 后续行为由 Control Plane + Data Plane + Trace Plane 共同驱动

---

# 14. Final Statement

> 本协议假定当前 workspace 已完成技术层 provision。
> 它的任务不是生成一套默认完整科研项目模板，而是帮助用户用“意图 + manifest + 初始材料”共同定义 workspace 的最小边界，再生成与之相称的初始化骨架。
