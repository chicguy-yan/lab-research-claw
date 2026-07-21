---
source_assets:
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/45307a7c_test_cases_writing.md
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
  - assets/uploads/ced68974_closure_mapping.md
created: 2026-03-22
---

# E_benchmark_prioritization
## 入选 benchmark
### 结论
建议将首版精简 benchmark 收束为 **8 个 session 类型**。
| session_id | family | session 类型 | 主要 seed | 主测能力 | 入选理由 |
|---|---|---|---|---|---|
| S1 | cross-family | Bootstrap / case routing | `PRO_PROMPT_PACKAGE_ARCHITECTURE` + `closure_mapping` + 三类 case index | bootstrap / guardrails / cross-session memory | 先测会不会做 closure 路由、read order 和 case 选池；否则后续 case 容易退化成普通摘要题 |
| S2 | literature | Literature baseline closure landing | L1 | object landing / artifact 写入 / guardrails | `strong_candidate` 且 `uncertainty_tags: none`，最适合做 literature baseline |
| S3 | literature | Literature migration anti-hallucination | L2 | hallucination guardrails | 最能测“结构调控文献被误写成当前体系已闭环机制” |
| S4 | experiment | Experiment screening → TASK skeleton | E1 | artifact 写入 / task landing | 最能测从实验问题到 `TASK_*` 骨架的收束能力 |
| S5 | experiment | Experiment minimal mechanism protocol | E2 | protocol organization / artifact 写入 / guardrails | experiment 首发 baseline 最合适，可评分性最高 |
| S6 | experiment | Experiment provenance adjudication | E3 | provenance control / hallucination guardrails / cross-session memory | 最能测计划态、执行态、写作态混写问题 |
| S7 | writing | Writing pack replay | W1 | pack-quality / artifact 写入 / binary 解析 | 最稳的 writing baseline，适合测从工作文档到最终交付的回放能力 |
| S8 | writing | Thesis reverse engineering | W2 | binary 解析 / state separation / guardrails | 最强 binary stress case，能测“已做 / 待做 / 已写 / 未写”分层 |
### 每个入选项对应的最小交付物
| session_id | 建议 artifact |
|---|---|
| S1 | `benchmark_case_pool_v1.md` / `session_read_plan.md` |
| S2 | `CONCEPT_L1_baseline_closure.md` |
| S3 | `bridge_vs_direct_support_matrix.md` |
| S4 | `TASK_screening_matrix.md` |
| S5 | `TASK_minimal_mechanism_closure.md` |
| S6 | `provenance_adjudication.md` |
| S7 | `PACK_group_meeting_replay.md` |
| S8 | `thesis_gap_map.md` |
## 覆盖理由
### 五类能力覆盖
| 能力 | 主要覆盖 session | 覆盖说明 |
|---|---|---|
| bootstrap | S1, S2, S4 | 先做 closure 路由、对象落点、case 选池，再下钻具体材料 |
| binary 解析 | S7, S8 | W1/W2 都涉及 PPTX 等最终件或半最终件，是首版最有代表性的 binary 测项 |
| artifact 写入 | S2, S4, S5, S7 | 覆盖 `CONCEPT_* / TASK_* / PACK_*` 三类落点 |
| 跨 session memory | S1, S6 | 分别覆盖“前轮路由承接”和“计划/执行/写作状态跨轮保持” |
| hallucination guardrails | S3, S5, S6, S8 | 覆盖文献迁移越界、实验条件乱编、binary 脑补、状态混写 |
### 为什么这 8 个足够做 v1
1. 三大类 family 都有覆盖：literature / experiment / writing。
2. 五类目标能力都有显式主测项，而不是隐含覆盖。
3. baseline、stress、guardrail 三层都有代表项，便于分批上线。
4. 优先选择 `strong_candidate` 或虽有风险但增益明显的 case，避免 v1 一开始就被高人工仲裁成本拖慢。
### 推荐分层
| 层级 | session |
|---|---|
| Baseline | S1, S2, S5, S7 |
| Stress | S3, S4, S8 |
| Guardrail / Adjudication | S6 |
## 暂缓项
### 高价值但建议暂缓到 v2 的 case
| case | 来源 | 暂缓理由类型 | 暂缓理由 |
|---|---|---|---|
| P1. Literature bridge-only boundary control | L3 | 对 v1 增益不够高 / 边界不清 | `conceptual_bridge_candidate` 且 `uncertain`；更适合做 challenge case，不适合抢占第一版 baseline 名额 |
| P2. Writing version evolution / handoff memory | W3 | 太依赖人工判读 | `versioned_pack_candidate` 且 `needs_manual_review`；需要回源多个版本件、PPT/DOC 时序和版本差异，v1 评分成本过高 |
### 其他暂缓模式
| 暂缓模式 | 适用对象 | 原因 |
|---|---|---|
| 信息重复 | L1/W1 的近似子变体 | 已有 case 能测到同类能力，首版新增区分度有限 |
| 边界不清 | L2 深拆、E3 fully-grounded gold | `needs_manual_review / mixed_draft_status / partly_planned` 较重，直接入 v1 容易把人工补全误当 gold |
| 太依赖人工判读 | W2 图号页号级仲裁、W3 多版本精细比对 | 需要大量回源 binary 原件，evaluator 一致性难保证 |
| 对第一版增益不够高 | L3 bridge-only 深拆、E1 的更细性能拟合派生题 | 有价值，但不如当前入选项更能立住 benchmark 地基 |
### 暂缓不等于删除
这些 case 不是没价值，而是：
- 更适合做 **v2 challenge / adjudication set**；
- 需要更强的原件回源与人工仲裁；
- 或与当前入选项相比，首版新增收益不够高。
## 一句话结论
首版 benchmark 建议采用“**8 个入选 + 2 个高价值暂缓**”的结构：
- 入选 8 个 session 负责先把 benchmark 地基立住；
- 暂缓项保留到 v2，用于扩展 bridge 边界控制与版本演化判读能力。
