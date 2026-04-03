---
name: multi_evidence_mechanism_judgment
description: 用于综合多类证据，判断当前最稳的机制解释、并存分支、矛盾点与结论上限，输出可复用的机制判断结果而不越级过度下结论。
allowed-tools: Read Write Edit Bash
license: Internal
---

# Multi-Evidence Mechanism Judgment

## Overview

这个 skill 用于处理**多源证据综合机制判断**任务。

它适用于这样的问题：用户手里已经有不止一种证据，例如文献线索、谱图判读、探针结果、淬灭实验、活性变化、对照组现象、结构变化或已有候选机理，希望把这些证据放在一起判断：

- 当前哪条机制解释最稳
- 哪些分支仍然并存
- 哪些证据彼此互相加强
- 哪些证据只是平行提示
- 哪些证据彼此存在张力或冲突
- 当前结论最多能推进到哪一层
- 下一步最值得优先补什么证据来完成收敛

这个 skill 的重点不是“把所有证据堆在一起写成一个顺滑故事”，而是输出一个**有分层、有边界、有置信度的综合判断结果**。

---

## When to Use This Skill

当满足以下任一情况时使用本 skill：

- 已经拥有多类证据，希望做一次综合机制判断
- 需要回答“现在最稳能说到哪一层”
- 需要比较多个候选机制在现有证据下各自的支持强弱
- 需要梳理哪些证据互相加强，哪些只是平行提示，哪些互相冲突
- 需要把局部判断整合成当前最稳的机制主线
- 需要明确指出当前仍并存的分支和尚未解决的关键矛盾
- 需要为后续写作、汇报或补实验提供一个克制但可执行的中间结论

---

## When NOT to Use This Skill

以下情况不要使用本 skill：

- 只有单一证据类型，尚未形成多源证据输入
- 主要任务是对一张或一组谱图做具体判读
  - 这类问题更适合交给图谱联合判读类 skill
- 主要任务是比较两条路径或两类氧化剂的整体差异
  - 这类问题更适合交给路径比较类 skill
- 主要任务是构建单一体系的机理分支图谱
  - 这类问题更适合交给机理分析类 skill
- 主要任务是建立 probe / scavenger / EPR 的证据等级矩阵
  - 这类问题更适合交给活性物种证据矩阵类 skill
- 主要任务是把所有内容整理成正式 evidence pack、claim-evidence 交付物或页面级写作结构
  - 这类问题更适合交给证据链聚合类 skill或结果组织类 skill

---

## Required Inputs

### Minimum Inputs

至少需要以下输入之一的组合：

- 两类及以上不同来源的证据
- 一组候选机制解释
- 一组需要被综合判断的文献、实验或表征结果
- 一组已经形成局部判断、但尚未做统一结论的分析材料

### Optional Inputs

以下输入会显著提升结果质量：

- 各证据来源的简要读图或读实验笔记
- 已有候选机制分支图
- 各证据对应的支持强度初步判断
- 用户当前写下的一版机制叙事草稿
- 想要排除或重点验证的 competing explanations
- 对照实验或反例信息
- 当前最担心被质疑的机制跳步点

### Supported Material Types

- pdf
- figure screenshots
- spectra notes
- experiment notes
- probe/scavenger summaries
- activity summaries
- md notes
- literature claim tables
- interpretation drafts

---

## Expected Outputs

本 skill 应输出以下类型的结构化结果：

- `judgment_question`
  - 本轮综合判断真正要回答的问题
- `candidate_mechanisms`
  - 当前待比较的候选机制或分支
- `evidence_groups`
  - 当前纳入综合判断的证据分组
- `evidence_convergence`
  - 哪些证据彼此互相加强
- `evidence_parallelism`
  - 哪些证据只是平行提示但不足以完成证明
- `evidence_tensions`
  - 哪些证据之间存在矛盾、张力或待解释之处
- `mechanism_support_ranking`
  - 各候选机制在现有证据下的支持强弱排序
- `current_best_supported_judgment`
  - 当前最稳、最克制的机制判断
- `coexisting_branches`
  - 仍无法排除、需要并存保留的分支
- `judgment_ceiling`
  - 当前证据最多允许把结论推进到哪一层
- `critical_gaps`
  - 关键缺口与最薄弱环节
- `next_best_discriminators`
  - 最值得优先补的判别性实验、表征或分析
- `judgment_narrative_spine`
  - 用 3 到 6 句写出当前最稳的综合判断叙事骨架

输出形式可以是：

- 综合判断表
- 证据会聚/张力清单
- 机制排序表
- 当前最稳结论与边界说明
- 下一步收敛建议
- 简短综合叙事骨架

---

## Workflow

### Step 1. 明确综合判断问题

先把输入重述为一个清晰的问题句。

这个问题句通常应回答：

- 当前究竟要判断什么
- 是在比较多个机制解释，还是在检验一条主线是否站得住
- 用户真正想知道的是：
  - “哪条最稳”
  - “哪些仍并存”
  - “能说到哪一步”
  - “下一步补什么最值”

不要一开始就把现有叙事当作默认主线，先重新定义本轮判断目标。

### Step 2. 列出候选机制与证据分组

把待比较的候选机制或分支显式列出来。

同时，把现有证据按来源分组，例如：

- 结构或材料特征
- 谱图判读
- probe / scavenger / EPR
- activity 或 selectivity 变化
- 对照实验
- 文献先例或类比支撑

这一步的重点是避免“证据全在一起，但没有层次”。

### Step 3. 判断哪些证据彼此会聚

找出那些真正互相加强的证据组合。

例如：

- 一类证据支持位点变化
- 一类证据支持某类中间过程
- 一类证据支持路径偏好变化

当这些证据在逻辑上形成连续链条时，可以视为会聚支持。

注意：会聚不等于已证明完整机制，只表示多类证据朝同一方向收敛。

### Step 4. 判断哪些证据只是平行提示

找出那些看起来方向一致，但仍不足以单独或联合完成证明的证据。

这类证据常见特征包括：

- 都与某解释相容
- 但彼此之间缺少真正的逻辑桥梁
- 或者只停留在同一层判断，无法推进到下一层

这一阶段的目标，是防止把“方向一致”误写成“证据闭环已成”。

### Step 5. 显式处理证据张力与矛盾

不要为了叙事顺滑而忽略不一致信息。

需要明确指出：

- 哪些证据彼此有张力
- 哪些现象暂时解释不通
- 哪些数据削弱了当前主假设
- 哪些地方需要保留 competing explanations

这一部分往往决定输出是否真正可信。

### Step 6. 给出支持排序与当前最稳判断

对候选机制进行当前支持强弱排序。

排序时要同时考虑：

- 证据数量
- 证据层次
- 证据会聚程度
- 是否存在关键反例或张力
- 是否仍依赖未验证跳步

然后给出一个**当前最稳、最克制**的综合判断：

- 可以写成主线的部分
- 只能写成候选解释的部分
- 暂时不能写入主结论的部分

### Step 7. 写清结论上限与下一步收敛动作

明确当前证据最多允许把结论推进到哪一层。

例如只到：

- 位点状态变化
- 某类中间过程倾向
- 某类路径更可能
- 某类机制暂被削弱但未完全排除

然后列出：

- 关键缺口
- 最值得优先补的判别性实验/表征
- 如果新证据出现，最可能改变哪个排序

### Step 8. 输出结构化综合判断结果

将结果整理成一个可复用的综合判断框架，通常包括：

- 判断问题
- 候选机制列表
- 证据分组
- 会聚支持
- 平行提示
- 证据张力
- 机制排序
- 当前最稳判断
- 结论上限
- 关键缺口
- 判别性下一步
- 综合叙事骨架

---

## Boundary with Sibling Skills

使用本 skill 时，注意与相邻 skill 的边界：

- 当重点是**多源证据放在一起做机制综合判断**时，优先使用本 skill
- 当重点是**一张或一组谱图本身如何判读**时，优先转给图谱联合判读类 skill
- 当重点是**probe / scavenger / EPR 等活性物种证据的等级整理**时，优先转给活性物种证据矩阵类 skill
- 当重点是**单一体系内部搭建机理分支图谱**时，优先转给机理分析类 skill
- 当重点是**两条路径或两类氧化剂的并排比较与可迁移性判断**时，优先转给路径比较类 skill
- 当重点是**把综合判断整理成正式 claim-evidence pack、章节或页面级输出**时，优先转给证据链聚合类 skill或结果组织类 skill

---

## Quality Checks

在输出前检查以下内容：

- [ ] 是否明确写出了本轮综合判断问题
- [ ] 是否显式列出了候选机制，而不是默认只有一条主线
- [ ] 是否把证据按来源分组，而不是混成一团
- [ ] 是否区分了证据会聚、平行提示和证据张力
- [ ] 是否对机制支持强弱进行了排序
- [ ] 是否写出了当前最稳判断，而不是只写“都可能”
- [ ] 是否写出了结论上限，而不是默认闭环已成
- [ ] 是否指出了仍并存的分支和关键缺口
- [ ] 是否给出了真正有判别力的下一步建议
- [ ] `judgment_narrative_spine` 是否足够克制、可接入下游证据链或写作

---

## Common Failure Modes

使用本 skill 时，尤其要避免以下问题：

- 只要证据多，就默认机制已定
- 把多个弱证据简单叠加，当成强证明
- 只写支持主线的证据，不处理反例和张力
- 把平行提示误写成证据会聚
- 默认“最顺眼”的机制就是当前最稳机制
- 说“整体支持某机制”，但不说明支持到了哪一层
- 只列结论，不列仍并存的分支
- 补实验建议过泛，例如“再做更多表征”
- 为了叙事顺滑，删掉当前最该保留的不确定性

---

## Red Flags / Escalation Notes

出现以下情况时，应降低结论强度或提示转交：

- 输入本质上还是单一证据类型，尚不足以做“多源综合判断”
- 不同证据之间冲突明显，但用户仍希望直接写成确定主线
- 当前主线高度依赖外部类比，而缺少当前问题内部的支撑闭环
- 用户真正需要的是正式 evidence pack、写作段落或 PPT 结构
- 当前问题实质上是“这张谱图怎么看”或“这个 probe 结果能说明什么”，而不是综合判断

---

## Example Patterns

### Example Pattern 1 · 把谱图、probe 和活性结果合在一起判断当前最稳机制

#### Typical User Ask
“我这里已经不止一类证据了，有谱图、有 probe 结果，也有活性变化。请帮我把它们放在一起看：哪些证据真的会聚到同一条解释，哪些只是方向一致但还不够，当前最稳的机制判断是什么，哪些地方还不能写死。”

#### Typical Inputs
- 一组谱图判读结果
- 一组 probe / scavenger / EPR 结果
- 一组 activity 或对照变化
- 可选：用户已有的候选机制主线
- 可选：文献中的类比性支持

#### Expected Output Shape
- `judgment_question`
- `candidate_mechanisms`
- `evidence_groups`
- `evidence_convergence`
- `evidence_parallelism`
- `evidence_tensions`
- `mechanism_support_ranking`
- `current_best_supported_judgment`
- `coexisting_branches`
- `judgment_ceiling`
- `critical_gaps`
- `next_best_discriminators`
- `judgment_narrative_spine`

#### Boundary Notes
- 本场景适合“多类证据已经在手，开始做综合判断”
- 如果重点是 probe 结果本身的证明力拆解，应先转给活性物种证据矩阵类 skill
- 如果重点是谱图本身的具体读法，应先转给图谱联合判读类 skill
- 如果后续要做正式 claim-evidence 聚合交付，应转给证据链聚合类 skill

---

### Example Pattern 2 · 不想只听一个机制，希望得到当前最稳的排序和边界

#### Typical User Ask
“我现在不想只听一个解释。请把现有所有证据放在一起，给我一个当前最稳的机制排序：哪条最受支持、哪条仍不能排除、哪些证据在互相打架、结论最多能推进到哪一步。”

#### Typical Inputs
- 两到四条候选机制解释
- 若干不同来源的证据摘要
- 可选：用户已经写过的一版主线叙事
- 可选：当前最担心被质疑的跳步点

#### Expected Output Shape
除了标准综合判断输出外，还应特别强调：

- `mechanism_support_ranking`
  - 不只给“主线”，还给排序
- `evidence_tensions`
  - 不回避当前打架的地方
- `judgment_ceiling`
  - 直接写清当前最多能说到哪
- `coexisting_branches`
  - 需要并存保留的解释

#### Boundary Notes
- 本场景适合“多分支并存，需要做当前最稳排序”
- 如果任务重点转成正式写作或汇报表达，应转给结果组织类 skill
- 如果重点转成外部机制与当前体系的可迁移性审计，应转给路径比较类 skill

---

## Example Requests

以下请求适合调用本 skill：

- “把这些不同来源的证据放在一起，告诉我当前最稳的机制判断。”
- “哪些证据是真的互相加强，哪些只是方向一致？”
- “我不想只听一个机制，请给我一个当前支持强弱排序。”
- “现在到底能说到哪一层，哪些地方还不能写死？”
- “把会聚证据、矛盾证据和下一步最该补的实验分开列出来。”

---

## Related Skills

- `mechanism_mapping`
- `oxidant_route_comparison`
- `spectroscopy_joint_interpretation`
- `reactive_species_evidence_matrix`
- `figure_claim_anchoring`
- `results_to_report_structuring`
- `mechanism_evidence_chain`