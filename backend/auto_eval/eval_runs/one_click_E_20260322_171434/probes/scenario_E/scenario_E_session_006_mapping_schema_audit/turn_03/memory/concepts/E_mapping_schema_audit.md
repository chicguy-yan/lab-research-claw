---
source_assets:
  - assets/data/53be2d7c_closure_mapping.json
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/428b081_research_os_ecosystem_map.md
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
  - assets/uploads/45307a7c_test_cases_writing.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/5ee0c395_test_cases_literature.md
created: 2026-03-22
---

# E_mapping_schema_audit
## 结论摘要
当前 `closure_mapping.json` 更接近 **scenario 级 case catalog / closure 索引**，可支持 case 选择、主线分组、测试类型路由；但若要直接喂给 evaluator loader 并进一步支持 turn 运行与 scorer 自动评分，仍缺少若干关键字段与统一表达。
---
## 必须字段
### 1) scenario级必须字段
这些字段是 loader 能把一条 closure case 稳定装配成 scenario 的最低要求。
- `scenario_id`
  - 当前可由 `id` 映射
  - 用途：唯一标识、缓存、日志、回放
- `closure_type`
  - 当前仅隐含在顶层数组名：`literature_closure / experiment_closure / writing_closure`
  - 建议下沉到每个 item
- `title`
  - 用途：展示、scenario 命名、审计
- `research_line`
  - 用途：主线分组、coverage 统计、benchmark 采样
- `target_object.type`
  - 当前散落在 `candidate_concept / candidate_task / candidate_pack`
  - 建议统一为：`concept | task | pack`
- `target_object.label`
  - 当前为 `candidate_*` 的字符串值
  - 用途：object landing 的目标比对
- `source_assets[]`
  - 当前 `source_files` 仅给出逻辑路径，不足以保证 package 内可解析
  - 至少应包含可读取的 `package_path` 或 `asset_id`
- `supported_tests[]`
  - 当前可由 `suitable_tests` 映射
  - 用途：声明该 scenario 支持哪些测试类型
- `runtime_readiness.state`
  - 当前缺失
  - 建议枚举：`ready | manual_review | blocked`
### 2) turn级必须字段
这些字段是 evaluator 真正发起单轮测试并可评分的最低要求。当前 `closure_mapping.json` 基本未提供。
- `turn_id`
  - 用途：逐轮跟踪与评分
- `scenario_id`
  - 用途：关联所属 scenario
- `test_type`
  - 当前只有 scenario 级 `suitable_tests`，缺少当前轮到底执行哪个 test
- `prompt_spec`
  - 用途：定义这一轮实际给模型的输入/提示词
- `expected_target_object`
  - 用途：明确这一轮预期落到哪个对象
- `required_assets[]`
  - 用途：限制并声明本轮至少应命中的资产
- `expected_output_contract`
  - 用途：规定输出格式与必备 section
- `scoring_spec`
  - 用途：定义评分维度、must-hit、fail-if
- `forbidden_overclaims[]`
  - 用途：禁止把计划态写成结果态、把注释写成事实等
---
## 可选字段
这些字段有助于 analyst 审阅、case 选择与风险提示，但不是运行时硬依赖。
### 1) analyst注释类
- `reason`
  - 说明为什么这条 case 值得选
- `analyst_notes`
  - 建议把所有解释性注释放入该块
- `object_hint`
  - 目前存在于 md 版，可保留给人读，但不建议 runtime 依赖
### 2) 风险与优先级类
- `status`
  - 当前为自由文本，如 `strong_candidate`、`high_value_but_partly_planned`
  - 建议降级为 analyst 视图字段；程序端改读 `runtime_readiness`
- `uncertainty_tags`
  - 当前更适合作为人工审阅提醒，而非程序 gate
- `priority`
  - 若后续需要按价值排序，可选增加
### 3) 扩展治理类
- `target_objects[]`
  - 若一个 case 可能桥接多个对象，可从单一 `target_object` 扩展到数组
- `entry_asset_id`
  - 指定优先读取入口文件，有利于 scenario 初始化
- `depends_on`
  - 多轮 scenario 时可记录依赖关系
- `notes_for_analyst`
  - 供人工维护的解释说明
---
## schema缺口
### 1) 对象字段未统一
当前分别使用：
- literature: `candidate_concept`
- experiment: `candidate_task`
- writing: `candidate_pack`
问题：
- generic loader 需要按 closure_type 分支解析
- scorer 难以统一比较目标对象
建议：
```json
"target_object": {
  "type": "concept|task|pack",
  "label": "..."
}
```
### 2) `closure_type` 未下沉到 item
问题：
- flatten 后会丢失 `literature / experiment / writing` 语义
- scenario registry / cache / scorer 若按 item 存储，会失去关键路由信息
建议：每个 item 显式携带 `closure_type`。
### 3) `source_files` 不是稳定 runtime 引用
当前 `source_files` 更像逻辑路径说明，如 `科研obsidian/...`，而非 package 内稳定可读取路径。
问题：
- loader 无法保证能直接解析资产
- trace replay 无法稳定回放
建议：
```json
"source_assets": [
  {
    "asset_id": "a1",
    "package_path": "assets/uploads/xxx.md",
    "logical_path": "科研obsidian/...",
    "role": "paper|note|experiment_record|draft_pack|final_pack"
  }
]
```
### 4) 缺少 turn级 contract
当前只有 `suitable_tests`，只能说明“适合测什么”，不能说明：
- 本轮 prompt 是什么
- 预期输出长什么样
- 需要命中哪些文件
- 怎么判分
这会导致：
- scenario loader 只能停在 case 目录层
- scorer 无法自动落地
### 5) `status / uncertainty_tags` 语义偏 analyst，不够程序化
当前值如：
- `strong_candidate`
- `candidate_with_partial_manual_linking`
- `high_value_but_partly_planned`
- `needs_manual_review`
- `uncertain`
问题：
- 人能理解，程序难稳定决策
- 无法直接判断 ready / warning / blocked
建议新增：
```json
"runtime_readiness": {
  "state": "ready|manual_review|blocked",
  "reasons": ["missing_raw_outputs", "partly_planned"]
}
```
### 6) 缺少文件角色字段
仅知道“有哪些 source file”还不够，scorer 还需要区分：
- paper
- literature note
- SOP
- experiment record
- draft pack
- final pack
否则难以判断模型是否把计划态误写成结果态。
### 7) 缺少评分边界
若要支持 scorer，至少还缺：
- `allowed_claims`
- `forbidden_overclaims`
- `required_trace_hits`
- `required_evidence_roles`
- `scoring_dimensions`
- `fail_if`
没有这些字段，`closure_mapping` 最多支持 test routing，不能支持自动评分。
---
## 建议的最小落地结构
### scenario级
```json
{
  "scenario_id": "experiment_closure_03",
  "closure_type": "experiment",
  "title": "...",
  "research_line": "...",
  "target_object": {
    "type": "task",
    "label": "..."
  },
  "source_assets": [
    {
      "asset_id": "a1",
      "package_path": "assets/uploads/xxx.md",
      "role": "experiment_record"
    }
  ],
  "supported_tests": ["object_landing_test", "trace_replay_test"],
  "runtime_readiness": {
    "state": "manual_review",
    "reasons": ["partly_planned"]
  }
}
```
### turn级
```json
{
  "turn_id": "experiment_closure_03__trace_replay__t1",
  "scenario_id": "experiment_closure_03",
  "test_type": "trace_replay_test",
  "prompt_spec": {
    "template_id": "trace_replay_v1",
    "user_prompt": "..."
  },
  "expected_target_object": {
    "type": "task",
    "label": "..."
  },
  "required_assets": ["a1"],
  "expected_output_contract": {
    "format": "markdown",
    "required_sections": ["trace", "evidence", "gaps"]
  },
  "scoring_spec": {
    "dimensions": ["trace_hit", "object_landing", "boundary_control"],
    "fail_if": ["treat_plan_as_result"]
  }
}
```
---
## 结论
- `closure_mapping.json` 现在可作为 **scenario 候选索引** 使用
- 若只做 case catalog / benchmark selector，可直接消费
- 若要直接喂给 evaluator loader 并继续支持 turn 执行与 scorer 自动评分，当前 schema 仍缺：
  - item级 `closure_type`
  - 统一的 `target_object`
  - 可解析的 `source_assets`
  - 程序化的 `runtime_readiness`
  - 完整的 `turn级 contract`
  - 明确的 `scoring_spec`
