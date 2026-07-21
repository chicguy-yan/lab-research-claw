---
source_assets:
  - assets/data/53be2d7c_closure_mapping.json
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/428b081_research_os_ecosystem_map.md
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/45307a7c_test_cases_writing.md
created: 2026-03-21
---

# E_mapping_schema_audit
## 背景
本审计面向 `closure_mapping` 直接喂给 evaluator loader / scorer 的场景。
结论基于以下材料：
- `assets/data/53be2d7c_closure_mapping.json`
- `assets/uploads/ced68974_closure_mapping.md`
- `assets/uploads/428b081_research_os_ecosystem_map.md`
- 辅助参考：`assets/uploads/5ee0c395_test_cases_literature.md`、`assets/uploads/4abcbbd4_test_cases_experiment.md`、`assets/uploads/45307a7c_test_cases_writing.md`
当前判断：现有 `closure_mapping.json` 更接近 **analyst 维护的 closure 目录**，还不是可直接执行的 evaluator runtime schema。最大问题是：**已有 scenario 草案层，但几乎没有 turn 层 contract**。
---
## 必须字段
### 1. 文件级必须字段
| 字段 | 说明 | 当前状态 |
|---|---|---|
| `schema_version` | loader 识别解析版本 | 缺失 |
| `scenarios[]` 或统一根节点 | 避免 runtime 依赖 `literature/experiment/writing` 三个顶层桶做特判 | 缺失 |
### 2. scenario级必须字段
这些字段定义“这到底是哪一个闭环场景”。
| 字段 | 用途 | 当前映射 / 问题 |
|---|---|---|
| `scenario_id` | 稳定主键 | 现有 `id` 可迁移 |
| `closure_type` | 指定 `literature / experiment / writing` | 当前只隐含在顶层桶名里，应下沉到每条 scenario |
| `title` | 展示名 / 日志名 / 报错定位 | 现有 `title` 可保留 |
| `target_object_type` | 指定最终对象类型：`concept / task / pack` | 当前散落在 `candidate_concept/task/pack` 字段名中，不统一 |
| `target_object_label` | 目标对象标签/名称 | 可由 `candidate_*` 值迁移 |
| `shared_asset_refs[]` | scenario 共享素材引用 | 现有 `source_files` 不是 runtime 可直接读取路径 |
| `turns[]` | 一个 scenario 下有哪些可执行 turn | 缺失 |
#### `shared_asset_refs[]` 最小建议结构
```json
{
  "asset_id": "a1",
  "workspace_path": "assets/uploads/xxx.md",
  "origin_path": "科研obsidian/xxx.md",
  "role": "primary_context",
  "required": true
}
```
### 3. turn级必须字段
这些字段定义“这一轮到底怎么问、怎么判”。
| 字段 | 用途 | 当前状态 |
|---|---|---|
| `turn_id` | scenario 内唯一轮次 ID | 缺失 |
| `test_type` | 如 `context_hit_test`、`object_landing_test`、`trace_replay_test`、`writing_organization_test` | 现仅以 `suitable_tests` 列表松散存在 |
| `user_request` | evaluator 实际喂给 agent 的题面 | 缺失 |
| `asset_scope` | 本轮允许/要求使用哪些资产 | 缺失 |
| `scorer_contract` | scorer 所用 rubric / 判分入口 | 缺失 |
| `gold_signals` 或 `pass_criteria` | 明确什么算命中、什么算通过 | 缺失 |
#### 不同测试类型常见最小 gold signal
- `context_hit_test`
  - `must_hit_asset_ids`
  - `allowed_extra_asset_ids`（可选）
  - `must_not_hit_asset_ids`（可选）
- `object_landing_test`
  - `expected_object_type`
  - `expected_object_label`
  - `label_aliases`（可选）
- `trace_replay_test`
  - `required_read_asset_ids`
  - `min_read_count`（可选）
  - `required_trace_actions`（可选）
- `writing_organization_test`
  - `expected_output_type`
  - `required_sections`
  - `section_order_constraints`（可选）
---
## 可选字段
### 1. 运行时可选字段
这些字段不是“没有就跑不起来”，但能提升稳定性、可扩展性或采样能力。
| 字段 | 用途 | 说明 |
|---|---|---|
| `research_line` | 主线分组 / coverage 统计 / 采样 | 当前更偏分析字段；若保留，建议配 registry |
| `benchmark_priority` | 指定优先跑哪些 scenario | ecosystem map 已有语义，但 JSON 中未结构化 |
| `runtime_flags` | 指定是否宽松打分、是否需人工复核 | 比自然语言 `status` 更适合运行时 |
| `difficulty` | benchmark 难度分层 | 便于 eval 分层采样 |
| `seed_strategy` | 场景偏 `concept_first/task_first/pack_first` | 更适合统计与生成策略控制 |
| `distractor_asset_refs[]` | 干扰素材 | 做 retrieval / context hit benchmark 时很有用 |
| `notes_for_loader` | loader 特殊装配说明 | 仅当少数场景需要 |
#### `runtime_flags` 建议结构
```json
{
  "source_completeness": "complete|partial|insufficient",
  "manual_review_required": false,
  "strict_scoring": true
}
```
### 2. 仅供分析但不影响运行的字段
这些字段适合 analyst / curator / reviewer，不应成为 loader/scorer 的硬依赖。
| 字段 | 作用 |
|---|---|
| `reason` | 解释为什么把这些文件归成一个 closure |
| 原始 `status` | 如 `strong_candidate`、`high_value_but_partly_planned`；适合人工评审 |
| 原始 `uncertainty_tags` | 风险提示、边界提醒 |
| `closure_mapping.md` 中的 prose | 人类审计版说明 |
| `ecosystem map` 中的说明性段落 | 宏观设计语义，不适合作为 runtime contract |
| `test_cases_*` 中的案例解释文本 | 辅助理解测试类型，不是逐 turn 的机器契约 |
---
## schema缺口
### 1. 硬缺口：不补基本跑不起来
1. **缺 `schema_version`**
   - loader 无法按版本分支解析。
2. **缺统一根节点 `scenarios[]`**
   - 现在必须依赖三类顶层桶做特殊逻辑。
3. **缺显式 `closure_type`**
   - 目前只在父层桶名里隐含，不利于 scenario 自描述。
4. **缺统一 `target_object_type` / `target_object_label`**
   - 现在用 `candidate_concept/task/pack` 三种异构字段表达，不利于统一 loader/scorer。
5. **`source_files` 不是 runtime 资产引用**
   - 需要 `workspace_path`，否则 evaluator 无法在当前 workspace 稳定打开素材。
6. **缺 `turns[]`**
   - 现在只有“适合哪些 tests”的标签，没有可执行 turn 定义。
7. **缺 `user_request`**
   - 没有题面，agent 无法执行。
8. **缺 `scorer_contract`**
   - 没有评分入口与 rubric，scorer 落不下来。
9. **缺 `gold_signals` / `pass_criteria`**
   - scorer 不知道什么算命中、什么算通过。
### 2. 中缺口：能凑合跑，但评分会飘
1. **`suitable_tests` 只有标签，没有展开策略**
   - 不清楚是一条 scenario 对应多个 turn，还是多个 scorer 共用一轮。
2. **`status` / `uncertainty_tags` 是自然语言，不是机器 gating**
   - 无法直接控制宽松/严格评分、人工复核等行为。
3. **`research_line` 无 registry**
   - 可用于分析，但不够稳定，难以做自动聚类与 coverage 审计。
4. **benchmark 优先级只存在于 ecosystem map prose**
   - runtime 无法直接按优先级选取场景。
### 3. 建议补齐的最小 runnable 结构
```json
{
  "schema_version": "closure_eval_v1",
  "scenarios": [
    {
      "scenario_id": "literature_closure_01",
      "closure_type": "literature",
      "title": "亚氯酸盐活化基线机制：Co3O4 -> Co(IV) + ClO2",
      "target_object_type": "concept",
      "target_object_label": "亚氯酸盐活化下的 Co(IV)=O / ClO2 双活性物种机制",
      "shared_asset_refs": [
        {
          "asset_id": "a1",
          "workspace_path": "assets/uploads/xxx.md",
          "origin_path": "科研obsidian/xxx.md",
          "role": "primary_context",
          "required": true
        }
      ],
      "turns": [
        {
          "turn_id": "literature_closure_01__context_hit",
          "test_type": "context_hit_test",
          "user_request": "请找出最相关材料并说明为什么。",
          "asset_scope": {
            "use_shared_assets": true
          },
          "scorer_contract": {
            "rubric_id": "context_hit_v1"
          },
          "gold_signals": {
            "must_hit_asset_ids": ["a1"]
          }
        }
      ],
      "analyst_notes": {
        "reason": "...",
        "status": "strong_candidate",
        "uncertainty_tags": []
      }
    }
  ]
}
```
### 4. 最终结论
当前 `closure_mapping.json` 适合做 **closure 编目与人工筛选**，但若要直接喂 evaluator loader，至少需要补齐：
- 文件级版本与统一根节点
- scenario 自描述字段
- runtime 可解析资产引用
- turn 级题面与评分契约
否则 loader 最多只能“看到候选 closure 列表”，不能稳定地装配成可评分 scenario-turn 实例。
