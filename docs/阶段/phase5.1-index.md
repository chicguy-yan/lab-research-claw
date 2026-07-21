# Phase 5 Closed Loops Dev Plan
## 主题：Three Closed Loops + Skills Runtime

## 0. 本 phase 的唯一目标

在同一个科研 workspace 下，优先跑通三个可演示、可迁移的科研闭环：

1. 文献机理闭环（mechanism_closure）
2. 实验证据闭环（experiment_closure）
3. 阶段汇报 / 写作闭环（stage_progress / writing_closure）

本 phase 只负责：
- 让三个闭环各自至少能跑一个真实场景
- 让对应 skill 真正被系统看到、被 Agent 读到、被任务用到
- 让 Prompt 注入链、workspace skill 目录、SKILLS_SNAPSHOT、read_file 读取链路打通

本 phase 不负责：
- TraceWriter 的完整闭环审计升级
- 从 trace 沉淀出新 skill
- UI 细节、初始化引导界面、交互 polish

这些统一放到：
- Phase 6：Trace Audit + Skill Crystallization
- Phase 7：UI / Onboarding / Initialization / Bug Polish

---

## 1. 当前系统边界（必须遵守）

### 1.1 顶层轻路由
只保留：
- stage_progress
- experiment_closure
- mechanism_closure
- writing_closure
- general_consult

route 当前用于：
- metadata
- context selection hint（后续扩展）
- atom_decision hint（后续扩展）
- trace（Phase 6 深化）

route 不用于：
- 后端 skill 匹配
- 后端 skill 排序

### 1.2 Skill Runtime 原则
- 后端只负责加载 registry、生成 SKILLS_SNAPSHOT、同步 system/workspace 两类技能
- PromptBuilder 只注入 Skills Snapshot，不注入完整 SKILL.md
- Agent 根据 snapshot，自主通过 read_file 读取具体 skill
- backend 不做 trigger 硬匹配，不做 route 排序，不自动决定读哪个 skill

### 1.3 Control Plane / Data Plane / Trace Plane
- Control Plane：定义怎么工作
- Data Plane：assets 存原始材料，memory 存 md 化沉淀
- Trace Plane：本 phase 只保留最低限度记录；完整审计升级放 Phase 6

---

## 2. 三个闭环定义

---

## 2.1 闭环 A：文献机理闭环

### route
`mechanism_closure`

### 典型用户问题
- 帮我拆这 5-7 篇 pdf，看看异质结如何促进高价金属/高价钴生成
- 把这些文献和现有机理证据串成阶段汇报
- 给我一版机制证据链 Pack 草图

### 本闭环目标
把一组文献输入组织成：
- 一个或多个 `TASK_mechanism_*`
- 一个 `PACK_mechanism_*` 或 `PACK_stage_report_*`

### 最小必需 assets
- 5-7 篇核心 pdf
- 1 份现有机理推导 md（可选）
- 1 份阶段汇报主题说明（可选）

### 必需 skills
1. `literature_pdf_4block`
   - 将 pdf 拆成：体系设置 / 活性物种证据 / 条件影响 / 对本体系启发
2. `evidence_chain_pack`
   - 将多篇文献收成证据链
3. `mechanism_stage_report`
   - 将文献与结论转成阶段小结或汇报结构

### 依赖模块
- `backend/graph/skill_loader.py`
- `backend/graph/prompt_builder.py`
- `backend/api/chat.py`
- `read_file` tool
- `write_file` tool

### 本闭环 Phase 5 验收
1. Prompt 中能看到完整 Skills Snapshot
2. Agent 至少实际读取 1 个文献类 skill
3. 能产出一个机制相关 Task 草稿或更新已有 Task
4. 能产出一个 Pack 草稿（阶段小结 / 证据链）
5. Trace 至少能看到 Agent 实际读了哪些 skill 文件

---

## 2.2 闭环 B：实验证据闭环

### route
`experiment_closure`

### 典型用户问题
- 这是 csv/xlsx，请帮我出图并判断结果
- 这是 PMSO / EPR / 光谱图，请帮我整理实验原理、SOP、结果摘要和缺失对照
- 把这次实验写成一个可持续更新的 Task

### 本闭环目标
把实验输入组织成：
- `TASK_<experiment_type>_*`
并允许：
- 输出 figures
- 写入 SOP/checklist
- 写入 run_records / derived_outputs / missing_or_next_step

### 最小必需 assets
- 1 份 csv/xlsx
- 1 份实验原理或 SOP md/txt
- 1 张图片或光谱（可选）

### 必需 skills
1. `csv_plot_kobs`
   - 从 csv/xlsx 生成基础曲线和拟合结果
2. `experiment_checklist`
   - 将原理 + SOP + 缺失对照整理成 checklist
3. `spectra_reading_note`
   - 对 EPR / XANES / EXAFS / 其他谱图做基础读图笔记

### 依赖模块
- `backend/graph/skill_loader.py`
- `backend/graph/prompt_builder.py`
- `backend/api/chat.py`
- `python_repl` tool
- `read_file` / `write_file` tool

### 本闭环 Phase 5 验收
1. Prompt 中能看到 Skills Snapshot
2. Agent 至少实际读取 1 个 experiment/figure/spectroscopy 类 skill
3. 能生成一个 figures 文件或 figure 摘要
4. 能把结果写入一个 `TASK_*` 文件
5. Trace 至少能看到 Agent 实际读取了哪些 skill 文件

---

## 2.3 闭环 C：阶段汇报 / 写作闭环

### route
`stage_progress` 或 `writing_closure`

### 典型用户问题
- 把最近两周推进整理成组会 PPT
- 帮我把已有实验与机理证据收成 Results & Discussion 目录
- 把 figures、Task、文献结论映射到页级结构

### 本闭环目标
把已有 Task / 文献 / figures 组织成：
- `PACK_stage_report_*`
- `PACK_writing_*`

### 最小必需 assets
- 1 份旧 PPT 或阶段汇报说明
- 1 份实验安排 / 证据链推导 md
- 已有 Task / figures（可由前两个闭环生成）

### 必需 skills
1. `stage_report_pack`
   - 生成组会 PPT 页级结构
2. `writing_rd_outline`
   - 生成 Results & Discussion 目录树
3. `figure_to_slide_map`
   - 把已有 figures 映射到 PPT 或写作结构

### 依赖模块
- `backend/graph/skill_loader.py`
- `backend/graph/prompt_builder.py`
- `backend/api/chat.py`
- `read_file` / `write_file` tool

### 本闭环 Phase 5 验收
1. Prompt 中能看到 Skills Snapshot
2. Agent 至少实际读取 1 个 ppt/word 类 skill
3. 能产出一个 `PACK_stage_report_*` 或 `PACK_writing_*`
4. Pack 中能引用已有 Task / figures / 文献结论
5. Trace 至少能看到 Agent 实际读取了哪些 skill 文件

---

## 3. Phase 5 必须完成的通用能力

### 3.1 Skills Runtime
必须完成：
- system + workspace 双来源 skills
- workspace `skills/registry.json` 自动初始化
- system skill 同步到 workspace `_system/` 命名空间
- `SKILLS_SNAPSHOT.md` 生成与注入
- Agent 自主 read_file 读取具体 `SKILL.md`

### 3.2 PromptBuilder
必须完成：
- 注入顺序固定为：
  1. Identity
  2. Tooling
  3. Workspace / Metadata
  4. Control Plane
  5. Skills Snapshot
  6. Memory Map
  7. User message
- 不注入完整 `SKILL.md`
- 保持无 snapshot 时向后兼容

### 3.3 Chat API
必须完成：
- `route` 字段进入 `ChatRequest`
- route 至少进入 metadata
- 每轮都能获得 snapshot
- Agent 可在这一轮根据 snapshot 自主读取具体 skill

### 3.4 写入安全
必须完成：
- `workspace/skills/` 可安全写入
- 路径不能逃出 workspace
- workspace 自定义 skill 默认不被 backend 隐式覆盖

---

## 4. 本 phase 不强求完成，但要留接口

### 4.1 Trace 深化（留到 Phase 6）
本 phase 只要求 trace 至少能看到实际读取了哪些 skill 文件。

完整升级留到 Phase 6，再统一补：
- route
- context_read
- asset_refs
- atom_decision
- output_refs
- missing_fields

### 4.2 Trace -> Skill 沉淀（留到 Phase 6）
`research_skill_creator` 可作为 system skill 进入 Phase 5 基础设施，但：
- 不强求本 phase 完整产品化
- 不强求从 trace 自动归纳 skill
- 不强求端到端验证全做完

### 4.3 UI / 初始化引导（留到 Phase 7）
- route selector
- workspace 初始化表单
- skills 菜单 UI
- trace replay 可视化
统一后置。

---

## 5. 三个闭环的开发顺序

建议顺序：

### Step A
先做 **实验证据闭环**
原因：
- 最直观
- 最容易验证 assets -> skill -> Task 链

### Step B
再做 **文献机理闭环**
原因：
- 最能体现科研场景理解和证据链能力

### Step C
最后做 **阶段汇报 / 写作闭环**
原因：
- 依赖前两个闭环的产物最明显
- Pack-first 最适合放在第三步验收

---

## 6. 给 CC 的任务

CC 负责：
1. 审查当前 Skills Runtime 是否已足以支撑三个闭环
2. 检查 registry / snapshot / workspace `_system/` 命名空间设计是否一致
3. 检查 PromptBuilder 的 block 顺序是否和冻结规范一致
4. 检查 Phase 5 / 6 / 7 边界是否清晰
5. 为每个闭环给出最小场景、最小 skill 集、风险点

CC 不负责：
- 大范围随意重写代码
- 把 Phase 6 的 trace / skill crystallization 提前塞进 Phase 5

---

## 7. 给 Codex 的任务

Codex 负责：
1. 按文件级清单落地 Skills Runtime
2. 跑 `phase5-dev-plan` 中已有测试，并补闭环相关测试
3. 为三个闭环分别补最小 smoke test / fixture
4. 确保：
   - snapshot 注入成功
   - Agent 可实际读取 skill
   - workspace skill 可见
   - system/workspace 双来源可共存

Codex 不负责：
- 发明新的架构层
- 把 route 写成 skill 硬匹配器
- 提前实现 Phase 6 的 trace -> skill 自动沉淀

---

## 8. 本 phase 的最终完成标准

Phase 5 通过，不看“实现了多少高级想法”，只看：

1. 三个闭环是否各自至少跑通一个真实场景
2. 每个闭环是否至少真实使用了一个对应 skill
3. PromptBuilder / snapshot / read_file / workspace skills 链路是否打通
4. system/workspace 双来源 skills 是否共存
5. trace 是否至少能看到 Agent 实际读取了哪些 skill 文件

如果以上 5 条成立，则 Phase 5 完成。