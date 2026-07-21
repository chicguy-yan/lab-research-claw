---
source_assets:
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/5c66efd3_【20260305大组会】工作文档.md
  - assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
  - assets/uploads/45307a7c_test_cases_writing.md
created: 2026-03-21
---

# E_handoff
## 先实现什么
### P0：先做写作闭环 bridge 的最小内核
先不要追求全类型通用 research OS，而是先打通这条最短且最有价值的链：
`closure candidate / work doc / stage note -> canonical pack/task object -> eval`
第一版最小输入：
- `closure_mapping`：提供对象优先级、状态、适配测试类型
- `0305 工作文档`：提供稳定的写作组织方式与 page-spec 约束
- `stage6 主线`：提供 mixed object 的真实样例
- `writing test cases`：提供最值得优先验证的 W1/W2 case
第一版最小输出：
1. `PackSpec`
2. `TaskSpec`
3. `GapAudit`
### v1 建议只做 3 个模块
#### 1) Bridge IR
定义统一 schema，先稳定对象落点，再谈复杂 agent。
建议核心字段：
- `id`
- `closure_type`
- `research_line`
- `object_hint`
- `source_files[]`
- `status`
- `uncertainty_tags[]`
- `suitable_tests[]`
- `derived_work_object`
建议拆出两个子对象：
- `PackSpec`
- `TaskSpec`
#### 2) Bridge Rules
先用规则 + 少量 LLM 提取，不要一开始就重度智能化。
优先规则：
- 写作导向输入优先落 `pack`
- 实验推进导向输入优先落 `task`
- 若同时包含章节组织与实验推进，允许落 `mixed`
- 未观测字段保留 `unknown/to_verify`，不要补齐
- 每个 section/page 必须带 source refs 或明确标待核对
#### 3) Eval Runner
第一版只做 3 个 eval：
- `object_landing_test`
- `writing_organization_test`
- `gap_audit_test`
### 第一批 test cases 优先级
#### Case 1：W1 - 0305 大组会 Pack
目标：验证能否稳定抽出 PackSpec 和 page-spec。
#### Case 2：W2 - 毕业论文章节反推
目标：验证能否识别“做了但还没写进去”的断裂，并输出 gap audit。
#### Case 3：stage6 mixed object
目标：验证能否同时生成 TaskSpec 与 PackSpec，而不是硬塞单一类型。
### 暂缓项
- W3 开题报告版本演化
- 复杂 trace replay
- 通用全类型 bridge
- PPT 深层自动排版与图像处理
---
## 可模板化部分
### 1. Page Spec 模板
这是最稳定、最适合直接编码的部分。
建议固定字段：
- `page_no`
- `title`
- `page_goal`
- `source_scope`
- `layout`
- `bullets`
- `quant_results`
- `footnotes`
- `transition_hint`
- `material_ops`
- `verification_status`
### 2. Gap Audit 模板
建议固定成 4 类 gap：
- `missing_source`
- `missing_condition`
- `missing_data`
- `missing_connection_to_chapter`
每个 gap 至少包含：
- `gap_type`
- `object_scope`
- `missing_field`
- `why_it_blocks`
- `source_anchor`
### 3. Closure Candidate -> Work Object 映射模板
`closure_mapping` 已经接近半结构化输入，适合直接转 fixture。
建议保留字段：
- `research_line`
- `object_hint`
- `suitable_tests`
- `status`
- `uncertainty_tags`
- `source_files`
### 4. 结论边界检查模板
适合写成 deterministic validator，而不是仅靠 prompt：
- 不得编造作者/图号/条件/数据/机理
- 不确定就标 `待核对`
- 主图必须可追溯 source
- 背景/综述图必须标来源
- 无 source 的 supported claim 直接 fail
### 5. Judge Rubric 模板
评分建议拆开，不要只有总分：
- `landing_correctness`
- `source_coverage`
- `gap_recall`
- `no_fabrication_compliance`
- `output_completeness`
- `uncertainty_honesty`
---
## 不要做错的事情
### 1. 不要一开始做“全类型通用 bridge”
第一版先把 `writing closure + mixed stage object` 做扎实，不要同时铺开 literature / experiment / version replay / thesis pack / daily timeline。
### 2. 不要把 candidate 静默升级为 confirmed
上游提取结果只能是候选对象。没有明确证据时，最多到 `draft`，不要直接写成 `confirmed`。
### 3. 不要为了结构完整偷偷补字段
缺 `page_no / fig_no / section / 实验条件 / source` 时，必须保留 `unknown / to_verify`，不要“合理补全”。
### 4. 不要奖励“写得像真的”
judge 不能因为文本流畅、自洽、像专家口吻就给高分。证据锚点应高于表达质量。
### 5. 不要把 instruction/template_text 当作项目事实
像 0305 工作文档中很多内容是写作要求、页面模板、示例约束，不是研究事实。loader 必须先分层：
- `instruction`
- `template_text`
- `plan`
- `fact`
- `evidence`
### 6. 不要把 gap 消灭成“看起来闭环”
bridge/eval 的价值之一就是发现缺口。缺口不是失败，伪闭环才是失败。
### 7. 不要把 source 当备注
每个 supported claim、section、page-spec 都应挂 source。source 缺失不是小问题，而是红线。
### 8. 不要把复杂 trace graph / graph DB 作为 v1 前提
先用 `source_files[] + page_specs[] + gap_items[] + transformation_log[]` 就够。别在 v1 上复杂基础设施。
### 9. 不要先做 PPT 深层自动化
0305 暴露的核心问题不是版式自动化，而是：
- source 对不对
- 逻辑链顺不顺
- 缺口有没有被识别
### 10. 不要只靠 prompt 做防幻觉
优先把这些写成代码级 validator：
- unknown-preserving schema
- source 必填约束
- candidate/draft/confirmed 生命周期
- hard fail 规则
- 报告标题不得高于正文证据等级
---
## 一句话 handoff
先实现一个“能把 stage6 + 0305 这类半计划、半写作、强 source 约束对象，稳定落成 Pack/Task 并输出 gap audit”的 bridge/eval 内核；先追求可验证，不追求全能。