---
title: "BOOTSTRAP.md — Workspace Init Protocol"
read_when:
  - first-run only
not_injected_after: init
---

# BOOTSTRAP.md — Workspace 初始化协议

> **边界声明**
> 本文件只在 workspace **首次启动**时使用，作用是点火——引导生成首批最小记忆文件，使系统进入可运行状态。
> 完成后本文件不参与任何后续 system prompt 注入，不作为常驻控制层正文。

---

## Phase 0 · 填写 Init Schema（由用户提供）

在开始生成任何文件之前，先向用户收集以下 **workspace_init_schema**。
所有字段均为必填，除非标注「可选」。
收集完成后，将 schema 用于 Phase 1–3 的文件生成，**不得硬编码科研主题**。

```yaml
workspace_init_schema:

  # 1. 单一研究主题（workspace 的北极星）
  research_topic:
    title: ""              # 例：Ce-Co₃O₄ 激活 NaClO₂ 实现选择性降解抗生素
    north_star: ""         # 一句话：我要证明……
    target_system: ""      # 污染物 / 氧化剂 / 催化剂（可简写）
    target_journal: ""     # 目标期刊（可选）

  # 2. 当前优先验证的 3 个闭环（按重要程度排序）
  # allowed_routes 必须从以下 4 个中选择：
  #   mechanism_closure | experiment_closure | stage_progress | writing_closure
  priority_loops:
    - id: "L1"
      claim: ""            # 一句可证伪断言
      why_urgent: ""       # 为什么现在最重要
      allowed_routes:      # 该闭环对应的路由（可多选）
        - mechanism_closure
    - id: "L2"
      claim: ""
      why_urgent: ""
      allowed_routes:
        - experiment_closure
    - id: "L3"
      claim: ""
      why_urgent: ""
      allowed_routes:
        - stage_progress

  # 3. 第一批 assets 分类清单
  assets_inventory:
    pdf:           []      # 已有文献路径列表（可空）
    data:          []      # csv / xlsx / txt 实验数据
    image_or_spectra: []   # png / jpg / tiff 图谱
    ppt_or_md:     []      # 汇报 ppt / 笔记 md

  # 4. 实验室现实约束
  lab_context:
    available_instruments: []   # 例：XRD, SEM, XPS, EPR
    unavailable_instruments: [] # 例：同步辐射（需预约）
    naming_convention: ""       # 样品命名规则
    contamination_risks: ""     # 例：Co 离子溶出、Cl 背景
    other_constraints: ""       # 人手、经费、时间窗口等

  # 5. 当前最重要交付（近期 deadline）
  current_deliverable:
    type: ""               # paper | stage_report | thesis_chapter | other
    deadline: ""           # 日期，例：2026-06-30
    description: ""        # 一句话说明交付内容

  # 6. 当前最大不确定性（最多 3 条）
  top_uncertainties:
    - ""
    - ""
    - ""
```

---

## Phase 1 · 生成 Layer1 身份文件

基于 schema，依次生成以下文件。
**每个文件必须调用 write_file 工具并收到成功返回后，才能标记为已完成。**

### 1-A · `memory/identity/project.md`

从 schema 的 `research_topic` + `priority_loops` + `top_uncertainties` + `current_deliverable` 生成。
结构沿用模板格式：Project Snapshot / 术语表 / Claim 判据 / 当前最大不确定性 / 近期验证计划。

### 1-B · `memory/identity/lab_context.md`

从 schema 的 `lab_context` 生成。
包含：可用仪器、不可用仪器、命名规则、污染风险、其他约束。

### 1-C · `memory/identity/context_budget.md`

固定内容，每个 workspace 相同，直接从模板复制写入。
（内容：单回合 token 预算、截断策略、Layer 注入优先级。）

---

## Phase 2 · 生成 Layer2 时间轴骨架

### 2-A · `memory/timeline/180d_index.md`

从 schema 的 `research_topic` + `current_deliverable.deadline` 生成。
包含：阶段划分（P01–P05）、里程碑时间节点、当前所在阶段标记。

---

## Phase 3 · 生成 Layer3 首批原子资产

### 3-A · `memory/concepts/CONCEPT_<topic>.md`

`<topic>` 取自 schema 的 `research_topic.title`（英文缩写或关键词，无空格）。
包含：id / name / scope / keywords / north_star / active_tasks（初始为空）。

### 3-B · `memory/tasks/TASK_bootstrap_initial_questions.md`

将 schema 的 `priority_loops` 中 3 个 claim 逐一写入为 Task 的 Claim 字段。
 Protocol 字段留空（待用户补充）。
 Run 字段留空（待实验后填写）。

---

## Phase 4 · 完成检查

生成完毕后，输出以下确认表：

| 文件 | 状态 |
|------|------|
| `memory/identity/project.md` | ✓ / ✗ |
| `memory/identity/lab_context.md` | ✓ / ✗ |
| `memory/identity/context_budget.md` | ✓ / ✗ |
| `memory/timeline/180d_index.md` | ✓ / ✗ |
| `memory/concepts/CONCEPT_<topic>.md` | ✓ / ✗ |
| `memory/tasks/TASK_bootstrap_initial_questions.md` | ✓ / ✗ |

全部 ✓ 后，告知用户：

> Workspace 初始化完成。BOOTSTRAP.md 已完成使命，后续对话将由控制平面核心文件（AGENTS / SOUL / IDENTITY / USER / project.md）接管；`SKILLS_SNAPSHOT.md` 会由运行时 `SkillLoader` 自动生成并注入。

---

## 附：生成文件时的通用约束

- **File-first**：每个文件通过 `write_file` 工具写入，工具返回成功后才算完成。
- **不硬编码主题**：所有领域词汇、体系名称、仪器名均来自用户填写的 schema，不自行假设。
- **不引入多 agent / RAG / skill proposal**：init 阶段只写文件，不触发任何复杂编排。
- **不参与后续注入**：本文件在 `PromptBuilder` 中仅在检测到 `first_run=True` 时读取；否则跳过。
