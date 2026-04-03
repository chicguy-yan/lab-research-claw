---
name: figure_claim_anchoring
description: 用于将图、原始数据、图中观察和文字论断进行一一锚定，明确每条 claim 的证据来源、支持强度与边界，输出可复用的图-句支撑结构。
allowed-tools: Read Write Edit Bash
license: Internal
---

# Figure Claim Anchoring

## Overview

这个 skill 用于处理**图-论断锚定**任务。

它适用于这样的问题：用户已经有图、谱图、表格、原始数据摘录、结果段落草稿或机制表述，希望判断：

- 哪张图在支撑哪句话
- 该图支撑的是直接结论、间接结论，还是只是提示性结论
- 哪些 claim 目前没有清晰图锚点
- 哪些图里真正能读出的信息，被文字写得过了头
- 如何把图号、观察事实、解释句和结论句整理成一条清楚的证据链

这个 skill 的重点不是“美化图注”或“润色论文语言”，而是建立一个**可审查的图-句支撑结构**，让每个重要论断都尽量能回到具体图和具体观察上。

---

## When to Use This Skill

当满足以下任一情况时使用本 skill：

- 需要判断某条论断到底由哪张图支撑
- 需要把图中观察、结果描述和结论句一一对应起来
- 需要审计当前文字是否超过了图本身能支撑的上限
- 需要找出哪些 claim 目前缺乏明确图锚点
- 需要把多张图组织成“哪张图支撑哪一层结论”的证据链
- 需要为后续写作、汇报、组图或 evidence pack 提供图句基础结构
- 需要从已有图和原始数据出发，重新收紧主张力度

---

## When NOT to Use This Skill

以下情况不要使用本 skill：

- 主要任务是对图谱本身做具体峰位或信号判读
  - 这类问题更适合交给图谱联合判读类 skill
- 主要任务是搭建单一体系的完整机理图谱
  - 这类问题更适合交给机理分析类 skill
- 主要任务是比较两条路径或两类氧化剂的差异
  - 这类问题更适合交给路径比较类 skill
- 主要任务是对 probe / scavenger / EPR 证据做等级矩阵整理
  - 这类问题更适合交给活性物种证据矩阵类 skill
- 主要任务是做多源证据综合判断
  - 这类问题更适合交给多证据综合判断类 skill
- 主要任务是页面布局、美化、排版或写作措辞润色
  - 这类问题更适合交给结果组织或写作类 skill

---

## Required Inputs

### Minimum Inputs

至少需要以下输入之一的组合：

- 一条或多条待支撑的 claim
- 一张或多张候选图
- 图中关键观察事实的描述
- 图号、表号、原始数据摘录或结果段落草稿

### Optional Inputs

以下输入会显著提升结果质量：

- 图对应的原始数据或峰表
- 图的对照样信息
- 当前已有的图注或结果描述
- 用户已经写好的机制句、结果句或讨论句
- 用户想要强调的结论层级
- 文献中的对应图句写法，用于做边界参考
- 已整理的图组顺序或章节结构草稿

### Supported Material Types

- pdf
- figure screenshots
- spectra images
- tables
- raw data excerpts
- md notes
- results drafts
- ppt notes
- claim lists

---

## Expected Outputs

本 skill 应输出以下类型的结构化结果：

- `anchoring_question`
  - 本轮图-句锚定真正要回答的问题
- `claim_list`
  - 当前待锚定的 claim 列表
- `candidate_figures`
  - 每条 claim 对应的候选图或数据来源
- `figure_observations`
  - 图中真正可直接读出的观察事实
- `claim_support_links`
  - 图、观察事实与 claim 之间的支撑关系
- `support_strength`
  - 每条 claim 的支撑强度分级
- `unsupported_or_overstated_claims`
  - 当前缺锚点或表述过界的 claim
- `best_anchor_for_each_claim`
  - 每条 claim 当前最合适的主锚点
- `missing_anchors`
  - 仍缺少图或数据支持的部分
- `tightened_claim_versions`
  - 收紧后更稳妥的 claim 表述
- `anchoring_narrative_spine`
  - 用 3 到 6 句写出当前最稳的图-句支撑骨架

输出形式可以是：

- 图-句映射表
- claim 锚点清单
- 图中观察 → 解释 → 结论分层表
- 过度论断清单
- 更稳妥表述建议
- 简短支撑骨架

---

## Workflow

### Step 1. 明确锚定问题

先把输入重述为一个清晰的问题句。

这个问题句通常应回答：

- 当前要锚定的是哪类论断
- 目标是：
  - 找到支撑图
  - 审计论断是否过界
  - 重写更稳妥的表述
  - 组织图与结论的对应关系
- 当前最重要的是补锚点、收紧 claim，还是澄清图的支持层级

不要一开始就默认“图肯定支撑这句话”，先明确本轮锚定目标。

### Step 2. 列出待锚定的 claim

把当前待处理的 claim 显式列出来，而不是整段文字整体处理。

每条 claim 应尽量拆成单独的可判断单元，例如：

- 材料结构发生了某种变化
- 位点状态发生了某种变化
- 某类中间过程更可能发生
- 某条路径更受支持
- 某个性能差异可由某种机制解释

这一步的重点是：一条句子里若混了多个层级，应先拆开。

### Step 3. 提取图中可直接观察的事实

对每张候选图，先只写“图里真正看得到什么”。

常见观察事实包括：

- 峰位或边位变化
- 强度增强或减弱
- 新峰、肩峰或壳层差异
- 对照样差异
- 趋势变化
- 某类信号有无
- 表格中的数值差异
- 原始数据中的定量变化

这一阶段只写观察事实，不直接提升为解释句或结论句。

### Step 4. 建立“图中观察 -> claim”的支撑关系

将每条图中观察与待锚定的 claim 建立联系。

建议至少区分：

- 直接支撑  
  图中观察本身较直接地支撑该 claim
- 间接支撑  
  图中观察与该 claim 一致，但还需要中间推理
- 仅提示  
  图中观察只能提示方向，不能独立支撑该 claim
- 不足以支撑  
  当前图与该 claim 的联系过弱或跳步过大

这一步的重点是，把图和 claim 的关系从“直觉觉得像”变成显式判断。

### Step 5. 审计过度论断与缺锚点位置

检查每条 claim 是否存在以下问题：

- 没有明确图锚点
- 图只能支持较低层结论，但文字已经写到更高层
- 一个图被拿去支撑过多层级的结论
- 多个图各支撑一小段，但文字被写成“一图定乾坤”
- 关键结论没有原始数据或图中观察支撑

将这些问题集中整理成：

- 过度论断清单
- 缺锚点清单
- 可收紧改写清单

### Step 6. 给出最优锚点与更稳妥表述

为每条 claim 选出当前最合适的主锚点，并给出更稳妥的写法。

一个更稳妥的 claim 应满足：

- 图号或数据来源清楚
- 图中观察与结论之间的逻辑跨度可接受
- 不越过当前证据上限
- 能区分“观察事实”“解释”“结论”

这一阶段不要求把文字写得华丽，而要写得稳、准、可回溯。

### Step 7. 输出结构化图-句支撑结果

将结果整理成一个可复用的锚定结构，通常包括：

- 锚定问题
- claim 列表
- 候选图与主锚点
- 图中观察事实
- 支撑强度
- 过度论断清单
- 缺锚点位置
- 收紧后的 claim 表述
- 图-句支撑骨架

---

## Boundary with Sibling Skills

使用本 skill 时，注意与相邻 skill 的边界：

- 当重点是**哪张图支撑哪句话，以及支撑强度有多高**时，优先使用本 skill
- 当重点是**图谱本身怎么读、峰怎么标、哪些特征意味着什么**时，优先转给图谱联合判读类 skill
- 当重点是**单一体系内部搭建机理分支图谱**时，优先转给机理分析类 skill
- 当重点是**两条路径或外部先例与当前问题之间的比较和可迁移性判断**时，优先转给路径比较类 skill
- 当重点是**probe / scavenger / EPR 等证据的等级矩阵**时，优先转给活性物种证据矩阵类 skill
- 当重点是**多源证据综合判断当前最稳机制**时，优先转给多证据综合判断类 skill
- 当重点是**把图句结构进一步排成汇报页面、章节顺序或写作提纲**时，优先转给结果组织类 skill或证据链聚合类 skill

---

## Quality Checks

在输出前检查以下内容：

- [ ] 是否明确写出了本轮图-句锚定问题
- [ ] 是否把待处理的 claim 拆成了单独可判断单元
- [ ] 是否先列图中观察事实，再谈解释或结论
- [ ] 是否区分了直接支撑、间接支撑、仅提示和不足以支撑
- [ ] 是否找出了没有明确锚点的 claim
- [ ] 是否找出了图支撑不足却写得过界的 claim
- [ ] 是否给出了更稳妥的 tightened claim 版本
- [ ] 是否避免把一个图的观察直接升级成完整机制主线
- [ ] `anchoring_narrative_spine` 是否足够短、稳、可接入后续 evidence pack 或写作组织

---

## Common Failure Modes

使用本 skill 时，尤其要避免以下问题：

- 看到图和 claim 大致相关，就默认锚定成立
- 不区分图中观察事实和后续解释
- 一个图被拿去支撑多个层级完全不同的结论
- 图只能支持趋势，文字却写成确定机制
- claim 很强，但没有明确图号或数据来源
- 只说“图支持了这句话”，不说明支持的是哪一层
- 只做语言润色，不审计支撑关系
- 为了让故事完整，忽略了缺锚点位置

---

## Red Flags / Escalation Notes

出现以下情况时，应降低结论强度或提示转交：

- 输入里几乎没有具体图或原始数据，只有强结论草稿
- 图本身仍未完成基础判读，却已经要求做图句锚定
- claim 层级明显高于当前图中观察可支持的上限
- 多个关键 claim 都缺锚点，但用户仍希望直接进入汇报或写作
- 用户真正需要的是“整套证据链怎么组织”或“PPT 怎么排版”，而不是图句锚定本身

---

## Example Patterns

### Example Pattern 1 · 审计“哪张图支撑哪句话”

#### Typical User Ask
“我现在有几条结论和几张图，但我不确定哪张图到底在支撑哪句话。请帮我把图、图中观察和结论句对应起来，并指出哪些 claim 写过了。”

#### Typical Inputs
- 一组待支撑的 claim
- 一组候选图
- 图中关键观察事实描述
- 可选：当前草稿中的结果句或机制句
- 可选：原始数据摘录

#### Expected Output Shape
- `anchoring_question`
- `claim_list`
- `candidate_figures`
- `figure_observations`
- `claim_support_links`
- `support_strength`
- `unsupported_or_overstated_claims`
- `best_anchor_for_each_claim`
- `missing_anchors`
- `tightened_claim_versions`
- `anchoring_narrative_spine`

#### Boundary Notes
- 本场景适合“先把每条 claim 压回具体图和数据”
- 如果后续要排成汇报结构，应转给结果组织类 skill
- 如果图本身还没读清楚，应先转给图谱联合判读类 skill

---

### Example Pattern 2 · 从原始图和结果草稿中收紧论断

#### Typical User Ask
“我已经写了一版结果描述，但我担心里面有些话超过了图本身能支撑的范围。请帮我按图去审计这些句子：哪些是稳的，哪些需要收紧，哪些现在其实还没有图锚点。”

#### Typical Inputs
- 结果段落草稿
- 对应图或表
- 可选：图注、原始数据摘录
- 可选：用户想保留的主论点

#### Expected Output Shape
除了标准锚定输出外，还应特别强调：

- `unsupported_or_overstated_claims`
  - 逐条列出过界句子
- `tightened_claim_versions`
  - 给出更稳妥的重写版本
- `support_strength`
  - 明确每句话当前的支撑等级

#### Boundary Notes
- 本场景适合“从草稿回压到图，减少过度表述”
- 如果重点转成正式 evidence pack，应转给证据链聚合类 skill
- 如果重点转成页面级讲述顺序，应转给结果组织类 skill

---

## Example Requests

以下请求适合调用本 skill：

- “哪张图到底支撑哪句话？”
- “这条 claim 现在有没有足够直接的图锚点？”
- “请把图中观察、解释和结论分开整理。”
- “哪些话现在写过了，哪些可以写得更稳？”
- “把这组图和这段结果草稿做一一对应审计。”

---

## Related Skills

- `mechanism_mapping`
- `oxidant_route_comparison`
- `spectroscopy_joint_interpretation`
- `reactive_species_evidence_matrix`
- `multi_evidence_mechanism_judgment`
- `results_to_report_structuring`
- `mechanism_evidence_chain`