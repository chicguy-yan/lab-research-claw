# BOOTSTRAP 协议设计意图

> 本文档说明 `backend/workspace-templates/BOOTSTRAP.md` 的设计决策，供开发与产品对齐使用。

---

## 1. 定位

BOOTSTRAP.md 是 **workspace 一次性点火协议**，不是常驻控制层文件。

它解决的问题是：当一个全新的 workspace 被创建时，系统没有任何记忆文件，Agent 无法判断用户在研究什么、有哪些约束、最重要的事情是什么。BOOTSTRAP 的唯一职责是引导生成首批最小记忆文件，使系统进入可运行状态。

**一句话定位：只负责点火，不参与后续每轮 prompt 注入。**

---

## 2. 边界

| 事项 | 结论 |
|------|------|
| 何时读取 | 仅在 `PromptBuilder` 检测到 `first_run=True` 时 |
| 是否常驻注入 | 否。初始化完成后不再出现在 system prompt 中 |
| 是否参与 context 预算 | 否。不计入 Layer1/2/3 的 token 配额 |
| 完成后是否删除 | 不强制删除；`PromptBuilder` 跳过即可 |

---

## 3. workspace_init_schema 字段设计理由

### 3.1 `research_topic`
所有后续文件的主题来源。不写死在模板里，而是从 schema 动态生成，使同一套 BOOTSTRAP 协议可适配任何学科和课题。

### 3.2 `priority_loops`（3 个优先验证闭环）
科研用户的核心记忆压力是「当前最需要验证什么」。要求填写 3 个可证伪 claim + 紧迫原因，使系统第一轮就能感知用户的实验优先级，而不是从零开始追问。这 3 个 claim 直接写入 `TASK_bootstrap_initial_questions.md`，成为首批 Layer3 原子资产。

每个闭环条目包含 `allowed_routes` 字段，取值必须从以下 4 个路由名中选择（可多选），与系统 intent router 保持一致：

| 路由名 | 对应场景 |
|--------|----------|
| `mechanism_closure` | 机理证据链验证（探针、淬灭剂、谱学等） |
| `experiment_closure` | 实验数据处理与闭环（数据上传、出图、SOP） |
| `stage_progress` | 阶段汇报与进度推进（PPT、组会、里程碑） |
| `writing_closure` | 论文写作与结构整理（章节、摘要、润色） |

### 3.3 `assets_inventory`
让系统在初始化阶段就知道「用户手头有什么」，为后续 assets 归类和 memory 写入提供索引基础。分为 4 类（pdf / data / image_or_spectra / ppt_or_md）对应实验研究场景的主要文件类型。

### 3.4 `lab_context`
实验室约束是高频上下文，但变化慢。集中写入 `lab_context.md` 后，后续每轮对话无需用户重复说明「我没有同步辐射」「样品命名是这个规则」。

### 3.5 `current_deliverable`
明确当前最重要交付与 deadline，使 `180d_index.md` 的时间轴有真实锚点，而不是填充空洞的模板占位符。

### 3.6 `top_uncertainties`
当前最大不确定性是科研场景中最容易被遗忘、但对 Agent 行为影响最大的信息。写入 `project.md` 后，Agent 在后续每轮对话中都能感知「哪些结论还不稳固」，避免过早给出确定性判断。

---

## 4. 生成文件与 Layer 的对应关系

```
workspace_init_schema
│
├─ research_topic + priority_loops + uncertainties + deliverable
│   └─► memory/identity/project.md          (Layer1)
│
├─ lab_context
│   └─► memory/identity/lab_context.md      (Layer1)
│
├─ [固定模板]
│   └─► memory/identity/context_budget.md   (Layer1)
│
├─ research_topic + deliverable.deadline
│   └─► memory/timeline/180d_index.md       (Layer2)
│
├─ research_topic.title
│   └─► memory/concepts/CONCEPT_<topic>.md  (Layer3)
│
└─ priority_loops[L1, L2, L3]
    └─► memory/tasks/TASK_bootstrap_initial_questions.md  (Layer3)
```

---

## 5. 设计约束

- **File-first**：所有文件通过 `write_file` 工具写入，工具返回成功后才算完成，不允许仅凭描述声称已完成。
- **不硬编码主题**：模板中不出现任何具体科研领域词汇，全部来自用户填写的 schema。
- **不引入复杂交互**：init 阶段只写文件，不触发 skill proposal、RAG、multi-agent 编排。
- **可扩展**：schema 字段可按需增加（如 `collaborators`、`funding_deadline`），不影响现有字段的生成逻辑。

---

## 6. PromptBuilder 集成要点

`PromptBuilder` 在构建 system prompt 时应做以下判断：

```python
if workspace.first_run:
    # 注入 BOOTSTRAP.md 全文，引导 Agent 收集 schema 并生成初始文件
    inject(BOOTSTRAP_MD)
else:
    # 跳过 BOOTSTRAP.md，按正常 Layer1→2→3 顺序注入
    inject(control_plane_files)
    inject(memory_map)
```

`first_run` 标志建议以 `memory/identity/project.md` 是否存在作为判断依据：文件不存在则视为 first-run。
