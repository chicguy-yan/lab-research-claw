# 写作与Pack闭环评测 Summary

- run_id: `one_click_D_20260322_171434`
- scenario_id: `scenario_D`
- turn_count: `31`
- average_score: `91.11`
- pass_rate: `93.55%`
- temporary_turn_count: `0`

## Hallucination Metrics
- metric_descriptions: `{'D_H1_version_authority_integrity': '统计是否正确区分 final docx/pptx、工作文档、中间版本与排版示例的 authority level。', 'D_H2_binary_extract_honesty': '统计在未真实解析 pptx/docx/pdf 时是否伪造页码、版式、章节细节或版本差异。', 'D_H3_pack_quality_integrity': '统计输出是否真正形成 pack-quality 对象，而不是普通摘要冒充 pack。', 'D_H4_figure_evidence_alignment': '统计是否把图组、证据链、章节主张映射清楚；若图和结论错配则扣分。', 'D_H5_bridge_overclaim_rate': '统计 selective oxidation / polymerization /背景论文 是否被过度包装成 thesis 主证。'}`
- rates: `{'unsupported_specificity': 0.129, 'trace_free_binary_certainty': 0.0, 'cross_system_overtransfer': 0.0323, 'absolute_overclaim_turns': 0.1935, 'source_confusion_turns': 0.0}`
- raw_counters: `{'unsupported_specificity': 4, 'trace_free_binary_certainty': 0, 'cross_system_overtransfer': 1, 'absolute_overclaim_turns': 6, 'source_confusion_turns': 0}`

## Session Scores
- scenario_D_session_001_bootstrap: `91.59`
- scenario_D_session_002_thesis_gapmap: `87.78`
- scenario_D_session_003_two_week_plan: `83.11`
- scenario_D_session_004_hvco_storyboard: `76.22`
- scenario_D_session_005_group_meeting_replay: `96.78`
- scenario_D_session_006_proposal_revision: `96.00`
- scenario_D_session_007_figure_layout_rules: `97.56`
- scenario_D_session_008_selective_oxidation_bridge: `96.78`
- scenario_D_session_009_thesis_storyline: `92.78`
- scenario_D_session_010_handoff: `92.33`

## Lowest Turns
- scenario_D_session_004_hvco_storyboard / turn 1: `38.33` (fail)
- scenario_D_session_003_two_week_plan / turn 3: `61.33` (partial)

## Artifact Outputs
- memory/packs/PACK_bootstrap_kickoff.md
- memory/packs/D_thesis_gapmap.md
- memory/packs/D_two_week_plan.md
- memory/packs/D_hvco_storyboard.md
- memory/packs/D_group_meeting_replay.md
- memory/packs/D_proposal_revision_matrix.md
- memory/packs/D_figure_layout_rules.md
- memory/concepts/D_selective_oxidation_bridge.md
- memory/packs/D_thesis_storyline_master.md
- memory/packs/D_handoff.md

## Temporary Dir Activity
- none

## Temporary Dir Checks
- none
