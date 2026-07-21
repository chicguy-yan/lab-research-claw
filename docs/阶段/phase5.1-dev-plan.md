# Phase 5.1 开发计划：三个科研闭环构建

> 目标：在 Phase 5 基础设施（SkillLoader / PromptBuilder / Chat API / 路径安全）之上，让三个科研闭环各自跑通至少一个真实场景，验证 **snapshot 注入 → Agent 读取 skill → 产出 Task/Pack** 的完整链路。

---

## 0. 前置状态

### Phase 5 已完成的基础设施
- `SkillLoader`：system + workspace 双来源加载、`_system/` 镜像、SKILLS_SNAPSHOT.md 生成
- `PromptBuilder`：7-block 注入顺序冻结，skills_snapshot 参数，向后兼容
- `Chat API`：`route` 字段进入 ChatRequest + metadata，每轮生成 snapshot
- `path_utils`：`skills/` 已在 WRITABLE_PREFIXES
- 测试：16/16 通过

### 不需要改动的核心模块
| 文件 | 原因 |
|------|------|
| `backend/graph/skill_loader.py` | 已支持任意数量 registry 条目 |
| `backend/graph/prompt_builder.py` | 已注入 snapshot |
| `backend/api/chat.py` | 已传递 route + snapshot |
| `backend/graph/path_utils.py` | `skills/` 已在 WRITABLE_PREFIXES |

### 现有 Skills 盘点（9 个系统技能 + 4 个 Anthropic 官方 skill）
| ID | 分类 | 本次角色 |
|----|------|----------|
| `csv_plot_kobs` | analysis | 闭环B 直接复用 ✅ |
| `writing_outline_rd` | word | 闭环C 直接复用 ✅ |
| `stage_report_ppt` | ppt | 闭环C 需重命名为 `stage_report_pack` ⚠️ |
| `paper_quad_summary` | literature | 作为 `literature_pdf_4block` 的 fork 参考 |
| `mechanism_evidence_chain` | analysis | 作为 `evidence_chain_pack` 的 fork 参考 |
| `synthesis_checklist` | experiment | 作为 `experiment_checklist` 的 fork 参考 |
| `deepresearch_prompt` | literature | 保留不动 |
| `experiment_matrix` | experiment | 保留不动 |
| `research_skill_creator` | meta | 保留不动 |
| `docx` | word | **新增** — Anthropic 官方 Word 文档 skill，支持 .docx 创建/编辑/分析，闭环C 写作输出 ✅ |
| `pdf` | analysis | **新增** — Anthropic 官方 PDF 处理 skill，支持读取/合并/拆分/创建/表单，闭环A 文献处理 ✅ |
| `pptx` | ppt | **新增** — Anthropic 官方 PPT skill，支持 .pptx 创建/编辑/分析，闭环C 汇报输出 ✅ |
| `skill_creator` | meta | **新增** — Anthropic 官方 skill 创建/优化/评估工具，支持 eval 驱动迭代 ✅ |

---

## 1. 需新建的 Skills（6 个科研 skill + 4 个 Anthropic 官方 skill）

| # | Skill ID | 闭环 | 参考来源 | 说明 |
|---|----------|------|----------|------|
| 1 | `experiment_checklist` | B-实验 | fork `synthesis_checklist` | 泛化为通用实验类型 |
| 2 | `spectra_reading_note` | B-实验 | 全新 | EPR/XANES/XPS/UV-Vis/Raman 读图笔记 |
| 3 | `literature_pdf_4block` | A-机理 | fork `paper_quad_summary` | 批量 PDF 四块拆解 + 跨文献对比 |
| 4 | `evidence_chain_pack` | A-机理 | fork `mechanism_evidence_chain` | 多源证据聚合为 Pack |
| 5 | `mechanism_stage_report` | A-机理 | 全新 | 机理证据链 → 阶段汇报桥接 |
| 6 | `figure_to_slide_map` | C-写作 | 全新 | 图表 → PPT 页/论文章节映射 |
| 7 | `docx` | C-写作 | Anthropic 官方 | Word 文档创建/编辑/分析，含 scripts/ 辅助工具 |
| 8 | `pdf` | A-机理/通用 | Anthropic 官方 | PDF 读取/合并/拆分/创建/表单填写，含 scripts/ |
| 9 | `pptx` | C-写作 | Anthropic 官方 | PPT 创建/编辑/分析，含 scripts/ + editing.md + pptxgenjs.md |
| 10 | `skill_creator` | 元工具 | Anthropic 官方 | Skill 创建/优化/评估，含 agents/ + eval-viewer/ + scripts/ |

---

## 2. 实施步骤

开发顺序遵循 phase5.1-index.md §5 建议：实验 → 机理 → 写作。

---

### Step A：实验证据闭环（experiment_closure）

#### A1. 新建 `backend/skills/experiment_checklist/SKILL.md`

**设计要点**（fork 自 `synthesis_checklist`，泛化）：
- `id`: `experiment_checklist`
- `name`: 通用实验 checklist（原理 + SOP + 缺失对照 + 记录项）
- `when_to_use`: 用户提供实验原理/SOP/数据，要求整理成 checklist 或审查缺失对照
- `inputs_required`: 实验类型、原理描述、已有 SOP（可选）、已有数据（可选）
- `outputs`: 按步骤 Markdown checklist、缺失对照清单、污染/干扰风险提醒、Memory patch 建议
- `reads`: `memory/identity/project.md`, `memory/identity/lab_context.md`, 相关 `TASK_*`
- `writes`: `memory/tasks/TASK_<experiment_type>_checklist.md`, `memory/timeline/days/<today>.md`
- `triggers`: `实验 checklist`, `SOP 整理`, `缺什么对照`, `实验流程`, `对照清单`
- `preferred_routes`: `["experiment"]`
- **执行计划**：
  1. 识别实验类型
  2. 从用户输入提取步骤
  3. 插入必需对照（空白/无催化剂/无氧化剂/探针/淬灭剂）
  4. 标记污染风险
  5. 输出 checklist + 缺失信息
- **Prompt snippet 要点**：不编造参数、必须显式列出缺失对照、每步一句话

#### A2. 新建 `backend/skills/spectra_reading_note/SKILL.md`

**设计要点**（全新）：
- `id`: `spectra_reading_note`
- `name`: 谱学读图笔记（EPR / XANES / EXAFS / XPS / UV-Vis / Raman）
- `when_to_use`: 用户上传或描述谱图数据，要求基础读图、峰位标注、判读逻辑
- `outputs`: 读图笔记（峰位/特征/归属）、判读逻辑表（特征 → 支持什么 → 局限性）、缺失信息清单、建议写入的 Task
- `reads`: `memory/identity/project.md`, 相关 `TASK_characterization_*`
- `writes`: `memory/tasks/TASK_spectra_<technique>_<topic>.md`
- `triggers`: `EPR 读图`, `XANES 分析`, `XPS 峰位`, `光谱分析`, `谱图笔记`, `Raman`, `UV-Vis 特征峰`
- `preferred_routes`: `["experiment", "mechanism_closure"]`
- **执行计划**：
  1. 识别谱学类型
  2. 列出观察到的特征（峰、边、肩峰）
  3. 给出暂定归属 + 参考文献
  4. 写明每个归属的局限性
  5. 输出读图笔记 + 缺失信息
- **Prompt snippet 要点**：峰位必须含误差范围、肩峰归属需半高宽证据、区分 confirmed vs tentative

#### A3. 更新 `backend/skills/registry.json`

添加 `experiment_checklist` 和 `spectra_reading_note` 两个条目。

#### A4. 新建 `backend/tests/test_closed_loop_experiment.py`

**测试项**：
1. SkillLoader snapshot 包含 `csv_plot_kobs` + `experiment_checklist` + `spectra_reading_note`
2. 系统技能镜像到 `workspace/skills/_system/` 成功
3. 每个 SKILL.md 可读且包含必需 section（meta / execution plan / prompt snippet）
4. `writes` 声明的路径在 WRITABLE_PREFIXES 内
5. registry 条目的 `preferred_routes` 包含 `"experiment"`

---

### Step B：文献机理闭环（mechanism_closure）

#### B1. 新建 `backend/skills/literature_pdf_4block/SKILL.md`

**设计要点**（fork 自 `paper_quad_summary`，扩展批量模式）：
- `id`: `literature_pdf_4block`
- `name`: PDF 文献四块拆解（体系设置 / 活性物种证据 / 条件影响 / 对本体系启发）
- `when_to_use`: 用户上传 1-7 篇 PDF 或粘贴文献内容，要求按四块拆解并映射到自己的体系
- `outputs`: 每篇四块摘要、跨文献对比矩阵（共性/差异）、可迁移实验清单、建议写入的 TASK/PACK
- `reads`: `memory/identity/project.md`, 相关 `TASK_mechanism_*`, `PACK_mechanism_*`
- `writes`: `memory/tasks/TASK_literature_<topic>.md`, 可选 `memory/packs/PACK_literature_<topic>.md`
- `triggers`: `拆这几篇 pdf`, `文献四块`, `按体系设置拆`, `文献对比`, `pdf 拆解`
- `preferred_routes`: `["mechanism_closure"]`
- **与 `paper_quad_summary` 的区别**：支持批量 PDF、输出跨文献对比表、显式目标 PACK 输出
- **执行计划**：
  1. 逐篇提取四块
  2. 构建跨文献对比矩阵
  3. 识别可迁移实验
  4. 输出逐篇摘要 + 对比 + 可操作项
- **Prompt snippet 要点**：不做全文摘要只提取可迁移信息、每条证据必须标注有无对照/局限性、输出 3-5 个可直接复现的实验

#### B2. 新建 `backend/skills/evidence_chain_pack/SKILL.md`

**设计要点**（fork 自 `mechanism_evidence_chain`，升级为 Pack 输出）：
- `id`: `evidence_chain_pack`
- `name`: 多源证据链聚合 Pack（文献 + 实验 + 推理 → 机理闭环草图）
- `when_to_use`: 用户已有多个 TASK（文献/实验/表征），要求汇总成一个证据链 Pack
- `outputs`: PACK_mechanism_*（Claim-Evidence 表、证据链图谱、缺口清单、下一步优先级矩阵）
- `reads`: `memory/identity/project.md`, `memory/tasks/TASK_mechanism_*`, `memory/tasks/TASK_characterization_*`, `memory/packs/PACK_literature_*`
- `writes`: `memory/packs/PACK_mechanism_<topic>.md`
- `triggers`: `证据链汇总`, `机理 pack`, `把这些证据串起来`, `证据链草图`, `闭环审计`
- `preferred_routes`: `["mechanism_closure"]`
- **与 `mechanism_evidence_chain` 的区别**：后者审计单个 claim 的证据；本 skill 聚合多源为可交付 Pack
- **执行计划**：
  1. 收集所有引用的 TASK
  2. 构建统一 Claim-Evidence 表
  3. 识别缺口和矛盾
  4. 生成 Pack（含叙事骨架）
  5. 输出下一步优先级矩阵
- **Prompt snippet 要点**：必须引用实际 TASK/PACK 文件路径、每个 claim 必须标注来源（文献 DOI 或实验 run）、缺口必须显式且可操作

#### B3. 新建 `backend/skills/mechanism_stage_report/SKILL.md`

**设计要点**（全新，桥接机理 → 汇报）：
- `id`: `mechanism_stage_report`
- `name`: 机理 → 阶段汇报桥接（从证据链 Pack 生成汇报结构）
- `when_to_use`: 用户已有机理证据链 Pack，要求转成阶段汇报或组会可用的结构
- `outputs`: 5-8 页汇报结构、每页 Claim + Evidence 映射、缺口与下一步、WPS AI 提示词（可选）
- `reads`: `memory/packs/PACK_mechanism_*`, `memory/identity/project.md`, `memory/timeline/stage_reports/`
- `writes`: `memory/timeline/stage_reports/Rxx_mechanism_YYYYMMDD.md`, `memory/packs/PACK_stage_report_mechanism_*.md`
- `triggers`: `机理汇报`, `把证据链变成汇报`, `机理阶段小结`, `mechanism report`
- `preferred_routes`: `["mechanism_closure", "stage_progress"]`
- **执行计划**：
  1. 读取机理 Pack
  2. 提取顶层 claim 及其证据状态
  3. 组织为汇报结构（开场：北极星 → 中间：逐 claim → 收尾：缺口 + 下一步）
  4. 输出阶段汇报 + 可选 WPS AI 提示词
- **Prompt snippet 要点**：每页恰好 1 个 claim + 其证据状态、缺口不是失败而是"下一个验证目标"、必须引用 Pack 文件路径

#### B4. 更新 `backend/skills/registry.json`

添加 `literature_pdf_4block`、`evidence_chain_pack`、`mechanism_stage_report` 三个条目。

#### B5. 新建 `backend/tests/test_closed_loop_mechanism.py`

**测试项**：
1. SkillLoader snapshot 包含三个机理类 skill
2. 系统技能镜像成功
3. SKILL.md 可读且包含必需 section
4. `writes` 路径（`memory/packs/PACK_mechanism_*`）在 WRITABLE_PREFIXES 内
5. registry 条目的 `preferred_routes` 包含 `"mechanism_closure"`

---

### Step C：阶段汇报/写作闭环（stage_progress / writing_closure）

#### C1. 重命名 `stage_report_ppt` → `stage_report_pack`

**操作**：
1. 重命名目录：`backend/skills/stage_report_ppt/` → `backend/skills/stage_report_pack/`
2. 更新 `SKILL.md`：
   - `id` 改为 `stage_report_pack`
   - 增加 Pack 级输出契约（`PACK_stage_report_*`）
   - 保留原有 triggers，新增 `stage_report_pack`
3. 更新 `registry.json`：条目 `id` 从 `stage_report_ppt` 改为 `stage_report_pack`，`entry` 路径同步更新

**影响**：已有 workspace 的 `_system/stage_report_ppt/` 镜像会残留但无害（SkillLoader 不删除旧镜像）。

#### C2. 新建 `backend/skills/figure_to_slide_map/SKILL.md`

**设计要点**（全新）：
- `id`: `figure_to_slide_map`
- `name`: 图表 → 页面/章节映射（PPT 或论文写作）
- `when_to_use`: 用户已有 figures/Task/Pack，要求把图映射到 PPT 页或论文章节
- `outputs`: 映射表（figure path → slide/section + caption + 1-sentence conclusion）、缺图清单、放图策略（主文 vs SI）
- `reads`: `assets/figures/`, `memory/tasks/TASK_*`, `memory/packs/PACK_*`, `memory/identity/project.md`
- `writes`: `memory/packs/PACK_figure_map_*.md`
- `triggers`: `图放哪页`, `figure mapping`, `图表映射`, `哪些图放主文`, `SI 放图策略`
- `preferred_routes`: `["stage_progress", "writing_closure"]`
- **执行计划**：
  1. 盘点所有可用 figures
  2. 将每个 figure 匹配到 Claim/Task
  3. 分配到 slide/section
  4. 决定主文 vs SI 放置
  5. 输出映射表 + 缺图清单
- **Prompt snippet 要点**：每个 figure 必须绑定到具体 Claim、主文只放直接支持主叙事的图、SI 放辅助/补充证据、必须输出 figure 路径而非描述

#### C3. 更新 `backend/skills/registry.json`

重命名 `stage_report_ppt` → `stage_report_pack`，添加 `figure_to_slide_map`。

#### C4. 新建 `backend/tests/test_closed_loop_writing.py`

**测试项**：
1. SkillLoader snapshot 包含 `stage_report_pack` + `writing_outline_rd` + `figure_to_slide_map`
2. 系统技能镜像成功
3. SKILL.md 可读且包含必需 section
4. `writes` 路径在 WRITABLE_PREFIXES 内
5. registry 条目的 `preferred_routes` 包含 `"stage_progress"` 或 `"writing_closure"`

---

### Step D：Anthropic 官方 Skill 集成（docx / pdf / pptx / skill-creator）

> 来源：https://github.com/anthropics/skills/tree/main/skills/

#### D1. 已完成：下载并放置到 `backend/skills/`

4 个官方 skill 已从 GitHub 下载并放置到对应目录：

| Skill | 目录 | 内容 |
|-------|------|------|
| `docx` | `backend/skills/docx/` | SKILL.md + scripts/（office 工具链：unpack/pack/validate/soffice + XML schemas） |
| `pdf` | `backend/skills/pdf/` | SKILL.md + forms.md + reference.md + scripts/（表单填写/字段提取/PDF 转图片等） |
| `pptx` | `backend/skills/pptx/` | SKILL.md + editing.md + pptxgenjs.md + scripts/（office 工具链 + thumbnail/clean/add_slide） |
| `skill-creator` | `backend/skills/skill-creator/` | SKILL.md + agents/（analyzer/comparator/grader）+ eval-viewer/ + scripts/（run_eval/benchmark/improve_description 等） |

#### D2. 已完成：更新 `backend/skills/registry.json`

- 版本升至 v0.4.0
- 新增 4 个条目：`docx`、`pdf`、`pptx`、`skill_creator`
- 同时修复了 `oxidant_route_comparison` 条目截断 bug

#### D3. 各 skill 在闭环中的角色

| Skill | 闭环角色 | 说明 |
|-------|----------|------|
| `docx` | 闭环C 写作输出 | 将 Results & Discussion 大纲或阶段报告输出为正式 .docx 文档 |
| `pdf` | 闭环A 文献输入 + 通用 | 读取/提取 PDF 文献内容，合并/拆分 PDF，创建报告 PDF |
| `pptx` | 闭环C 汇报输出 | 将阶段汇报结构输出为正式 .pptx 演示文稿（补充 `stage_report_ppt` 的结构规划能力） |
| `skill_creator` | 元工具 | 用于创建新 skill、运行 eval 测试、基准分析、迭代优化现有 skill |

#### D4. 依赖说明

官方 skill 的 scripts/ 需要以下依赖（按需安装，不影响核心 SkillLoader 加载）：

| 依赖 | 用途 | 安装命令 |
|------|------|----------|
| `markitdown[pptx]` | pptx/docx 文本提取 | `pip install "markitdown[pptx]"` |
| `pptxgenjs` | 从零创建 pptx | `npm install -g pptxgenjs` |
| `docx` (npm) | 从零创建 docx | `npm install -g docx` |
| `pypdf` | PDF 基础操作 | `pip install pypdf` |
| `pdfplumber` | PDF 表格/文本提取 | `pip install pdfplumber` |
| `reportlab` | 创建 PDF | `pip install reportlab` |
| `Pillow` | 缩略图生成 | `pip install Pillow` |
| LibreOffice (`soffice`) | PDF 转换 | 系统安装 |
| Poppler (`pdftoppm`) | PDF 转图片 | `brew install poppler` |

---

## 3. registry.json 最终状态（v0.4，19 个条目）

| # | ID | 分类 | 状态 |
|---|-----|------|------|
| 1 | `synthesis_checklist` | experiment | 保留 |
| 2 | `stage_report_pack` | ppt | 重命名自 `stage_report_ppt` |
| 3 | `deepresearch_prompt` | literature | 保留 |
| 4 | `paper_quad_summary` | literature | 保留 |
| 5 | `experiment_matrix` | experiment | 保留 |
| 6 | `csv_plot_kobs` | analysis | 保留 |
| 7 | `writing_outline_rd` | word | 保留 |
| 8 | `mechanism_evidence_chain` | analysis | 保留 |
| 9 | `research_skill_creator` | meta | 保留 |
| 10 | `experiment_checklist` | experiment | **新建** |
| 11 | `spectra_reading_note` | analysis | **新建** |
| 12 | `literature_pdf_4block` | literature | **新建** |
| 13 | `evidence_chain_pack` | analysis | **新建** |
| 14 | `mechanism_stage_report` | analysis | **新建** |
| 15 | `figure_to_slide_map` | ppt | **新建** |
| 16 | `docx` | word | **新增（Anthropic 官方 skill）** |
| 17 | `pdf` | analysis | **新增（Anthropic 官方 skill）** |
| 18 | `pptx` | ppt | **新增（Anthropic 官方 skill）** |
| 19 | `skill_creator` | meta | **新增（Anthropic 官方 skill）** |

---

## 4. 文件变更清单

### 新建（13 个文件/目录）
1. `backend/skills/experiment_checklist/SKILL.md`
2. `backend/skills/spectra_reading_note/SKILL.md`
3. `backend/skills/literature_pdf_4block/SKILL.md`
4. `backend/skills/evidence_chain_pack/SKILL.md`
5. `backend/skills/mechanism_stage_report/SKILL.md`
6. `backend/skills/figure_to_slide_map/SKILL.md`
7. `backend/skills/docx/` — Anthropic 官方 docx skill（含 SKILL.md + scripts/）
8. `backend/skills/pdf/` — Anthropic 官方 pdf skill（含 SKILL.md + scripts/ + forms.md + reference.md）
9. `backend/skills/pptx/` — Anthropic 官方 pptx skill（含 SKILL.md + scripts/ + editing.md + pptxgenjs.md）
10. `backend/skills/skill-creator/` — Anthropic 官方 skill-creator（含 SKILL.md + agents/ + scripts/ + eval-viewer/）
11. `backend/tests/test_closed_loop_experiment.py`
12. `backend/tests/test_closed_loop_mechanism.py`
13. `backend/tests/test_closed_loop_writing.py`

### 修改（2 个文件）
1. `backend/skills/registry.json` — 版本升至 v0.4，新增 6 + 4 条目（含 4 个 Anthropic 官方 skill），修复 `oxidant_route_comparison` 截断 bug，重命名 1 条目
2. `backend/skills/stage_report_ppt/` → `backend/skills/stage_report_pack/` — 目录重命名 + SKILL.md 更新

---

## 5. 验证方式

### 自动化测试
```bash
PYTHONPYCACHEPREFIX=/tmp/pycache backend/.venv/bin/python -m unittest discover -s backend/tests -v
```
预期：原 16 项 + 新 3 个测试文件全部通过。

### 手动集成验证（每个闭环一个最小场景）

**闭环 B（实验证据）**：
> "这是一份 PMSO 实验的 CSV 数据，请帮我出图并整理成 checklist"
- 验证：Agent 读取 `csv_plot_kobs` + `experiment_checklist` skill → 产出 figure + TASK

**闭环 A（文献机理）**：
> "帮我把这 3 篇文献按四块拆解，然后串成证据链 Pack"
- 验证：Agent 读取 `literature_pdf_4block` + `evidence_chain_pack` skill → 产出 PACK_mechanism_*

**闭环 C（阶段汇报/写作）**：
> "把最近的实验和机理证据整理成组会 PPT 结构"
- 验证：Agent 读取 `stage_report_pack` + `figure_to_slide_map` skill → 产出 PACK_stage_report_*

---

## 6. 风险点与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| Snapshot 体积增长 | 19 个 skill 约 5-6KB，仍在合理范围 | 监控，必要时精简 triggers 描述 |
| 旧 workspace 残留镜像 | 重命名后 `_system/stage_report_ppt/` 残留 | 无害，Phase 7 清理 |
| SKILL.md prompt snippet 质量 | 新 skill 未经实际对话验证 | Phase 5.1 只要求跑通链路，调优放后续迭代 |
| 跨闭环依赖 | 闭环 C 依赖 A/B 的产物 | 开发顺序已保证：B → A → C |
| Anthropic 官方 skill 含 scripts/ 子目录 | docx/pptx/pdf/skill-creator 带有辅助脚本和依赖 | 脚本按需使用，不影响 SkillLoader 加载；依赖（markitdown/pptxgenjs/reportlab 等）按需安装 |
| 官方 skill 与现有 skill 功能重叠 | `pptx` 与 `stage_report_ppt`、`skill-creator` 与 `research_skill_creator` 有部分重叠 | 官方 skill 偏通用文件操作，现有 skill 偏科研场景；两者互补，不冲突 |

---

## 7. Phase 边界提醒

**本 Phase 只做**：
- 让三个闭环各自至少跑通一个真实场景
- 让 skill 被系统看到、被 Agent 读到、被任务用到
- 让 Prompt 注入链、workspace skill 目录、SKILLS_SNAPSHOT、read_file 链路打通

**不做（留给后续 Phase）**：
- Phase 6：TraceWriter 完整闭环审计升级、从 trace 沉淀新 skill
- Phase 7：UI 细节、初始化引导界面、route selector、交互 polish


## 8. Skill 创建自检
每创建一个新 skill，请不要只提交 SKILL.md，还要附一份 skill review note，按以下 8 项自检：

1. 这个 skill 是否只解决一件高频、可复用的事？
2. 名称是否是动作/流程，而不是科研结论？
3. 输入是否明确（用户会给什么 assets）？
4. 输出是否明确（会生成什么 artifact / patch）？
5. 是否写清楚了证据不足时的处理方式？
6. 是否写清楚了边界和禁止事项？
7. 是否能迁移到别的 workspace，而不是写死当前课题？
8. 是否已经在一个真实闭环样例中被调用并通过？

同时请确保它符合 Claude 官方 skill best practices：
- concise
- well-structured
- discoverable
- tested with real usage
