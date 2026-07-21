# Phase 5.1 开发日志

> 目标：完成核心科研 skill 体系重构 — 统一 SKILL.md 格式、对齐 registry.json、集成 Anthropic 官方 foundation skill、清理遗留结构问题

## 文件创建/更新记录

### Step 1 核心科研 Skill 新建（7 个 portable core skill）

以下 skill 采用统一的新格式（frontmatter + Overview + When to Use + Boundary with Sibling Skills + Quality Checks + Common Failure Modes + Red Flags + Example Patterns + Related Skills）：

- 创建：`backend/skills/mechanism_mapping/SKILL.md`
  - 机理分支图谱搭建（结构→位点→过程→结果）
  - 原 `mechanism_evidence_chain/SKILL.md` 内容实际是 mechanism_mapping，重命名目录以匹配
- 创建：`backend/skills/oxidant_route_comparison/SKILL.md`（重写）
  - 反应路径比较（位点要求/基元步骤/可迁移性/边界）
  - 新增 Boundary with Sibling Skills、Common Failure Modes、Red Flags、Example Patterns 段落
- 创建：`backend/skills/spectroscopy_joint_interpretation/SKILL.md`
  - 谱图联合判读（XANES/EXAFS/XPS/EPR/Raman 等）
- 创建：`backend/skills/reactive_species_evidence_matrix/SKILL.md`
  - 活性物种证据矩阵（探针/淬灭/EPR→证据等级）
- 创建：`backend/skills/multi_evidence_mechanism_judgment/SKILL.md`
  - 多源证据综合机制判断（会聚/张力/排序/上限）
- 创建：`backend/skills/figure_claim_anchoring/SKILL.md`
  - 图-论断锚定（哪张图支撑哪句话）
- 创建：`backend/skills/results_to_report_structuring/SKILL.md`
  - 结果到汇报/写作结构组织（北极星→分段→图策略→缺口）

### Step 2 Anthropic 官方 Foundation Skill 集成（4 个）

来源：https://github.com/anthropics/skills/tree/main/skills/

- 创建：`backend/skills/docx/` — Word 文档创建/编辑/分析（含 SKILL.md + scripts/）
- 创建：`backend/skills/pdf/` — PDF 处理（读取/合并/拆分/创建/表单填写，含 SKILL.md + scripts/ + forms.md + reference.md）
- 创建：`backend/skills/pptx/` — PPT 演示文稿创建/编辑/分析（含 SKILL.md + scripts/ + editing.md + pptxgenjs.md）
- 创建：`backend/skills/skill-creator/` — Skill 创建/优化/评估工具（含 SKILL.md + agents/ + eval-viewer/ + scripts/）

### Step 3 目录结构修复

- 修复：`backend/skills/oxidant_route_comparison/examples/examples/` → `examples/`
  - 问题：examples 目录双层嵌套，example_1.md 和 example_2.md 在 `examples/examples/` 下
  - 处理：扁平化为 `examples/example_1.md`、`examples/example_2.md`
- 修复：`backend/skills/multi_e_idence_mechanism_judgment/` → `multi_evidence_mechanism_judgment/`
  - 问题：目录名拼写错误，少了字母 `v`
  - 处理：重命名目录
- 修复：`backend/skills/mechanism_evidence_chain/` → `mechanism_mapping/`
  - 问题：目录名是 `mechanism_evidence_chain`，但 SKILL.md frontmatter name 和内容都是 `mechanism_mapping`
  - 处理：重命名目录以匹配实际内容

### Step 4 registry.json 更新

- 修改：`backend/skills/registry.json`
  - 版本从 `0.2.1` 升至 `0.4.0`
  - 移除旧条目 `mechanism_evidence_chain`（目录已重命名为 `mechanism_mapping`）
  - 移除 3 个目录已不存在的条目：`paper_quad_summary`、`experiment_matrix`、`csv_plot_kobs`
  - 新增 `oxidant_route_comparison` 条目（之前被 `mechanism_evidence_chain` 占位）
  - 新增 6 个核心科研 skill 条目：`mechanism_mapping`、`spectroscopy_joint_interpretation`、`reactive_species_evidence_matrix`、`multi_evidence_mechanism_judgment`、`figure_claim_anchoring`、`results_to_report_structuring`
  - 新增 4 个 Anthropic 官方 skill 条目：`docx`、`pdf`、`pptx`、`skill_creator`
  - 最终 16 个条目，全部与磁盘目录一一对应

### Step 5 模板与文档更新

- 重写：`backend/skills/_skill_template/SKILL.md`
  - 从旧的 6 段式结构（Skill meta / Intent routing / Context loading / Execution plan / Output contract / Memory patch / Prompt snippet）
  - 更新为新统一格式（frontmatter + Overview + When to Use + When NOT + Required Inputs + Expected Outputs + Workflow + Boundary + Quality Checks + Common Failure Modes + Red Flags + Example Patterns + Example Requests + Related Skills）
- 重写：`backend/skills/README.md`
  - 新增 SKILL.md 统一结构规范
  - 新增 Skill 分类表（analysis / literature / experiment / word / ppt / meta / foundation）
  - 新增目录结构说明（核心科研 skill vs foundation skill）
  - 新增注册要求说明

## 已处理问题

1. **mechanism_evidence_chain 身份错位**
   - 问题：目录名和 registry id 是 `mechanism_evidence_chain`，但 SKILL.md 内容实际是 `mechanism_mapping`
   - 处理：重命名目录为 `mechanism_mapping`，registry 条目同步更新

2. **oxidant_route_comparison examples 双层嵌套**
   - 问题：`examples/examples/example_1.md` 多了一层目录
   - 处理：扁平化为 `examples/example_1.md`

3. **multi_evidence_mechanism_judgment 目录名拼写错误**
   - 问题：`multi_e_idence_mechanism_judgment` 少了字母 `v`
   - 处理：重命名为 `multi_evidence_mechanism_judgment`

4. **registry 与磁盘不一致**
   - 问题：3 个旧条目（paper_quad_summary / experiment_matrix / csv_plot_kobs）指向不存在的目录；7 个新 skill 目录未注册
   - 处理：移除 3 个无目录条目，补注册所有新 skill

5. **_skill_template 过时**
   - 问题：模板仍是旧的 6 段式结构，与新 skill 格式完全不同
   - 处理：重写为新统一格式

6. **SKILL.md 格式两套并存**
   - 问题：旧 skill（paper_quad_summary 等）用简化版 meta/output/prompt 结构，新 skill 用 frontmatter + 完整段落结构
   - 处理：新 skill 全部统一为 portable core skill 格式；旧 skill 保留原样（synthesis_checklist / stage_report_ppt / deepresearch_prompt / writing_outline_rd 仍可用）

## 测试结果

| # | 测试项 | 预期 | 状态 |
|---|--------|------|------|
| 1 | registry.json 16 个条目全部有对应 SKILL.md | 0 missing | ✅ PASS |
| 2 | 磁盘上 16 个 skill 目录全部在 registry 中 | 0 orphan | ✅ PASS |
| 3 | 所有新 SKILL.md frontmatter name 与 registry id 一致 | 全部匹配 | ✅ PASS |
| 4 | oxidant_route_comparison/examples/ 无双层嵌套 | 扁平结构 | ✅ PASS |
| 5 | multi_evidence_mechanism_judgment 目录名正确 | 无拼写错误 | ✅ PASS |

## Phase 5.1 产出汇总

| 指标 | 值 |
|------|-----|
| 新建 SKILL.md | 7 个核心科研 skill |
| 集成官方 skill | 4 个（docx / pdf / pptx / skill-creator） |
| 目录结构修复 | 3 处（双层嵌套 / 拼写错误 / 身份错位） |
| registry 条目 | 从 10 个整理为 16 个（移除 4 个无效 + 新增 10 个） |
| 模板/文档更新 | 2 个（_skill_template + README.md） |
| registry 版本 | 0.2.1 → 0.4.0 |

## 当前 Skill 全景

| # | ID | category | 来源 |
|---|-----|----------|------|
| 1 | synthesis_checklist | experiment | 旧有 |
| 2 | stage_report_ppt | ppt | 旧有 |
| 3 | deepresearch_prompt | literature | 旧有 |
| 4 | writing_outline_rd | word | 旧有 |
| 5 | oxidant_route_comparison | analysis | 重写 |
| 6 | literature_review | literature | 旧有 |
| 7 | mechanism_mapping | analysis | 新建（原 mechanism_evidence_chain 重命名） |
| 8 | spectroscopy_joint_interpretation | analysis | 新建 |
| 9 | reactive_species_evidence_matrix | analysis | 新建 |
| 10 | multi_evidence_mechanism_judgment | analysis | 新建 |
| 11 | figure_claim_anchoring | analysis | 新建 |
| 12 | results_to_report_structuring | word | 新建 |
| 13 | docx | word | Anthropic 官方 |
| 14 | pdf | analysis | Anthropic 官方 |
| 15 | pptx | ppt | Anthropic 官方 |
| 16 | skill_creator | meta | Anthropic 官方 |

## 遗留文件说明

以下文件属于早期三层架构（SKILL.md + BINDING.md + eval_prompts.md）的遗留，核心内容已合并进对应 SKILL.md 的 Boundary with Sibling Skills 等段落：

- `backend/skills/mechanism_mapping/BINDING.md`
- `backend/skills/mechanism_mapping/eval_prompts.md`
- `backend/skills/oxidant_route_comparison/BINDING.md`
- `backend/skills/oxidant_route_comparison/eval_prompts.md`
- `backend/skills/REVIEW.md`

这些文件对 SkillLoader 和 Agent 运行时无影响，保留作为开发参考文档。

## Phase 5.1 → 后续衔接

| 本轮提供 | 后续如何使用 |
|----------|-------------|
| 16 个 skill 全部注册且可被 SkillLoader 加载 | Agent 可通过 SKILLS_SNAPSHOT 发现并 read_file 读取 |
| 7 个核心科研 skill 覆盖机理分析全链路 | 闭环 A/B/C 验证时可直接调用 |
| 4 个 Anthropic 官方 skill 提供 foundation 能力 | PDF/Word/PPT 处理 + skill 自创建 |
| 统一 SKILL.md 格式 + 模板 | 后续新建 skill 有标准起点 |
| registry v0.4.0 | SkillLoader 无需代码改动即可加载全部 skill |

---

**开发完成日期**：2026-03-15
