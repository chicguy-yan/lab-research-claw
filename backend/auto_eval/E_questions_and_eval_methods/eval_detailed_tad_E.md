# Scenario E 详细评测设计 TAD

## 0. 文档定位
- 对应文件：`eval_detailed_tad_E.md`
- 对应 scenario：`scenario_E`
- questions json：`E_scenario_questions.json`
- 评分细则总数：`93`（31 turns × 3）
- LLM-judge 细则数：`31`（每个 turn 1 条，满足不低于 1/3）

## 1. 场景定位
该场景围绕“材料科研智能体能否站在 benchmark/evaluator 视角做桥接，而不是回到研究内容本身”展开。它要求系统能从 package architecture、closure mapping、test cases 与 representative assets 中抽出 read-order、priority、schema、failure modes 与 prompt contract。

### 1.1 本场景重点测什么
- bridge 层 read-order 与 selective drill-down
- literature / experiment / writing 三类 closure 选型
- schema 审计与 prompt contract
- cross-closure 断链/误迁移模式
- 可交给 Codex 的 handoff 与 evaluator 自身 anti-hallucination

### 1.2 与系统基类的衔接方式
- 由 `scenario_E_registry.build_default_criteria()` 自动从 `E_scenario_questions.json` 生成 93 条 criterion。
- 由 `scenario_E_runbook.evaluate_turn()` 统一调度内容规则、trace/artifact 检查、LLM-judge 与 hallucination flags。
- 由 `scenario_E_llm_judges.build_llm_prompt()` 组装专家 prompt。
- 由 `scenario_E_hallucination_checks.aggregate_hallucination_metrics()` 汇总该场景特有的幻觉子指标。

## 2. 源文件清单与角色
- `CLOSURE_JSON`：closure mapping 机器可读版本，用于 loader/schema 设计
  - path: `outputs/closure_mapping.json`
- `CLOSURE_MD`：closure mapping 可读版本，用于分析与解释
  - path: `outputs/closure_mapping.md`
- `PRO_ARCH_MD`：增强包 package architecture 文档，定义 A/B/C/D/E 逻辑包
  - path: `outputs/pro_dataset_expanded_20260317/PRO_PROMPT_PACKAGE_ARCHITECTURE.md`
- `ECOSYSTEM_MD`：research OS ecosystem map，概述三条研究主线与对象关系
  - path: `outputs/research_os_ecosystem_map.md`
- `TEST_EXPERIMENT_MD`：experiment closure 测试用例说明
  - path: `outputs/test_cases_experiment.md`
- `TEST_LITERATURE_MD`：literature closure 测试用例说明
  - path: `outputs/test_cases_literature.md`
- `TEST_WRITING_MD`：writing closure 测试用例说明
  - path: `outputs/test_cases_writing.md`
- `HVCO_PACK_MD`：跨闭环示例中的高价钴 pack
  - path: `科研obsidian/0-毕业论文安排20251230/0305大组会指导自己实验，精读并梳理出激励链条（数据量+逻辑确定））/高价钴框架/【PACK】高价钴氧物种生成机理链.md`
- `CE_PPTX`：跨闭环示例中的 Ce-Co3O4 写作素材
  - path: `科研obsidian/0-毕业论文安排20251230/Ce掺杂Co3O4亚氯酸盐高级氧化.pptx`
- `THESIS_WORKDOC_MD`：跨闭环示例中的 thesis 工作文档
  - path: `科研obsidian/0-毕业论文安排20251230/【毕业论文】工作文档0305.md`
- `OX_SELECTIVE_PPTX`：跨闭环示例中的旁支 bridge 写作素材
  - path: `科研obsidian/0-毕业论文安排20251230/选择性氧化框架/0327大组会-颜雍颀.pptx`
- `STAGE6_MAIN_MD`：experiment closure representative file（第六阶段主线）
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第六阶段0305/【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md`
- `STAGE4_CE_MD`：experiment closure representative file（第四阶段 Ce 主线）
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第四阶段/【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`
- `AOPS_MAIN_MD`：亚氯酸盐 AOPs 主线文档，提供 experiment/literature 连接点
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/1-主逻辑/【亚氯酸盐AOPs】.md`
- `GM_FINAL_PPTX`：writing closure representative final deck
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/20260305大组会-颜雍颀-v5_最终交付.pptx`
- `GM_WORKDOC_MD`：writing closure representative working document
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/【20260305大组会】工作文档.md`

## 3. session 设计概览
- 1. `scenario_E_session_001_bootstrap` — [EVAL][E] bootstrap bridge workspace；T1：这个 workspace 我想定义成 `跨闭环桥接容器`，主要是把文献、实验... / T2：补一个限制：这个容器的职责不是重新读完所有原始材料，而是先用 bridge ... / T3：可以，确认初始化。完成后请确保 seed pack 至少能回答三件事：`这个...
- 2. `scenario_E_session_002_package_read_order` — [EVAL][E] package architecture and read order；T1：我现在要开始真正构 benchmark 了。请你结合 closure_map... / T2：再补一个`停止下钻条件`：什么时候说明某个 closure 已经足够清晰，不... / T3：把这轮存成 `memory/packs/E_package_read_ord...
- 3. `scenario_E_session_003_literature_priority` — [EVAL][E] literature closure priority；T1：如果只先做 literature_closure 这一类 benchmark... / T2：再给我定义每一类 literature closure 的`成功信号`和`失... / T3：把这轮整理成 `memory/packs/E_literature_prio...
- 4. `scenario_E_session_004_experiment_priority` — [EVAL][E] experiment closure priority；T1：如果只先做 experiment_closure 这一类 benchmark... / T2：顺便再帮我定义一下：一个模型如果真的理解了 experiment closu... / T3：把它保存成 `memory/packs/E_experiment_prior...
- 5. `scenario_E_session_005_writing_priority` — [EVAL][E] writing closure priority；T1：如果只先做 writing_closure 这一类 benchmark，请你... / T2：我还想让你给出一个`pack 质量标准`：什么叫真正的 pack，什么只是普... / T3：请把结论存成 `memory/packs/E_writing_priorit...
- 6. `scenario_E_session_006_mapping_schema_audit` — [EVAL][E] closure mapping schema audit；T1：我准备把 closure_mapping 直接喂给 evaluator lo... / T2：你再帮我把这些字段分成三层：`scenario级必须字段`、`turn级必须... / T3：把这轮保存成 `memory/concepts/E_mapping_sche...
- 7. `scenario_E_session_007_cross_closure_failure_modes` — [EVAL][E] cross-closure chain and failure modes；T1：如果我把文献、实验、写作三条线真的串起来，最容易在哪些地方断链？请你结合高价... / T2：再补一个`误迁移模式`清单：哪些情况下模型很容易把文献里的启发直接说成实验结... / T3：请把这轮整理成 `memory/concepts/E_cross_closu...
- 8. `scenario_E_session_008_benchmark_prioritization` — [EVAL][E] benchmark prioritization；T1：如果我只能先做一版精简 benchmark，你帮我从 literature ... / T2：再补一列：为什么有些 case 现在先不做？我希望看到的是‘暂缓理由’，比如... / T3：把结果存成 `memory/packs/E_benchmark_priori...
- 9. `scenario_E_session_009_prompt_contract` — [EVAL][E] prompt contract for bridge evaluator；T1：我准备开始写 scenario json 和 scorer 了。请你结合 p... / T2：另外我很在意两类 guardrail：`binary_grounding_r... / T3：把它保存成 `memory/packs/E_prompt_contract....
- 10. `scenario_E_session_010_handoff` — [EVAL][E] bridge eval handoff；T1：最后请你站在‘我要把这套 bridge/eval 设计交给 Codex 落代... / T2：再给我一个`bridge evaluator anti-hallucinat... / T3：把最后的 handoff 存成 `memory/packs/E_handof...

## 4. 评分实现策略
每个 turn 固定三条细则：
1. `RULE`：检查关键术语覆盖、对象是否落地、是否触碰禁词/过强断言。
2. `TRACE / ARTIFACT / HALLUCINATION`：检查是否真的读了该读的文件、是否解析了 binary、是否写出预期 artifact、是否存在 source_assets frontmatter、是否出现典型幻觉模式。
3. `LLM_JUDGE`：用场景化专家 prompt 做语义评价，输出结构化 JSON。

### 4.1 turn / session / scenario 聚合
- turn_score = 3 条 criterion 均值
- session_score = 3 个 turn 均值
- scenario_score = 10 个 session 均值
- 另行输出场景级 hallucination 子指标，不与总分混淆

## 5. LLM-Judge Prompt 库
### 5.1 `E_PROMPT_EVIDENCE_EXPERT`
你是一名长期设计 benchmark、evaluator、数据集包架构与科研智能体协议的系统评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补系统设计。你要重点检查：回答是否真正站在 bridge/eval 视角而不是研究内容视角；是否清楚区分 package architecture、closure mapping、ecosystem map、test cases 与 downstream representative assets 的角色；是否把 loader / runner / scorer / llm-judge / report 等对象说清楚；是否明确哪些是 runtime 必须字段、哪些只是 analyst 注释；是否避免泛泛而谈的“平台化建议”。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.2 `E_PROMPT_CLOSURE_EXPERT`
你是一名擅长把复杂 benchmark 设计收束成可实现协议的系统架构师。请判断这条回答能否作为 bridge/eval closure 的稳定对象：它是否真正形成了 read-order、priority、schema、prompt contract、failure mode 或 handoff 这类可执行对象；是否区分了 scenario/session/turn/criterion 层级；是否兼顾实现成本、覆盖度与可评分性；是否能够被 Codex 直接消费为实现输入。不要用自己的经验替模型补上尚未写出的系统约束，只按现有回答评分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.3 `E_PROMPT_HALLUCINATION_EXPERT`
你是一名专门审查 evaluator 自身幻觉的系统评估专家。请重点盯住：模型是否把 bridge 层索引文件说成原始科研证据；是否把 schema / prompt contract 讲得很完整却没有落到 loader-runner-scorer 的真实接口；是否忽略 binary grounding、source-layer honesty、stop rule、跨 session memory 等关键 guardrail；是否把 benchmark 选型说成“覆盖全面”但其实没有能力覆盖矩阵；是否在没有 trace/文件依据的情况下臆测 closure mapping 中的字段含义。遇到这种系统性自我欺骗要严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

## 6. 场景特有 hallucination 子指标
- `E_H1_schema_runtime_fidelity`：统计 scenario/session/turn/criterion 字段建议是否真正可被 loader-runner-scorer 消费，而非高层空话。
- `E_H2_bridge_source_honesty`：统计是否正确区分 bridge 层索引文件与原始科研证据，避免把 mapping 说成事实本身。
- `E_H3_priority_coverage_integrity`：统计 benchmark prioritization 是否同时覆盖 bootstrap、binary、artifact、memory、guardrail 等关键能力。
- `E_H4_cross_closure_failure_awareness`：统计是否识别 literature→experiment→writing 的断链点与误迁移模式。
- `E_H5_evaluator_self_guardrails`：统计是否把 binary_grounding_required、source-layer honesty、stop-rule、abstain 等 evaluator 自身护栏落到接口层。

## 7. Python 原型模块职责
- `scenario_E_registry.py`：加载 scenario json、生成 CriterionSpec、校验 file coverage、统计 turns/binary/prior-memory。
- `scenario_E_content_checks.py`：关键术语覆盖、禁词惩罚、prior memory 痕迹、内容规则评分。
- `scenario_E_trace_checks.py`：trace 解析、tool usage 检查、binary grounding 检查、write/read 行为判定。
- `scenario_E_artifact_checks.py`：artifact 存在性、required sections、source_assets frontmatter、preview 生成。
- `scenario_E_llm_judges.py`：专家 prompt 模板、prompt 选择器、judge 输入组装、JSON 输出解析。
- `scenario_E_hallucination_checks.py`：unsupported specificity、source confusion、cross-transfer、artifact fabrication 等 flags 与子指标聚合。
- `scenario_E_runbook.py`：把 registry / checks / judge 串成统一 scenario runtime blueprint。

## 8. 90 条评分细则
## 01. [EVAL][E] bootstrap bridge workspace
- session_id: `scenario_E_session_001_bootstrap`
- 目标：该 session 必须复用 __bootstrap__。

### Turn 1
- 用户上传：PRO_PROMPT_PACKAGE_ARCHITECTURE.md、research_os_ecosystem_map.md、closure_mapping.json
- 关注关键词：跨闭环桥接容器 / benchmark / eval system / package architecture / closure mapping / ecosystem map
- `E-S001-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 workspace 定义成 bridge/eval 容器，明确 primary object 是 bridge pack 而不是原始实验或文献容器。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S001-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“bootstrap 阶段至少应读取 md/json 文件，并避免默认生成实验/写作内容。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S001-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 scope 是否真正围绕 bridge/eval 任务，而不是把它误当成普通研究 workspace。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：不是重新读完所有原始材料 / 该读什么 / 暂时不该读什么 / bridge/handoff
- `E-S001-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 generation plan 收紧到 selective reading 和 bridge handoff，而非全面 ingest。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S001-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮应体现 skip-by-design：不默认创建大量概念/任务文件。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S001-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断是否真正理解 bridge 容器的职责：先决策阅读路径，再进入具体对象。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：确认初始化 / 这个包测什么 / 不等于原始全集 / 下一步先读哪一组文件 / PACK_bootstrap_kickoff
- `E-S001-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“完成 bootstrap 并生成 bridge seed pack，强调 package purpose 和 read-order。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S001-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/PACK_bootstrap_kickoff.md` 存在、section 覆盖 ['这个包测什么', '它为什么不等于原始全集', '下一步先读哪一组文件']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S001-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 seed pack 是否真正服务 bridge/eval，而不是泛泛数据集说明。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 02. [EVAL][E] package architecture and read order
- session_id: `scenario_E_session_002_package_read_order`
- 目标：主测 bridge 层的 read-order 设计。

### Turn 1
- 用户上传：closure_mapping.md、test_cases_literature.md、test_cases_experiment.md
- 关注关键词：读取顺序 / 哪层索引 / 哪类 closure / 什么时候下钻原始文件 / evaluator 视角
- `E-S002-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须从 evaluator 视角设计 package read order，而不是按研究内容平铺。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S002-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 mapping 与 test cases，并体现‘先索引后下钻’的读取策略。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S002-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 read order 是否真的服务 benchmark 构建。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：停止下钻条件 / closure 已经足够清晰 / 必须回源文件 / 不能只停留在 bridge 层
- `E-S002-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须定义 stop rules 与 fallback-to-source rules。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S002-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用 mapping/test-cases 结果，不应给泛泛的‘看情况’。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S002-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 stop rules 是否具体、可执行。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：建议读取顺序 / 每一步要确认的对象 / 停止下钻条件 / E_package_read_order
- `E-S002-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 bridge 读取顺序固定成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S002-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_package_read_order.md` 存在、section 覆盖 ['建议读取顺序', '每一步要确认的对象', '停止下钻条件']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S002-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否能直接指导 benchmark engineer 的首轮阅读。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 03. [EVAL][E] literature closure priority
- session_id: `scenario_E_session_003_literature_priority`
- 目标：主测 bridge 系统对 literature_closure 的筛选与评分意识。

### Turn 1
- 用户上传：test_cases_literature.md、【PACK】高价钴氧物种生成机理链.md、closure_mapping.md
- 关注关键词：literature_closure / 优先级 / 基线 chlorite 机制 / Ce-Co3O4/电子结构迁移 / high-valent metal-oxo / selective oxidation bridge / 模型幻觉
- `E-S003-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对 literature closures 做 benchmark 优先级划分，并考虑 hallucination 区分度。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S003-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 test cases + mapping + hvco pack，不应只从难易度主观排序。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S003-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断优先级判断是否真正服务 benchmark 价值，而非 researcher 兴趣。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：成功信号 / 失败信号 / source layer / 边界 / 迁移关系
- `E-S003-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 literature closure 的成功/失败信号操作化。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S003-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用 prior mapping/read order 结果，明确哪些信号来自 trace、哪些来自回答质量。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S003-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断成功/失败信号是否具有可评分性。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：优先级 / 为什么 / 评价信号 / E_literature_priority
- `E-S003-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 literature priority 结果沉淀为 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S003-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_literature_priority.md` 存在、section 覆盖 ['优先级', '为什么', '评价信号']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S003-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否足以指导 scenario 选型与评分设计。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 04. [EVAL][E] experiment closure priority
- session_id: `scenario_E_session_004_experiment_priority`
- 目标：主测 experiment_closure 的 benchmark 区分度与 trace 特征。

### Turn 1
- 用户上传：test_cases_experiment.md、【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md、【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md、【亚氯酸盐AOPs】.md
- 关注关键词：experiment_closure / 筛选矩阵 / 最小机理闭环 / Ce 线证据链 / 任务落地能力 / 乱编实验条件
- `E-S004-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对 experiment closures 做 benchmark 优先级排序，并强调 task-landing 与 condition-hallucination 风险。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S004-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 test cases 与三条实验主线，不应仅按主观难度排序。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S004-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断排序是否真正服务 task closure benchmark 的区分力。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：真的理解了 experiment closure / trace 里通常会出现什么 / 读 SOP / 写 task / 承认信息不够
- `E-S004-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 experiment closure 的 trace 特征说清楚。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S004-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮的输出本身就是 trace-spec 设计，应区分 read/parse/write/abstain 四类行为。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S004-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断是否把 experiment closure 的真实行为学特征抽出来了。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：优先级 / 关键trace / 高风险 hallucination 点 / E_experiment_priority
- `E-S004-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 experiment priority 结果固定成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S004-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_experiment_priority.md` 存在、section 覆盖 ['优先级', '关键trace', '高风险 hallucination 点']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S004-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否可以直接服务 experiment benchmark 的选型与评测。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 05. [EVAL][E] writing closure priority
- session_id: `scenario_E_session_005_writing_priority`
- 目标：主测 writing_closure 的区分度、binary grounding 与 pack-quality 设计。

### Turn 1
- 用户上传：test_cases_writing.md、Ce掺杂Co3O4亚氯酸盐高级氧化.pptx、【毕业论文】工作文档0305.md、0327大组会-颜雍颀.pptx、20260305大组会-颜雍颀-v5_最终交付.pptx、【20260305大组会】工作文档.md
- 关注关键词：writing_closure / 组会 pack 复盘 / thesis reverse engineering / 旁支桥接写作 / pack-quality / 读二进制时的幻觉
- `E-S005-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对 writing closures 做 benchmark 优先级排序，并突出 pack-quality 与 binary hallucination。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S005-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“涉及多个 pptx + md，若提出 pack-quality 标准应体现对二进制理解边界的谨慎。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_hallucination_checks.compute_turn_flags()`。
- `E-S005-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断优先级是否真正反映 writing closure 的评测价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：pack 质量标准 / 真正的 pack / 普通摘要 / 最容易造假的点 / PPT / 工作文档 / 最终稿之间最容易混的地方
- `E-S005-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须定义 pack-quality，并指出 writing closure 中最易造假的源头。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S005-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用 prior pack replay / storyline thinking，不要给空泛标准。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S005-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断质量标准是否足够具体，能区分一般总结与高质量 pack。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：优先级 / pack质量标准 / 最容易造假的点 / E_writing_priority
- `E-S005-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 writing priority 结果固定成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S005-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_writing_priority.md` 存在、section 覆盖 ['优先级', 'pack质量标准', '最容易造假的点']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S005-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否足以指导 writing benchmark 的首批选型。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 06. [EVAL][E] closure mapping schema audit
- session_id: `scenario_E_session_006_mapping_schema_audit`
- 目标：主测桥接层 schema 审计与运行时字段抽象。

### Turn 1
- 用户上传：closure_mapping.json、closure_mapping.md、research_os_ecosystem_map.md
- 关注关键词：closure_mapping / evaluator loader / 运行时必须有的字段 / analyst 注释 / schema 不够
- `E-S006-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须站在 evaluator loader 视角审 schema，而不是只解释 mapping 内容。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S006-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应同时读取 json 与 md，并注意两者的一致性/冗余。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S006-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 schema 审计是否可直接指导实现，而非高层建议。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：scenario级必须字段 / turn级必须字段 / 仅供分析但不影响运行的字段 / 还缺字段
- `E-S006-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 schema 缺口具体化到 scenario/turn/runtime 层级。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S006-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 schema audit，不应只给抽象字段名。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S006-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断字段分层是否与评测系统实现真实对齐。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：必须字段 / 可选字段 / schema缺口 / E_mapping_schema_audit
- `E-S006-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 schema 审计沉淀为概念卡。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S006-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/E_mapping_schema_audit.md` 存在、section 覆盖 ['必须字段', '可选字段', 'schema缺口']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S006-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept 是否真正能被 codex/工程实现直接消费。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 07. [EVAL][E] cross-closure chain and failure modes
- session_id: `scenario_E_session_007_cross_closure_failure_modes`
- 目标：主测 cross-closure 断链与 hallucination 模式抽象。

### Turn 1
- 用户上传：【PACK】高价钴氧物种生成机理链.md、【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md、【毕业论文】工作文档0305.md、【亚氯酸盐AOPs】.md
- 关注关键词：跨闭环断链表 / literature -> experiment / experiment -> writing / source layer 自己就混了
- `E-S007-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须识别三条线衔接中的断链点与 source-layer 混乱点。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S007-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取四个跨层来源，并尝试结合已建立的 mapping/priority 结果。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S007-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 failure mode 分析是否真正抓住 cross-closure benchmark 的难点。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：误迁移模式 / 文献里的启发直接说成实验结论 / 写作草稿直接说成稳定结果 / hallucination 指标
- `E-S007-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 cross-closure 误迁移模式抽象成可评测的 hallucination 类型。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S007-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接 failure mode 分析，并转换成 evaluator 可用指标。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S007-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断是否真正把 failure mode 翻译成评测项，而不是泛泛风险提醒。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：断链点 / 误迁移模式 / 防呆规则 / E_cross_closure_failure_modes
- `E-S007-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 cross-closure failure modes 固化为概念卡。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S007-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/E_cross_closure_failure_modes.md` 存在、section 覆盖 ['断链点', '误迁移模式', '防呆规则']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S007-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept 是否能直接支撑后续 hallucination 指标设计。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 08. [EVAL][E] benchmark prioritization
- session_id: `scenario_E_session_008_benchmark_prioritization`
- 目标：主测首版 benchmark 的范围收敛。

### Turn 1
- 用户上传：test_cases_literature.md、test_cases_experiment.md、test_cases_writing.md、PRO_PROMPT_PACKAGE_ARCHITECTURE.md
- 关注关键词：精简 benchmark / 8-12 个最代表性的 session 类型 / bootstrap / binary 解析 / artifact 写入 / 跨 session memory
- `E-S008-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须给出首版 benchmark 的 representative set，并保证能力覆盖。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S008-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取三类 test_cases 与 package architecture，不可只凭直觉挑题。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S008-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 prioritization 是否兼顾覆盖度与实现成本。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：为什么有些 case 现在先不做 / 暂缓理由 / 信息重复 / 边界不清 / 太依赖人工判读 / 增益不够高
- `E-S008-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须给出 benchmark 暂缓项及其具体理由。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S008-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 prioritization 结果，体现覆盖/成本/可评测性的平衡。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S008-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断暂缓理由是否具有工程上的说服力。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：入选 benchmark / 覆盖理由 / 暂缓项 / E_benchmark_prioritization
- `E-S008-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把首版 benchmark 选型结果沉淀为 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S008-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_benchmark_prioritization.md` 存在、section 覆盖 ['入选 benchmark', '覆盖理由', '暂缓项']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S008-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否可以直接用于第一版 benchmark 范围冻结。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 09. [EVAL][E] prompt contract for bridge evaluator
- session_id: `scenario_E_session_009_prompt_contract`
- 目标：主测 bridge 层字段契约与 guardrail 的工程化。

### Turn 1
- 用户上传：PRO_PROMPT_PACKAGE_ARCHITECTURE.md、closure_mapping.json、closure_mapping.md
- 关注关键词：bridge evaluator 的 prompt contract / scenario 级 / session 级 / turn 级 / loader / runner
- `E-S009-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 prompt contract 具体化到 scenario/session/turn 三个层级。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S009-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应结合 architecture 与 mapping，不应停留在抽象 schema 建议。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S009-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断字段设计是否足够支撑自动化运行和评分。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：binary_grounding_required / source-layer honesty / 需要哪些字段 / runner / scorer 里落地
- `E-S009-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 binary grounding 与 source-layer honesty 转成可运行的 contract 字段和执行逻辑。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S009-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 contract 设计，明确 loader/runner/scorer 各自消费哪些字段。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S009-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 guardrails 是否已从原则落成可实现接口。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：scenario级字段 / turn级字段 / 评分级字段 / E_prompt_contract
- `E-S009-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 prompt contract 固化成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S009-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_prompt_contract.md` 存在、section 覆盖 ['scenario级字段', 'turn级字段', '评分级字段']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S009-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否可直接交给 Codex 作为实现输入。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 10. [EVAL][E] bridge eval handoff
- session_id: `scenario_E_session_010_handoff`
- 目标：最终 handoff session，评测 bridge/eval 体系能否被工程化交接。

### Turn 1
- 用户上传：closure_mapping.md、【20260305大组会】工作文档.md、【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md、test_cases_writing.md
- 关注关键词：交给 Codex 落代码 / 第一优先要实现什么 / 最适合模板化 / 先别过度工程化
- `E-S010-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须以实现 handoff 的视角给出 build-first / template-first / avoid-overengineering 的建议。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S010-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应结合 bridge documents 与 representative downstream assets，不应只给泛泛工程建议。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S010-T01-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 handoff 是否真的能让实现者快速开工。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：bridge evaluator anti-hallucination 规则清单 / loader / runner / llm-judge / 报告器 / 系统层护栏
- `E-S010-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须抽象出 evaluator 自身的 anti-hallucination 规则，并映射到系统组件。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S010-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应综合前序 failure modes / prompt contract / priority 结果，形成系统级 guardrails。”。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()`。
- `E-S010-T02-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断规则清单是否覆盖 evaluator 自身最容易出错的环节。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：先实现什么 / 可模板化部分 / 不要做错的事情 / E_handoff
- `E-S010-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要将 bridge/eval 设计的最终 handoff 固化成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_E_content_checks.evaluate_content_rule()`。
- `E-S010-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/E_handoff.md` 存在、section 覆盖 ['先实现什么', '可模板化部分', '不要做错的事情']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_E_trace_checks.evaluate_trace_rule()` + `scenario_E_artifact_checks.evaluate_artifact_rule()`。
- `E-S010-T03-C3` [LLM_JUDGE | 100] 使用 `E_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 handoff 是否足够清晰，能直接支持 Codex 开始实现。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_E_llm_judges.build_llm_prompt()` + `parse_judge_response()`。


## 9. 实施注意事项
- 如果某个 turn 声明 `binary_grounding_required=true`，而 trace 中既没有 `terminal/python_repl` 解析痕迹、回答里也没有明确承认边界，则相关 criterion 直接重罚。
- 如果 turn 的 `expected_artifacts` 不为空，则默认要求 trace 中出现 `write_file` 或等价写入动作。
- 所有写入到 `memory/` 的 artifact，若基于上传源文件生成，优先检查 `source_assets` frontmatter 是否存在。
- 若回答复用了 prior sessions 的产物，但没有任何 prior-memory 痕迹（如前序 concept / pack 名称、memory 路径、或显式引用），在 RULE/LLM_JUDGE 中都应酌情扣分。

## 10. 一句话结论
Scenario E 的核心不是单看回答“像不像懂”，而是联合检查：**对象是否落地、trace 是否诚实、artifact 是否真实、binary 是否被真正解析、source-layer 是否被清楚区分。**