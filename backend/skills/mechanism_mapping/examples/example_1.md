# Example 1 · 从结构变化到路径偏好的机理图谱

## Typical User Ask
“我现在有几条零散线索：一个是材料结构发生了变化，一个是表征提示位点状态变了，一个是反应表现也不同。请不要直接下结论，先把可能的机理分支列出来，并区分哪些有证据、哪些只是合理推断。”

## Typical Inputs
- 2 到 5 篇相关文献的摘录或图
- 若干表征现象摘要
- 一组性能或路径差异现象
- 用户当前的候选解释 1 到 3 条
- 可选：已有证据链草稿

## Expected Output Shape
### mechanism_question
一句话定义本轮机理问题

### branch_map
列出 2 到 4 条候选机理分支，每条分支包含：
- 结构特征
- 位点变化
- 中间过程含义
- 反应结果或路径偏好

### feature_to_site_mapping
把“结构变化”翻译成“位点变化”

### site_to_process_mapping
把“位点变化”翻译成“中间过程或路径差异”

### evidence_status
按分支标注：
- 直接证据支持
- 间接证据支持
- 类比支持
- 推断
- 待验证

### unresolved_issues
列出当前最关键的 2 到 4 个未解决问题

### validation_suggestions
给出下一步最值得优先验证的实验或表征

### mechanism_narrative_spine
用 3 到 6 句写出当前最稳的主线叙事

## Common Failure Modes
- 看到一个解释就过早收敛成单一路径
- 用“协同增强”“电子转移改善”代替具体机理关系
- 没有区分证据支持和合理猜想
- 只列结构变化，没有真正落到位点和路径
- 只输出综述感段落，没有结构化结果

## Boundary Notes
- 本 skill 负责“搭机理图谱”，不负责多源 claim 的统一聚合交付
- 如果重点已经从“机理分支”转向“证据链审计与聚合”，应转给 `mechanism_evidence_chain` 或 `evidence_chain_pack`
- 如果重点是谱图本身的联合判读，应转给 `spectroscopy_joint_interpretation`
- 如果重点是路径/氧化剂对比，应转给 `oxidant_route_comparison`