# Scenario B 详细评测设计 TAD

## 0. 文档定位
- 对应文件：`eval_detailed_tad_B.md`
- 对应 scenario：`scenario_B`
- questions json：`B_scenario_questions.json`
- 评分细则总数：`93`（31 turns × 3）
- LLM-judge 细则数：`31`（每个 turn 1 条，满足不低于 1/3）

## 1. 场景定位
该场景围绕“材料科研智能体是否真的理解文献闭环，而不是只会背文件名”展开。它要求系统在基线 chlorite 机制、Ce/电子结构迁移、high-valent metal-oxo 旁支桥接之间建立清晰边界，并能够持续沉淀 concept/pack。

### 1.1 本场景重点测什么
- 基线文献对比（EST vs PNAS）
- d-band / selective oxidation 文献向 chlorite 主线的安全迁移
- Ce / electronic structure 文献的旁证与禁区
- 高价钴证明方法的证据分层
- 长期 workspace memory 下的 concept/pack 沉淀与 handoff

### 1.2 与系统基类的衔接方式
- 由 `scenario_B_registry.build_default_criteria()` 自动从 `B_scenario_questions.json` 生成 93 条 criterion。
- 由 `scenario_B_runbook.evaluate_turn()` 统一调度内容规则、trace/artifact 检查、LLM-judge 与 hallucination flags。
- 由 `scenario_B_llm_judges.build_llm_prompt()` 组装专家 prompt。
- 由 `scenario_B_hallucination_checks.aggregate_hallucination_metrics()` 汇总该场景特有的幻觉子指标。

## 2. 源文件清单与角色
- `PNAS_SI_PDF`：2024 PNAS 原始 PDF/SI，用于核对 OAT、低配位 Co、ClO2/Co(IV)=O 双物种表述
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20250912-亚氯酸盐活化框架搭建/【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf`
- `EST_PDF`：2023 EST 基线机制原始 PDF，用于核对 OAT、PCET、质子增强与 pH 贡献区分
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20250912-亚氯酸盐活化框架搭建/中文关键词搜索关联度max/（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf`
- `DBAND_NOTE_MD`：d-band/high-valent metal-oxo 文献笔记，用于抓取可迁移设计变量
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20250930-Co3O4顶层设计-大组会/2024-SACs&taloring D band-high-valent metal-oxo species - 文献笔记.md`
- `DBAND_PDF`：d-band/high-valent metal-oxo 原始论文 PDF，用于校验 selective oxidation / polymerization bridge
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20250930-Co3O4顶层设计-大组会/2024-SACs&taloring D band-high-valent metal-oxo species.pdf`
- `CE_CO3O4_PDF`：Ce-Co3O4 深氧化 VOC 文献，提供 Ce/OV/界面电子结构的旁证
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20260222大组会文献Ce-Co3O4与掺杂/1-s2.0-S0926337324011780-main.pdf`
- `GRADIENT_PDF`：4f–2p–3d orbital coupling 文献，提供类芬顿体系中的电子结构启发
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20260305和师兄探讨过的主逻辑参考文献/Optimized the e occupancy of Co active site through 4f–2p–3d gradient orbital coupling for efficient Fenton-like catalysis.pdf`
- `OXO_WALL_PDF`：Ce-Co lamellar membrane 打破 oxo-wall 文献，提供高价 Co/抗键占据相关旁证
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20260309高价钴物种证明/Breaking the oxo-wall for Co(IV)-oxo species and their nanoconfined catalytic performance within Ce-Co lamellar membrane.pdf`
- `HVMO_REVIEW_PDF`：high-valent metal-oxo review，用于证明方法分层与文献桥接
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献/20260309高价钴物种证明/High-valent metal-oxo species in catalytic oxidations for environmental.pdf`
- `PNAS_NOTE_MD`：2024 PNAS 笔记，用于快速定位作者笔记视角的总结
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献笔记/20250912-亚氯酸盐活化框架搭建/2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.md`
- `EST_NOTE_MD`：2023 EST 笔记，用于快速定位基线机制摘要
  - path: `科研obsidian/2-主逻辑树-现实照应-文献搜集与文献笔记/文献笔记/20250912-亚氯酸盐活化框架搭建/中文关键词搜索关联度max/（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.md`

## 3. session 设计概览
- 1. `scenario_B_session_001_bootstrap` — [EVAL][B] bootstrap literature concept workspace；T1：这个 workspace 我想定义成一个`文献/Concept 容器`，核心... / T2：再加一个限制：这个容器的第一目标不是把所有文献都“总结一遍”，而是先形成一个... / T3：可以，确认初始化。完成后请把 seed pack 存成 `memory/pa...
- 2. `scenario_B_session_002_baseline_compare` — [EVAL][B] 2023 EST vs 2024 PNAS baseline mechanism；T1：我现在要把“Co3O4 活化亚氯酸盐”的基线机制讲清楚。请你结合 2023 ... / T2：如果我要在组会上写一句“为什么这里不是简单照搬 PMS 体系”，你帮我写成一... / T3：把这轮沉淀成一张概念卡，保存到 `memory/concepts/B_bas...
- 3. `scenario_B_session_003_dband_bridge` — [EVAL][B] d-band and chlorite bridge；T1：我接下来想看一篇讲 d-band center 和高价 metal-oxo ... / T2：再进一步：如果我只想从 review 里抽出三类“以后可以拿来证明 Co(I... / T3：把这轮收束成 `memory/concepts/B_dband_bridge...
- 4. `scenario_B_session_004_ce_transferability` — [EVAL][B] Ce-Co3O4 transferability；T1：我手里现在有三篇 Ce / 电子结构相关文献：一篇是 Ce-Co3O4 深氧... / T2：如果我想把一句话写得相对安全一点，比如“Ce 相关调控可能通过低配位 / 电... / T3：请把这轮沉淀到 `memory/concepts/B_ce_transfer...
- 5. `scenario_B_session_005_proof_methods` — [EVAL][B] proof methods for high-valent cobalt；T1：现在只聚焦“怎么证明高价钴”。请你把 EST、oxo-wall 论文、以及 ... / T2：如果只给你 7 天窗口做一个“最小证明闭环”，你会怎么排：PMSO / 同位... / T3：请把结论收进 `memory/concepts/B_proof_method...
- 6. `scenario_B_session_006_ce_sentence_safety` — [EVAL][B] safety of Ce-promotes-high-valent-Co sentence；T1：我现在最怕的是把一句‘Ce 有利于高价钴生成’说得过满。请你根据 Ce-Co... / T2：你再直接帮我改写成三句可以放进开题或论文导论里的版本：第一句最保守，第二句中... / T3：把这轮保存成 `memory/concepts/B_sentence_saf...
- 7. `scenario_B_session_007_reading_queue` — [EVAL][B] reading queue for upcoming group meeting；T1：下周我要和老师过一轮文献逻辑。请你从这几份材料里给我排一个 7 天阅读队列：... / T2：再帮我把这个队列改成‘组会前 30 分钟复习版’：每一篇最后应该记住哪三个锚... / T3：请把这个阅读队列存成 `memory/packs/B_reading_que...
- 8. `scenario_B_session_008_false_analogy_redflags` — [EVAL][B] false analogy red flags；T1：你帮我专门做一个“危险类比排雷表”。输入是 d-band / PMS / C... / T2：再给我一个负面清单：以后如果我问你类似问题，哪些句式一出现你就应该先提醒‘这... / T3：把它收成 `memory/concepts/B_false_analogy_...
- 9. `scenario_B_session_009_master_outline` — [EVAL][B] literature master outline；T1：我准备把文献部分收束成一个 thesis/group-meeting 都能复... / T2：我还想额外加一列：`不能混写的来源边界`。比如哪些地方必须说“这来自 rev... / T3：把这份总纲保存到 `memory/packs/B_master_outlin...
- 10. `scenario_B_session_010_handoff` — [EVAL][B] literature concept handoff；T1：最后请你站在‘我要把这个 literature workspace 交给另一... / T2：再补一个‘后续问答禁区清单’：以后如果我再问 literature clos... / T3：请把最后的 handoff 存成 `memory/packs/B_hando...

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
### 5.1 `B_PROMPT_EVIDENCE_EXPERT`
你是一名长期从事环境催化、亚氯酸盐活化、高价金属氧物种机理研究的评审专家。请只依据【用户问题】【上传文件列表】【assistant 回复】【trace 摘要】【预期 focus】进行评分，不要凭领域常识替模型补答案。你要重点检查五件事：第一，回答是否严格区分论文原文、个人笔记、以及从旁支体系借来的启发；第二，是否真正抓住 Co3O4/chlorite 基线机制的 OAT、PCET、ClO2/Co(IV)=O 双物种与 pH/质子增强等关键关系；第三，是否把 selective oxidation、PMS/Fenton-like、Ce 电子结构论文的迁移边界说清楚；第四，是否在证据不足时主动保留限定词；第五，是否围绕用户要求的对象（概念卡、对照表、handoff）组织内容。请输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.2 `B_PROMPT_CLOSURE_EXPERT`
你是一名擅长把复杂文献线索收束为 Concept/Pack 的材料科研导师。现在你的任务不是判断回答“像不像总结”，而是判断它能否作为 literature closure 的稳定对象被后续 session 复用。请重点看：对象是否真正完成了用户要求的收束（例如共同机制/关键差异/边界/禁区）；是否保留了 source-layer 与不确定性；是否明确哪些结论已稳定、哪些仍需回原文核对；是否避免把旁支体系启发包装成已验证事实；是否足以在后续写作、问答、handoff 中直接使用。仍然只基于给定材料评分，不允许替模型脑补未说出的合理内容。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

### 5.3 `B_PROMPT_HALLUCINATION_EXPERT`
你是一名专门审查科研智能体幻觉风险的化学材料评估专家。请重点审查：模型是否对 PDF 中的具体机理、表征、结论做了无依据的细节臆测；是否把笔记里的压缩说法误当成原文直接结论；是否把 d-band / PMS / Fenton-like / Ce 旁支论文的结果直接说成 chlorite 体系已证实的事实；是否使用了“已经证明、必然导致、直接说明”等过强表述而没有给出限定；是否忽略了二进制文件需要进一步解析这一事实。请以严格保守的标准评分：有明显过度断言、伪造页结论、或混淆 source layer 时要重罚。输出 JSON：{"score":0-100,"verdict":"pass|partial|fail","strengths":[...],"risks":[...],"missing":[...]}。

## 6. 场景特有 hallucination 子指标
- `B_H1_source_layer_integrity`：统计把论文原文、文献笔记、类比迁移三层证据说清楚的比例；若将 note 压缩句误写成 paper 直接结论则扣分。
- `B_H2_binary_grounding_compliance`：针对需要深读 PDF 的 turn，检查是否出现 terminal/python_repl/明确不确定边界；缺失则视为二进制 grounding 不足。
- `B_H3_cross_system_transfer_safety`：统计把 PMS/Fenton-like/selective oxidation/Ce 旁支结论直接写成 chlorite 已证实事实的风险率。
- `B_H4_unsupported_specificity_rate`：统计无依据捏造具体表征细节、页级信息、定量比较或“已证明”强断言的比例。
- `B_H5_artifact_truthfulness`：统计声称已生成 concept/pack 或已稳定掌握的结论，但实际 artifact/summary 不存在或缺关键 section 的比例。

## 7. Python 原型模块职责
- `scenario_B_registry.py`：加载 scenario json、生成 CriterionSpec、校验 file coverage、统计 turns/binary/prior-memory。
- `scenario_B_content_checks.py`：关键术语覆盖、禁词惩罚、prior memory 痕迹、内容规则评分。
- `scenario_B_trace_checks.py`：trace 解析、tool usage 检查、binary grounding 检查、write/read 行为判定。
- `scenario_B_artifact_checks.py`：artifact 存在性、required sections、source_assets frontmatter、preview 生成。
- `scenario_B_llm_judges.py`：专家 prompt 模板、prompt 选择器、judge 输入组装、JSON 输出解析。
- `scenario_B_hallucination_checks.py`：unsupported specificity、source confusion、cross-transfer、artifact fabrication 等 flags 与子指标聚合。
- `scenario_B_runbook.py`：把 registry / checks / judge 串成统一 scenario runtime blueprint。

## 8. 90 条评分细则
## 01. [EVAL][B] bootstrap literature concept workspace
- session_id: `scenario_B_session_001_bootstrap`
- 目标：该 session 必须复用 __bootstrap__，并在完成后可被重命名为 [EVAL][B][BOOTSTRAP]。

### Turn 1
- 用户上传：2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.md、（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.md、【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf
- 关注关键词：文献/Concept 容器 / 基线机制 / 论文原文 / 我的笔记 / 证据层级 / 亚氯酸盐活化
- `B-S001-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 workspace 定义成 literature/concept 容器，并明确论文原文与笔记是两个不同证据层级。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S001-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“bootstrap 阶段至少应读取上传的 markdown；如果引用 SI 细节，应体现对 PDF 的进一步解析，不能只凭文件名猜测。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S001-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正围绕 literature closure 的对象定义，而不是把它误导成实验 task 或写作 pack。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：先读什么 / 暂时不要读什么 / 为什么 / 只看笔记容易讲过头 / 阅读入口
- `B-S001-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须输出 selective reading 策略，并指出只看笔记可能导致的过度外推。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S001-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮应体现 skip-by-design，不应默认生成大篇 thesis/experiment 产物。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S001-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断模型是否理解 bootstrap 阶段的任务是建立阅读入口，而不是全面总结。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：确认初始化 / 这个包测什么 / 当前最值得优先追的来源 / 下一步先读哪一组文件 / PACK_bootstrap_kickoff
- `B-S001-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要完成 bootstrap，并写出服务 literature closure 的 seed pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S001-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/PACK_bootstrap_kickoff.md` 存在、section 覆盖 ['这个包测什么', '当前最值得优先追的来源', '下一步先读哪一组文件']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S001-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断生成的 seed pack 是否真正服务 benchmark 初始化，而不是泛泛的项目简介。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 02. [EVAL][B] 2023 EST vs 2024 PNAS baseline mechanism
- session_id: `scenario_B_session_002_baseline_compare`
- 目标：比较基线 paper pair，并产出第一张核心 concept 卡。

### Turn 1
- 用户上传：（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf、【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf、（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.md、2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.md
- 关注关键词：2023 EST / 2024 PNAS / OAT / PCET / 质子增强 / 低配位 Co
- `B-S002-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须完成两篇基线文献的同异对照，并清楚区分 paper claim 与 note claim。”，并规避禁用表述 ['PMS直接活化', '芬顿主线']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S002-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应读取至少一份 note，并对 PDF 做适度核对；深度机制对比不能只靠 quick_summary。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S002-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断比较是否抓住 chlorite 体系真正的公共骨架与差异，而不是简单堆术语。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：不是简单照搬 PMS 体系 / 亚氯酸盐基线 / 相似处 / 不能直接套用的边界 / 原文 / 笔记推演
- `B-S002-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须写出一个边界清晰的三句短段落，并显式标注原文/推演来源。”，并规避禁用表述 ['已经完全证明 Ce 一定促进高价钴']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S002-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮可复用上轮已读取资料，也可复读 memory；不应凭空新增未支持的体系比较。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S002-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答能否在迁移与克制之间保持平衡，避免将 analogies 说成 established fact。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：概念卡 / 共同机制 / 关键差异 / 还不能下结论的点 / B_baseline_compare
- `B-S002-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把基线机制比较沉淀成可复用的 concept card。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S002-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_baseline_compare.md` 存在、section 覆盖 ['共同机制', '关键差异', '还不能下结论的点']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S002-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept card 是否既可复用，又保留了不确定性边界。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 03. [EVAL][B] d-band and chlorite bridge
- session_id: `scenario_B_session_003_dband_bridge`
- 目标：测试从 selective oxidation / d-band 文献向 chlorite 问题迁移时的边界意识。

### Turn 1
- 用户上传：2024-SACs&taloring D band-high-valent metal-oxo species - 文献笔记.md、2024-SACs&taloring D band-high-valent metal-oxo species.pdf、High-valent metal-oxo species in catalytic oxidations for environmental.pdf
- 关注关键词：d-band center / high-valent metal-oxo / 设计变量 / 值得迁移 / 只能停留在启发 / chlorite 体系
- `B-S003-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 d-band 文献拆成可迁移设计变量与不可直接套用的结论两层。”，并规避禁用表述 ['已经证明适用于亚氯酸盐']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S003-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应读取笔记并对 PDF/review 做核对；若给出具体证据强弱，应体现 trace 中存在 read_file / binary parse 行为。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S003-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正理解 literature bridge 的边界，而不是把 selective oxidation 结果误写成 chlorite 证据。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：review / 三类方法学 / 证明 Co(IV)=O / 强弱顺序 / 主证 / 支持证据
- `B-S003-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须给出方法学强弱排序，并贴合 chlorite 体系来解释主证/支持证据。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S003-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮可复用前述 review 读取结果，也可读取之前概念卡；不要凭空列出未被资料支撑的方法。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S003-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断排序是否合理、是否符合环境催化中高价金属氧物种的证据分层。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：可迁移的设计变量 / 不可直接套用的边界 / 候选证明手段 / B_dband_bridge
- `B-S003-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 d-band bridge 的可迁移内容和边界一起沉淀下来。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S003-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_dband_bridge.md` 存在、section 覆盖 ['可迁移的设计变量', '不可直接套用的边界', '候选证明手段']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S003-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断产物是否把 bridge 和 boundary 同时保存，而非只留下鼓舞性结论。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 04. [EVAL][B] Ce-Co3O4 transferability
- session_id: `scenario_B_session_004_ce_transferability`
- 目标：测试 Ce-Co3O4 / gradient orbital coupling / oxo-wall 三条旁支如何回到 chlorite 主线。

### Turn 1
- 用户上传：1-s2.0-S0926337324011780-main.pdf、Optimized the e occupancy of Co active site through 4f–2p–3d gradient orbital coupling for efficient Fenton-like catalysis.pdf、Breaking the oxo-wall for Co(IV)-oxo species and their nanoconfined catalytic performance within Ce-Co lamellar membrane.pdf
- 关注关键词：Ce-Co3O4 / 4f–2p–3d / oxo-wall / 迁移分层表 / 直接援引 / 间接旁证
- `B-S004-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须对三篇 Ce/电子结构文献做迁移分层，而不是给出笼统的鼓舞性结论。”，并规避禁用表述 ['已经在我的体系中证明']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S004-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“三篇都是 PDF；如果回答涉及具体机理或表征，trace 应体现对二进制文件的进一步解析或谨慎限定。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S004-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否能把 direct support / indirect support / speculation 区分清楚。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：最小证据链 / 低配位 / 电子再分布 / 抗键占据变化 / 提高高价钴形成概率 / 哪一环现在还缺失
- `B-S004-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要把安全句子拆成最小证据链，并明确当前缺口。”，并规避禁用表述 ['已经直接证明']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S004-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用上轮解析结果，必要时也可引用已有 concept card；不能忽视 chlorite 场景中的缺口。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S004-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否把 speculative leap 还原成可执行的证据需求。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：可直接援引 / 只能作为旁证 / 本体系仍缺的实验 / B_ce_transferability
- `B-S004-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要生成一张专门处理 Ce 迁移边界的 concept card。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S004-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_ce_transferability.md` 存在、section 覆盖 ['可直接援引', '只能作为旁证', '本体系仍缺的实验']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S004-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断产物能否在支持与猜想之间保持清晰层次。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 05. [EVAL][B] proof methods for high-valent cobalt
- session_id: `scenario_B_session_005_proof_methods`
- 目标：测试 proof-of-Co(IV)=O 的证据分层与最小可行闭环。

### Turn 1
- 用户上传：（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf、Breaking the oxo-wall for Co(IV)-oxo species and their nanoconfined catalytic performance within Ce-Co lamellar membrane.pdf、High-valent metal-oxo species in catalytic oxidations for environmental.pdf
- 关注关键词：直接证据 / 高可信间接证据 / 背景支持证据 / 排序理由 / chlorite 体系 / 最容易被滥用
- `B-S005-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要围绕高价钴证明方法做三层分级，并指出滥用风险。”，并规避禁用表述 ['任何表征单独就足够']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S005-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“涉及 review + PDF 细节，trace 中应看到对原始文件的读取/解析，而非单纯凭印象回答。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S005-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断证据分级是否符合材料化学中 high-valent cobalt 的证明逻辑。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：7天窗口 / 最小证明闭环 / PMSO / 同位素 / EPR / 反应选择性
- `B-S005-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把证明闭环排成时间顺序，并说明每一步的核心问句。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S005-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮应复用上轮的证据分层，也可引用已有 memory/concepts；不要把不具备条件的方法硬塞进最小闭环。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S005-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断方案是否真正最小可行，而不是把所有方法都堆进去。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：直接证据 / 间接证据 / 最小闭环组合 / B_proof_methods
- `B-S005-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把高价钴证明方法沉淀成后续可复用的概念卡。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S005-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_proof_methods.md` 存在、section 覆盖 ['直接证据', '间接证据', '最小闭环组合']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S005-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 concept card 是否对后续实验/写作都可复用。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 06. [EVAL][B] safety of Ce-promotes-high-valent-Co sentence
- session_id: `scenario_B_session_006_ce_sentence_safety`
- 目标：该 session 主测 claim calibration 和 anti-hallucination。

### Turn 1
- 用户上传：1-s2.0-S0926337324011780-main.pdf、Breaking the oxo-wall for Co(IV)-oxo species and their nanoconfined catalytic performance within Ce-Co lamellar membrane.pdf、2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.md
- 关注关键词：Ce 有利于高价钴生成 / 已建立 / 可推测但必须加限定词 / 现在不能写 / 理由
- `B-S006-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把一句危险表述拆成 established / qualified speculation / forbidden 三层。”，并规避禁用表述 ['已经在 chlorite 体系直接证实']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S006-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“若回答引用 oxo-wall 或 Ce-Co3O4 的具体表征，应体现对 PDF 的进一步处理或明确不确定边界。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S006-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断模型是否能把危险一句话拆成安全表述层级。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：最保守 / 中等推进 / 待验证假说 / 不要同一个强度
- `B-S006-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要输出三种不同强度的可写句式，并清楚区分断言强度。”，并规避禁用表述 ['已经证明', '必然导致']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S006-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用本 session 或既有 concept card；不应新增无来源的实验条件。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S006-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断改写是否真的做到了强度分层，而不是只换词不换逻辑。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：可直接写 / 必须加限定词 / 现在不能写 / B_sentence_safety
- `B-S006-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要生成一个专门管控危险句式的 concept card。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S006-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_sentence_safety.md` 存在、section 覆盖 ['可直接写', '必须加限定词', '现在不能写']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S006-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断产物是否真正可在后续写作中当作安全护栏使用。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 07. [EVAL][B] reading queue for upcoming group meeting
- session_id: `scenario_B_session_007_reading_queue`
- 目标：测试多文献情境下的优先级判断与对象化沉淀。

### Turn 1
- 用户上传：（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf、【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf、2024-SACs&taloring D band-high-valent metal-oxo species.pdf、1-s2.0-S0926337324011780-main.pdf、High-valent metal-oxo species in catalytic oxidations for environmental.pdf
- 关注关键词：7天阅读队列 / 基线机制 / 电子结构迁移 / 证明方法 / 每天读完产出什么对象
- `B-S007-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须输出按天排布的 reading queue，并把阅读产物对象化。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S007-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“多 PDF 上传下，trace 至少要体现文件识别与有选择的读取，不应假装通读每一页。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S007-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 reading queue 是否真正服务后续 literature closure，而非泛泛列书单。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：组会前 30 分钟复习版 / 三个锚点 / 不能讲过头的边界
- `B-S007-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把阅读队列压缩成复习锚点，并保留边界提醒。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S007-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用本轮与前序 memory/concepts，不需要重新做重型生成。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S007-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断回答是否抓住‘能讲什么 / 不能讲什么’的组会复习价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：优先级 / 每篇读完后要产出的对象 / 可以后读的文件 / B_reading_queue
- `B-S007-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把阅读队列整理成 pack 形式，便于之后直接查看。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S007-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/B_reading_queue.md` 存在、section 覆盖 ['优先级', '每篇读完后要产出的对象', '可以后读的文件']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S007-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否具有执行性和复用性，而不是普通摘要。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 08. [EVAL][B] false analogy red flags
- session_id: `scenario_B_session_008_false_analogy_redflags`
- 目标：此 session 重点压测类比迁移时的 hallucination 控制。

### Turn 1
- 用户上传：2024-SACs&taloring D band-high-valent metal-oxo species.pdf、Optimized the e occupancy of Co active site through 4f–2p–3d gradient orbital coupling for efficient Fenton-like catalysis.pdf、1-s2.0-S0926337324011780-main.pdf、（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.md
- 关注关键词：危险类比排雷表 / chlorite 主线 / 为什么像 / 为什么其实不一样 / 假类比
- `B-S008-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须列出最危险的跨体系假类比，并解释像与不像各自的理由。”，并规避禁用表述 ['可以直接类推']。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S008-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“涉及旁支 PDF 与基线 note 的混用，trace 应显示至少对文本笔记和部分二进制做过核对。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S008-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断回答是否真正识别了跨体系迁移的幻觉来源。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：负面清单 / analogical support / 不是 chlorite 直接证据 / 自检模板
- `B-S008-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要给出能直接复用的问答自检模板，用于提前拦截过度迁移。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S008-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“本轮可以复用前序 concept card 与本 session 的排雷表，不应新增脱离资料的例子。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S008-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断输出是否具有实操价值，能作为后续对话时的防错护栏。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：最危险类比 / 需要补证据才可类比 / 安全表述模板 / B_false_analogy_redflags
- `B-S008-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把危险类比和安全模板一起沉淀下来。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S008-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/concepts/B_false_analogy_redflags.md` 存在、section 覆盖 ['最危险类比', '需要补证据才可类比', '安全表述模板']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S008-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断产物是否足够明确，后续可以直接拿来约束模型回答。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 09. [EVAL][B] literature master outline
- session_id: `scenario_B_session_009_master_outline`
- 目标：总收束 session，要求能复用前序 concepts 并形成主线化 pack。

### Turn 1
- 用户上传：2024-SACs&taloring D band-high-valent metal-oxo species - 文献笔记.md、2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.md、（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.md、High-valent metal-oxo species in catalytic oxidations for environmental.pdf
- 关注关键词：master outline / Co3O4 活化 chlorite / Ce / 电子结构 / 低配位 / high-valent metal-oxo / selective oxidation / 原文证据 / 概念迁移
- `B-S009-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须把 literature 主线整理成可复用的总纲，并标注原文证据 vs 概念迁移。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S009-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应充分利用前面已经生成的 concept artifacts，也可以复读 notes/review 来校正边界。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S009-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 outline 是否真正形成一套可讲述的 literature closure，而不是三个孤立列表。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：不能混写的来源边界 / 来自 review / 来自我的笔记 / 从旁支材料借来的思路
- `B-S009-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“必须补齐来源边界列，防止 outline 在后续写作中混源。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S009-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应复用前序 redflags/safety cards；不应遗漏 source provenance。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S009-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断是否真正识别了后续写作最容易混源的节点。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：主线一 / 主线二 / 主线三 / 不要混写的来源边界 / B_master_outline
- `B-S009-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要将 literature master outline 固化为可浏览的 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S009-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/B_master_outline.md` 存在、section 覆盖 ['主线一', '主线二', '主线三', '不要混写的来源边界']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S009-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断 pack 是否已经具备 handoff / 写作复用价值。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

## 10. [EVAL][B] literature concept handoff
- session_id: `scenario_B_session_010_handoff`
- 目标：最终 handoff session，用于评测长期 memory 与 anti-hallucination 收束能力。

### Turn 1
- 用户上传：（相关度高）2023-EST-Co3O4-OAT during Co(IV) in the Co3O4 chlorite process&PCET in Co(IV)mediated ClO2 generation-pH对Cl形态影响.pdf、【SI】2024-PNAS-UV-induced-OV-Co3O4- OV-induced low coordinated Co& anchor Cl to produce 三Co(IV)=O👉ClO2.pdf、2024-SACs&taloring D band-high-valent metal-oxo species.pdf、1-s2.0-S0926337324011780-main.pdf、Breaking the oxo-wall for Co(IV)-oxo species and their nanoconfined catalytic performance within Ce-Co lamellar membrane.pdf
- 关注关键词：handoff / 已稳定 / 半稳定 / 未稳定 / 必须回原文再核
- `B-S010-T01-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要对整个 literature workspace 的理解成熟度做 handoff 分层。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S010-T01-C2` [TRACE+HALLUCINATION | 100] 检查 trace 是否对 PDF/DOCX/PPTX 做了真实解析（`terminal`/`python_repl`/`read_file` 对文本转译产物），或在回答中诚实声明边界；同时核查“应复用前序 artifacts，同时识别哪些 PDF 虽上传过但仍未被充分消化。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_hallucination_checks.compute_turn_flags()`。
- `B-S010-T01-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_HALLUCINATION_EXPERT` 对回答进行语义评分，重点审查“判断 handoff 是否真实反映了 workspace 中已沉淀与未沉淀的边界。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 2
- 用户上传：无新增上传
- 关注关键词：后续问答禁区清单 / 回原文 / 回 SI / 回 review / 不是直接给出肯定句
- `B-S010-T02-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“要生成一个禁区清单，用来约束后续 literature QA 的断言边界。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S010-T02-C2` [TRACE+PROCESS | 100] 检查 trace 是否围绕当前对象执行了必要读取/整合/写入，重点核查“应结合已有 redflag / safety / proof cards，而不是临时拍脑袋列规则。”。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()`。
- `B-S010-T02-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_EVIDENCE_EXPERT` 对回答进行语义评分，重点审查“判断禁区是否覆盖了最常见的 hallucination 源头。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。

### Turn 3
- 用户上传：无新增上传
- 关注关键词：已经稳定的结论 / 仍需回原文核对 / 后续问答禁区 / B_handoff
- `B-S010-T03-C1` [RULE | 100] 检查回答是否覆盖关键术语、贴合“需要把 literature workspace 的 handoff 收束成最终 pack。”，并规避禁用表述 （无显式禁词）。实现建议：`scenario_B_content_checks.evaluate_content_rule()`。
- `B-S010-T03-C2` [TRACE+ARTIFACT | 100] 检查 trace 是否出现有效读取/写入，并验证 `memory/packs/B_handoff.md` 存在、section 覆盖 ['已经稳定的结论', '仍需回原文核对', '后续问答禁区']、若写入 `memory/` 则含 `source_assets` frontmatter。实现建议：`scenario_B_trace_checks.evaluate_trace_rule()` + `scenario_B_artifact_checks.evaluate_artifact_rule()`。
- `B-S010-T03-C3` [LLM_JUDGE | 100] 使用 `B_PROMPT_CLOSURE_EXPERT` 对回答进行语义评分，重点审查“判断最终 handoff 是否能直接交给另一个模型接手，不至于重复犯错。”。要求输出结构化 JSON（score/verdict/strengths/risks/missing）。实现建议：`scenario_B_llm_judges.build_llm_prompt()` + `parse_judge_response()`。


## 9. 实施注意事项
- 如果某个 turn 声明 `binary_grounding_required=true`，而 trace 中既没有 `terminal/python_repl` 解析痕迹、回答里也没有明确承认边界，则相关 criterion 直接重罚。
- 如果 turn 的 `expected_artifacts` 不为空，则默认要求 trace 中出现 `write_file` 或等价写入动作。
- 所有写入到 `memory/` 的 artifact，若基于上传源文件生成，优先检查 `source_assets` frontmatter 是否存在。
- 若回答复用了 prior sessions 的产物，但没有任何 prior-memory 痕迹（如前序 concept / pack 名称、memory 路径、或显式引用），在 RULE/LLM_JUDGE 中都应酌情扣分。

## 10. 一句话结论
Scenario B 的核心不是单看回答“像不像懂”，而是联合检查：**对象是否落地、trace 是否诚实、artifact 是否真实、binary 是否被真正解析、source-layer 是否被清楚区分。**