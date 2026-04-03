# Binding · oxidant_route_comparison

## Purpose
将 portable core skill `oxidant_route_comparison` 接入当前科研 workspace 的机理比较闭环。

## Default Route
- `mechanism_closure`

## Invocation Role
本 skill 作为“跨路径 / 跨体系比较层”使用。
它负责把两类路径、两类氧化剂或外部先例与当前体系之间的机制关系整理为：
- 路径摘要
- 位点要求矩阵
- 可迁移性分级
- 边界提醒
- 优先验证建议

## Typical Upstream Inputs
- `literature_pdf_4block` 输出的逐篇文献摘要
- `mechanism_mapping` 输出的单一路径机理草图
- 用户直接提供的外部文献 claim、图号或机制语句
- 用户已写好的比较性机制段落草稿

## Typical Downstream Handoffs
- 当比较结果需要聚合成统一证据链交付物时：
  - `mechanism_evidence_chain`
  - `evidence_chain_pack`
- 当比较结果需要进入阶段汇报或写作编排时：
  - `mechanism_stage_report`
  - `stage_report_pack`
  - `writing_outline_rd`
- 当需要进一步审计图句支撑关系时：
  - `figure_claim_anchoring`
  - `figure_to_slide_map`

## Default Output Mapping
建议将本 skill 的输出映射为：
- 路径对照表
- 位点要求矩阵
- 可迁移性分级表
- 边界提醒清单
- 验证优先级列表
- 简短比较叙事骨架

## Trigger Hints
以下问法优先考虑命中本 skill：
- “这两条路径的关键差异是什么”
- “哪些文献结论能借，哪些不能”
- “两类路径对位点要求有什么不同”
- “我不想硬套外部机制，请分开可迁移和不可迁移部分”
- “外部先例能解释到哪一层，哪些地方还得重证”

## Non-Preferred Cases
以下情况不优先命中本 skill：
- 单一体系的机理分支搭建
- 单张谱图的细读和峰位判定
- 活性物种探针选择性矩阵构建
- 多个 claim / experiment note 的统一 evidence pack 聚合
- 页面级汇报结构整理