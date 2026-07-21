# Phase 5.4 开发计划

## 一、目标

Phase 5.4 的目标，不是继续补一个 bootstrap 状态卡片，而是把 bootstrap 做成一个严格、可交互、可完成交接的初始化流程。

用户进入一个新建 workspace 后，不应直接进入普通 chat，而应先通过 bootstrap 引导完成以下事情：

1. 明确这个 workspace 到底是什么语义容器
2. 明确它不负责什么
3. 明确当前更适合从哪类工作对象起手
4. 提供最少但足够的初始上下文与代表性材料
5. 生成与该 scope 相称的最小骨架
6. 将 workspace 从 bootstrap 态切换到正常可用态

一句话：

> 5.4 要把 bootstrap 从“状态门禁”升级为“严格协议驱动的初始化对话流”。

## 二、当前问题

Phase 5.3 已经完成了 workspace runtime 隔离、manifest 生命周期字段和前端 gate，但仍有明显缺口：

1. 前端只有 gate，没有真正的 bootstrap 交互流
2. 用户不知道该上传什么，也不知道该如何描述 workspace 需求
3. bootstrap 生命周期虽然有定义，但没有真正按协议分阶段执行
4. 普通 chat、bootstrap chat、manifest 状态流转之间没有形成严格闭环
5. 创建 workspace 后，用户只知道“还不能聊天”，但不知道下一步该做什么

## 三、5.4 的产品定义

5.4 中的 bootstrap 必须同时满足三个层面：

### 1. 交互层

表现形态是 chat-like guided flow。

也就是说：

- 用户通过几轮自然对话完成初始化
- 不是一次性长表单
- 也不是只显示一段说明文字

### 2. 协议层

bootstrap 必须严格遵守 `BOOTSTRAP.md` 的阶段定义推进，不能跳过关键阶段，也不能直接简化为“一轮问答后自动完成”。

### 3. 生命周期层

bootstrap 在状态上独立于普通 chat。

要求：

- bootstrap 未完成前，不能进入普通 chat
- bootstrap 完成后，自动 handoff 给普通 workspace runtime
- manifest 生命周期更新由 runner 负责，不由普通 agent 写文件逻辑负责

## 四、必须实现的严格流程

Phase 5.4 按以下阶段实现 bootstrap：

### Phase A：Scope Discovery

目标：

先识别当前 workspace 想被定义成什么研究容器。

至少识别以下字段：

- `semantic_scope`
- `time_mode`
- `primary_object`
- `exclusions`

输出：

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

### Phase B：Initial Asset Intake

目标：

引导用户提供 1 到 5 个最具代表性的初始材料，帮助 bootstrap 不只依赖口头描述。

前端必须明确提示用户可以上传的材料类型，例如：

- 核心 pdf / 综述
- 当前组会 PPT
- 实验 csv / xlsx
- 实验记录 / md 笔记
- 写作草稿
- 图谱 / figure 草稿

输出：

```yaml
initial_asset_status:
  presence: present|missing
  sufficiency: sufficient|partial|insufficient
  tendency: literature_heavy|experiment_heavy|writing_heavy|mixed|unknown
  asset_paths: []
  notes: []
```

### Phase C：Asset Parse Handoff

目标：

对当前 workspace 下的代表性材料做轻量解析交接，而不是完整 ingest。

边界：

- 不做深度 pdf 解析
- 不做复杂表格抽取
- 不做完整知识图谱构建

输出：

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

### Phase D：Scope Confirmation

目标：

结合用户描述、manifest、初始材料和轻量解析结果，正式确认当前 workspace 的最小语义边界。

必须生成文件：

- `memory/identity/workspace_scope.md`

输出：

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

### Phase E：Generation Plan

目标：

把 confirmed scope 翻译成初始化动作。

必须回答：

- 哪些文件必须生成
- 哪些文件条件生成
- 哪些文件应显式跳过
- 首批 Layer3 应从哪里起手

输出：

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

### Phase F：Minimal Identity Generation

默认必须生成：

- `memory/identity/workspace_scope.md`
- `memory/identity/project.md`
- `memory/identity/context_budget.md`（若当前系统仍使用该机制）

条件生成：

- `memory/identity/lab_context.md`
- 或 `memory/identity/work_context.md`

### Phase G：Timeline Generation（条件）

按 `time_mode` 决定生成：

- `memory/timeline/180d_index.md`
- `memory/timeline/current_stage.md`
- `memory/timeline/current_sprint.md`
- 或不生成 timeline

### Phase H：Layer3 Seed Generation（条件）

按 `seed_strategy` 决定是否生成：

- kickoff `Concept`
- kickoff `Task`
- kickoff `Pack`
- 或 `no_seed`

要求：

- 若已有初始材料，则 seed 尽量带来源依据
- 不允许无依据生成空心 seed

### Phase I：Manifest Lifecycle Update

状态更新必须由 bootstrap runner 负责，而不是由普通文件写入逻辑负责。

严格流转规则：

- `pending | failed -> running`
- `running -> completed`
- `running -> failed`

约束：

- `completed` 后不再进入 bootstrap 主流程
- 普通 chat 不得隐式接管 bootstrap

### Phase J：Completion Summary and Bootstrap-to-Active Handoff

目标：

输出初始化结论，并把 workspace 交回正常运行态。

completion summary 至少包含：

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
```

handoff 只有在以下条件全部满足时才成立：

1. `workspace_scope.md` 已生成
2. generation plan 已执行完毕
3. completion summary 已输出
4. manifest 已写为 `completed`

## 五、前端交互要求

5.4 的前端不能只给用户一个“开始初始化”按钮，必须真正承担“引导用户完成初始化”的职责。

### 1. 明确告诉用户你需要什么

前端 bootstrap 界面必须明确说明：

- 这个 workspace 是做什么的
- 它不负责什么
- 当前主要工作对象偏向什么
- 该上传哪些代表性材料

### 2. 明确告诉用户该怎么描述

前端应提供可参考的表达模板，例如：

- 这是一个文献整理 workspace，主要用于……
- 这是一个阶段推进 workspace，当前只负责……
- 这是一个写作 / 汇报 workspace，目标是……

### 3. 明确告诉用户“最小可用上下文”是什么

即使用户暂时没有很多材料，也至少应能在前端看到以下最小要求：

- 一句话说明 workspace 的目的
- 1 到 3 条 exclusions
- 当前偏向 `Concept / Task / Pack` 哪类工作对象
- 如果方便，上传 1 到 5 个代表性文件

### 4. bootstrap 中的前端状态切换

前端必须明确分三态：

- `pending | failed`：显示 bootstrap gate + 初始化入口
- `running`：显示 bootstrap 专用 chat，而不是普通 chat
- `completed`：显示正常 chat

## 六、后端实现要求

后端需要引入一个真正的 bootstrap runner，负责：

- bootstrap 专用 session
- bootstrap 阶段状态推进
- scope draft / confirmed scope / generation plan
- 文件生成
- manifest 生命周期更新
- completion summary 输出

同时需要补上普通 chat 的后端硬 gate：

- 当 `bootstrap_status != completed` 时，不允许进入普通 chat
- bootstrap 必须通过专用 route 或专用模式进入 runner

## 七、文件生成约束

Phase 5.4 必须遵守以下文件生成原则：

### must_generate

只生成最小但够用的初始化骨架。

### conditional_generate

只有在 scope 明确要求时才生成，不得为了显得完整而乱补文件。

### skip_by_design

若旧版模板文件不适合当前 workspace，必须显式记为“有意跳过”。

不得默认生成的旧行为包括：

- `memory/timeline/180d_index.md`
- `memory/concepts/CONCEPT_<topic>.md`
- `memory/tasks/TASK_bootstrap_initial_questions.md`
- `memory/identity/lab_context.md`

## 八、验收标准

5.4 至少应满足以下验收：

1. 新建 workspace 后，不进入普通 chat，而进入 bootstrap 入口
2. 点击开始初始化后，进入 bootstrap 专用聊天流
3. 用户即使不清楚该上传什么，也能通过前端提示完成最小初始化输入
4. bootstrap 严格执行 Phase A-J，不允许跳过 scope confirmation 与 generation plan
5. `workspace_scope.md` 必须在完成前生成
6. manifest 必须由 runner 更新，而不是由普通写文件逻辑更新
7. bootstrap 成功后自动进入正常 chat
8. bootstrap 失败后保留最小生成结果并允许 retry

## 九、开发顺序

建议按以下顺序推进：

1. 明确前端 bootstrap 引导结构与文案
2. 实现后端 bootstrap runner 状态机
3. 接入 bootstrap 专用 chat 路由
4. 实现 scope confirmation 与 generation plan 预览
5. 实现最小 identity / timeline / seed 文件生成
6. 接入 manifest 生命周期更新
7. 补齐测试、手测清单与失败重试路径

## 十、关键原则

1. bootstrap 不是普通 chat
2. bootstrap 不是静态表单
3. bootstrap 是“严格协议 + 交互引导 + 生命周期闭环”
4. 前端必须承担“教会用户如何初始化”的责任，不能把理解成本全部甩给用户
5. 初始化成功不是“文件越多越好”，而是后续系统能快速理解这个 workspace 是什么、不是什么、该从哪起手
