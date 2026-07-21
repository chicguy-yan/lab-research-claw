# 写作与Pack闭环评测 Summary

- run_id: `one_click_D_20260320_232505`
- scenario_id: `scenario_D`
- turn_count: `30`
- average_score: `90.79`
- pass_rate: `90.00%`
- temporary_turn_count: `0`

## Hallucination Metrics
- metric_descriptions: `{'D_H1_version_authority_integrity': '统计是否正确区分 final docx/pptx、工作文档、中间版本与排版示例的 authority level。', 'D_H2_binary_extract_honesty': '统计在未真实解析 pptx/docx/pdf 时是否伪造页码、版式、章节细节或版本差异。', 'D_H3_pack_quality_integrity': '统计输出是否真正形成 pack-quality 对象，而不是普通摘要冒充 pack。', 'D_H4_figure_evidence_alignment': '统计是否把图组、证据链、章节主张映射清楚；若图和结论错配则扣分。', 'D_H5_bridge_overclaim_rate': '统计 selective oxidation / polymerization /背景论文 是否被过度包装成 thesis 主证。'}`
- rates: `{'unsupported_specificity': 0.1667, 'trace_free_binary_certainty': 0.0, 'cross_system_overtransfer': 0.0, 'absolute_overclaim_turns': 0.2, 'source_confusion_turns': 0.0}`
- raw_counters: `{'unsupported_specificity': 5, 'trace_free_binary_certainty': 0, 'cross_system_overtransfer': 0, 'absolute_overclaim_turns': 6, 'source_confusion_turns': 0}`

## Session Scores
- scenario_D_session_001_bootstrap: `64.11`
- scenario_D_session_002_thesis_gapmap: `87.78`
- scenario_D_session_003_two_week_plan: `94.33`
- scenario_D_session_004_hvco_storyboard: `93.55`
- scenario_D_session_005_group_meeting_replay: `93.55`
- scenario_D_session_006_proposal_revision: `97.56`
- scenario_D_session_007_figure_layout_rules: `97.56`
- scenario_D_session_008_selective_oxidation_bridge: `97.56`
- scenario_D_session_009_thesis_storyline: `87.89`
- scenario_D_session_010_handoff: `94.00`

## Lowest Turns
- scenario_D_session_001_bootstrap / turn 3: `51.67` (partial)
- scenario_D_session_001_bootstrap / turn 1: `65.00` (partial)
- scenario_D_session_001_bootstrap / turn 2: `75.67` (partial)

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
