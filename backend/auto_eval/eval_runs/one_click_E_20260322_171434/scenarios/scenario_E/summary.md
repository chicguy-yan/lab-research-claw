# 跨闭环桥接评测 Summary

- run_id: `one_click_E_20260322_171434`
- scenario_id: `scenario_E`
- turn_count: `31`
- average_score: `95.69`
- pass_rate: `100.00%`
- temporary_turn_count: `0`

## Hallucination Metrics
- metric_descriptions: `{'E_H1_schema_runtime_fidelity': '统计 scenario/session/turn/criterion 字段建议是否真正可被 loader-runner-scorer 消费，而非高层空话。', 'E_H2_bridge_source_honesty': '统计是否正确区分 bridge 层索引文件与原始科研证据，避免把 mapping 说成事实本身。', 'E_H3_priority_coverage_integrity': '统计 benchmark prioritization 是否同时覆盖 bootstrap、binary、artifact、memory、guardrail 等关键能力。', 'E_H4_cross_closure_failure_awareness': '统计是否识别 literature→experiment→writing 的断链点与误迁移模式。', 'E_H5_evaluator_self_guardrails': '统计是否把 binary_grounding_required、source-layer honesty、stop-rule、abstain 等 evaluator 自身护栏落到接口层。'}`
- rates: `{'unsupported_specificity': 0.0, 'trace_free_binary_certainty': 0.0, 'cross_system_overtransfer': 0.0, 'absolute_overclaim_turns': 0.1613, 'source_confusion_turns': 0.0}`
- raw_counters: `{'unsupported_specificity': 0, 'trace_free_binary_certainty': 0, 'cross_system_overtransfer': 0, 'absolute_overclaim_turns': 5, 'source_confusion_turns': 0}`

## Session Scores
- scenario_E_session_001_bootstrap: `94.00`
- scenario_E_session_002_package_read_order: `97.56`
- scenario_E_session_003_literature_priority: `97.56`
- scenario_E_session_004_experiment_priority: `96.00`
- scenario_E_session_005_writing_priority: `98.33`
- scenario_E_session_006_mapping_schema_audit: `96.00`
- scenario_E_session_007_cross_closure_failure_modes: `93.44`
- scenario_E_session_008_benchmark_prioritization: `98.45`
- scenario_E_session_009_prompt_contract: `93.44`
- scenario_E_session_010_handoff: `92.67`

## Lowest Turns
- none

## Artifact Outputs
- memory/packs/PACK_bootstrap_kickoff.md
- memory/packs/E_package_read_order.md
- memory/packs/E_literature_priority.md
- memory/packs/E_experiment_priority.md
- memory/packs/E_writing_priority.md
- memory/concepts/E_mapping_schema_audit.md
- memory/concepts/E_cross_closure_failure_modes.md
- memory/packs/E_benchmark_prioritization.md
- memory/packs/E_prompt_contract.md
- memory/packs/E_handoff.md

## Temporary Dir Activity
- none

## Temporary Dir Checks
- none
