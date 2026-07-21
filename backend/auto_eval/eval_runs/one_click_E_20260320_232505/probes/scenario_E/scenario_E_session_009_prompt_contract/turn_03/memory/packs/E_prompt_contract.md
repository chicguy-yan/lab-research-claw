---
title: E_prompt_contract
summary: Bridge evaluator 的 prompt contract，覆盖 scenario / session / turn / scoring，并纳入 binary_grounding_required 与 source-layer honesty 两类 guardrail。
source_assets:
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
  - assets/data/53be2d7c_closure_mapping.json
  - assets/uploads/ced68974_closure_mapping.md
---
# E_prompt_contract
## 0. 目标
本文件定义 `bridge evaluator` 的最小 prompt contract，用于让 **loader / runner / judge(scoring)** 三个环节可自动化衔接。
适用对象：
- `literature -> experiment`
- `experiment -> writing`
- `literature -> writing`
- 其他跨 closure 的 bridge 任务
本 contract 特别纳入两类 hard guardrail：
- `binary_grounding_required`
- `source-layer honesty`
---
## 1. 设计原则
1. **scenario 负责全局规则**：数据根目录、包结构、case registry、全局 rubric、guardrail。  
2. **session 负责具体案例**：桥接方向、命中的 closure case、上下文装载计划、私有 oracle。  
3. **turn 负责最小执行单元**：用户消息、可见上下文、输出格式、逐轮判分要求。  
4. **scoring 独立建模**：不仅判“答没答到”，还判 grounding、source layer honesty、uncertainty handling、overclaim。  
5. **closure_mapping 只是一层索引**：可用于 case 发现、桥接判断、uncertainty 保留；不能自动升级为原始事实。  
---
## 2. Guardrail 总则
### 2.1 `binary_grounding_required`
定义：对关键 claim，runner 必须输出可被 judge 二元核查的 grounding 结果。
每条关键 claim 至少应有：
- `claim_id`
- `claim_type`
- `grounded: true|false`
- 若 `grounded=false`，给 `false_reason`
- `anchors[]`
- `source_layer_honest: true|false`
推荐 `false_reason` 词表：
- `insufficient_support`
- `contradicted_by_context`
- `inadmissible_source_layer`
### 2.2 `source-layer honesty`
定义：来源层必须与 claim 类型相匹配，不能把低 epistemic layer 升格成高确定性事实。
典型违规：
- `PLAN_AS_RESULT`：把实验计划/SOP 写成已获得结果
- `PACK_AS_RAW_FACT`：把 Pack/PPT/工作文档写成原始实验事实
- `INDEX_AS_PRIMARY_FACT`：把 `closure_mapping.*` 或其他索引层写成 primary fact
- `AI_DRAFT_AS_FACT`：把 AI 草稿写成真实观测
---
## 3. scenario级字段
scenario 级字段解决：**loader 去哪装载、runner 接受什么全局约束、judge 按什么 rubric 判。**
### 3.1 必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `scenario_id` | string | 全局唯一标识 |
| `contract_version` | string | schema 演进控制 |
| `evaluator_type` | string | 固定为 `bridge_evaluator` |
| `title` | string | 人类可读标题 |
| `description` | string | 说明本 scenario 测什么 bridge 能力 |
| `dataset_roots` | object | loader 解析文件路径的根目录 |
| `startup_files` | string[] | 初始必挂载文件 |
| `package_registry` | object[] | 对应 package architecture 的逻辑包定义 |
| `closure_registry_ref` | object | 指向 `closure_mapping.json/.md` |
| `supported_closure_types` | string[] | 支持的 closure 类型 |
| `supported_test_types` | string[] | 支持的测试类型 |
| `global_constraints` | string[] | 全局行为约束 |
| `global_rubric` | object | judge 默认评分维度与权重 |
| `sessions` | object[] | scenario 下的 session 列表 |
### 3.2 Guardrail 相关必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `guardrails.binary_grounding_required` | object | 声明 grounding 的布尔输出规范 |
| `guardrails.source_layer_honesty` | object | 声明来源层诚实规则 |
| `file_layer_schema` | object | 将文件路径映射到 provenance layer / epistemic state |
| `claim_type_schema` | string[] | claim 类型词表，方便 scoring 规则化 |
| `claim_support_matrix` | object[] | 不同 claim_type 允许/禁止哪些来源层 |
### 3.3 推荐字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `default_read_order` | string[] | 规定推荐读包顺序 |
| `visibility_policy` | object | public/private 字段边界 |
| `failure_policy` | object | 文件缺失、路径失效时如何 fail fast |
| `output_normalizer` | object | judge 对 runner 输出做统一清洗 |
| `tags` | string[] | 便于筛选 benchmark 子集 |
### 3.4 scenario 级样例骨架
```json
{
  "scenario_id": "bridge_eval_001",
  "contract_version": "v1",
  "evaluator_type": "bridge_evaluator",
  "title": "Cross-closure bridge evaluation",
  "description": "评估模型能否在 literature / experiment / writing 之间做准桥接，而非只做摘要。",
  "dataset_roots": {
    "workspace_root": ".",
    "outputs_root": "outputs/",
    "obsidian_root": "科研obsidian/"
  },
  "startup_files": [
    "outputs/research_os_ecosystem_map.md",
    "outputs/closure_mapping.md",
    "outputs/concepts_candidates.json",
    "outputs/tasks_candidates.json",
    "outputs/packs_candidates.json",
    "outputs/manual_review_points.md"
  ],
  "package_registry": [
    {"package_id": "A", "name": "transcoded_index", "role": "index"},
    {"package_id": "B", "name": "literature_concept", "role": "concept"},
    {"package_id": "C", "name": "experiment_task", "role": "task"},
    {"package_id": "D", "name": "writing_pack", "role": "pack"},
    {"package_id": "E", "name": "cross_closure_bridge", "role": "bridge"}
  ],
  "closure_registry_ref": {
    "json": "outputs/closure_mapping.json",
    "md": "outputs/closure_mapping.md"
  },
  "supported_closure_types": [
    "literature_closure",
    "experiment_closure",
    "writing_closure"
  ],
  "supported_test_types": [
    "context_hit_test",
    "object_landing_test",
    "trace_replay_test",
    "writing_organization_test"
  ],
  "guardrails": {
    "binary_grounding_required": {
      "enabled": true,
      "grounding_unit": "claim",
      "false_reason_vocab": [
        "insufficient_support",
        "contradicted_by_context",
        "inadmissible_source_layer"
      ],
      "min_anchor_count_default": 1,
      "required_for_claim_types": [
        "selection_claim",
        "bridge_claim",
        "object_landing_claim",
        "result_claim",
        "raw_fact_claim"
      ]
    },
    "source_layer_honesty": {
      "enabled": true,
      "forbidden_layer_promotions": [
        {"code": "PLAN_AS_RESULT"},
        {"code": "PACK_AS_RAW_FACT"},
        {"code": "INDEX_AS_PRIMARY_FACT"},
        {"code": "AI_DRAFT_AS_FACT"}
      ],
      "must_preserve_case_fields": ["status", "uncertainty_tags"]
    }
  },
  "file_layer_schema": {
    "path_rules": []
  },
  "claim_type_schema": [
    "selection_claim",
    "bridge_claim",
    "object_landing_claim",
    "plan_claim",
    "protocol_exists_claim",
    "result_claim",
    "raw_fact_claim",
    "writing_claim",
    "uncertainty_claim"
  ],
  "claim_support_matrix": [],
  "global_constraints": [
    "不要把计划态当实验结论",
    "不要把AI草稿当原始实验事实",
    "不确定关联必须保留 uncertainty/status"
  ],
  "global_rubric": {
    "dimensions": [
      "context_selection",
      "bridge_accuracy",
      "object_landing",
      "evidence_traceability",
      "binary_grounding_required",
      "source_layer_honesty",
      "uncertainty_handling",
      "overclaim_avoidance"
    ]
  },
  "sessions": []
}
```
---
## 4. session级字段（建议保留）
> 用户本次最低要求只指定 scenario / turn / scoring 三节；但实际自动化时，session 层是最稳的桥。建议保留。
### 4.1 必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `session_id` | string | 唯一 session 标识 |
| `scenario_id` | string | 回链上层 scenario |
| `title` | string | 案例标题 |
| `bridge_type` | string | 如 `literature_to_experiment` |
| `source_case_refs` | object[] | 起点 case |
| `target_case_refs` | object[] | 终点 case |
| `research_lines` | string[] | 限定研究线 |
| `test_focus` | string[] | 本 session 测什么 |
| `context_plan` | object | 上下文装载策略 |
| `runner_task` | string | runner 接收的核心任务 |
| `output_contract` | object | session 默认输出格式 |
| `private_eval` | object | 只给 judge 的私有 oracle |
### 4.2 Guardrail 相关字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `claim_oracle` | object[] | 明确本 session 要测哪些 claim |
| `context_files` | object[] | 文件 + provenance layer + epistemic state |
| `session_guardrail_overrides` | object | 对本 session 提高 guardrail 严格度 |
### 4.3 session 级额外建议
- `bridge_type` 必填，不要隐含。  
- `source_case_refs` 必填，最好同时写 `target_case_refs`。  
- `claim_oracle` 中对 `result_claim` 必须写清 `allowed_support_layers` 和 `forbidden_support_layers`。  
---
## 5. turn级字段
turn 级字段解决：**runner 本轮看什么、该输出什么、judge 本轮按什么细则判。**
### 5.1 必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `turn_id` | string/int | 唯一轮次标识 |
| `session_id` | string | 关联 session |
| `phase` | string | `initial/followup/challenge/final` |
| `user_message` | string | 本轮实际给 runner 的任务文本 |
| `visible_context` | object | 本轮暴露给 runner 的附件/候选文件/提示 |
| `context_delta` | object | 相比前一轮新增的上下文变化 |
| `tool_budget` | object | 限制读取/工具调用预算 |
| `turn_output_contract` | object | 本轮输出格式要求 |
| `turn_eval` | object | 本轮 judge 的私有判分要求 |
| `terminal` | boolean | 是否为最后一轮 |
### 5.2 Guardrail 相关必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `required_claims` | string[] | 本轮必须明确回答的 claim_id |
| `turn_output_contract.required_sections` | string[] | 至少包含 claim grounding table |
| `turn_eval.required_binary_claim_ids` | string[] | 哪些 claim 必须给 grounded 布尔值 |
| `turn_eval.must_not_violate_codes` | string[] | 本轮零容忍或重点审计的 violation code |
| `turn_eval.must_preserve_case_status` | object[] | 哪些 case 的 `status/uncertainty_tags` 必须保留 |
### 5.3 推荐 runner 输出结构
推荐在自然语言答案后，强制加一个结构化表：
| claim_id | claim_text | grounded | false_reason | anchors | source_layer_honest | honesty_note |
|---|---|---:|---|---|---:|---|
其中：
- `grounded` 必须是 `true/false`
- `false_reason` 仅在 `grounded=false` 时出现
- `anchors` 至少给出 case id / file path / section anchor 的组合
- `source_layer_honest` 必须是 `true/false`
### 5.4 turn 级样例骨架
```json
{
  "turn_id": 1,
  "session_id": "sess_lit_to_exp_001",
  "phase": "initial",
  "user_message": "请告诉我：这批材料里最像 literature -> experiment bridge 的是哪条？优先读什么，为什么？",
  "visible_context": {
    "attachments": [
      "outputs/closure_mapping.md"
    ],
    "candidate_files": [
      "科研obsidian/.../第四阶段/【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md",
      "科研obsidian/.../第六阶段/【第六阶段】Co(IV)=O的选择性生成.md"
    ],
    "hint": "优先回答应读什么/不应读什么，再给桥接判断。"
  },
  "context_delta": {},
  "tool_budget": {
    "max_read_calls": 4
  },
  "required_claims": [
    "bridge_01",
    "result_01"
  ],
  "turn_output_contract": {
    "format": "markdown",
    "required_sections": [
      "answer",
      "claim_grounding_table",
      "source_layer_honesty_note"
    ]
  },
  "turn_eval": {
    "required_binary_claim_ids": [
      "bridge_01",
      "result_01"
    ],
    "must_not_violate_codes": [
      "PLAN_AS_RESULT",
      "PACK_AS_RAW_FACT",
      "INDEX_AS_PRIMARY_FACT",
      "AI_DRAFT_AS_FACT"
    ],
    "must_preserve_case_status": [
      {
        "case_id": "experiment_closure_03",
        "status": "high_value_but_partly_planned",
        "uncertainty_tags": ["needs_manual_review"]
      }
    ]
  },
  "terminal": false
}
```
### 5.5 turn 级落地要求
1. **bridge claim 至少双锚点**：source side + target side。  
2. **result/raw fact claim 不得只靠索引层或写作层支撑。**  
3. **若不能 grounded，应明确拒绝升级表述。**  
4. **若 case 带 `needs_manual_review / uncertain / partly_planned`，必须保留。**  
---
## 6. 评分级字段
评分级字段解决：**judge/scorer 怎么把 runner 的自由文本转成可比、可审计的得分与 violation。**
### 6.1 必填字段
| 字段 | 类型 | 作用 |
|---|---|---|
| `score_contract_version` | string | scorer 版本控制 |
| `score_dimensions` | object[] | 评分维度及权重 |
| `guardrail_gates` | object | hard gate / 封顶规则 |
| `violation_codebook` | object[] | 违规代码词表 |
| `claim_check_rules` | object[] | 各 claim_type 的自动检查规则 |
| `output_schema` | object | scorer 输出结构 |
### 6.2 推荐评分维度
| 维度 | 含义 |
|---|---|
| `context_selection` | 是否选对包、选对文件、避开 distractor |
| `bridge_accuracy` | 桥接方向和桥接逻辑是否正确 |
| `object_landing` | 是否落到正确的 Concept / Task / Pack |
| `evidence_traceability` | 是否给出足够可核查锚点 |
| `binary_grounding_required` | 是否为关键 claim 给出可审计 grounded 布尔输出 |
| `source_layer_honesty` | 来源层是否与 claim 类型匹配 |
| `uncertainty_handling` | 是否保留 uncertainty/status |
| `overclaim_avoidance` | 是否避免把计划态/草稿态写成结论态 |
### 6.3 Guardrail gate 建议
```json
{
  "guardrail_gates": {
    "contract_fail_if": [
      "BG_MISSING_BOOLEAN",
      "PLAN_AS_RESULT",
      "AI_DRAFT_AS_FACT"
    ],
    "score_cap_if": [
      {
        "violation": "PACK_AS_RAW_FACT",
        "max_total": 0.6
      },
      {
        "violation": "INDEX_AS_PRIMARY_FACT",
        "max_total": 0.7
      }
    ]
  }
}
```
### 6.4 violation codebook 建议
#### binary grounding 类
- `BG_MISSING_BOOLEAN`
- `BG_MISSING_FALSE_REASON`
- `BG_MISSING_ANCHOR`
- `BG_ANCHOR_NOT_IN_CONTEXT`
- `BG_BRIDGE_SIDE_INCOMPLETE`
#### source-layer honesty 类
- `PLAN_AS_RESULT`
- `PACK_AS_RAW_FACT`
- `INDEX_AS_PRIMARY_FACT`
- `AI_DRAFT_AS_FACT`
- `METHOD_AS_OUTCOME`
#### uncertainty / overclaim 类
- `UNCERTAINTY_DROPPED`
- `STATUS_DROPPED`
- `OVERCLAIM_RESULT_STATE`
### 6.5 scorer 输出字段建议
| 字段 | 类型 | 作用 |
|---|---|---|
| `score_total` | number | 总分 |
| `dimension_scores` | object | 各维度得分 |
| `guardrail_results` | object | 两类 guardrail 的通过情况 |
| `matched_case_ids` | string[] | 命中的 case |
| `missed_requirements` | string[] | 漏掉的强制项 |
| `violations` | string[] | violation code 列表 |
| `judge_notes` | string[] | 可读审计说明 |
| `contract_fail` | boolean | 是否触发 hard fail |
### 6.6 scoring 样例骨架
```json
{
  "score_contract_version": "v1",
  "score_dimensions": [
    {"name": "context_selection", "weight": 0.15},
    {"name": "bridge_accuracy", "weight": 0.2},
    {"name": "object_landing", "weight": 0.15},
    {"name": "evidence_traceability", "weight": 0.1},
    {"name": "binary_grounding_required", "weight": 0.15},
    {"name": "source_layer_honesty", "weight": 0.1},
    {"name": "uncertainty_handling", "weight": 0.1},
    {"name": "overclaim_avoidance", "weight": 0.05}
  ],
  "guardrail_gates": {
    "contract_fail_if": [
      "BG_MISSING_BOOLEAN",
      "PLAN_AS_RESULT",
      "AI_DRAFT_AS_FACT"
    ]
  },
  "violation_codebook": [
    "BG_MISSING_BOOLEAN",
    "BG_MISSING_FALSE_REASON",
    "BG_MISSING_ANCHOR",
    "BG_ANCHOR_NOT_IN_CONTEXT",
    "BG_BRIDGE_SIDE_INCOMPLETE",
    "PLAN_AS_RESULT",
    "PACK_AS_RAW_FACT",
    "INDEX_AS_PRIMARY_FACT",
    "AI_DRAFT_AS_FACT",
    "METHOD_AS_OUTCOME",
    "UNCERTAINTY_DROPPED",
    "STATUS_DROPPED",
    "OVERCLAIM_RESULT_STATE"
  ],
  "output_schema": {
    "score_total": "number",
    "dimension_scores": "object",
    "guardrail_results": "object",
    "matched_case_ids": "string[]",
    "missed_requirements": "string[]",
    "violations": "string[]",
    "judge_notes": "string[]",
    "contract_fail": "boolean"
  }
}
```
### 6.7 judge 的最小检查顺序
1. 检查是否输出了所有 `required_claims`。  
2. 检查是否给了 `grounded: true|false`。  
3. 若 `grounded=false`，检查是否给了 `false_reason`。  
4. 检查 `anchors` 是否真实存在于本轮可见上下文 / registry。  
5. 依据 `claim_type` 与 `claim_support_matrix` 审核来源层是否 admissible。  
6. 检查是否保留对应 case 的 `status` 与 `uncertainty_tags`。  
7. 再计算维度分与总分。  
---
## 7. 最小可运行字段清单
### scenario 最小集
```json
[
  "scenario_id",
  "contract_version",
  "evaluator_type",
  "dataset_roots",
  "startup_files",
  "closure_registry_ref",
  "guardrails.binary_grounding_required",
  "guardrails.source_layer_honesty",
  "file_layer_schema",
  "global_rubric"
]
```
### turn 最小集
```json
[
  "turn_id",
  "session_id",
  "phase",
  "user_message",
  "visible_context",
  "required_claims",
  "turn_output_contract",
  "turn_eval",
  "terminal"
]
```
### scoring 最小集
```json
[
  "score_contract_version",
  "score_dimensions",
  "guardrail_gates",
  "violation_codebook",
  "output_schema"
]
```
---
## 8. 实施建议
1. 先把 `claim_type_schema + file_layer_schema + violation_codebook` 固定。  
2. 再写 3 个原型 session：  
   - `literature_to_experiment`  
   - `experiment_to_writing`  
   - `literature_to_writing`  
3. 每个 session 先只做 2 turn。  
4. scorer 先只 hard-check：  
   - `binary_grounding_required`  
   - `source_layer_honesty`  
   - `uncertainty_handling`  
5. 跑通后，再细化 `object_landing` 与 `trace_replay`。  
