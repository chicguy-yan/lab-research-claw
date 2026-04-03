# Example 1 · 比较两条氧化路径对活性位点要求的差异

## Typical User Ask
“我现在看到两类外部文献路径都在讨论高活性中间状态，但我不想直接照搬。请帮我比较这两条路径到底分别依赖什么样的活性位点，哪些结论可以迁移，哪些只是看起来像，实际上不能直接借来解释当前体系。”

## Typical Inputs
- 2 到 4 篇代表两条路径的文献摘录
- 每条路径各 1 到 2 个关键机制 claim
- 若干位点特征关键词
  - 例如低配位、共价性增强、电子结构变化、中间态稳定等
- 可选：用户当前体系的初步表征线索
- 可选：用户已写出的机制表述草稿

## Expected Output Shape

### comparison_question
一句话定义本轮真正要比较的问题：
不是“谁更强”，而是“这两条路径分别要求什么样的位点，以及哪些证据能跨体系迁移”。

### route_summaries
分别概括两条路径的核心逻辑：
- 关键活化步骤
- 活性位点在其中扮演的角色
- 更偏向哪类基元步骤

### site_requirement_matrix
并排整理两条路径对活性位点的要求，例如：
- 配位环境
- 电子结构倾向
- 对中间态的稳定能力
- 对特定过程的促进能力

### elementary_step_differences
明确列出两条路径最关键的步骤差异，而不是只比较结果

### transferability_assessment
对每个重要 claim 分级：
- 可迁移
- 仅可类比
- 不可迁移
- 需要重新验证

### non_portable_claims
显式标出不应照搬的外部机制语言

### boundary_notes
给出后续写作或解释时必须保留的边界提醒

### validation_priorities
指出最值得优先补的实验或表征，用于判定哪些外部逻辑真的适用

### comparison_narrative_spine
用 3 到 6 句写出最稳的比较主线：
- 哪些要求是共享的
- 哪些步骤是特定路径专属的
- 哪些部分可以借
- 哪些部分必须重新证明

## Common Failure Modes
- 把“都需要高活性位点”误写成“机制相同”
- 只比较性能或结果，不比较关键步骤
- 看到外部文献中有熟悉术语就直接迁移
- 不区分“可以借位点要求”和“不能借具体步骤”
- 可迁移性只给标签，不解释原因

## Boundary Notes
- 本 example 适合“路径比较 + 可迁移性判断”
- 如果任务重点转成单一体系的机理分支搭建，应转给 `mechanism_mapping`
- 如果任务重点转成探针与活性物种证据矩阵，应转给 `reactive_species_evidence_matrix`
- 如果任务重点转成多源 evidence 的统一聚合，应转给 `mechanism_evidence_chain`