# Binding · mechanism_mapping

## Purpose
将 portable core skill `mechanism_mapping` 接入当前科研 workspace 的机理闭环。

## Default Route
- `mechanism_closure`

## Invocation Role
本 skill 作为“机理分析前置层”使用。
它负责把零散文献、表征线索和实验现象整理成候选机理分支图谱。

## Typical Upstream Inputs
- `literature_pdf_4block` 的逐篇四块摘要
- `spectra_reading_note` 的读图笔记
- 用户直接提供的实验现象摘要
- 用户已有的零散候选解释

## Typical Downstream Handoffs
- 当重点转为 claim-evidence-gap 聚合时：
  - `mechanism_evidence_chain`
  - `evidence_chain_pack`
- 当重点转为阶段汇报组织时：
  - `mechanism_stage_report`
  - `stage_report_pack`
- 当重点转为图表到页面映射时：
  - `figure_to_slide_map`

## Default Output Mapping
建议将本 skill 的输出映射为：
- 机理草图
- 分支表
- 证据状态表
- 待验证问题列表

## Trigger Hints
以下问法优先考虑命中本 skill：
- “先把可能的机理分支列出来”
- “不要先下结论，先搭机理图谱”
- “结构变化可能如何影响位点，再影响反应路径”
- “先区分哪些有证据，哪些只是推断”

## Non-Preferred Cases
以下情况不优先命中本 skill：
- 单张谱图的细读与峰位判定
- 两条氧化路径的严格对照分析
- 多个 claim 的统一证据链 Pack 聚合
- 汇报页面或写作提纲整理