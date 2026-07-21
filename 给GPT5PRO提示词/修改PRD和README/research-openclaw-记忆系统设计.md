# prompt_prd.md — Researchloop-OpenClaw Prompt & Memory PRD（v0.1）

> 目标：指导你实现一个模仿 OpenClaw 的 Researchloop-OpenClaw Agent，让实验型科研用户在 180 天周期内完成 **实验闭环 → 机理证据链闭环 → 阶段汇报闭环 → 写作闭环**。  
> 核心原则：**File-first Memory（文件即记忆）/ Skills as Plugins（技能即插件）/ 透明可控（Trace 可回放）**。

---

## 1. 产品范围与用户场景（基于 180 天对话数据）

### 1.1 用户的记忆压力源（你必须“替用户记住”的东西）

1) **阶段性推进压力**  
- 每 2–3 周一次“第 N 次阶段汇报”，用户经常带 `assets/ppt_pack/Rxx_YYYYMMDD` 素材路径。  
- 需求是：快速从“过去一段时间的 day/week/task”中汇总成 PPT。

2) **实验闭环压力**  
- “今天做了什么 / 是否支撑主线 / 还缺什么对照/表征”。  
- 高频交付：合成 checklist、参数矩阵、以及“这组 XRD/SEM/XPS 能证明什么不能证明什么”。

3) **机理证据链压力**  
- 用户反复追问 Co(IV) / ClO₂ “硬证据链”，强调 PMSO 探针 + DPD 显色 + 淬灭剂 + 必要空白/对照 的组合与判据。

4) **写作结构压力**  
- Results & Discussion 目录树 + 每节中心句 + 主文/SI 放图策略。

### 1.2 你的 Agent 在 180 天中要解决的“闭环任务”

- **粗粒度（阶段级）**：阶段里程碑、主线假设、最大不确定性、下一步验证计划  
- **细粒度（每日级）**：每天 SOP、编号/污染风险提醒、数据路径、拟合结果、图表产物  
- **跨周期（证据链）**：Claim–evidence 可追溯、Protocol 可复用、RunResult 可反向索引  
- **可沉淀（技能）**：高重复交付自动提炼为 Skill

---

## 2. 核心架构：三层记忆 + 插件技能 + Trace 回放

### 2.1 三层记忆（File-first）

> 三层来自你的《记忆系统设计.md》，并与 OpenClaw 的“Project Context 注入”机制对齐。

- **Layer1：Identity（长期稳定）**  
  目标：让系统长期知道“你是谁、项目是什么、输出该长什么样”。  
  文件：`memory/identity/user.md / project.md / lab_context.md / context_budget.md`

- **Layer2：Timeline（阶段→周→天→阶段汇报）**  
  目标：把 180 天从“阶段计划”落到“每天执行”，并能自动汇总成阶段汇报 Pack。  
  文件：`memory/timeline/180d_index.md` + `phases/` + `weeks/` + `days/` + `stage_reports/`

- **Layer3：Atom Notes（跨周期资产）**  
  推荐对外展示 **Concept / Task / Pack**：  
  - Concept：主题容器（你在验证什么）  
  - Task：一次验证任务（Claim + Protocol + Run）  
  - Pack：交付物容器（组会/机理/写作/图集）  
  文件：`memory/concepts/`、`memory/tasks/`、`memory/packs/`  

### 2.2 Skills as Plugins（技能即插件）

- 目录：`skills/<skill_id>/SKILL.md`
- 规则：**一个文件夹 = 一个能力**，可直接拖入工作区启用
- 必须可审计：SKILL.md 写清楚
  - 何时触发（intent / triggers）
  - 读哪些文件（reads）
  - 写哪些文件（writes）
  - 输出结构（output contract）

### 2.3 Trace（透明可控）

- 每回合写入：`.openclaw/context_trace/TXXXX.json`
- 最小字段：
  - context_read / context_write / missing / skills_selected / tool_calls / artifacts

---

## 3. Prompt 拼接 PRD（最关键）

Researchloop-OpenClaw 的“上下文拼接”完全复刻 OpenClaw 的 content-level 规则，并扩展到三层记忆与 skills。

### 3.1 两条消息模型（system + user）

最终发给模型的是两条消息：

1) **system**：运行环境 + 工具说明 + 工作区说明 +（可选）可信入站元信息 + **Project Context（文件注入）**  
2) **user**：非可信上下文（转发/引用/最近聊天记录等）+ 用户正文（本轮请求 + 附件/路径）

> 关键：**可信入站元信息放 system**；**非可信上下文放 user，并标记 untrusted**。

### 3.2 system prompt 的拼接结构（块与块之间一个空行）

#### 3.2.1 固定块顺序（从上到下）

1. 身份行（固定开头）  
   `You are a personal assistant running inside OpenClaw.`  
   > 可以保留 OpenClaw 原句，保持兼容；Researchloop 的差异写在 Workspace 块里。

2. Tooling（工具概览，可选但建议保留）  
   ```
   ## Tooling
   - file: Read/write workspace files
   - python: Data processing / plotting
   - pdf: Read & cite PDFs
   ...
   ```

3. Workspace（工作区说明）  
   说明：
   - 工作目录路径
   - 你必须以“注入文件”为本轮事实来源
   - 缺信息要列 missing，不允许脑补

4. Inbound Context（可信元信息，可选）  
   ```
   ## Subagent Context
   ## Inbound Context (trusted metadata)
   ```json
   { "platform": "...", "timezone": "...", "language": "zh-CN", ... }
   ```
   ```

5. Project Context（文件注入，固定标题）  
   ```
   # Project Context
   The following project context files have been loaded:

   ## <absolute_path_1>

   <file_1_content>

   ## <absolute_path_2>

   <file_2_content>
   ```

#### 3.2.2 Project Context：注入文件列表与排序（Researchloop 扩展版）

> OpenClaw 的默认顺序是：AGENTS → SOUL → TOOLS → IDENTITY → USER → …  
> Researchloop 在此基础上增加三层记忆与技能文件。

**A. 永远注入（workspace root 基础文件，按存在性）**

1. `AGENTS.md`
2. `SOUL.md`
3. `TOOLS.md`
4. `IDENTITY.md`
5. `USER.md`
6. `HEARTBEAT.md`（若存在）
7. `BOOTSTRAP.md`（首次启动时存在）
8. `MEMORY.md`（长期摘要；仅 main session）

**B. 业务必读（Layer1 Identity）**

9. `memory/identity/user.md`
10. `memory/identity/project.md`
11. `memory/identity/lab_context.md`
12. `memory/identity/context_budget.md`（可选）

**C. 业务按需（Layer2 Timeline）**

13. `memory/timeline/180d_index.md`
14. 当前阶段：`memory/timeline/phases/<current>.md`
15. 若请求涉及“最近/今天”：注入对应 `days/YYYY-MM-DD.md`（今天 + 昨天）
16. 若是阶段汇报：注入时间范围内的 `weeks/` 或若干 `days/`
17. 若是阶段汇报：注入上一份 `stage_reports/Rxx_*.md`

**D. 业务按需（Layer3 Atom Notes）**

18. 当前 Concept：`memory/concepts/CONCEPT_*.md`
19. 相关 Task：`memory/tasks/TASK_*.md`
20. 相关 Pack：`memory/packs/PACK_*.md`

**E. Skills（插件技能）**

21. `skills/registry.json`（只读）
22. 本次命中的 1–3 个 skill 的 `skills/<id>/SKILL.md`

> 注：顺序原则 = **稳定 → 变化 → 本轮相关**。  
> 这能最大化可控性：模型先拿到“规则”，再拿到“最近发生了什么”。

### 3.3 裁剪与预算（必须实现）

你需要实现两级预算：

- `perFileMaxChars`：单文件最大注入字符数  
- `totalMaxChars`：Project Context 总最大字符数

裁剪策略：优先保留标题/字段/表格/判据，尾部截断用 `…`，并在 trace 记录 `truncated=true`。

### 3.4 user 消息拼接（untrusted + body）

user 消息由两段组成（中间空一行）：

1) **untrusted blocks**（存在才加）  
每段：
- 标题（固定短语之一，如 `Chat history since last reply (untrusted, for context)`）
- JSON 代码块（内容来自外部平台/引用/转发/历史）

2) **用户正文**（本轮请求文本）  
若只有媒体无文字：`[User sent media without caption]`

---

## 4. Runtime Loop：一次对话如何“读→做→写→沉淀”

> 这是 Agent 的默认闭环：Ingest → Plan → Close → Pack → Skill Mining

### 4.1 Ingest（摄取）

- 把用户输入映射成：
  - 本轮 intent（阶段汇报/合成 checklist/机理审计/写作结构/作图拟合…）
  - 相关对象：Concept / Task / Pack
- 如果缺少证据锚点或路径：先写 Missing checklist，不要直接下结论

### 4.2 Plan（计划）

- 输出可执行计划：今天/本周要做什么  
- 将计划写入：`memory/timeline/days/<today>.md` 的 `planned_tasks[]`

### 4.3 Close（闭环）

- 用户提供实验结果/表征结果后：
  - 写入 Task 的 Run 区块（含 raw_data_paths、quick_results、verdict）
  - 更新 Concept 的 active_tasks

### 4.4 Pack（交付）

- 阶段汇报：生成 `PACK_stage_report_*` 并绑定 `assets/ppt_pack/...`
- 机理闭环：生成 `PACK_mechanism_*`（Claim→evidence→判据→下一步）
- 写作：生成 `PACK_writing_*`（目录树/中心句/放图策略）

### 4.5 Skill Mining（沉淀）

当检测到高度重复的交付（例如“按时间顺序 checklist”“阶段汇报 PPT 提示词”）：

- 把“固定流程 + 参数位”抽象成 `skills/<new_skill>/SKILL.md`
- 更新 `skills/registry.json`
- 在 trace 中记录：`skill_mined_from: [Txxxx, Tyyyy, ...]`

---

## 5. 模型输出协议（给前端的默认结构）

除非用户显式要求“只要结果”，否则默认输出：

1. `## Context Trace (public)`  
   - 读了哪些文件（路径列表）
   - 写了哪些文件（路径列表）
2. `## Rationale (public)`  
   - 用 5–10 条要点描述推理链条  
   - 每条要点标注引用的文件路径（例如：`memory/identity/project.md#3.1`）
3. `## Deliverable`  
   - 用户要的交付物（checklist / 矩阵 / PPT / 目录树 / 代码…）
4. `## Missing info checklist`（如果存在缺口）  
5. `## Memory patch (proposed)`  
   - 新增/更新文件建议（字段级别）

---

## 6. 典型场景 → 读写策略（从 180 天对话抽象）

> 下述每个场景都应该尽量通过“选 skill + 选文件”完成，而不是硬编码。

### 6.1 合成 checklist（高频）

- 读：lab_context + today day + 历史 synthesis task（可选）
- 写：today day（artifact/decisions）+ synthesis task（可复用 SOP）

### 6.2 实验矩阵（最高频）

- 读：project 判据 + 已有 task/pack + today day
- 写：`TASK_experiment_matrix_*` + today day 的 planned_tasks

### 6.3 机理证据链审计（高频、强约束）

- 读：project 判据（尤其 Co(IV)/ClO₂）+ mechanism tasks + papers（如有）
- 写：`TASK_mechanism_*` + `PACK_mechanism_*`

### 6.4 “能证明什么不能证明什么”（表征审计）

- 读：对应表征数据所在 task 的 evidence + project 判据
- 输出：两列表格（can prove / cannot prove）+ 下一步补齐建议（最小对照集）

### 6.5 阶段汇报（每 2–3 周）

- 读：time_range 内 days/weeks + 上一份 stage_report + 关键 packs
- 写：`stage_reports/Rxx_...` + `PACK_stage_report_*` + 更新 `180d_index.md`

### 6.6 写作结构（R&D 目录树）

- 读：project 北极星 + 已有 packs（图/结论）
- 写：`PACK_writing_*`

### 6.7 CSV 作图 + kobs 拟合

- 读：数据路径（assets/data）+ user 输出偏好
- 写：figure + `TASK_figure_kobs_*`（记录拟合方法与路径）

---

## 7. 端到端例子（必须包含在 PRD）

> 例子选择“阶段汇报”，因为它同时覆盖：Timeline 汇总、Pack 交付、ppt_pack 路径绑定、missing 追要。

### 7.1 用户输入（user message body）

用户说：

> “帮我做第 6 次阶段汇报（R06），素材都放在 `assets/ppt_pack/R06_20251123/`。请给我 PPT 的页级结构 + 每页中心句 + WPS AI 提示词。我这两周主要做了材料合成和 DPD 显色。”

并且平台还提供（untrusted）历史引用/转发等。

### 7.2 Orchestrator 选择文件（context_read plan）

- Layer1（必读）：
  - `memory/identity/user.md`
  - `memory/identity/project.md`
  - `memory/identity/lab_context.md`
- Layer2（按范围）：
  - `memory/timeline/180d_index.md`
  - `memory/timeline/phases/P02_material_screening.md`（示例）
  - 最近 2–3 周 `memory/timeline/weeks/YYYY-Wxx.md`（如不存在则用 days）
  - 上一次 `memory/timeline/stage_reports/R05_20251105.md`
- Layer3（按需）：
  - 与 DPD/机理相关的 `TASK_mechanism_*`
  - 合成相关 `TASK_synthesis_*`
- Skills：
  - `skills/registry.json`
  - `skills/stage_report_ppt/SKILL.md`

### 7.3 system prompt（最终字符串示例，简化版）

> 注意：真实实现中需要把每个文件的**全文**注入到 `# Project Context`，这里为了示例只展示结构。

```text
You are a personal assistant running inside OpenClaw.

## Tooling
- file: Read/write workspace files
- python: Data processing / plotting

## Workspace
Your working directory is: /workspace
Use the injected Project Context files as the source of truth for this run.
If key info is missing, write a Missing info checklist. Do NOT guess.

## Subagent Context
## Inbound Context (trusted metadata)
```json
{
  "platform": "web",
  "timezone": "Asia/Shanghai",
  "language": "zh-CN",
  "session_type": "main"
}
```

# Project Context
The following project context files have been loaded:

## /workspace/AGENTS.md

<...file content...>

## /workspace/memory/identity/project.md

<...file content...>

## /workspace/skills/stage_report_ppt/SKILL.md

<...file content...>
```

### 7.4 user prompt（最终字符串示例）

```text
Chat history since last reply (untrusted, for context)
```json
{
  "recent_messages": [
    "User: 我这两周主要做了材料合成和 DPD 显色",
    "Assistant: 我需要 time_range 与关键数据路径"
  ]
}
```

帮我做第 6 次阶段汇报（R06），素材都放在 assets/ppt_pack/R06_20251123/。
请给我：PPT 页级结构 + 每页中心句 + WPS AI 提示词。
```

### 7.5 模型输出（前端显示建议）

```markdown
## Context Trace (public)
**Read**
- memory/identity/project.md
- memory/timeline/stage_reports/R05_20251105.md
- skills/stage_report_ppt/SKILL.md
...
**Write (proposed)**
- memory/timeline/stage_reports/R06_20251123.md
- memory/packs/PACK_stage_report_R06_20251123.md

## Rationale (public)
1) 阶段汇报必须围绕 project 北极星与 KPI 组织（见 memory/identity/project.md）  
2) 本阶段结果按 Claim→Evidence 排列；没有 evidence 的部分标注为缺口  
3) PPT 每页最多 2 图 + 2 句结论；需要的图必须给路径或“待补”  
...

## Deliverable
（这里输出 10–14 页 PPT 结构、每页中心句、需要的图/表清单、WPS AI prompt）

## Missing info checklist
- 缺：这两周关键图的路径（XRD/DPD/动力学曲线…）
- 缺：每张图对应的条件（pH、剂量、初始浓度…）
...

## Memory patch (proposed)
- Create: memory/timeline/stage_reports/R06_20251123.md（填 time_range/topline/key_results/...）
- Create: memory/packs/PACK_stage_report_R06_20251123.md（绑定 task_refs 与 assets）
```

### 7.6 本回合 trace 写入（示例）

写入 `.openclaw/context_trace/T0154.json`（turn_id 仅示例）：

```json
{
  "turn_id": "T0154",
  "timestamp": "2025-11-23T22:11:00+08:00",
  "user_request_summary": "R06 阶段汇报：PPT 结构 + WPS AI prompt",
  "context_read": [
    {"path":"memory/identity/project.md","why":"北极星与判据","keys":["north_star","kpi"]},
    {"path":"memory/timeline/stage_reports/R05_20251105.md","why":"承接上次汇报","keys":["key_results","blockers"]},
    {"path":"skills/stage_report_ppt/SKILL.md","why":"执行技能","keys":["output_contract"]}
  ],
  "context_write": [
    {"path":"memory/timeline/stage_reports/R06_20251123.md","op":"create","patch":["topline_story=...","assets_pack=assets/ppt_pack/R06_20251123/"]},
    {"path":"memory/packs/PACK_stage_report_R06_20251123.md","op":"create","patch":["task_refs+=TASK_...","final_assets+=assets/ppt_pack/R06_20251123/"]}
  ],
  "missing": [
    {"field":"figure_paths","ask_user":"请给出本阶段关键图/数据的路径（assets/...）或上传文件。"}
  ],
  "skills_selected": ["stage_report_ppt"],
  "tool_calls": [],
  "artifacts": ["assets/ppt_pack/R06_20251123/"]
}
```

---

## 8. 非目标（v0.1 不做）

- 不做向量数据库/embedding 检索（保持 file-first）
- 不做自动执行破坏性操作（删除/覆盖），只输出 patch 建议或走显式确认
- 不强制用户每天写 6 类细粒度对象（Paper/Claim/…），对外以 Concept/Task/Pack 为主

---

## 9. 你需要实现的最小 MVP（建议）

只做 3 个闭环即可跑起来：

1. **Ingest**：新建 Task（写 Claim + evidence）  
2. **Plan**：生成 Protocol（steps + controls）  
3. **Close**：写 Run（raw_data_paths + verdict）并导出 Pack（阶段汇报或机理包）


