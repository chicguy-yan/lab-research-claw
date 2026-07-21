# one_click_B_20260320_232505 结果分析与 Badcase（重扫版）

## 1. 分析范围

- 分析对象：`backend/auto_eval/eval_runs/one_click_B_20260320_232505`
- 场景：`scenario_B`
- 主题：文献与 Concept 闭环评测
- 重扫方法：
  1. 复扫 `overall_summary.json` 与 30 条 turn 结果 json
  2. 延续当前报告里已经挑出的 5 个 priority badcase
  3. 对每条 case 做多标签标记，再统计标签占比

## 2. 核心结论

- 总分：`91.76`
- 通过率：`86.67%`（`26/30`）
- 最低 4 个 turn 里，有 3 个都集中在 `session_001_bootstrap`
- 最高优先级问题不是“文献能力不够”，而是 `bootstrap 初始化模板劫持`
- 如果只把 bootstrap 三轮从当前分数拉到 `85`，场景均分可从 `91.76 -> 94.43`，通过率可直接提升 `+10 个百分点`

一句话判断：B 场景主体能力已经可用，但当前最伤整体体验的不是知识错，而是“开场没接题”和“证据层级标签不够硬”。

## 3. 标签体系

| 标签 | 含义 | 典型外显症状 |
|---|---|---|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 被通用初始化 YAML 劫持，没有直接回答用户要的 literature closure 起手动作 | 回 scope confirmation，不回答“先读什么/先写什么” |
| `READING_ENTRY_MISSING` | 没有把阅读入口、优先级、skip-by-design 讲清楚 | 缺“先读什么、暂不读什么、为什么” |
| `SOURCE_LAYER_LABEL_MISSING` | 没明确区分 paper / note / bridge inspiration | 来源边界列不完整，handoff 不够稳 |
| `ARTIFACT_EXECUTION_GAP` | 用户要写 pack/concept，但没有真正落盘 | `write_file` 缺失，artifact 不存在 |
| `MEMORY_REUSE_SIGNAL_WEAK` | 回答或 trace 没显式承接 prior memory | trace 没读 memory，回答也没引用前序产物 |
| `UNSUPPORTED_SPECIFICITY` | 细节写得像真，但来源支撑不够硬 | 压缩稿、复习稿、对照列写得过满 |

## 4. 标签统计

### 4.1 Priority badcase 集合（n=5）

| 标签 | case 数 | 占比 |
|---|---:|---:|
| `BOOTSTRAP_TEMPLATE_HIJACK` | 3 | `60%` |
| `READING_ENTRY_MISSING` | 3 | `60%` |
| `SOURCE_LAYER_LABEL_MISSING` | 2 | `40%` |
| `MEMORY_REUSE_SIGNAL_WEAK` | 2 | `40%` |
| `ARTIFACT_EXECUTION_GAP` | 1 | `20%` |
| `UNSUPPORTED_SPECIFICITY` | 1 | `20%` |

### 4.2 全量 30 turn 的结构化信号

- `content_fail = 3`，全部来自 bootstrap 三轮
- `trace_fail = 2`，都和 bootstrap / artifact 执行缺口有关
- `artifact_fail = 1`，即 `PACK_bootstrap_kickoff.md` 未生成
- `judge_partial = 5`，说明“语义上接题不够硬”的问题仍存在
- `unsupported_specificity = 2/30 = 6.67%`
- `absolute_overclaim_turns = 11/30 = 36.67%`

## 5. 先修哪两类问题

### P0：`BOOTSTRAP_TEMPLATE_HIJACK` + `READING_ENTRY_MISSING`

- badcase 占比：`60%`
- 业务影响：直接吞掉 3 个最低分 turn，是当前通过率差的主因
- 预期收益：单修这一类，可把 pass rate 从 `86.67%` 拉到 `96.67%`

PM 级修复建议：

- `Prompt`
  - 给 bootstrap 单独加 `B_BOOTSTRAP_LITERATURE_ENTRY` prompt，不允许输出通用 scope YAML 作为主答案
  - 把第一轮回答 contract 固定成：`先从哪条主线起手`、`paper vs note 证据层级`、`先读/暂不读/为什么`
- `Log / Eval`
  - 给 bootstrap 三轮单独加 hard check：如果 assistant 首屏出现 `confirmed_scope`、`Phase A-C`、`scope confirmation` 而未命中 `key_terms`，直接判 fail
  - 在报告里单独输出 `bootstrap_alignment_rate`
- `Code / Product`
  - 在 bootstrap route 增加场景化分流，B 场景默认进 literature-first bootstrap，而不是通用模板
  - 对 `session_001` 启用更强的 answer-shape validator
- `Model / Tuning`
  - 先不用急着换基模，优先做 prompt/router 修复
  - 若修完 prompt 后仍稳定回模板，再考虑做 bootstrap few-shot 或轻量 SFT

### P1：`SOURCE_LAYER_LABEL_MISSING`

- badcase 占比：`40%`
- 业务影响：不是最低分主因，但会直接伤害“科研可信度”和 handoff 复用性

PM 级修复建议：

- `Prompt`
  - 对 outline / handoff / reading queue 类问题，强制输出三列：`来自 review`、`来自我的笔记`、`从旁支材料借来的思路`
- `Log / Eval`
  - 新增 `source_layer_column_coverage` 指标，而不是只看泛化的关键词命中
- `Code / Product`
  - 对 `memory/concepts` 和 `memory/packs` 生成器增加 source-layer 模板片段
- `Model / Tuning`
  - 收集 20-30 条高质量文献闭环样本，专门训练“来源分层写法”

## 6. 逐 Case 标签清单

### Case 1：`session_001 / turn_01`，分数 `50.00`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`READING_ENTRY_MISSING`、`SOURCE_LAYER_LABEL_MISSING`
- 证据：`content_fail`；`trace_fail`；judge 缺失 `文献/Concept 容器 / 基线机制 / 论文原文 / 我的笔记 / 证据层级`
- 错误总结：模型回了通用初始化模板，没有回答“基线机制还是 Ce 迁移先起手”，也没给 evidence layer 切分
- PM 动作：直接改 bootstrap 首轮 prompt contract，并把 evidence-layer 变成必答字段

### Case 2：`session_001 / turn_02`，分数 `73.33`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`READING_ENTRY_MISSING`
- 证据：judge 缺失 `先读什么 / 暂时不要读什么 / 为什么 / 阅读入口`
- 错误总结：看起来没报错，但本质上没把“阅读入口”落地
- PM 动作：把 `先读/不读/原因` 变成结构化输出槽位；未命中即判 partial/fail

### Case 3：`session_001 / turn_03`，分数 `51.67`

- 标签：`BOOTSTRAP_TEMPLATE_HIJACK`、`ARTIFACT_EXECUTION_GAP`
- 证据：`trace_fail`；`artifact_fail`；预期 `memory/packs/PACK_bootstrap_kickoff.md` 未生成
- 错误总结：不仅没接题，还没把 seed pack 落盘，导致初始化闭环断掉
- PM 动作：在 artifact turn 增加 `must_write_artifact` 守卫；trace 无 `write_file` 直接 fail

### Case 4：`session_009 / turn_02`，分数 `78.00`

- 标签：`SOURCE_LAYER_LABEL_MISSING`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：content 只命中 1 个关键术语；judge 缺 `来自 review / 来自我的笔记 / 从旁支材料借来的思路`
- 错误总结：方向对，但没把来源边界显式标出来，导致 outline 不够可信
- PM 动作：给 outline/handoff 类模板加固定三列；trace 里要求至少一次 memory read

### Case 5：`session_007 / turn_02`，分数 `87.67`

- 标签：`UNSUPPORTED_SPECIFICITY`、`MEMORY_REUSE_SIGNAL_WEAK`
- 证据：`unsupported_specificity = true`；judge 虽 pass，但仍缺 `三个锚点`
- 错误总结：过程分高，但压缩稿写得过满，已经接近“高过程分但用户仍会不放心”的典型 badcase
- PM 动作：对 reading queue / recap 类问题增加“最多给到哪一级细节”的约束

## 7. 建议排期

1. 第 1 周：修 `bootstrap prompt + route + hard check`
2. 第 2 周：补 `source-layer` 模板与对应 scorer
3. 第 3 周：收敛 `unsupported_specificity`，避免高分下的细节过满

## 8. 最终判断

这份 run 最该优先修的不是“再补更多文献知识”，而是把开场三轮从通用初始化模板里拽出来。B 场景当前已经能做出不错的文献闭环，但 bootstrap 和来源分层一旦不稳，就会直接削弱你最想讲的“科研可信度”和“长期记忆容器”叙事。
