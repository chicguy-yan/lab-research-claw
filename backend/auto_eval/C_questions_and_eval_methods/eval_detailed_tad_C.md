# Scenario C 详细评测设计 TAD

## 0. 文档定位
- 对应文件：`eval_detailed_tad_C.md`
- 对应 scenario：`scenario_C`
- questions json：`C_scenario_questions.json`
- 评分细则总数：`93`（31 turns × 3）
- LLM-judge 细则数：`31`（每个 turn 1 条，满足不低于 1/3）

## 1. 场景定位
该场景围绕“材料科研智能体能否把实验主线落成 task，而不是泛泛讲机理”展开。它覆盖合成 checklist、性能/动力学矩阵、最小机理闭环、Ce 线 task board、章节依赖图与 experiment handoff。

### 1.1 本场景重点测什么
- stage2 synthesis checklist 与标号/交叉污染防错
- 性能+动力学 screening matrix
- PMSO / ClO2 / EPR 最小机理闭环
- Ce-Co3O4 两周任务板与依赖关系
- 章节-实验依赖图与实验 handoff

### 1.2 与系统基类的衔接方式
- 由 `scenario_C_registry.build_default_criteria()` 自动从 `C_scenario_questions.json` 生成 93 条 criterion。
- 由 `scenario_C_runbook.evaluate_turn()` 统一调度内容规则、trace/artifact 检查、LLM-judge 与 hallucination flags。
- 由 `scenario_C_llm_judges.build_llm_prompt()` 组装专家 prompt。
- 由 `scenario_C_hallucination_checks.aggregate_hallucination_metrics()` 汇总该场景特有的幻觉子指标。

## 2. 源文件清单与角色
- `BENCHMARK_RATIONALE_MD`：实验/Task benchmark 设计说明，强调实验目标→方法→证据→下一步
  - path: `C_EXPERIMENT_TASK_BENCHMARK_RATIONALE.md`
- `STAGE2_SYNTHESIS_MD`：第二阶段合成总表，含称量、标号、水热/煅烧等关键操作
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/2-材料合成方法/【第二阶段】材料合成方法汇总.md`
- `STAGE2_WHY_MD`：第二阶段 why/how 文档，用于解释为何从 Co3O4 起步
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第二阶段/【第二阶段实验脉络：Co3O4What？Why？How？】.md`
- `STAGE2_RECORD_MD`：第二阶段实验记录，补充现场执行与样品管理细节
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第二阶段/【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md`
- `CLO2_METHOD_DOCX`：ClO2 测试方法 docx，二进制方法参考文档
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第五阶段：最小机理闭环/ClO2测试方法文献/方法整理.docx`
- `AOPS_MD`：第五阶段亚氯酸盐 AOPs 主线文档，描述最小机理闭环需要的测试对象
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第五阶段：最小机理闭环/【亚氯酸盐AOPs】 1.md`
- `CLO2_EPR_MODEL_MD`：ClO2 EPR 测试方法建模文档，用于 EPR 路线设计
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第五阶段：最小机理闭环/【第五阶段】ClO2的EPR测试方法建模.md`
- `STAGE6_MAIN_MD`：第六阶段高价钴/苯酚主线文档，用于章节-实验映射
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第六阶段0305/【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md`
- `STAGE4_CE_MD`：第四阶段 Ce-Co3O4 机理主线文档，用于 Ce 线任务分解
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/第四阶段/【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`
- `PMSO_CLO2_SOP_MD`：PMSO 探针和 ClO2 显色 SOP，含关键试剂与分析链
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/2-逻辑节点/【亚氯酸盐AOPs活性物种测试】PMSO探针和ClO2显色.md`
- `PROBE_QUENCHER_SOP_MD`：探针/淬灭/显色通用 SOP
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/2-逻辑节点/【实验sop】关键活性物种の探针&淬灭&显色剂.md`
- `QUENCHER_SOP_MD`：·OH/1O2/O2- 淬灭动力学 SOP，含母液/加样量
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/2-逻辑节点/【第五阶段实验sop】·OH、1O2、O2-掩蔽动力学（淬灭）.md`
- `EPR_SOP_MD`：自由基 EPR 测试 SOP，含 DMPO/TEMP 等条件
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/2-逻辑节点/【第五阶段实验sop】·OH、1O2、O2-的EPR测试.md`
- `CEO2_SOP_MD`：CeO2 合成与淬灭实验 SOP，含 reflux / calcination 细节
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/2-逻辑节点/【第六阶段】亚氯酸盐体系！CeO2合成&淬灭实验sop.md`
- `GRAPHPAD_MD`：GraphPad 性能+动力学数据处理说明
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/3-节点外工具/【Graphpad】性能体系：性能+动力学.md`

## 3. session 设计概览
- 1. `scenario_C_session_001_bootstrap` — [EVAL][C] bootstrap experiment task workspace；T1：这个 workspace 我想定义成 `实验/Task 容器`，目标不是先讲... / T2：再补一个限制：这个容器的职责不是帮我写综述，而是把`本周要做的实验`拆成能执... / T3：可以，确认初始化。请把 seed pack 存成 `memory/packs...
- 2. `scenario_C_session_002_stage2_checklist` — [EVAL][C] stage2 synthesis checklist；T1：我准备今天照着《第二阶段材料合成方法汇总》去做一轮初始 Co3O4 / Cu... / T2：再单独帮我抽一张`标号防错清单`：从配液、称量、转移、取出内胆、洗涤、烘干到... / T3：把这轮整理成 `memory/tasks/C_stage2_checklis...
- 3. `scenario_C_session_003_screening_matrix` — [EVAL][C] stage2 screening and kinetics；T1：我不想只停留在“把材料做出来”。请你结合第二阶段 why/how、实验记录、... / T2：再往下走一步：请你给我一个最小数据表模板。我要知道原始数据、归一化后的降解曲... / T3：请把这轮保存成 `memory/tasks/C_screening_matr...
- 4. `scenario_C_session_004_why_co3o4` — [EVAL][C] why Co3O4 and when to upgrade；T1：我在写 task board 的开头时总会把“为什么先做 Co3O4”写得很... / T2：顺手再帮我把它改写成一个更适合贴在 task 文档开头的版本：要求短、硬、能... / T3：把它沉淀成 `memory/concepts/C_why_co3o4.md`...
- 5. `scenario_C_session_005_pmso_clo2` — [EVAL][C] PMSO and ClO2 minimal mechanism task；T1：现在进入第五阶段的最小机理闭环。请你结合《亚氯酸盐AOPs》、PMSO+Cl... / T2：你再补一列`哪些信息是直接针对 chlorite，哪些只是通用方法参考`。我... / T3：把这轮存成 `memory/tasks/C_pmso_clo2_minima...
- 6. `scenario_C_session_006_epr_strategy` — [EVAL][C] direct EPR vs spin-trap strategy；T1：如果目标是把 Co(IV)=O、ClO2、·OH、1O2 这些线索尽量分开看... / T2：请你站在‘实验资源有限’的角度，再做一个取舍：如果只能先启动一条主线、一条备... / T3：把这轮整理成 `memory/tasks/C_epr_strategy.md...
- 7. `scenario_C_session_007_quencher_matrix` — [EVAL][C] quencher matrix and concentration sanity；T1：我想把淬灭实验做成一个不会乱的矩阵。请你结合‘关键活性物种の探针&淬灭&显色... / T2：再单独帮我找`最可能把体系搞歪的浓度区间`。比如哪些加得太狠可能直接改变基底... / T3：请把它存成 `memory/tasks/C_quencher_matrix....
- 8. `scenario_C_session_008_ce_task_board` — [EVAL][C] Ce-Co3O4 mechanism board；T1：我想把 Ce-Co3O4 这条线变成一个两周 task board。请你结合... / T2：再帮我区分一下：哪些是`必须做`，哪些是`有条件再做`，哪些是`失败时的回退... / T3：把这轮保存成 `memory/tasks/C_ce_task_board.m...
- 9. `scenario_C_session_009_chapter_dependency` — [EVAL][C] chapter-linked experiment dependency map；T1：我想把实验任务和写作章节提前挂钩。请你结合第六阶段主线、GraphPad 笔... / T2：如果 direct proof 暂时做不出来，你再帮我写一个`不失真但能先推... / T3：请把这轮存成 `memory/packs/C_chapter_depende...
- 10. `scenario_C_session_010_handoff` — [EVAL][C] experiment task handoff；T1：最后请你帮我做一个 experiment handoff：把第二阶段合成、第... / T2：再补一个`实验规划 anti-hallucination 清单`：以后如果我... / T3：把最后的 handoff 存成 `memory/packs/C_handof...

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
### 5.1 `C_PROMPT_EVIDENCE_EXPERT`
你是一名长期负责环境催化实验设计、SOP 审核与研究生 task board 把关的评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补完实验条件。你要重点检查：回答是否把 stage2 合成、PMSO/ClO2、EPR、quencher、CeO2 合成等内容真正翻译成可执行 task；是否清楚区分原始记录、SOP、通用方法文档与当前体系的既定条件；是否避免编造浓度、加样量、容器、时序、仪器条件；是否解释了每一步要回答的机制问题；是否在信息不足时诚实提示‘需回 SOP / 回 docx / 回记录’。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.2 `C_PROMPT_CLOSURE_EXPERT`
你是一名擅长把实验主线压缩成 Task/Pack 的材料科研项目经理。请判断这条回答能否被当作 experiment closure 的稳定对象：它是否有清晰的任务目标、执行顺序、依赖关系、回退路线与结果判读；是否真的把实验对象落到 checklist / matrix / task board，而不是写成机理散文；是否保留了条件边界与误判风险；是否足够具体到研究生日常可以照着执行或继续补充。请严格只基于给定材料评分，不要用你自己的实验经验替模型补缺。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.3 `C_PROMPT_HALLUCINATION_EXPERT`
你是一名专门审查科研实验规划幻觉的化学评估专家。请重点盯住四类风险：第一，模型是否捏造了称量量、浓度、加样量、时间、容器、仪器设置等具体条件；第二，是否把通用方法参考（尤其 docx、通用 SOP）直接当成当前 chlorite 体系的既定条件；第三，是否在没有 trace 解析二进制文档的情况下，装作已经看到了其中的细节；第四，是否忽略了依赖关系、把失败回退路线说成可选装饰。只要出现明显编条件、伪造可执行细节、或不诚实地越过信息边界，就应严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

## 6. 场景特有 hallucination 子指标
- `C_H1_condition_fabrication_rate`：统计无来源捏造称量量、浓度、加样量、时间、仪器条件等实验细节的比例。
- `C_H2_sop_scope_honesty`：统计能否区分“当前体系既定条件”和“通用 SOP / docx 参考条件”；混淆则扣分。
- `C_H3_binary_method_grounding`：对 docx / 复杂 SOP 相关 turn，检查是否有真实解析或明确的不确定性声明。
- `C_H4_trace_to_task_alignment`：统计 trace 是否真的围绕 task 落地（读 SOP→写 task→必要时 abstain），而不是给空泛实验建议。
- `C_H5_reagent_interference_awareness`：统计淬灭剂/探针使用中是否提示可能改变基底反应、产生误判或交叉干扰。

## 7. Python 原型模块职责
- `scenario_C_registry.py`：加载 scenario json、生成 CriterionSpec、校验 file coverage、统计 turns/binary/prior-memory。
- `scenario_C_content_checks.py`：关键术语覆盖、禁词惩罚、prior memory 痕迹、内容规则评分。
- `scenario_C_trace_checks.py`：trace 解析、tool usage 检查、binary grounding 检查、write/read 行为判定。
- `scenario_C_artifact_checks.py`：artifact 存在性、required sections、source_assets frontmatter、preview 生成。
- `scenario_C_llm_judges.py`：专家 prompt 模板、prompt 选择器、judge 输入组装、JSON 输出解析。
- `scenario_C_hallucination_checks.py`：unsupported specificity、source confusion、cross-transfer、artifact fabrication 等 flags 与子指标聚合。
- `scenario_C_runbook.py`：把 registry / checks / judge 串成统一 scenario runtime blueprint。

## 8. 90 条评分细则
## 01. [EVAL][C] bootstrap experiment task workspace
- session_id: `scenario_C_session_001_bootstrap`
- 目标：该 session 必须复用 __bootstrap__。

### Turn 1
- 用户上传：C_EXPERIMENT_TASK_BENCHMARK_RATIONALE.md、【第二阶段】材料合成方法汇总.md、【第二阶段实验脉络：Co3O4What？Why？How？】.md
- 关注关键词：实验/Task 容器 / benchmark rationale / 合成 checklist / 性能筛选矩阵 / 最小机理闭环 / 接下来该做哪些实验对象
- `C-S001-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 workspace 定义成 experiment/task 容器，并给出最合适的起手对象。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S001-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“bootstrap 阶段至少应读取 markdown 源；不应误入 literature summary 或 writing pack。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S001-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模型是否真正理解 experiment closure 的核心是任务落地，而不是泛泛整理研究背景。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：本周要做的实验 / 拆成能执行的 task / 先产出哪类 task 对象 / 暂时不该展开哪些线
- `C-S001-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须输出 task-oriented 的初始化策略，并指出暂缓线索。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S001-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮应体现 skip-by-design，不应默认生成大篇综述或写作材料。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S001-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模型是否把实验 workspace 的职责压缩到近期可执行对象。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：确认初始化 / 这个包测什么 / 先做哪类任务 / 暂不展开的线 / PACK_bootstrap_kickoff
- `C-S001-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要完成实验 workspace 的 bootstrap，并落一份 seed pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S001-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/PACK_bootstrap_kickoff.md` 存在、section 覆盖 ['这个包测什么', '先做哪类任务', '暂不展开的线']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S001-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 seed pack 是否明确了 task-first 的初始化目标。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 02. [EVAL][C] stage2 synthesis checklist
- session_id: `scenario_C_session_002_stage2_checklist`
- 目标：主测 stage2 synthesis 是否能被准确拆成现场执行 task。

### Turn 1
- 用户上传：【第二阶段】材料合成方法汇总.md、【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md
- 关注关键词：按时间顺序的 checklist / 称量量 / 容器 / 标号 / 搅拌 / 水热
- `C-S002-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 Stage2 合成步骤转成按时间顺序的操作 checklist，并突出标号/交叉污染风险。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S002-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取两份 stage2 markdown，并尽量引用其中的具体量与风险提示。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S002-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 checklist 是否真的可执行，而不是松散总结。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：标号防错清单 / 瓶身 / 离心管 / 坩埚 / 同步写标号 / 具体后果
- `C-S002-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要给出贯穿全过程的标号防错方案，并说明漏写的具体后果。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S002-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用 stage2 资料和上轮结果，不需要离开当前 task 主题。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S002-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正抓住实验现场最容易出错的节点。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：按时间顺序 checklist / 标号和防交叉污染 / 需要现场记录的数据 / C_stage2_checklist
- `C-S002-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 stage2 合成 checklist 固化为 task 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S002-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_stage2_checklist.md` 存在、section 覆盖 ['按时间顺序 checklist', '标号和防交叉污染', '需要现场记录的数据']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S002-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 task 文档是否可以直接带进实验台旁边使用。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 03. [EVAL][C] stage2 screening and kinetics
- session_id: `scenario_C_session_003_screening_matrix`
- 目标：主测从合成走向筛选矩阵和动力学对象化。

### Turn 1
- 用户上传：【第二阶段实验脉络：Co3O4What？Why？How？】.md、【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md、【Graphpad】性能体系：性能+动力学.md
- 关注关键词：性能+动力学筛选矩阵 / 材料横轴 / 性能指标 / 动力学指标 / GraphPad / 决定值不值得往 Ce-Co3O4 升级
- `C-S003-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须给出 stage2 screening matrix，并能支持后续升级决策。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S003-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 why/how、record 与 GraphPad 笔记，不应只输出空泛 KPI。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S003-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断矩阵是否真正能服务材料筛选与下一阶段决策。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：最小数据表模板 / 原始数据 / 归一化后的降解曲线 / 伪一级拟合 / 误差线 / 重复实验
- `C-S003-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要输出可直接落地的数据表模板，并指出关键不可丢字段。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S003-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用上一轮 matrix 与 GraphPad 逻辑，不应跳去无关实验设计。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S003-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模板是否足够细，能支持后续绘图和拟合复现。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：材料维度 / 性能维度 / GraphPad输出要求 / C_screening_matrix
- `C-S003-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 screening 逻辑沉淀为后续可复用 task。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S003-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_screening_matrix.md` 存在、section 覆盖 ['材料维度', '性能维度', 'GraphPad输出要求']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S003-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断该任务文件是否兼顾实验设计和数据处理。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 04. [EVAL][C] why Co3O4 and when to upgrade
- session_id: `scenario_C_session_004_why_co3o4`
- 目标：主测实验路线起点合理性与升级触发条件。

### Turn 1
- 用户上传：C_EXPERIMENT_TASK_BENCHMARK_RATIONALE.md、【第二阶段实验脉络：Co3O4What？Why？How？】.md、【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md
- 关注关键词：为什么从 Co3O4 起步 / 为什么不是一开始就上更复杂体系 / 什么时候升级到 Ce-Co3O4 / benchmark rationale
- `C-S004-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 why Co3O4 的理由、跳步风险、升级条件拆清楚。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S004-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 rationale + why/how + record，不可只给泛泛的材料学套话。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S004-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真的理解阶段性研究设计，而不是抽象科学意义。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：短 / 硬 / 能指导行动 / task 文档开头 / 表述写太重 / 先验站队
- `C-S004-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要把 why Co3O4 改写成 task-board 可用的开场，并保留谨慎边界。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S004-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用本 session 的逻辑，不需要新增其它来源。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S004-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断文本是否兼具方向感与证据克制。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：为什么从Co3O4开始 / 升级条件 / 不能跳步的原因 / C_why_co3o4
- `C-S004-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要形成一个专门解释 stage2 起点与升级条件的 concept card。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S004-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/C_why_co3o4.md` 存在、section 覆盖 ['为什么从Co3O4开始', '升级条件', '不能跳步的原因']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S004-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept card 是否能够作为后续实验/写作共享的前言对象。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 05. [EVAL][C] PMSO and ClO2 minimal mechanism task
- session_id: `scenario_C_session_005_pmso_clo2`
- 目标：主测第五阶段最小机制闭环、docx grounding 与条件克制。

### Turn 1
- 用户上传：【亚氯酸盐AOPs】 1.md、【亚氯酸盐AOPs活性物种测试】PMSO探针和ClO2显色.md、方法整理.docx
- 关注关键词：最小机制任务链 / 试剂准备 / 取样 / PMSO/PMSO2 / ClO2 测定 / 结果怎么判读
- `C-S005-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把第五阶段最小机理闭环拆成可执行 task 链，覆盖 PMSO 与 ClO2 两条检测线。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S005-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“包含 docx；若回答涉及 docx 里的具体方法差异，trace 应体现对二进制的解析或明确不确定边界。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_hallucination_checks.compute_turn_flags()`。
- `C-S005-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断方案是否真正服务 chlorite 体系的最小机理闭环，而不是泛化的高级氧化综述。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：直接针对 chlorite / 通用方法参考 / 不要直接当成既定条件 / docx
- `C-S005-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须区分 chlorite-specific 条件与 generic analytical reference，防止条件被误写成既定值。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S005-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用本轮读取结果，并对 docx 的不确定部分保持诚实。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S005-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模型是否具备方法学迁移时的边界意识。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：最小闭环目标 / 实验步骤 / 结果判读 / C_pmso_clo2_minimal_mechanism
- `C-S005-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 PMSO + ClO2 最小机理闭环固定成 task 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S005-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_pmso_clo2_minimal_mechanism.md` 存在、section 覆盖 ['最小闭环目标', '实验步骤', '结果判读']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S005-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断该任务文档是否足够具体，后续可直接执行。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 06. [EVAL][C] direct EPR vs spin-trap strategy
- session_id: `scenario_C_session_006_epr_strategy`
- 目标：主测方法学取舍与 binary 文档 grounding。

### Turn 1
- 用户上传：【第五阶段】ClO2的EPR测试方法建模.md、【第五阶段实验sop】·OH、1O2、O2-的EPR测试.md、方法整理.docx
- 关注关键词：直接 EPR / 加捕获剂的 EPR / 显色/探针 / 最能回答什么 / 最不能回答什么 / Co(IV)=O
- `C-S006-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须比较三条检测路线在当前机制问题中的能力边界。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S006-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“包含 EPR md + docx，若给出具体实验配置或限制，trace 应有相应读取或解析行为。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_hallucination_checks.compute_turn_flags()`。
- `C-S006-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断比较是否真正服务问题分辨，而不是泛泛介绍 EPR。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：实验资源有限 / 一条主线 / 一条备线 / 结论边界 / 失败后的回退路径
- `C-S006-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须给出资源受限下的主线/备线选择，并带回退策略。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S006-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用上轮的路线比较，不应脱离当前资料新增昂贵方法。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S006-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断选择是否体现最小可行和失败回退意识。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：首选路线 / 并行路线 / 结论边界 / C_epr_strategy
- `C-S006-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要沉淀一份 EPR/探针策略 task 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S006-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_epr_strategy.md` 存在、section 覆盖 ['首选路线', '并行路线', '结论边界']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S006-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 task 文档是否真的能指导资源有限时的实验路线选择。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 07. [EVAL][C] quencher matrix and concentration sanity
- session_id: `scenario_C_session_007_quencher_matrix`
- 目标：主测 quencher / probe 条件是否被准确提取并用于反误判。

### Turn 1
- 用户上传：【实验sop】关键活性物种の探针&淬灭&显色剂.md、【第五阶段实验sop】·OH、1O2、O2-掩蔽动力学（淬灭）.md、【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
- 关注关键词：quencher matrix / 母液 / 目标浓度 / 加样量 / 主要想排除什么 / 最容易引入什么干扰
- `C-S007-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把淬灭/探针方案整理成浓度明确、干扰明确的矩阵。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S007-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取两份 SOP 和 stage6 主线，不应只给淬灭剂名称列表。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S007-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断矩阵是否兼顾可执行性与误判风险。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：最可能把体系搞歪的浓度区间 / 改变基底反应 / 看起来像抑制了某物种 / 风险提醒
- `C-S007-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要指出 quencher 使用中的高风险浓度与误判来源。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S007-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应基于 SOP 数字和 stage6 语境做风险解释，不可机械抄表。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S007-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否体现了实验判断而不是表格搬运。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：淬灭剂矩阵 / 浓度与加样量 / 可能误判 / C_quencher_matrix
- `C-S007-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要将 quencher 设计固化成 task 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S007-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_quencher_matrix.md` 存在、section 覆盖 ['淬灭剂矩阵', '浓度与加样量', '可能误判']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S007-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断文档是否能真正指导后续淬灭实验设计。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 08. [EVAL][C] Ce-Co3O4 mechanism board
- session_id: `scenario_C_session_008_ce_task_board`
- 目标：主测 Ce 线从 stage4 走向 stage6 的 task orchestration。

### Turn 1
- 用户上传：【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md、【第六阶段】亚氯酸盐体系！CeO2合成&淬灭实验sop.md、【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
- 关注关键词：两周 task board / CeO2 / Ce-Co3O4 样品准备 / 性能回测 / 高价钴证据 / 依赖关系
- `C-S008-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 Ce 线拆成两周内可执行的并行任务板，并标出依赖关系。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S008-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 stage4/stage6/ceo2 sop，不应只输出概念化路线图。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S008-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断任务板是否兼具样品制备、性能验证与机制证据三条线。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：必须做 / 有条件再做 / 失败时的回退路线 / CeO2 合成不稳定 / 后移
- `C-S008-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要完成 must-have / conditional / fallback 的任务分层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S008-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应基于上轮依赖关系来给出顺序调整，不应忽视制样失败对后续任务的连锁影响。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S008-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否有真实项目管理感，而不是平铺任务清单。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：必须做 / 依赖关系 / 失败回退路线 / C_ce_task_board
- `C-S008-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 Ce 线任务板沉淀成可执行 task 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S008-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/tasks/C_ce_task_board.md` 存在、section 覆盖 ['必须做', '依赖关系', '失败回退路线']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S008-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 task board 是否具备执行顺序和失败回退逻辑。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 09. [EVAL][C] chapter-linked experiment dependency map
- session_id: `scenario_C_session_009_chapter_dependency`
- 目标：主测 experiment closure 与 future chapter structure 的对接。

### Turn 1
- 用户上传：【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md、【Graphpad】性能体系：性能+动力学.md、【亚氯酸盐AOPs】 1.md
- 关注关键词：章节-实验依赖图 / 第一章高价钴选择性生成 / 第二章苯酚/淬灭/活性图 / 共用方法
- `C-S009-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把章节目标映射到实验依赖与数据处理依赖上。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S009-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取 stage6、graphpad、AOPS 主线，并能复用已有 task cards。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S009-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正让 experiment closure 与 future writing closure 对齐。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：direct proof 暂时做不出来 / 不失真但能先推进写作 / supporting evidence / 必须留白
- `C-S009-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要给出 direct proof 缺席时的写作推进策略，强调不失真。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S009-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应基于依赖图与前序 proof/quencher/epr tasks，而不是随意补洞。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S009-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断方案是否诚实且仍具推进性。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：第一章 / 第二章 / 共用方法与卡点 / C_chapter_dependency
- `C-S009-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把章节-实验依赖图沉淀成 pack 文档。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S009-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/C_chapter_dependency.md` 存在、section 覆盖 ['第一章', '第二章', '共用方法与卡点']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S009-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否真正有助于把实验任务接到写作主线。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 10. [EVAL][C] experiment task handoff
- session_id: `scenario_C_session_010_handoff`
- 目标：最终 handoff session，用于评测实验 workspace 的状态管理与反幻觉规则。

### Turn 1
- 用户上传：【第二阶段】材料合成方法汇总.md、【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md、【亚氯酸盐AOPs】 1.md、【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md、【第五阶段实验sop】·OH、1O2、O2-的EPR测试.md
- 关注关键词：experiment handoff / 当前有哪些任务在飞 / 每个任务最缺什么 / 下一步先做什么
- `C-S010-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对整个实验 workspace 的任务状态做 handoff 分层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S010-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用前序 tasks/packs，并与这轮上传文件核对，不应忽视 stage5/stage6 之间的连接。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S010-T01-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 handoff 是否真正反映了实验任务的当前状态与缺口。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：anti-hallucination 清单 / 回 SOP / 回原始记录 / 回方法文档 / 不要直接编条件
- `C-S010-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要生成实验规划问答的防幻觉清单。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S010-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应基于 docx/SOP/record 的二义性来给出 guardrails。”。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()`。
- `C-S010-T02-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断清单是否击中实验规划最常见的编条件风险。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：当前任务板 / 未闭环的关键证据 / 后续问答禁区 / C_handoff
- `C-S010-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要将实验 workspace 的 handoff 形成最终 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_C_content_checks.evaluate_content_rule()`。
- `C-S010-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/C_handoff.md` 存在、section 覆盖 ['当前任务板', '未闭环的关键证据', '后续问答禁区']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_C_trace_checks.evaluate_trace_rule()` + `scenario_C_artifact_checks.evaluate_artifact_rule()`。
- `C-S010-T03-C3` [LLM_JUDGE | 100] 使用 `C_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断最终 handoff 是否足以让另一个模型继续接手实验任务。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_C_llm_judges.build_llm_prompt()` + `parse_judge_response()`。


## 9. 实施注意事项
- 如果某个 turn 声明 `binary_grounding_required=true`，而 trace 中既没有 `terminal/python_repl` 解析痕迹、回答里也没有明确承认边界，则相关 criterion 直接重罚。
- 如果 turn 的 `expected_artifacts` 不为空，则默认要求 trace 中出现 `write_file` 或等价写入动作。
- 所有写入到 `memory/` 的 artifact，若基于上传源文件生成，优先检查 `source_assets` frontmatter 是否存在。
- 若回答复用了 prior sessions 的产物，但没有任何 prior-memory 痕迹（如前序 concept / pack 名称、memory 路径、或显式引用），在 RULE/LLM_JUDGE 中都应酌情扣分。

## 10. 一句话结论
Scenario C 的核心不是单看回答“像不像懂”，而是联合检查：**对象是否落地、trace 是否诚实、artifact 是否真实、binary 是否被真正解析、source-layer 是否被清楚区分。**