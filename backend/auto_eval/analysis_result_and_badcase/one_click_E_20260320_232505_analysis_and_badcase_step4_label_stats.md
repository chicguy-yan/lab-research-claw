# one_click_E_20260320_232505 结果分析与 Badcase（重扫版）

## 1. 分析范围

- 分析对象：`backend/auto_eval/eval_runs/one_click_E_20260320_232505`
- 场景：`scenario_E`
- 主题：跨闭环桥接评测
- 重扫方法：
  1. 复扫 `overall_summary.json` 与 30 条 turn 结果 json
  2. 延续当前报告里已经挑出的 5 个 priority badcase
  3. 对每条 case 做多标签标记，再统计标签占比

## 2. 核心结论

- 总分：`91.77`
- 通过率：`90.00%`（`27/30`）
- 3 个未过线 turn 全部来自 `session_001_bootstrap`
- 第二大类问题不是“不会做 bridge/eval”，而是“能分析，但还不够最小可执行”
- 如果只把 bootstrap 三轮拉到 `85`，场景均分可从 `91.77 -> 93.86`，通过率可提升 `+10 个百分点`

一句话判断：E 场景已经能输出高质量 bridge/eval 分析，但开场识别不到 bridge container，进入 contract 任务后又容易滑回系统设计散文。

## 3. 标签体系

| 标签 | 含义 | 典型外显症状 |
|---|---|---|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 开场被通用初始化模板劫持，没有切进 bridge/eval 容器 | 回 scope YAML，而不是 read-order / entrypoint |
| `SELECTIVE_READ_ORDER_NOT_ANSWERED` | 没回答“该读什么、暂不读什么、为什么” | read-order 不够具体 |
| `BRIDGE_PROTOCOL_NOT_MINIMAL` | 回答方向对，但没有压到最小字段和最小 stop rule | 更像架构说明，不像协议 |
| `FIELD_LANDING_WEAK` | 没把字段落到 loader / runner / scorer 的接口消费面 | 说抽象 schema，不说 runtime 必需字段 |
| `ARTIFACT_EXECUTION_GAP` | 用户要求写 pack，但没真正落盘 | `write_file` 缺失，artifact 不存在 |
| `MEMORY_REUSE_SIGNAL_WEAK` | prior mapping / read-order / handoff 承接不显式 | trace/回答的 memory 信号弱 |

## 4. 标签统计

### 4.1 Priority badcase 集合（n=5）

| 标签 | case 数 | 占比 |
|---|---:|---:|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 3 | `60%` |
| `SELECTIVE_READ_ORDER_NOT_ANSWERED` | 3 | `60%` |
| `BRIDGE_PROTOCOL_NOT_MINIMAL` | 2 | `40%` |
| `FIELD_LANDING_WEAK` | 2 | `40%` |
| `ARTIFACT_EXECUTION_GAP` | 1 | `20%` |
| `MEMORY_REUSE_SIGNAL_WEAK` | 2 | `40%` |

### 4.2 全量 30 turn 的结构化信号

- `content_fail = 3`
- `trace_fail = 1`
- `artifact_fail = 1`
- `judge_partial = 4`
- `unsupported_specificity = 2/30 = 6.67%`
- `absolute_overclaim_turns = 7/30 = 23.33%`

## 5. 先修哪两类问题

### P0：`BOOTSTRAP_TEMPLATE_HIJACK` + `SELECTIVE_READ_ORDER_NOT_ANSWERED`

- badcase 占比：`60%`
- 业务影响：直接阻断 bridge/eval 容器的首轮定位
- 预期收益：修掉后，场景通过率可从 `90%` 拉到 `100%`

PM 级修复建议：

- `Prompt`
  - 给 E 场景单独写 `BRIDGE_BOOTSTRAP_ENTRY` prompt，首轮必须回答 `package architecture / closure mapping / ecosystem map` 谁先读、为什么
  - 第二轮固定回答 `该读什么 / 暂不该读什么 / 为什么 / bridge-handoff 长什么样`
- `Log / Eval`
  - 新增 `bridge_entry_alignment_rate`
  - bootstrap 三轮未命中 bridge 入口词时直接 fail
- `Code / Product`
  - 桥接容器走独立 bootstrap route，不复用 research workspace 模板
  - bootstrap 收尾 turn 强制写 `PACK_bootstrap_kickoff.md`
- `Model / Tuning`
  - 先修 route 和 prompt，不建议先动基模

### P1：`BRIDGE_PROTOCOL_NOT_MINIMAL` + `FIELD_LANDING_WEAK`

- badcase 占比：`40%`
- 业务影响：会让回答“看起来对”，但实现者仍然不知道该怎么写 loader/runner/scorer

PM 级修复建议：

- `Prompt`
  - contract/schema 类任务强制输出三层：`字段名`、`由谁消费`、`为什么必须`
  - stop-rule 类任务强制输出 `可停在 bridge 层 / 必须回源` 二分表
- `Log / Eval`
  - 新增 `field_landing_coverage` 指标，检查是否显式提到 loader、runner、scorer 的消费点
  - 对 prompt contract 新增 “最小字段数 + 运行落地点” scorer
- `Code / Product`
  - 让 bridge 文档模板内置 `consumer=loader|runner|scorer|reporter`
- `Model / Tuning`
  - 采集一批“协议最小化”样本，减少系统设计散文倾向

## 6. 逐 Case 标签清单

### Case 1：`session_001 / turn_01`，分数 `65.00`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`SELECTIVE_READ_ORDER_NOT_ANSWERED`
- 证据：judge 缺 `跨闭环桥接容器 / benchmark / eval system / package architecture / closure mapping`
- 错误总结：用户问“从哪个桥接入口起手”，模型回了通用 scope YAML
- PM 动作：首轮改成桥接入口优先级判断

### Case 2：`session_001 / turn_02`，分数 `75.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`SELECTIVE_READ_ORDER_NOT_ANSWERED`
- 证据：judge 缺 `不是重新读完所有原始材料 / 该读什么 / 暂时不该读什么 / bridge/handoff`
- 错误总结：没有把 bridge 容器的 selective reading 说清楚
- PM 动作：第二轮固定输出 selective read-order

### Case 3：`session_001 / turn_03`，分数 `51.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`ARTIFACT_EXECUTION_GAP`
- 证据：`trace_fail`、`artifact_fail`，`PACK_bootstrap_kickoff.md` 未生成
- 错误总结：bridge 容器没有形成 seed pack，导致后续 handoff 层缺入口
- PM 动作：artifact turn 强制落盘

### Case 4：`session_002 / turn_02`，分数 `85.33`

- 标签：`BRIDGE_PROTOCOL_NOT_MINIMAL`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：judge 虽 pass，但缺 `closure 已经足够清晰 / 不能只停留在 bridge 层`
- 错误总结：stop rule 有价值，但不够二元，不够实现型
- PM 动作：stop rule 改成 `可停 / 必须回源` 明细表

### Case 5：`session_009 / turn_02`，分数 `85.33`

- 标签：`BRIDGE_PROTOCOL_NOT_MINIMAL`、`FIELD_LANDING_WEAK`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：judge 缺 `需要哪些字段 / runner / scorer 里落地`
- 错误总结：contract 方向对，但没把字段真正落到组件接口
- PM 动作：prompt contract 默认输出 `字段 -> 消费者 -> 校验规则`

## 7. 建议排期

1. 第 1 周：修 bridge bootstrap 的入口识别
2. 第 2 周：把 stop-rule 和 prompt-contract 都改成最小协议模板
3. 第 3 周：给 loader / runner / scorer 增加字段消费检查

## 8. 最终判断

这份 run 已经能支撑“我们有桥接层评测”的叙事，但还不够支撑“我们已经把 bridge/eval 协议完全落到实现接口”这类更强说法。先把 bootstrap 和最小协议模板修稳，产品叙事会更硬。
