---
title: "BOOTSTRAP.md"
role: "workspace first-run initialization protocol"
read_when:
  - first entry into a provisioned workspace
status: active
not_persistent_after_completion: true
---

# BOOTSTRAP.md

> 本文件是 workspace 首次进入时的初始化协议。
>
> 它运行在一个已经完成技术层 provision 的 workspace runtime 内，
> 不负责创建 workspace，不负责长期巡航，也不负责完整资产解析。
>
> 它的职责只有四件事：
>
> 1. 识别并确认当前 workspace 的最小语义边界
> 2. 引导用户提供少量代表性初始 assets 辅助初始化
> 3. 生成与该 scope 相称的最小 memory 骨架
> 4. 将控制权交回常驻控制层，由 bootstrap runner 负责生命周期状态流转
>
> 一句话：
>
> BOOTSTRAP 只负责把一个“已 provision 的技术 workspace”初始化成一个“已确认边界的研究容器”。

---

# 0. Role, Preconditions, and Exit Rule

## 0.1 本文件是什么

本文件是一个 first-run initialization protocol。

它负责：

- 在首次进入某个 workspace 时执行初始化
- 将“技术作用域”桥接到“语义作用域”
- 生成最小但够用的初始化骨架
- 输出 completion summary
- 完成后退出

它不是：

- 创建 workspace 的 API 说明
- workspace provision 脚本
- 常驻控制层
- 资产解析器
- 多 agent 编排器
- 完整科研项目模板生成器

---

## 0.2 适用前提

只有在以下条件满足时，才允许执行本协议：

1. 当前请求已明确定位到某个 `workspace_id`
2. 对应 workspace 目录已存在
3. `workspace_manifest.json` 已存在
4. `workspace_manifest.json.bootstrap_status` 为：
   - `pending`
   - 或 `failed`
5. 当前 workspace runtime 已可访问：
   - `assets/`
   - `memory/`
   - `context_trace/`
6. 当前 workspace 的 file/exec tools 已可用
7. 负责该 workspace 的 bootstrap runner 已存在，且可更新 manifest 生命周期状态

如果以上任一前提不满足：

- 不要执行 bootstrap 主流程
- 应先返回或记录前置条件缺失
- 不要假装初始化成功

---

## 0.3 本文件与 5.3 runtime 的关系

本文件假定：

- workspace 已通过 `POST /api/workspaces` 完成 provision
- 前端已进入某个具体 workspace
- 后端已按 `workspace_id` 进入对应 runtime
- 当前读写、assets、sessions、trace 都已经具有 workspace 作用域

所以：

- 5.3 负责“这个 workspace 怎么跑”
- BOOTSTRAP 负责“这个 workspace 到底是什么”

---

## 0.4 退出规则

当以下条件满足时，本文件必须退出：

1. `workspace_scope.md` 已生成
2. generation plan 已完成执行
3. completion summary 已输出
4. bootstrap runner 已将 `workspace_manifest.json.bootstrap_status` 更新为 `completed`

退出后：

- 本文件不再进入后续常驻控制层 prompt
- 后续对话与文件操作全部交由正常 workspace runtime routing 处理
- 不得在已完成 workspace 上重复执行 bootstrap 主流程，除非 runner 允许进入 `failed -> retry`

---

# 1. Bootstrap Lifecycle in Workspace Runtime

## 1.1 workspace 生命周期

一个 workspace 的合理生命周期分为三段：

### A. provision

技术层已建立：

- workspace 目录已创建
- 模板已复制
- `workspace_manifest.json` 已写入
- `bootstrap_status = pending`

### B. bootstrap

首次进入 workspace 时：

- 执行本协议
- 识别 scope
- 生成初始化骨架
- 由 bootstrap runner 更新 manifest 生命周期状态

### C. active

bootstrap 成功后：

- `bootstrap_status = completed`
- 后续所有请求均按正常 workspace runtime 流程执行

---

## 1.2 BOOTSTRAP 在其中的位置

BOOTSTRAP 是：

> provision 之后、active 之前的过渡协议。

它不负责：

- 创建 runtime
- 切换 runtime
- 维护全局 current workspace
- 持续做动态 scope 判断
- 直接回写 `workspace_manifest.json`

---

# 2. Initialization Principles

## 2.1 workspace 的双重含义

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

---

## 2.2 初始化成功标准

初始化完成，不以“生成文件越多越好”为标准，而以以下问题能否被后续控制层快速回答为标准：

1. 这个 workspace 是什么语义容器
2. 它不包含什么
3. 它是否需要 timeline
4. 它更适合从 `Concept / Task / Pack` 的哪一类起手
5. 首批 memory 是否尽量与初始 assets 建立来源关系
6. 哪些文件是有意跳过，而不是漏做

---

## 2.3 初始化复杂度边界

初始化阶段不做：

- 多 agent 编排
- 数据库编排
- 跨 workspace 资产整合
- 完整 ingest
- 完整知识抽取
- 自动 skill proposal 上线
- 默认完整 180 天科研主线设定

---

# 3. Bootstrap Inputs

执行本协议时，允许使用以下输入：

## 3.1 用户输入

- 用户对该 workspace 的口头描述
- 用户当前目标
- 用户对 workspace 边界的主观定义
- 用户补充的初始说明

## 3.2 manifest 输入

从 `workspace_manifest.json` 读取：

- `workspace_id`
- `display_name`
- `description`
- `bootstrap_status`
- `created_at`
- `updated_at`

manifest 是机器侧输入锚点，但它不等于最终 scope。

## 3.3 初始 assets

用户在当前 workspace 下上传的少量代表性材料。

## 3.4 parsing skill 返回结果

若有调用已有解析 skill，则其轻量摘要可作为输入之一。

---

# 4. Phase A · Scope Discovery

## 4.1 目标

先形成一个 scope draft，但不立即拍板。

本阶段要回答：

> 当前这个已 provision 的 workspace，想被当成什么研究容器？

---

## 4.2 scope discovery 必须识别的最小内容

### A. semantic_scope

从以下类型中选择最接近的一类：

- `mainline`
- `stage`
- `branch`
- `literature`
- `writing`
- `custom`

### B. time_mode

从以下类型中选择：

- `long_horizon`
- `current_stage`
- `short_sprint`
- `no_timeline`

### C. primary_object

从以下类型中选择：

- `concept_first`
- `task_first`
- `pack_first`
- `mixed`
- `undecided`

### D. exclusions

至少列出 1 到 3 条本 workspace 明显不负责的内容。

---

## 4.3 scope discovery 的依据

scope draft 可以参考：

- 用户表述
- `workspace_manifest.json.display_name`
- `workspace_manifest.json.description`

但此时不允许只凭 manifest 就认定最终 scope。

---

## 4.4 输出

形成内部草案：

```yaml
scope_draft:
  semantic_scope: ""
  time_mode: ""
  primary_object: ""
  exclusions: []
  confidence: low|medium|high
  basis:
    - user_statement
    - workspace_manifest
```

---

# 5. Phase B · Initial Asset Intake

## 5.1 目标

引导用户在当前 workspace 下先提供 1 到 5 个最能代表当前工作边界或当前工作焦点的初始 assets。

这一步的目标不是完整导入，而是让 bootstrap 不只依赖口头描述。

---

## 5.2 引导原则

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

---

## 5.3 intake 只做轻分类

本阶段不做深解析，只做：

### A. presence

- `present`
- `missing`

### B. sufficiency

- `sufficient`
- `partial`
- `insufficient`

### C. tendency

- `literature_heavy`
- `experiment_heavy`
- `writing_heavy`
- `mixed`
- `unknown`

---

## 5.4 输出

```yaml
initial_asset_status:
  presence: present|missing
  sufficiency: sufficient|partial|insufficient
  tendency: literature_heavy|experiment_heavy|writing_heavy|mixed|unknown
  asset_paths: []
  notes: []
```

---

## 5.5 边界

- 没有初始 assets，也允许轻量初始化
- 但必须显式记录 `missing`
- 不得将本阶段扩展为完整 ingest
- 不得读取其他 workspace 的 assets

---

# 6. Phase C · Asset Parse Handoff

## 6.1 目标

如当前 workspace 已有代表性初始 assets，则在必要时调用已有 parsing skill，获取可供 bootstrap 使用的轻量解析结果。

---

## 6.2 职责边界

### BOOTSTRAP 不负责

- pdf 深解析
- csv 内容抽取
- 图谱判读
- 结构化来源锚点实现
- asset-to-memory 映射实现

### 这些统一由已有 skill 负责

- asset 解析
- 内容提炼
- source linking
- 输出可被初始化消费的轻量摘要

---

## 6.3 BOOTSTRAP 在这里只做三件事

1. 判断是否需要触发 parsing skill
2. 将当前 workspace 的初始 assets 交给对应 skill
3. 接收轻量结果并用于后续 scope confirmation 与 generation plan

---

## 6.4 允许消费的 parsing 结果

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

说明：

- `likely_role`：该 asset 更像支撑 `Concept / Task / Pack` 中哪类对象
- `scope_signal`：对 scope 的支持或修正信号
- `source_summary`：可用于初始化文件的来源摘要

---

## 6.5 未触发 skill 时

也必须显式记录：

```yaml
parse_handoff_result:
  used: false
  reason: "..."
```

---

# 7. Phase D · Scope Confirmation

## 7.1 目标

结合：

- 用户表述
- manifest
- 初始 assets
- parsing skill 结果

正式确认当前 workspace 的最小语义边界。

---

## 7.2 必须确认的内容

```yaml
confirmed_scope:
  semantic_scope: ""
  time_mode: ""
  primary_object: ""
  exclusions: []
  evidence_basis:
    - user_statement
    - workspace_manifest
    - initial_assets
    - parse_handoff
```

---

## 7.3 输出文件

本阶段必须生成：

- `memory/identity/workspace_scope.md`

---

## 7.4 `workspace_scope.md` 最小内容要求

该文件至少应包含：

### A. Workspace Purpose

一句话说明本 workspace 是什么研究容器。

### B. Semantic Scope

明确其属于：

- `mainline / stage / branch / literature / writing / custom`

### C. Time Mode

明确其时间语义。

### D. Primary Work Object

明确其初始化后更偏向：

- `Concept`
- `Task`
- `Pack`
- 或 mixed

### E. Exclusions

明确它不负责什么。

### F. Initialization Evidence Basis

说明该判断来自：

- 用户表述
- manifest
- 哪些初始 assets
- 是否用了 parsing skill

---

# 8. Phase E · Generation Plan

## 8.1 目标

把 confirmed scope 翻译成初始化动作。

本阶段要回答：

- 哪些文件必须生成
- 哪些文件条件生成
- 哪些文件应显式跳过
- 首批 Layer3 应如何起手

---

## 8.2 必须形成的 generation plan

```yaml
bootstrap_plan:
  bootstrap_runtime_workspace_id: ""
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

## 8.3 generation 原则

### must_generate

只保留最小骨架文件。

### conditional_generate

只有在 scope 明确需要时才生成。

### skip_by_design

若旧版默认文件不适合本 workspace，必须显式记为有意跳过。

---

## 8.4 不得默认生成的旧行为

除非 generation plan 明确要求，否则不得默认生成：

- `memory/timeline/180d_index.md`
- `memory/concepts/CONCEPT_<topic>.md`
- `memory/tasks/TASK_bootstrap_initial_questions.md`
- `memory/identity/lab_context.md`

---

# 9. Phase F · Minimal Identity Generation

## 9.1 目标

生成后续控制层快速拿上下文所需的最小 identity 骨架。

---

## 9.2 默认必须生成的文件

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

---

## 9.3 `project.md` 的职责

`project.md` 不再承担 workspace 命名元数据职责。
workspace 命名与生命周期状态由 `workspace_manifest.json` 承担。

`project.md` 只负责写 agent 可读内容，例如：

- 当前 workspace 的目的
- 它与整体研究主线的关系（若存在）
- 当前近期交付或当前工作焦点
- 当前主要不确定性
- 当前工作对象偏向

---

## 9.4 条件生成：`lab_context.md`

仅当 confirmed scope 明显包含实验推进语义时，才允许生成：

- `memory/identity/lab_context.md`

例如：

- `mainline`
- `stage`
- 实验导向的 `branch`

如果 workspace 是：

- `writing`
- `literature`
- 非实验导向 `custom`

则默认跳过，或改用更轻替代：

- `memory/identity/work_context.md`

---

# 10. Phase G · Timeline Generation（Conditional）

## 10.1 目标

timeline 是 scope 驱动的条件产物，不是 runtime 成立的前提。

---

## 10.2 条件分支

### 若 `time_mode = long_horizon`

生成：

- `memory/timeline/180d_index.md`

### 若 `time_mode = current_stage`

生成：

- `memory/timeline/current_stage.md`

### 若 `time_mode = short_sprint`

生成：

- `memory/timeline/current_sprint.md`

### 若 `time_mode = no_timeline`

不生成 timeline 文件。

---

## 10.3 约束

- timeline 是否生成，不影响 workspace runtime 成立
- timeline 只影响后续 agent 如何理解时间推进
- 不得为了“显得完整”而硬写长期路线图

---

# 11. Phase H · Layer3 Seed Generation（Conditional）

## 11.1 目标

根据 confirmed scope 决定是否 seed Layer3，以及从哪类对象起手。

---

## 11.2 seed_strategy 允许值

- `concept_first`
- `task_first`
- `pack_first`
- `mixed_seed`
- `no_seed`

---

## 11.3 条件分支

### A. `concept_first`

适用于：

- `mainline`
- 部分主题导向 `literature`

允许生成：

- 首个 `Concept`

### B. `task_first`

适用于：

- `stage`
- `branch`
- 实验推进型 workspace

允许生成：

- kickoff `Task`

### C. `pack_first`

适用于：

- `writing`
- 汇报导向 workspace
- 文献整合型 workspace

允许生成：

- kickoff `Pack`

### D. `mixed_seed`

仅在 generation plan 明确给出理由时使用。

### E. `no_seed`

适用于：

- 边界仍不稳定
- 初始材料不足
- 当前只完成 scope 初始化

此时允许 bootstrap 成功完成。
也就是说：

> Layer3 seed 的存在与否，不是 bootstrap 成功与否的硬前提。

---

## 11.4 来源要求

若当前 workspace 下存在初始 assets 且 parse handoff 已成功产出结果，则首批 Layer3 seed 应尽量带：

- source refs
- 初始化依据说明
- 对应 asset path 或来源摘要

不得生成无来源、无依据的空心 seed。

---

# 12. Phase I · Manifest Lifecycle Update

## 12.1 目标

将 bootstrap 从“说明文”变成“状态协议”。

---

## 12.2 状态流转规则

`workspace_manifest.json` 的生命周期更新不由 BOOTSTRAP agent 通过普通写文件工具完成，
而由 5.3 的 workspace runtime / bootstrap runner 负责。

### 进入 bootstrap 前

如果 manifest 状态为：

- `pending`
- 或 `failed`

则开始执行前，runner 应更新为：

- `running`

并同步更新：

- `updated_at`

### 成功完成后

初始化成功后，runner 必须写回 manifest：

- `bootstrap_status = completed`
- `updated_at = now`

可选地补充：

- `last_bootstrap_error = ""`

### 失败时

若 bootstrap 中途失败，runner 应写回 manifest：

- `bootstrap_status = failed`
- `updated_at = now`

建议可选记录：

- `last_bootstrap_error`

### completed 后的约束

一旦 `bootstrap_status = completed`：

- 后续请求不再进入 bootstrap 主流程
- 后续行为由正常 workspace runtime routing 处理

---

# 13. Phase J · Completion Summary and Bootstrap-to-Active Handoff

## 13.1 目标

输出初始化结论，并把该 workspace 从 bootstrap 交回 active runtime。

---

## 13.2 completion summary 必须包含

```yaml
bootstrap_completion_summary:
  workspace_id: ""

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
  manifest_status_after_bootstrap: ""

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

## 13.3 `default_context_priority` 要求

必须明确后续控制层默认优先读什么。

例如：

- 固定脊梁优先
- 写作型优先 Pack
- 实验阶段型优先 active Task + lab context
- 文献型优先 relevant Pack / Concept / literature-derived notes

---

## 13.4 Bootstrap-to-Active handoff 条件

只有在以下条件全部满足时，才算 handoff 完成：

1. `workspace_scope.md` 已生成
2. generation plan 已执行完毕
3. completion summary 已输出
4. runner 已将 manifest 写为 `completed`

此后：

> 当前 workspace 进入 active 状态。
> 后续所有请求都按正常 workspace runtime 执行，而不再进入 bootstrap 主流程。

---

# 14. Failure Handling

## 14.1 失败时的原则

若初始化过程中出现问题：

- 应尽量保留已经成功生成的最小文件
- runner 必须更新 manifest 状态为 `failed`
- 必须显式记录失败原因
- 不得伪装为 completed
- 不得因为局部失败就删除整个 workspace provision 结果

---

## 14.2 允许的保守降级

即使以下情况发生，也允许 bootstrap 以较轻方式完成或部分完成：

- 没有初始 assets
- 初始 assets 不足
- parse skill 未触发
- parse skill 返回结果有限
- 当前不适合 seed Layer3

但这些都必须在 summary 中显式记录。

---

# 15. Guardrails

以下规则为红线，不得违反。

## 15.1 关于 workspace

- 不要默认每个 workspace 都是完整科研主线
- 不要将 workspace type、route、skill category 混为一谈

## 15.2 关于与 5.3 的边界

- 不要让 BOOTSTRAP 负责创建 workspace
- 不要让 BOOTSTRAP 负责切换 runtime
- 不要让 BOOTSTRAP 接管请求级 workspace routing
- 不要让 BOOTSTRAP 替代 `workspace_manifest.json` 的机器状态职责

## 15.3 关于初始化复杂度

- 不要把 scope discovery 做成长问卷
- 不要引入多 agent、数据库、复杂审批流
- 不要把初始化扩展成完整 ingest 系统

## 15.4 关于文件生成

- 不要默认每个 workspace 都生成 `180d_index.md`
- 不要默认每个 workspace 都 seed `Concept`
- 不要默认每个 workspace 都生成 bootstrap task
- 不要默认每个 workspace 都生成 `lab_context.md`

## 15.5 关于 assets

- bootstrap 可以请求少量初始 assets 辅助初始化
- 但不得把自己扩展为完整资产解析器
- 资产解析必须通过已有 skill 完成
- 若无初始 assets，允许轻量初始化，但必须显式记录缺口
- 资产读取、解析和写回必须严格限定在当前 workspace 范围内

## 15.6 关于用户主导权

- bootstrap 可以帮助归纳和确认 scope
- 但不得完全替用户拍板研究边界
- 当用户表述与初始材料冲突时，应显式提示并请求确认，而不是静默覆盖

## 15.7 关于退出

- 初始化完成后，`BOOTSTRAP.md` 不再参与常驻控制层注入
- 后续行为由 Control Plane + Data Plane + Trace Plane 共同驱动

---

# 16. Final Statement

> 本协议假定当前 workspace 已完成技术层 provision。
> 它的任务不是生成一套默认完整科研项目模板，而是帮助用户用“意图 + manifest + 初始材料”共同定义 workspace 的最小边界，再生成与之相称的初始化骨架，并由 bootstrap runner 将该 workspace 正式推进到 active 状态。
