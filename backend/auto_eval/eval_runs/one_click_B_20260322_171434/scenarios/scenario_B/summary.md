# 文献与Concept闭环评测 Summary

- run_id: `one_click_B_20260322_171434`
- scenario_id: `scenario_B`
- turn_count: `31`
- average_score: `96.11`
- pass_rate: `100.00%`
- temporary_turn_count: `0`

## Hallucination Metrics
- metric_descriptions: `{'B_H1_source_layer_integrity': '统计把论文原文、文献笔记、类比迁移三层证据说清楚的比例；若将 note 压缩句误写成 paper 直接结论则扣分。', 'B_H2_binary_grounding_compliance': '针对需要深读 PDF 的 turn，检查是否出现 terminal/python_repl/明确不确定边界；缺失则视为二进制 grounding 不足。', 'B_H3_cross_system_transfer_safety': '统计把 PMS/Fenton-like/selective oxidation/Ce 旁支结论直接写成 chlorite 已证实事实的风险率。', 'B_H4_unsupported_specificity_rate': '统计无依据捏造具体表征细节、页级信息、定量比较或“已证明”强断言的比例。', 'B_H5_artifact_truthfulness': '统计声称已生成 concept/pack 或已稳定掌握的结论，但实际 artifact/summary 不存在或缺关键 section 的比例。'}`
- rates: `{'unsupported_specificity': 0.0968, 'trace_free_binary_certainty': 0.0, 'cross_system_overtransfer': 0.0968, 'absolute_overclaim_turns': 0.2581, 'source_confusion_turns': 0.0}`
- raw_counters: `{'unsupported_specificity': 3, 'trace_free_binary_certainty': 0, 'cross_system_overtransfer': 3, 'absolute_overclaim_turns': 8, 'source_confusion_turns': 0}`

## Session Scores
- scenario_B_session_001_bootstrap: `92.84`
- scenario_B_session_002_baseline_compare: `96.00`
- scenario_B_session_003_dband_bridge: `100.00`
- scenario_B_session_004_ce_transferability: `99.22`
- scenario_B_session_005_proof_methods: `97.56`
- scenario_B_session_006_ce_sentence_safety: `95.89`
- scenario_B_session_007_reading_queue: `94.33`
- scenario_B_session_008_false_analogy_redflags: `95.56`
- scenario_B_session_009_master_outline: `92.33`
- scenario_B_session_010_handoff: `98.45`

## Lowest Turns
- none

## Artifact Outputs
- memory/packs/PACK_bootstrap_kickoff.md
- memory/concepts/B_baseline_compare.md
- memory/concepts/B_dband_bridge.md
- memory/concepts/B_ce_transferability.md
- memory/concepts/B_proof_methods.md
- memory/concepts/B_sentence_safety.md
- memory/packs/B_reading_queue.md
- memory/concepts/B_false_analogy_redflags.md
- memory/packs/B_master_outline.md
- memory/packs/B_handoff.md

## Temporary Dir Activity
- none

## Temporary Dir Checks
- none
