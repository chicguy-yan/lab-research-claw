---
name: results_to_report_structuring
description: 用于把已有结果、图、证据和结论组织成可汇报或可写作的结构，明确先后顺序、每页/每节主 claim、图的放置策略以及缺口与下一步。
allowed-tools: Read Write Edit Bash
license: Internal
---

# Results to Report Structuring

## Overview

这个 skill 用于处理**结果到汇报/写作结构的组织**任务。

它适用于这样的问题：用户已经有了一批结果、图、读图结论、机制判断、证据链片段、Task 或 Pack 草稿，希望把这些内容组织成：

- 一次阶段汇报
- 一套组会/PPT 结构
- 一段论文结果与讨论的章节顺序
- 一份中期小结或阶段报告骨架

这个 skill 的重点不是美化页面，也不是单独读图或单独做机制分析，而是把已有结果整理成一个**可讲、可写、可检查逻辑跳步**的结构。

它应回答的核心问题包括：

- 先证明什么，再证明什么
- 每一页 / 每一节的主 claim 是什么
- 哪张图该放在主线，哪张图更适合放补充部分
- 哪些地方证据已经够形成主叙事，哪些地方还只能写成缺口或下一步
- 如何让一套结果形成清晰的“北极星 → 分段支撑 → 缺口与下一步”的结构

---

## When to Use This Skill

当满足以下任一情况时使用本 skill：

- 用户已经有一批结果，希望整理成阶段汇报或写作结构
- 需要决定“先讲什么、后讲什么”
- 需要把图、claim、证据状态映射到 slide 或 section
- 需要判断哪些图应该放主线，哪些放补充或 SI
- 需要把实验结果、机理判断和证据链片段组织成一个更清楚的叙事顺序
- 需要生成 5 到 10 页左右的汇报骨架，或一个可扩展的章节骨架
- 需要把“当前最稳能说的内容”与“仍是缺口/下一步的内容”明确分开

---

## When NOT to Use This Skill

以下情况不要使用本 skill：

- 主要任务是读某张图或某组谱图
  - 这类问题更适合交给图谱联合判读类 skill
- 主要任务是比较两条路径或两类氧化剂的差异
  - 这类问题更适合交给路径比较类 skill
- 主要任务是搭建单一体系的机理分支图谱
  - 这类问题更适合交给机理分析类 skill
- 主要任务是整理 probe / scavenger / EPR 等活性物种证据矩阵
  - 这类问题更适合交给活性物种证据矩阵类 skill
- 主要任务是做多源证据综合判断
  - 这类问题更适合交给多证据综合判断类 skill
- 主要任务是审计哪张图支撑哪句话
  - 这类问题更适合交给图-论断锚定类 skill
- 输入里几乎没有结果、图或中间结论，只是一个空主题

---

## Required Inputs

### Minimum Inputs

至少需要以下输入之一的组合：

- 一组图或结果条目
- 一组已形成的 claim 或中间结论
- 一组 Task / note / result summary
- 一份待整理成汇报或写作结构的材料集合

### Optional Inputs

以下输入会显著提升结果质量：

- 图号、图注或 figure list
- 当前已有的 claim-evidence 对照
- 证据链草稿或机制判断草稿
- 用户对目标形式的要求
  - 例如组会、阶段汇报、论文结果部分、PPT、WPS/Word 大纲
- 已有的章节结构草稿或页面顺序草稿
- 当前最想强调的主线
- 当前最担心逻辑跳步的位置
- 区分主文 / 补充 / SI 的偏好

### Supported Material Types

- figure screenshots
- ppt notes
- md notes
- result summaries
- task lists
- evidence summaries
- claim lists
- raw outline drafts
- pdf excerpts

---

## Expected Outputs

本 skill 应输出以下类型的结构化结果：

- `report_goal`
  - 本轮结构整理要服务的目标
- `north_star_claim`
  - 整体汇报或写作最上层的核心主张
- `section_or_slide_sequence`
  - 页面或章节的顺序安排
- `one_claim_per_unit`
  - 每页/每节的主 claim 列表
- `claim_to_evidence_mapping`
  - 每页/每节 claim 对应的证据与图
- `figure_placement_strategy`
  - 图的放置策略，包括主线、补充、SI/附录建议
- `missing_support_or_missing_figures`
  - 缺图、缺支持或跳步位置
- `gap_and_next_step_block`
  - 缺口与下一步应如何组织
- `presentation_or_writing_tone_notes`
  - 更适合汇报还是更适合论文写作的表达提醒
- `report_narrative_spine`
  - 用 5 到 8 句串起整套结构的叙事骨架

输出形式可以是：

- 5 到 10 页汇报结构
- 章节顺序提纲
- 每页 claim + evidence 映射表
- figure 放置策略表
- 缺图与跳步提醒清单
- 简短汇报/写作叙事骨架

---

## Workflow

### Step 1. 明确目标交付形式

先把输入整理成一个清晰的目标问题。

这个问题通常应回答：

- 当前是要做阶段汇报、组会 PPT、论文结果部分，还是阶段性小结
- 希望输出是：
  - slide 结构
  - section 结构
  - 简报大纲
  - 写作骨架
- 当前最重要的是：
  - 让逻辑顺起来
  - 压缩内容
  - 找出跳步和缺图
  - 明确下一步怎么讲

不要一开始就排页面，先定义“这套结构是给谁看、拿来干嘛”。

### Step 2. 找出北极星 claim

在已有结果中提炼一个最上层的 `north_star_claim`。

它不是所有细节的堆叠，而是：

- 这次汇报/写作最想让听众或读者带走的一句话
- 当前已有证据最能支撑的上层主线
- 后续每页/每节都要服务的核心目标

如果当前证据还不够支撑强主张，应主动把北极星 claim 收紧，而不是强行拔高。

### Step 3. 把结果拆成“每页/每节一个主 claim”

将已有结果拆成若干逻辑单元。

每个单元应尽量满足：

- 只承担一个主 claim
- 有对应证据支撑
- 与前后单元有清晰顺序关系

常见顺序包括：

- 先给问题和北极星
- 再给基础现象或材料/体系建立
- 再给关键位点/结构/机制证据
- 再给综合判断
- 最后给缺口与下一步

不要让一页/一节承担过多层级的主张。

### Step 4. 绑定每页/每节的证据与图

为每个单元分配最能直接支撑它的图或证据。

建议至少回答：

- 这一页/这一节的主图是什么
- 该图在支撑哪一层 claim
- 是否还有辅助图
- 该单元有没有缺图或证据不足的问题

这一阶段应遵循：

- 主线只放直接支持主叙事的图
- 辅助、补充或用于回应质疑的图可放到补充部分或 SI/附录
- 每张图尽量绑定到一个明确 claim，而不是松散地“放着看看”

### Step 5. 审计结构跳步与缺口

检查当前结构中是否存在以下问题：

- 某页/某节的 claim 跳得太高
- 前一页和后一页之间逻辑桥梁缺失
- 关键 claim 缺图或缺直接支持
- 补充图误占主线位置
- 主线图承担了过多层级的解释任务
- 缺口与下一步没有显式组织出来

把这些位置整理成：

- 缺图清单
- 逻辑跳步清单
- 需要收紧 claim 的位置
- 需要后移到补充或 SI 的内容

### Step 6. 组织“缺口与下一步”模块

不要把缺口当成失败，而要把它组织成结构中的一个自然部分。

建议明确：

- 当前已经站稳的部分
- 当前仍然薄弱的部分
- 下一步优先验证的目标
- 为什么这一步是最值得做的

这一块在阶段汇报里尤其重要，因为它决定你讲完后是“卡住了”，还是“下一步路线明确”。

### Step 7. 输出结构化汇报/写作骨架

将结果整理成一个可直接复用的结构，通常包括：

- 目标交付形式
- 北极星 claim
- 每页/每节顺序
- 每页/每节主 claim
- claim 对应的图和证据
- 主线 vs 补充/SI 放置策略
- 缺图与跳步清单
- 缺口与下一步模块
- 简短叙事骨架

---

## Boundary with Sibling Skills

使用本 skill 时，注意与相邻 skill 的边界：

- 当重点是**把已有结果组织成汇报或写作结构**时，优先使用本 skill
- 当重点是**哪张图支撑哪句话**时，优先转给图-论断锚定类 skill
- 当重点是**单一体系内部搭建机理分支图谱**时，优先转给机理分析类 skill
- 当重点是**两条路径的比较与可迁移性判断**时，优先转给路径比较类 skill
- 当重点是**谱图本身如何判读**时，优先转给图谱联合判读类 skill
- 当重点是**多源证据综合判断当前最稳机制**时，优先转给多证据综合判断类 skill
- 当重点是**正式 claim-evidence pack 的聚合、审计与交付**时，优先转给证据链聚合类 skill

---

## Quality Checks

在输出前检查以下内容：

- [ ] 是否明确写出了本轮汇报/写作结构整理的目标
- [ ] 是否提炼出了一个足够克制的北极星 claim
- [ ] 是否做到了每页/每节尽量只有一个主 claim
- [ ] 是否为每页/每节绑定了主图或主证据
- [ ] 是否明确区分了主线图与补充/SI 图
- [ ] 是否找出了缺图、跳步和过强主张的位置
- [ ] 是否显式组织了缺口与下一步
- [ ] 是否避免把“证据还不够”的部分硬塞进主线
- [ ] `report_narrative_spine` 是否足够短、稳、可直接转为 PPT/写作骨架

---

## Common Failure Modes

使用本 skill 时，尤其要避免以下问题：

- 一上来就排页数，没有先提炼北极星 claim
- 一页/一节塞多个主 claim，导致听众抓不住重点
- 图只是堆上去，没有明确绑定到具体 claim
- 主线和补充证据不分，导致主叙事被稀释
- 结构顺序只是“结果罗列”，不是“论证顺序”
- 缺口与下一步被省略，或者只是空泛写“后续还要继续研究”
- 为了讲得完整，把当前证据不足的内容也写成主线
- 只做页面标题，不写每页/每节到底要证明什么

---

## Red Flags / Escalation Notes

出现以下情况时，应降低结构强度或提示转交：

- 当前还没有形成稳定的结果或 claim，却要求直接排完整汇报
- 图本身仍未完成基础判读，却已经要决定放主线还是补充
- 多源证据之间冲突明显，但用户仍想直接输出顺滑主线
- 关键页缺乏直接支撑图，却想让其承担核心 claim
- 用户真正需要的是“哪张图支撑哪句话”，而不是整体结构
- 用户真正需要的是“当前最稳机制判断”，而不是讲述顺序

---

## Example Patterns

### Example Pattern 1 · 把最近的实验和机理证据整理成组会结构

#### Typical User Ask
“把最近的实验结果和机理证据整理成一次组会可以讲的结构。请告诉我先证明什么、再证明什么，每页放什么图，哪些图该放主线，哪些更适合放补充。”

#### Typical Inputs
- 一批最近实验结果
- 若干图或 figure list
- 一份初步的机制判断或证据链片段
- 可选：用户已有的草稿顺序
- 可选：当前最想强调的主线

#### Expected Output Shape
- `report_goal`
- `north_star_claim`
- `section_or_slide_sequence`
- `one_claim_per_unit`
- `claim_to_evidence_mapping`
- `figure_placement_strategy`
- `missing_support_or_missing_figures`
- `gap_and_next_step_block`
- `report_narrative_spine`

#### Boundary Notes
- 本场景适合“已有结果在手，开始组织成组会/PPT”
- 如果重点是图句一一锚定，应先转给图-论断锚定类 skill
- 如果重点是当前最稳机制到底是什么，应先转给多证据综合判断类 skill

---

### Example Pattern 2 · 从结果草稿中收紧主线，区分主文与补充

#### Typical User Ask
“我已经有一批图和结果草稿，但感觉主线有点散。请帮我收紧：哪些图最适合放主线，哪些其实更适合放补充或 SI，哪些 claim 现在还不够格放在前面。”

#### Typical Inputs
- 图组或 figure list
- 当前结果草稿或写作草稿
- 可选：章节结构草稿
- 可选：用户自己最喜欢但不确定是否该前置的图

#### Expected Output Shape
除了标准结构输出外，还应特别强调：

- `figure_placement_strategy`
  - 主线图 vs 补充/SI 图的分配
- `missing_support_or_missing_figures`
  - 当前前置 claim 是否缺支持
- `one_claim_per_unit`
  - 重排后每页/每节的主 claim

#### Boundary Notes
- 本场景适合“从已有图和草稿中收紧主线”
- 如果重点转成正式 claim-evidence pack 聚合，应转给证据链聚合类 skill
- 如果重点转成具体语言收紧和图句支撑审计，应转给图-论断锚定类 skill

---

## Example Requests

以下请求适合调用本 skill：

- “帮我把这些结果整理成一次组会/PPT 的结构。”
- “先证明什么、再证明什么，给我一个讲述顺序。”
- “哪些图应该放主线，哪些更适合放补充或 SI？”
- “请把每页/每节的主 claim 和对应证据列出来。”
- “把缺口和下一步也整理成结构的一部分。”

---

## Related Skills

- `figure_claim_anchoring`
- `mechanism_mapping`
- `oxidant_route_comparison`
- `spectroscopy_joint_interpretation`
- `reactive_species_evidence_matrix`
- `multi_evidence_mechanism_judgment`
- `mechanism_evidence_chain`