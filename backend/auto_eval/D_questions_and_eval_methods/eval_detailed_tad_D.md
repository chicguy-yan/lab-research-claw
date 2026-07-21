# Scenario D 详细评测设计 TAD

## 0. 文档定位
- 对应文件：`eval_detailed_tad_D.md`
- 对应 scenario：`scenario_D`
- questions json：`D_scenario_questions.json`
- 评分细则总数：`93`（31 turns × 3）
- LLM-judge 细则数：`31`（每个 turn 1 条，满足不低于 1/3）

## 1. 场景定位
该场景围绕“材料科研智能体能否把写作碎片收束成 pack-quality 交付件，而不是普通摘要”展开。它要求系统能够处理 markdown + pptx + docx + pdf 的混合素材，并识别版本权威性与图组组织逻辑。

### 1.1 本场景重点测什么
- thesis gap map 与 storyline master
- 高价钴主证链 storyboard
- group meeting 交付件复盘
- proposal 多版本 revision reasoning
- figure/layout 规则抽取与 writing handoff

### 1.2 与系统基类的衔接方式
- 由 `scenario_D_registry.build_default_criteria()` 自动从 `D_scenario_questions.json` 生成 93 条 criterion。
- 由 `scenario_D_runbook.evaluate_turn()` 统一调度内容规则、trace/artifact 检查、LLM-judge 与 hallucination flags。
- 由 `scenario_D_llm_judges.build_llm_prompt()` 组装专家 prompt。
- 由 `scenario_D_hallucination_checks.aggregate_hallucination_metrics()` 汇总该场景特有的幻觉子指标。

## 2. 源文件清单与角色
- `HVCO_PACK_MD`：高价钴机理链核心 pack，提供 thesis/group meeting 的主证链草图
  - path: `科研obsidian/0-毕业论文安排20251230/0305大组会指导自己实验，精读并梳理出激励链条（数据量+逻辑确定））/高价钴框架/【PACK】高价钴氧物种生成机理链.md`
- `HVCO_PROOF_PPTX`：高价钴证明实验 PPT，二进制写作素材
  - path: `科研obsidian/0-毕业论文安排20251230/0305大组会指导自己实验，精读并梳理出激励链条（数据量+逻辑确定））/高价钴框架/高价钴证明实验.pptx`
- `PROGRESS_PLAN_MD`：进度规划文档，用于两周排期与交付路线
  - path: `科研obsidian/0-毕业论文安排20251230/20251230【进度规划】.md`
- `CE_PPTX`：Ce 掺杂 Co3O4 汇报 PPT，提供 chapter / group meeting 素材
  - path: `科研obsidian/0-毕业论文安排20251230/Ce掺杂Co3O4亚氯酸盐高级氧化.pptx`
- `THESIS_WORKDOC_MD`：毕业论文工作文档，记录图组与 thesis 组织线索
  - path: `科研obsidian/0-毕业论文安排20251230/【毕业论文】工作文档0305.md`
- `PROPOSAL_V3_PPTX`：开题报告 V3 PPT，中间版本素材
  - path: `科研obsidian/0-毕业论文安排20251230/开题/开题报告-颜雍颀-V3.pptx`
- `FIG_LAYOUT_PPTX`：文章图片排版经验 PPT，用于 layout 规则抽取
  - path: `科研obsidian/0-毕业论文安排20251230/文章图片排版【机密】.pptx`
- `ANGEW_PDF`：CeO2/Co3O4 相关 Angew 文献，作为背景/旁证素材
  - path: `科研obsidian/0-毕业论文安排20251230/材料表征/20260307同步辐射分析/Angew Chem Int Ed - 2022 - Song - Overturned Loading of Inert CeO2 to Active Co3O4 for Unusually Improved Catalytic.pdf`
- `POLYMER_MD`：高价钴+聚合证据链调研文档，用于 discussion bridge
  - path: `科研obsidian/0-毕业论文安排20251230/聚合框架/【gpt文献调研：高价钴氧物种生成+聚合证据链】.md`
- `OX_SELECTIVE_PPTX`：0327 大组会 PPT，选择性氧化/旁支写作素材
  - path: `科研obsidian/0-毕业论文安排20251230/选择性氧化框架/0327大组会-颜雍颀.pptx`
- `PATHWAY_PDF`：electron-transfer vs polymerization 反应路径调控论文
  - path: `科研obsidian/0-毕业论文安排20251230/选择性氧化框架/reaction-pathway-tuning-between-electron-transfer-mediated-degradation-and-polymerization-in-fe-mos2-based-persulfate.pdf`
- `PROPOSAL_MD`：开题报告重构版 markdown
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/1-开题报告准备-重构/【开题报告】.md`
- `PROPOSAL_PLAN_MD`：开题报告准备脉路
  - path: `科研obsidian/1-主逻辑树-自上而下（脉络）+自下而上（结果）/1-开题报告准备-重构/【开题报告准备脉路】.md`
- `PROPOSAL_TEMPLATE_MD`：开题报告范本 markdown
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/1-开题报告范本/【开题报告】.md`
- `PROPOSAL_FINAL_DOCX`：开题报告 final docx，最终稿权威来源
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/1-开题报告范本/开题报告final-20251229/开题报告-颜雍颀(1).docx`
- `GM_FINAL_PPTX`：20260305 大组会最终交付 PPT
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/20260305大组会-颜雍颀-v5_最终交付.pptx`
- `LIT_REPORT_PPTX`：literature_report_FINAL，示例汇报 deck
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/literature_report_FINAL_v2-1.pptx`
- `GM_WORKDOC_MD`：20260305 大组会工作文档
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/【20260305大组会】工作文档.md`
- `EXAMPLE_PDF`：示例 PPT PDF，用于排版/节奏参考
  - path: `科研obsidian/3-sop库：主逻辑-逻辑节点-节点外工具-节点外求助/20260305大组会/示例ppt.pdf`

## 3. session 设计概览
- 1. `scenario_D_session_001_bootstrap` — [EVAL][D] bootstrap writing pack workspace；T1：这个 workspace 我想定义成一个 `写作/Pack 容器`。它的职责... / T2：再加一个限制：这个容器不是用来重写论文全文的，而是要先判断`哪个 pack ... / T3：可以，确认初始化。请把 seed pack 存成 `memory/packs...
- 2. `scenario_D_session_002_thesis_gapmap` — [EVAL][D] thesis figure and evidence gap map；T1：我现在最需要的是一张 thesis gap map。请你结合毕业论文工作文档... / T2：你再进一步，把这些缺口按`最先补会影响最大的`顺序排一下。不是简单按难度，而... / T3：把这轮保存成 `memory/packs/D_thesis_gapmap.m...
- 3. `scenario_D_session_003_two_week_plan` — [EVAL][D] progress plan into two-week execution；T1：请你把我现在的进度规划，转成一个接下来两周的`交付件导向排期`。输入是进度规... / T2：再补一个‘日复盘模板’：每天结束时，我最少应该检查哪几项，才能知道这天到底是... / T3：把这轮存成 `memory/packs/D_two_week_plan.md...
- 4. `scenario_D_session_004_hvco_storyboard` — [EVAL][D] high-valent cobalt evidence storyboard；T1：我想把‘高价钴证明’这条线讲成一个能上 thesis / group mee... / T2：请再补一列`不能越界的表述`。比如哪些表征只能说明更容易形成高价钴，哪些不能... / T3：把这轮保存成 `memory/packs/D_hvco_storyboard...
- 5. `scenario_D_session_005_group_meeting_replay` — [EVAL][D] 20260305 group meeting replay；T1：我想把 20260305 这次大组会反向拆解一下：请你结合那份工作文档、最终... / T2：如果让我今天重做这套组会包，你再帮我给出一个`第一轮 revision ch... / T3：把结论存成 `memory/packs/D_group_meeting_re...
- 6. `scenario_D_session_006_proposal_revision` — [EVAL][D] proposal revision matrix；T1：我想把开题报告的多版本演化梳理清楚。请你结合 proposal 的准备脉路、... / T2：你再给我标一列：哪些地方是‘写得更锋利了’，哪些地方其实只是‘删掉了含糊表述... / T3：把这轮保存成 `memory/packs/D_proposal_revisi...
- 7. `scenario_D_session_007_figure_layout_rules` — [EVAL][D] figure layout rules；T1：我想把‘文章图片排版【机密】’里的经验抽出来，变成自己 thesis / 汇... / T2：再给我一个`常见错误清单`：哪些页看起来很努力，但实际上信息密度失衡、图和结... / T3：把这轮整理成 `memory/packs/D_figure_layout_r...
- 8. `scenario_D_session_008_selective_oxidation_bridge` — [EVAL][D] selective oxidation and polymerization bridge；T1：我想把 selective oxidation / polymerizati... / T2：顺手再给我做一个`风险语句清单`：以后如果我在写作里问到类似桥接问题，哪些说... / T3：把它沉淀成 `memory/concepts/D_selective_oxi...
- 9. `scenario_D_session_009_thesis_storyline` — [EVAL][D] thesis storyline master；T1：现在请你把 thesis 的主线真正收起来。结合 Ce 掺杂 Co3O4 P... / T2：再帮我补上`缺口`这一列：每章如果现在就写，会缺哪类图、哪类对照、哪类解释。... / T3：请把它保存到 `memory/packs/D_thesis_storylin...
- 10. `scenario_D_session_010_handoff` — [EVAL][D] writing pack handoff；T1：最后请你站在‘我要把这个 writing workspace 交给另一个模型... / T2：再补一个`后续写作 anti-hallucination 清单`：如果以后我... / T3：请把最后的 handoff 存成 `memory/packs/D_hando...

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
### 5.1 `D_PROMPT_EVIDENCE_EXPERT`
你是一名长期指导博士论文、开题答辩、组会汇报与科研写作 pack 设计的导师型评审。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】评分，不要替模型补写作结构。你要重点检查：回答是否真正围绕 pack-quality 交付件组织；是否区分最终稿、工作文档、中间版本、排版示例、背景论文等不同 authority level；是否能够把 thesis / proposal / group meeting / storyboard / layout rule 转成可复用的交付对象；是否在二进制 PPTX/DOCX/PDF 信息不足时保持诚实；是否避免把版本草稿说成稳定结论。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.2 `D_PROMPT_CLOSURE_EXPERT`
你是一名擅长把科研写作碎片收束成 Pack 的高级编辑与课题导师。请判断这条回答是否已经形成可复用的 writing closure 对象：是否清晰指向某个交付件（storyline、gap map、revision matrix、layout rule、handoff）；是否含有足够的结构、权威来源排序、风险提示与下一步动作；是否能够在后续 thesis / proposal / group meeting 中直接复用；是否避免只做普通摘要而没有 pack 的组织价值。不要根据经验替模型补出未写出的结构，要严格按现有回答给分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.3 `D_PROMPT_HALLUCINATION_EXPERT`
你是一名专门审查科研写作与二进制文档幻觉的评估专家。请重点检查：模型是否在未真正解析 PPTX/DOCX/PDF 的情况下伪造页数、版式、章节内容或版本差异；是否把工作文档和最终稿混为一谈；是否把排版/风格参考误写成科学主张来源；是否把旁支 bridge 或背景论文过度包装成 thesis 主证；是否用‘最终稿明确说明’‘这页 PPT 证明了’等强断言而没有真实依据。出现明显二进制臆测、版本混淆或 authority level 失真时应严厉扣分。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

## 6. 场景特有 hallucination 子指标
- `D_H1_version_authority_integrity`：统计是否正确区分 final docx/pptx、工作文档、中间版本与排版示例的 authority level。
- `D_H2_binary_extract_honesty`：统计在未真实解析 pptx/docx/pdf 时是否伪造页码、版式、章节细节或版本差异。
- `D_H3_pack_quality_integrity`：统计输出是否真正形成 pack-quality 对象，而不是普通摘要冒充 pack。
- `D_H4_figure_evidence_alignment`：统计是否把图组、证据链、章节主张映射清楚；若图和结论错配则扣分。
- `D_H5_bridge_overclaim_rate`：统计 selective oxidation / polymerization /背景论文 是否被过度包装成 thesis 主证。

## 7. Python 原型模块职责
- `scenario_D_registry.py`：加载 scenario json、生成 CriterionSpec、校验 file coverage、统计 turns/binary/prior-memory。
- `scenario_D_content_checks.py`：关键术语覆盖、禁词惩罚、prior memory 痕迹、内容规则评分。
- `scenario_D_trace_checks.py`：trace 解析、tool usage 检查、binary grounding 检查、write/read 行为判定。
- `scenario_D_artifact_checks.py`：artifact 存在性、required sections、source_assets frontmatter、preview 生成。
- `scenario_D_llm_judges.py`：专家 prompt 模板、prompt 选择器、judge 输入组装、JSON 输出解析。
- `scenario_D_hallucination_checks.py`：unsupported specificity、source confusion、cross-transfer、artifact fabrication 等 flags 与子指标聚合。
- `scenario_D_runbook.py`：把 registry / checks / judge 串成统一 scenario runtime blueprint。

## 8. 90 条评分细则
## 01. [EVAL][D] bootstrap writing pack workspace
- session_id: `scenario_D_session_001_bootstrap`
- 目标：该 session 必须复用 __bootstrap__。

### Turn 1
- 用户上传：【PACK】高价钴氧物种生成机理链.md、【毕业论文】工作文档0305.md、20251230【进度规划】.md
- 关注关键词：写作/Pack 容器 / 哪些交付件最值得整理成 pack / 章节主线 / 图组缺口 / 组会交付件
- `D-S001-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 workspace 定义成 writing/pack 容器，并选出最合适的起手交付对象。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S001-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“bootstrap 阶段至少应读取三个 markdown 来源，并避免误转成实验 task 容器。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S001-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正围绕交付件组织，而不是回到研究综述。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：哪个 pack 最有复用价值 / 哪个文件是权威来源 / 哪个只能当参考素材 / 起步策略
- `D-S001-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要给出 pack-first 的启动策略，并区分 authority vs reference。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S001-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮应体现 selective organization，不应默认生成大段正文。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S001-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模型是否理解 writing closure 的对象是交付件及其权威层级。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：确认初始化 / 这个包测什么 / 优先整理哪类交付件 / 哪些文件只是参考 / PACK_bootstrap_kickoff
- `D-S001-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要完成 writing workspace 的 bootstrap，并写出 seed pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S001-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/PACK_bootstrap_kickoff.md` 存在、section 覆盖 ['这个包测什么', '优先整理哪类交付件', '哪些文件只是参考']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S001-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 seed pack 是否为 writing closure 提供了清晰的组织入口。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 02. [EVAL][D] thesis figure and evidence gap map
- session_id: `scenario_D_session_002_thesis_gapmap`
- 目标：主测 thesis 组织与图组缺口识别。

### Turn 1
- 用户上传：【毕业论文】工作文档0305.md、20251230【进度规划】.md、【20260305大组会】工作文档.md
- 关注关键词：thesis gap map / 哪些已经能写 / 哪些有数据但逻辑还没串 / 哪些根本还缺实验
- `D-S002-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 thesis 当前状态拆成图组/证据/逻辑缺口三层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S002-T01-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应读取三份 markdown，并尽量把 gap map 对应到具体图组或章节。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S002-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 gap map 是否真能指导 thesis 收束，而不是空泛待办清单。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：最先补会影响最大的 / 同时解锁多少后续写作/汇报工作 / 排序
- `D-S002-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要按解锁效应而非难度对 thesis 缺口重新排序。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S002-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用上轮 gap map 结果，不应脱离已有文件随意加任务。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S002-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断排序逻辑是否体现交付导向，而不仅是实验导向。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：已有图组 / 缺口 / 优先补的实验 / D_thesis_gapmap
- `D-S002-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 thesis gap map 沉淀成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S002-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_thesis_gapmap.md` 存在、section 覆盖 ['已有图组', '缺口', '优先补的实验']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S002-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否可以直接用于后续 thesis 管理。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 03. [EVAL][D] progress plan into two-week execution
- session_id: `scenario_D_session_003_two_week_plan`
- 目标：主测把进度规划翻译成交付件排期。

### Turn 1
- 用户上传：20251230【进度规划】.md、【20260305大组会】工作文档.md、Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
- 关注关键词：两周交付件导向排期 / 每天/每两天 / 图 / 表 / pack / PPT 页面
- `D-S003-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 progress plan 转成交付件导向的两周排期，而不是只列实验动作。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S003-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“包含 pptx；若回答涉及 Ce deck 里的具体内容，trace 应体现对二进制的解析或明确限定。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S003-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断排期是否真正以交付件推进为核心。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：日复盘模板 / 推进 thesis / 组会 / proposal / 碎活
- `D-S003-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要给出日复盘模板，让 daily work 与交付件保持对齐。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S003-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮排期，不要脱离具体交付件。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S003-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模板是否真正帮助 researcher 做交付闭环，而不是空泛效率建议。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：按天排期 / 交付件 / 风险与回退 / D_two_week_plan
- `D-S003-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把两周排期固化成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S003-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_two_week_plan.md` 存在、section 覆盖 ['按天排期', '交付件', '风险与回退']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S003-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否已经是 researcher 可直接执行的排期板。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 04. [EVAL][D] high-valent cobalt evidence storyboard
- session_id: `scenario_D_session_004_hvco_storyboard`
- 目标：主测高价钴主证链在写作场景中的对象化。

### Turn 1
- 用户上传：【PACK】高价钴氧物种生成机理链.md、高价钴证明实验.pptx、Angew Chem Int Ed - 2022 - Song - Overturned Loading of Inert CeO2 to Active Co3O4 for Unusually Improved Catalytic.pdf
- 关注关键词：高价钴证明 / storyboard / 每一页/每一图最想回答什么 / 主证 / 支持证据 / 背景材料
- `D-S004-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把高价钴 story 拆成 page/figure-level storyboard，并区分证据层级。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S004-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“包含 pptx/pdf；若引用具体页/表征，trace 应体现对二进制的解析。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S004-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 storyboard 是否真的可用于 thesis / meeting 叙事，而不是简单摘要。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：不能越界的表述 / 更容易形成高价钴 / 不能直接说已经证明 Co(IV)=O / 讲稿脚注
- `D-S004-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 high-valent cobalt 叙事中的危险表述单独抽出来。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S004-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 storyboard 结果，不应新增无来源断言。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S004-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断危险表述列表是否具有真实的 anti-overclaim 价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：主证链 / 辅助证据 / 不能越界的表述 / D_hvco_storyboard
- `D-S004-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把高价钴 storyboard 固化为 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S004-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_hvco_storyboard.md` 存在、section 覆盖 ['主证链', '辅助证据', '不能越界的表述']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S004-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否能直接支撑 group meeting/thesis 的讲述设计。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 05. [EVAL][D] 20260305 group meeting replay
- session_id: `scenario_D_session_005_group_meeting_replay`
- 目标：主测从 pack 成品反向归纳组织逻辑。

### Turn 1
- 用户上传：【20260305大组会】工作文档.md、20260305大组会-颜雍颀-v5_最终交付.pptx、literature_report_FINAL_v2-1.pptx、示例ppt.pdf
- 关注关键词：大组会反向拆解 / 最终采用了什么结构 / 信息密度 / 讲述节奏 / 为什么它长成这样
- `D-S005-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对 group meeting 交付件做结构与节奏复盘，而非内容摘要。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S005-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“涉及多个 ppt/pdf；trace 应体现对二进制的解析，避免虚构页面结构。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S005-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断复盘是否真正抓住了 pack-quality 交付件的组织逻辑。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：第一轮 revision checklist / 最该先改 / 暂时可以接受 / 只会越改越乱
- `D-S005-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要给出 revision 优先级，而不是泛泛建议。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S005-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮对 pack 结构的复盘，不应离开具体交付件。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S005-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 revision checklist 是否有真实的编辑价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：结构复盘 / 做得好的地方 / 如果重做先改什么 / D_group_meeting_replay
- `D-S005-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 group meeting 复盘整理成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S005-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_group_meeting_replay.md` 存在、section 覆盖 ['结构复盘', '做得好的地方', '如果重做先改什么']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S005-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否可直接用于下一次组会准备。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 06. [EVAL][D] proposal revision matrix
- session_id: `scenario_D_session_006_proposal_revision`
- 目标：主测 proposal 多版本二进制材料的比较与 revision reasoning。

### Turn 1
- 用户上传：开题报告-颜雍颀-V3.pptx、【开题报告】.md、【开题报告准备脉路】.md、【开题报告】.md、开题报告-颜雍颀(1).docx
- 关注关键词：版本修订矩阵 / 补什么 / 删什么 / 收紧了什么科学主张 / proposal
- `D-S006-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须比较 proposal 多版本的演化，并总结每次修订的功能。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S006-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“含 pptx/docx；若回答涉及版本差异，trace 应体现对二进制的解析，不可凭名称猜内容。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S006-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断矩阵是否真实反映了 proposal 的收束过程。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：写得更锋利了 / 删掉了含糊表述 / 仍然存在逻辑跳跃 / revision sense
- `D-S006-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要对 proposal 修订做质量层面的判断，而不仅是逐字差异。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S006-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮版本矩阵，不应脱离版本证据做空泛评论。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S006-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断 revision sense 是否准确、细腻，符合真实学术写作迭代。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：版本差异 / 增强项 / 仍需修补 / D_proposal_revision_matrix
- `D-S006-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要形成一份 proposal revision pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S006-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_proposal_revision_matrix.md` 存在、section 覆盖 ['版本差异', '增强项', '仍需修补']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S006-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否能直接支持后续开题/论文写作修订。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 07. [EVAL][D] figure layout rules
- session_id: `scenario_D_session_007_figure_layout_rules`
- 目标：主测二进制排版样例向规则 pack 的转译。

### Turn 1
- 用户上传：文章图片排版【机密】.pptx、【毕业论文】工作文档0305.md、Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
- 关注关键词：图文排版规则 / 图-文比例 / 脚注 / 图题 / 信息层级 / 页内逻辑流
- `D-S007-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须从排版素材中抽出可复用的 figure/layout 规则。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S007-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“包含 pptx；如果引用具体版式，应体现对二进制内容的解析或承认不确定边界。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S007-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正抽到了可执行的 layout 规则，而不是泛泛审美建议。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：常见错误清单 / 信息密度失衡 / 图和结论不匹配 / 脚注不够 / 不适合口头讲
- `D-S007-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要输出反面规则清单，以避免 layout 类交付件中的典型问题。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S007-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 layout 规律，不应离开具体交付语境。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S007-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断错误清单是否对 researcher 真有纠偏作用。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：排版规则 / 图注脚注规则 / 常见错误 / D_figure_layout_rules
- `D-S007-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 layout 经验沉淀成可复用 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S007-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_figure_layout_rules.md` 存在、section 覆盖 ['排版规则', '图注脚注规则', '常见错误']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S007-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否具备跨 thesis / PPT 复用价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 08. [EVAL][D] selective oxidation and polymerization bridge
- session_id: `scenario_D_session_008_selective_oxidation_bridge`
- 目标：主测旁支文献到 writing discussion 的安全桥接。

### Turn 1
- 用户上传：【gpt文献调研：高价钴氧物种生成+聚合证据链】.md、0327大组会-颜雍颀.pptx、reaction-pathway-tuning-between-electron-transfer-mediated-degradation-and-polymerization-in-fe-mos2-based-persulfate.pdf、Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
- 关注关键词：selective oxidation / polymerization / discussion bridge / 只能写成启发 / 现在不该进正文
- `D-S008-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 selective oxidation / polymerization 内容分为 discussion bridge / inspiration / forbidden 三层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S008-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“涉及 md+pptx+pdf；trace 应体现对二进制与文本的联合读取，不可臆造图页信息。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S008-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正处理好了旁支写作的边界。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：风险语句清单 / 自动降级 / 可能相关 / 可启发 / 待验证 / 已经观察到
- `D-S008-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要形成桥接写作时的风险语句清单。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S008-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应承接上轮 bridge 分层结果，不应新增脱离来源的强断言。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S008-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断清单是否足够严格，能有效降低写作幻觉。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：可进入写作的桥 / 只适合作讨论的桥 / 风险语句 / D_selective_oxidation_bridge
- `D-S008-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要将旁支桥接逻辑沉淀为 concept card。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S008-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/D_selective_oxidation_bridge.md` 存在、section 覆盖 ['可进入写作的桥', '只适合作讨论的桥', '风险语句']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S008-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept card 是否能在写作时真实约束过度桥接。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 09. [EVAL][D] thesis storyline master
- session_id: `scenario_D_session_009_thesis_storyline`
- 目标：主测 thesis 全局 storyline 收束能力。

### Turn 1
- 用户上传：Ce掺杂Co3O4亚氯酸盐高级氧化.pptx、【PACK】高价钴氧物种生成机理链.md、【毕业论文】工作文档0305.md、0327大组会-颜雍颀.pptx
- 关注关键词：thesis storyline master / 每一章主要回答什么问题 / 各章之间靠什么逻辑接起来 / 每章最关键的图组是什么
- `D-S009-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须形成 thesis 的总主线，并把章节问题和关键图组对应起来。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S009-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应结合前序 packs/concepts 与本轮上传素材，不可只给通用论文大纲。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S009-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 storyline 是否足够具体，能指导后续 thesis 收束。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：缺口 / 会缺哪类图 / 哪类对照 / 哪类解释 / 章节之间接不起来
- `D-S009-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 storyline 与 gap map 再次合并，指出章节连接处的断点。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S009-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用 thesis gap map 与当前 storyline，不应遗失交叉章节依赖。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S009-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断是否真正发现了影响 thesis 连贯性的关键缺口。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：章节主线 / 图组映射 / 缺口 / D_thesis_storyline_master
- `D-S009-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 thesis 主线总收束成 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S009-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_thesis_storyline_master.md` 存在、section 覆盖 ['章节主线', '图组映射', '缺口']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S009-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断最终 storyline pack 是否已经具备 thesis 级别的组织价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 10. [EVAL][D] writing pack handoff
- session_id: `scenario_D_session_010_handoff`
- 目标：最终 handoff session，主测版本权威性判断与写作防幻觉规则。

### Turn 1
- 用户上传：【20260305大组会】工作文档.md、【PACK】高价钴氧物种生成机理链.md、开题报告-颜雍颀(1).docx、20260305大组会-颜雍颀-v5_最终交付.pptx、Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
- 关注关键词：writing workspace handoff / 权威来源 / 版本中间态 / 排版/风格参考
- `D-S010-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须按 authority level 对 writing workspace 中的文件做 handoff 分层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S010-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应复用前序 packs 并结合本轮上传文件，不可忽略 docx/pptx 的权威性差异。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_hallucination_checks.compute_turn_flags()`。
- `D-S010-T01-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 handoff 是否真的能帮助下一个模型少走弯路。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：后续写作 anti-hallucination 清单 / 需要回原文页 / 需要回版本源文件 / 需要确认是不是最终稿
- `D-S010-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要生成跨 pptx/docx/pdf 的写作防幻觉规则。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S010-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应结合本 scenario 里多版本、多二进制来源的经验总结规则。”。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()`。
- `D-S010-T02-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断清单是否针对 writing closure 的真实痛点，而不是通用套话。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：权威来源排序 / 仍有冲突的点 / 后续写作禁区 / D_handoff
- `D-S010-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 writing workspace 的 handoff 收束为最终 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_D_content_checks.evaluate_content_rule()`。
- `D-S010-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/D_handoff.md` 存在、section 覆盖 ['权威来源排序', '仍有冲突的点', '后续写作禁区']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_D_trace_checks.evaluate_trace_rule()` + `scenario_D_artifact_checks.evaluate_artifact_rule()`。
- `D-S010-T03-C3` [LLM_JUDGE | 100] 使用 `D_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 handoff pack 是否适合直接交给另一个模型继续写作。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_D_llm_judges.build_llm_prompt()` + `parse_judge_response()`。


## 9. 实施注意事项
- 如果某个 turn 声明 `binary_grounding_required=true`，而 trace 中既没有 `terminal/python_repl` 解析痕迹、回答里也没有明确承认边界，则相关 criterion 直接重罚。
- 如果 turn 的 `expected_artifacts` 不为空，则默认要求 trace 中出现 `write_file` 或等价写入动作。
- 所有写入到 `memory/` 的 artifact，若基于上传源文件生成，优先检查 `source_assets` frontmatter 是否存在。
- 若回答复用了 prior sessions 的产物，但没有任何 prior-memory 痕迹（如前序 concept / pack 名称、memory 路径、或显式引用），在 RULE/LLM_JUDGE 中都应酌情扣分。

## 10. 一句话结论
Scenario D 的核心不是单看回答“像不像懂”，而是联合检查：**对象是否落地、trace 是否诚实、artifact 是否真实、binary 是否被真正解析、source-layer 是否被清楚区分。**