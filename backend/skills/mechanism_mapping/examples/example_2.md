# Example 2 · 从多条候选机理链条反推关键判别实验

## Typical User Ask
“我现在不想只听一个解释。请先把可能的机理链条分开列出来，再告诉我：同一组已有实验在不同链条下分别支持什么、不支持什么，以及下一步做哪类实验最能把这些路径区分开。”

## Typical Inputs
- 2 到 4 条候选机理解释
- 一组已有实验现象摘要
- 若干表征结果摘要
- 相关文献中的支持性片段或图号
- 可选：用户已经整理过的初步证据链

## Expected Output Shape

### mechanism_question
一句话定义当前真正要回答的问题：
不是“哪个机制听起来最合理”，而是“现有证据能把哪些分支区分开，哪些还区分不开”。

### branch_map
列出 2 到 4 条候选机理分支，每条分支包含：
- 关键结构或位点前提
- 预期中间过程
- 最终会导致的路径偏好或结果差异

### evidence_to_branch_mapping
把已有证据逐条映射到不同分支：
- 哪条证据支持分支 A
- 哪条证据只能弱支持分支 B
- 哪条证据对多个分支都不具区分性

### non_discriminating_evidence
列出“看起来有信息量，但实际上不足以区分路径”的证据

### discriminating_experiments
给出最值得优先补的判别实验或表征，并说明：
- 为什么它能区分路径
- 预期看到什么信号
- 如果结果相反又意味着什么

### unresolved_issues
列出当前仍无法回答的关键问题

### mechanism_narrative_spine
用 3 到 5 句总结当前最稳的叙事：
- 哪些分支仍并存
- 哪些分支已经被削弱
- 下一步最该做什么来进一步收敛

## Common Failure Modes
- 看到一个“最顺眼”的分支就直接收敛
- 把所有已有实验都写成支持主假设，而不讨论其区分性
- 没有把“支持”和“能区分”分开
- 补实验建议写得过泛，例如“再做更多表征”
- 只列结论，不写如果结果相反意味着什么

## Boundary Notes
- 本 example 适合“多路径并存、要靠证据继续收敛”的机理分析
- 如果任务重点已经转成“把多个文献/实验/Task 汇总成正式证据链交付物”，应转给 `mechanism_evidence_chain` 或 `evidence_chain_pack`
- 如果输入主体是单张谱图或单类表征，优先转给 `spectroscopy_joint_interpretation`
- 如果重点是两类氧化剂/两条反应路径的并排比较，优先转给 `oxidant_route_comparison`