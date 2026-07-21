# one_click_D_20260320_232505 结果分析与 Badcase（重扫版）

## 1. 分析范围

- 分析对象：`backend/auto_eval/eval_runs/one_click_D_20260320_232505`
- 场景：`scenario_D`
- 主题：写作与 Pack 闭环评测
- 重扫方法：
  1. 复扫 `overall_summary.json` 与 30 条 turn 结果 json
  2. 延续当前报告里已经挑出的 5 个 priority badcase
  3. 对每条 case 做多标签标记，再统计标签占比

## 2. 核心结论

- 总分：`90.79`
- 通过率：`90.00%`（`27/30`）
- 3 个未过线 turn 全部来自 `session_001_bootstrap`
- 第二大类问题是“写作对象已经判断对了，但没有压成真正 pack-quality 的交付件”
- 如果只把 bootstrap 三轮拉到 `85`，场景均分可从 `90.79 -> 92.88`，通过率可提升 `+10 个百分点`

一句话判断：D 场景不是不会做 thesis/storyline/gapmap，而是开场识别不到 `pack-first`，后续又容易从交付件退回成长篇说明文。

## 3. 标签体系

| 标签 | 含义 | 典型外显症状 |
|---|---|---|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 开场仍被通用初始化模板劫持，没有切进写作/Pack 容器 | 回 scope YAML，而不是交付件优先级 |
| `PACK_OBJECT_NOT_COMPRESSED` | 回答有内容，但没压成交付件形态 | 更像长文分析，不像 board/matrix/pack |
| `AUTHORITY_LABEL_MISSING` | 没讲清 final deck / 工作文档 / 参考素材的 authority level | 用户无法判断哪个能直接写入交付件 |
| `ARTIFACT_EXECUTION_GAP` | 用户要求落盘 pack，但没有真正生成文件 | `write_file` 缺失，artifact 不存在 |
| `MEMORY_REUSE_SIGNAL_WEAK` | prior pack / workdoc / timeline 承接不够显式 | trace/回答里的复用痕迹弱 |
| `OVERCLAIM_STYLE_RISK` | 叙事有把 bridge 线包装成 thesis 主证的风险 | 语言过满，边界不够硬 |

## 4. 标签统计

### 4.1 Priority badcase 集合（n=5）

| 标签 | case 数 | 占比 |
|---|---:|---:|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 3 | `60%` |
| `PACK_OBJECT_NOT_COMPRESSED` | 2 | `40%` |
| `AUTHORITY_LABEL_MISSING` | 2 | `40%` |
| `ARTIFACT_EXECUTION_GAP` | 1 | `20%` |
| `MEMORY_REUSE_SIGNAL_WEAK` | 1 | `20%` |
| `OVERCLAIM_STYLE_RISK` | 1 | `20%` |

### 4.2 全量 30 turn 的结构化信号

- `content_fail = 3`
- `content_partial = 4`
- `trace_fail = 1`
- `artifact_fail = 1`
- `judge_partial = 6`
- `unsupported_specificity = 5/30 = 16.67%`
- `absolute_overclaim_turns = 6/30 = 20.00%`

## 5. 先修哪两类问题

### P0：`BOOTSTRAP_TEMPLATE_HIJACK`

- badcase 占比：`60%`
- 业务影响：3 个最低分 turn 全集中在这类问题
- 预期收益：修掉后，场景通过率可从 `90%` 拉到 `100%`

PM 级修复建议：

- `Prompt`
  - 给 D 场景单独写 `PACK_FIRST_BOOTSTRAP` prompt，首轮必须回答 `章节主线 / 图组缺口 / 组会交付件` 谁先做
  - 第二轮固定回答 `哪个 pack 最有复用价值`、`哪个文件是权威来源`、`哪个只能当参考`
- `Log / Eval`
  - 增加 `pack_container_alignment_rate`
  - bootstrap 三轮若未命中 pack-object 关键词，直接 fail
- `Code / Product`
  - 写作容器走独立 bootstrap route，不复用 literature/concept 初始化模板
  - 对 bootstrap 收尾 turn 强制写 `PACK_bootstrap_kickoff.md`
- `Model / Tuning`
  - 先修 prompt/router，暂不建议优先换基模

### P1：`PACK_OBJECT_NOT_COMPRESSED` + `AUTHORITY_LABEL_MISSING`

- badcase 占比：`40%`
- 业务影响：即使分数过线，用户也会觉得“内容好，但不够能交付”

PM 级修复建议：

- `Prompt`
  - 对 gapmap/storyline/revision 类任务强制输出 `board / table / matrix`，禁止默认写成长文说明
  - pack 类回答强制加入 `权威来源 / 工作文档 / 参考素材` 三层 authority 标记
- `Log / Eval`
  - 增加 `pack_shape_coverage` 指标，检查是否真的生成表格化交付件
  - 对 authority level 新增专门 scorer
- `Code / Product`
  - pack 模板库内置 `authority_level`、`reusability`、`next_action`
- `Model / Tuning`
  - 采集 thesis gapmap / storyboard / revision matrix 的高质量样本做 few-shot

## 6. 逐 Case 标签清单

### Case 1：`session_001 / turn_01`，分数 `65.00`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`AUTHORITY_LABEL_MISSING`
- 证据：judge 缺 `写作/Pack 容器 / 哪些交付件最值得整理成 pack / 章节主线 / 图组缺口 / 组会交付件`
- 错误总结：用户在问“先整理哪个交付件”，模型却回了通用初始化模板
- PM 动作：首轮改成交付件优先级板

### Case 2：`session_001 / turn_02`，分数 `75.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`AUTHORITY_LABEL_MISSING`
- 证据：judge 缺 `哪个 pack 最有复用价值 / 哪个文件是权威来源 / 哪个只能当参考素材`
- 错误总结：没有把 authority level 变成可执行判断
- PM 动作：固定输出 authority triage

### Case 3：`session_001 / turn_03`，分数 `51.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`ARTIFACT_EXECUTION_GAP`
- 证据：`trace_fail`、`artifact_fail`，`PACK_bootstrap_kickoff.md` 未生成
- 错误总结：初始化闭环没完成，pack 容器没有 seed
- PM 动作：artifact turn 强制落盘

### Case 4：`session_002 / turn_02`，分数 `80.33`

- 标签：`PACK_OBJECT_NOT_COMPRESSED`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：content 只命中 1 个关键术语；judge 虽 pass，但缺 `最先补会影响最大的 / 同时解锁多少后续写作/汇报工作`
- 错误总结：结论方向对，但没压成最利于写作管理的 leverage board
- PM 动作：gapmap 输出改成排序表 + leverage 列

### Case 5：`session_009 / turn_02`，分数 `80.67`

- 标签：`PACK_OBJECT_NOT_COMPRESSED`、`OVERCLAIM_STYLE_RISK`
- 证据：judge partial；缺 `会缺哪类图 / 哪类对照 / 哪类解释 / 章节之间接不起来`
- 错误总结：storyline 有内容，但没有压成“缺图/缺对照/缺解释”的 pack 形态
- PM 动作：storyline 默认输出 gap table，而不是散文式解释

## 7. 建议排期

1. 第 1 周：修 bootstrap 的 pack-first route
2. 第 2 周：给所有写作对象加 authority-level 模板
3. 第 3 周：把 gapmap/storyline/revision 统一压成 matrix 输出

## 8. 最终判断

这份 run 说明 D 场景的问题不在“内容理解”，而在“交付件对象化”。如果要让产品叙事更像真实科研工作流，D 场景最值得优先补的是 `pack-first bootstrap` 和 `交付件形态约束`。
