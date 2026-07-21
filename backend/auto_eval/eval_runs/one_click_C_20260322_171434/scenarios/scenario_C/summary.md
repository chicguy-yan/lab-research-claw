# 实验与Task闭环评测 Summary

- run_id: `one_click_C_20260322_171434`
- scenario_id: `scenario_C`
- turn_count: `31`
- average_score: `93.92`
- pass_rate: `96.77%`
- temporary_turn_count: `0`

## Hallucination Metrics
- metric_descriptions: `{'C_H1_condition_fabrication_rate': '统计无来源捏造称量量、浓度、加样量、时间、仪器条件等实验细节的比例。', 'C_H2_sop_scope_honesty': '统计能否区分“当前体系既定条件”和“通用 SOP / docx 参考条件”；混淆则扣分。', 'C_H3_binary_method_grounding': '对 docx / 复杂 SOP 相关 turn，检查是否有真实解析或明确的不确定性声明。', 'C_H4_trace_to_task_alignment': '统计 trace 是否真的围绕 task 落地（读 SOP→写 task→必要时 abstain），而不是给空泛实验建议。', 'C_H5_reagent_interference_awareness': '统计淬灭剂/探针使用中是否提示可能改变基底反应、产生误判或交叉干扰。'}`
- rates: `{'unsupported_specificity': 0.2903, 'trace_free_binary_certainty': 0.0, 'cross_system_overtransfer': 0.0, 'absolute_overclaim_turns': 0.129, 'source_confusion_turns': 0.0}`
- raw_counters: `{'unsupported_specificity': 9, 'trace_free_binary_certainty': 0, 'cross_system_overtransfer': 0, 'absolute_overclaim_turns': 4, 'source_confusion_turns': 0}`

## Session Scores
- scenario_C_session_001_bootstrap: `90.34`
- scenario_C_session_002_stage2_checklist: `96.00`
- scenario_C_session_003_screening_matrix: `95.00`
- scenario_C_session_004_why_co3o4: `94.00`
- scenario_C_session_005_pmso_clo2: `92.00`
- scenario_C_session_006_epr_strategy: `96.00`
- scenario_C_session_007_quencher_matrix: `91.89`
- scenario_C_session_008_ce_task_board: `96.67`
- scenario_C_session_009_chapter_dependency: `93.44`
- scenario_C_session_010_handoff: `95.11`

## Lowest Turns
- scenario_C_session_001_bootstrap / turn 3: `75.67` (partial)

## Artifact Outputs
- memory/packs/PACK_bootstrap_kickoff.md
- memory/tasks/C_stage2_checklist.md
- memory/tasks/C_screening_matrix.md
- memory/concepts/C_why_co3o4.md
- memory/tasks/C_pmso_clo2_minimal_mechanism.md
- memory/tasks/C_epr_strategy.md
- memory/tasks/C_quencher_matrix.md
- memory/tasks/C_ce_task_board.md
- memory/packs/C_chapter_dependency.md
- memory/packs/C_handoff.md

## Temporary Dir Activity
- none

## Temporary Dir Checks
- none
