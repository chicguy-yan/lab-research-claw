# one_click_C_20260320_232505 结果分析与 Badcase（重扫版）

## 1. 分析范围

- 分析对象：`backend/auto_eval/eval_runs/one_click_C_20260320_232505`
- 场景：`scenario_C`
- 主题：实验与 Task 闭环评测
- 重扫方法：
  1. 复扫 `overall_summary.json` 与 30 条 turn 结果 json
  2. 延续当前报告里已经挑出的 5 个 priority badcase
  3. 对每条 case 做多标签标记，再统计标签占比

## 2. 核心结论

- 总分：`91.72`
- 通过率：`90.00%`（`27/30`）
- 3 个未过线 turn 全部来自 `session_001_bootstrap`
- 第二大类问题不是“不会做 task”，而是 `unsupported_specificity` 偏高，导致实验设计看起来很强，但 source-grounded honesty 不够稳
- 如果只把 bootstrap 三轮拉到 `85`，场景均分可从 `91.72 -> 93.81`，通过率可提升 `+10 个百分点`

一句话判断：C 场景的 task 化能力已经可用，但“先落 task 对象”这件事还不稳，而且进入矩阵/依赖图任务后容易写得过满。

## 3. 标签体系

| 标签 | 含义 | 典型外显症状 |
|---|---|---|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 开场被通用初始化模板劫持，没有切到 task-first | 回 scope YAML，不回答先做哪类 task |
| `TASK_OBJECT_NOT_LANDED` | 没把用户要的 checklist/matrix/minimal closure 落成对象 | 回答抽象，不像实验台旁边可执行任务 |
| `ARTIFACT_EXECUTION_GAP` | 用户要求写 pack/task，但没真正落盘 | `write_file` 缺失，artifact 不存在 |
| `UNSUPPORTED_SPECIFICITY` | 主动补出过多实验细节、样品编码、时间点、方法池 | 看起来专业，但来源支撑不够 |
| `OVER_COMPLETED_DEPENDENCY_GRAPH` | 依赖图和筛选矩阵补得太满 | 多出用户没要求的对照链和节点 |
| `MEMORY_REUSE_SIGNAL_WEAK` | trace/回答里 prior memory 承接信号不够强 | memory read 弱，跨 session 复用不显式 |

## 4. 标签统计

### 4.1 Priority badcase 集合（n=5）

| 标签 | case 数 | 占比 |
|---|---:|---:|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 3 | `60%` |
| `TASK_OBJECT_NOT_LANDED` | 3 | `60%` |
| `UNSUPPORTED_SPECIFICITY` | 2 | `40%` |
| `OVER_COMPLETED_DEPENDENCY_GRAPH` | 2 | `40%` |
| `MEMORY_REUSE_SIGNAL_WEAK` | 2 | `40%` |
| `ARTIFACT_EXECUTION_GAP` | 1 | `20%` |

### 4.2 全量 30 turn 的结构化信号

- `content_fail = 3`，全部来自 bootstrap 三轮
- `trace_fail = 1`
- `artifact_fail = 1`
- `judge_partial = 5`
- `unsupported_specificity = 9/30 = 30.00%`
- `absolute_overclaim_turns = 4/30 = 13.33%`

## 5. 先修哪两类问题

### P0：`BOOTSTRAP_TEMPLATE_HIJACK` + `TASK_OBJECT_NOT_LANDED`

- badcase 占比：`60%`
- 业务影响：3 个最低分 turn 全在这里，且直接阻断 task-first 初始化
- 预期收益：修掉后，场景通过率可从 `90%` 拉到 `100%`

PM 级修复建议：

- `Prompt`
  - 给 C 场景单独做 `TASK_FIRST_BOOTSTRAP` prompt，要求首轮必须在 `合成 checklist / 性能筛选矩阵 / 最小机理闭环` 三者中做优先级判断
  - 第二轮固定回答槽位：`本周要做的实验`、`先产出哪类 task`、`暂不展开哪些线`
- `Log / Eval`
  - 新增 `task_object_landing_rate`
  - bootstrap 三轮未命中 task-object 关键词时直接 fail，而不是靠 judge partial 兜底
- `Code / Product`
  - session_001 使用独立 route 或独立 system prompt，不复用通用 bootstrap
  - artifact turn 增加 `must_write_pack` 守卫
- `Model / Tuning`
  - 优先做 prompt/router 修复
  - 若仍常回长篇 scope 文，再做 task-first few-shot 或 SFT

### P1：`UNSUPPORTED_SPECIFICITY` + `OVER_COMPLETED_DEPENDENCY_GRAPH`

- badcase 占比：`40%`
- 全量信号：`unsupported_specificity = 30%`
- 业务影响：这类问题会制造“过程分高但用户不放心”的隐性风险

PM 级修复建议：

- `Prompt`
  - 对 matrix/dependency 类问题加明确约束：不允许补充未在来源中出现的样品编码、固定时间点、额外方法池
  - 强制输出 `已知 / 推测 / 待确认` 三栏
- `Log / Eval`
  - 细化 `unsupported_specificity`，区分“合理抽象”与“伪精确”
  - 对实验条件类 claim 增加 `claim_grounding_table`
- `Code / Product`
  - matrix/dag 生成器默认压缩成最小可执行版，而不是专家建议散文
- `Model / Tuning`
  - 收集“少写更准”的 task 样本，专门抑制实验细节过拟合

## 6. 逐 Case 标签清单

### Case 1：`session_001 / turn_01`，分数 `65.00`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`TASK_OBJECT_NOT_LANDED`
- 证据：judge 缺 `实验/Task 容器 / benchmark rationale / 合成 checklist / 性能筛选矩阵 / 最小机理闭环`
- 错误总结：用户问“先从哪类 task 起手”，模型答“scope 如何确认”
- PM 动作：把优先级判断写成必答字段

### Case 2：`session_001 / turn_02`，分数 `75.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`TASK_OBJECT_NOT_LANDED`
- 证据：judge 缺 `本周要做的实验 / 拆成能执行的 task / 暂时不该展开哪些线`
- 错误总结：仍然没有把实验 workspace 压到近期可执行对象
- PM 动作：第二轮改成固定 task board 输出

### Case 3：`session_001 / turn_03`，分数 `51.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`ARTIFACT_EXECUTION_GAP`
- 证据：`trace_fail`、`artifact_fail`，`PACK_bootstrap_kickoff.md` 未生成
- 错误总结：初始化闭环没收住，导致后续 task-first 记忆层没有 seed pack
- PM 动作：artifact turn 强制 `write_file`

### Case 4：`session_003 / turn_01`，分数 `80.67`

- 标签：`UNSUPPORTED_SPECIFICITY`、`OVER_COMPLETED_DEPENDENCY_GRAPH`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：`unsupported_specificity = true`；judge 仍缺 `性能+动力学筛选矩阵 / 材料横轴 / 性能指标`
- 错误总结：矩阵设计能力强，但补了太多来源未证实的结构化细节
- PM 动作：给筛选矩阵加最小字段 contract，不允许自由扩表

### Case 5：`session_009 / turn_01`，分数 `85.33`

- 标签：`UNSUPPORTED_SPECIFICITY`、`OVER_COMPLETED_DEPENDENCY_GRAPH`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：`unsupported_specificity = true`；judge 虽 pass，但关键信息仍缺失
- 错误总结：章节依赖图可用，但有过度补全倾向，容易让用户以为这些依赖已被实验验证
- PM 动作：依赖图默认分成 `已锁定依赖 / 推测依赖 / 待验证依赖`

## 7. 建议排期

1. 第 1 周：单独修 bootstrap 的 task-first route
2. 第 2 周：给 matrix / dependency 任务加 `claim_grounding_table`
3. 第 3 周：把 `unsupported_specificity` 拆成实验条件、样品编码、方法池三类子指标

## 8. 最终判断

这份 run 已经证明 C 场景“能做 task”不是问题，真正的问题是“什么时候该收口到最小 task 对象”还不稳。先修 bootstrap，再压制 unsupported specificity，整体体验会明显比继续加知识更有效。
