# Traceable Loop Demo (可追溯闭环 Demo) — Claude Code 直接可读规格

> 目标：把“科研卡住的一句话”变成 **可追溯的三张卡 + 一个可交付成果**。  
> 关键词：**信任（证据链）**、**马上交付**、**本地可改**、**轻量试探**、**简单规则的复杂涌现**。

---

## 0. Demo 的一句话定义（必须不跑偏）

用户随口说一句科研卡点 → 系统问一个 A/B → 生成并落盘三张 Markdown 卡片（Evidence / Task / Result） → 输出一个交付物（默认 SOP 或 PPT 大纲）  
并且：每条建议都严格区分 **事实区 vs 推断区**，推断必须能 **trace 回指证据锚点**。

---

## 1. 这版 Demo 为什么是最优 MVP（原则层，避免工程爆炸）

### 1.1 信任原则（最核心）
- 用户不信任 AI 的根因：看不到 **证据从哪来**、**推断怎么走**、**哪里可以改**。
- 因此系统必须默认输出：
  - 【事实区】只放“用户说的/文件里看到的/计算得到的”
  - 【推断区】只放“解释/原因桶/建议/下一步”
  - 推断后必须带 trace：引用的 evidence id 列表

### 1.2 马上交付原则（今晚少崩溃一次）
- MVP 的价值不是“科研更好”，而是：**今晚组会能讲清楚，明天能直接做**。
- 所以 Demo 必须在 5 分钟内完成一个闭环：
  - 输入一点点乱信息 → 压成结构 → 产出可执行交付物

### 1.3 交互原则（不装读心术）
- 只做一次轻量试探：
  - “你现在更想要：A 直接下一步动作 / B 先想清楚原因再动？”
- 用户不选也行：靠后续行为自动切换（追问 why → explore；追问 steps → ddl）。

### 1.4 工程原则（本地、可复现、可修改）
- 不用数据库、不做向量库、不做复杂多 agent 编排。
- 所有状态写入 `memory/` 下的 Markdown 文件；用户改文件即生效（尤其 prompts）。
- 任何“很酷但会爆炸”的想法，必须先能落到：
  1) 一张卡片上
  2) 一条命令可复现
  3) 能增强信任（否则不做）

---

## 2. Demo 交付清单（Claude Code 必须产出）

### 2.1 CLI 命令（最小集）
- `new "<user_sentence>"`  
  创建一次对话会话，写入初始 Evidence（用户一句话）
- `add-evidence <path_or_text>`  
  添加证据锚点（文件路径/文本）
- `run --deliverable sop|ppt_outline|talk_track|progress_note`  
  触发一次“路由 + 执行”，生成 Task + Result
- `timeline`  
  按时间列出历史 evidence/tasks/results（“旧数据突然能用上”的爽点）

> 说明：CLI 的实现语言不限（Python/Node 均可）。重点是落盘结构与输出格式。

### 2.2 目录结构（必须严格一致）
```
memory/
  index.md
  evidence/
    EVD-YYYYMMDD-XXX.md
  tasks/
    TSK-YYYYMMDD-XXX.md
  results/
    RES-YYYYMMDD-XXX.md
prompts/
  router.md
  worker.md
config.yml
scripts/
  demo1_ddl.jsonl
  demo2_explore.jsonl
  golden_checks.md
```

---

## 3. 三类卡片的 Schema（强约束，才能强信任）

### 3.1 Evidence Card（证据锚点卡）
文件：`memory/evidence/EVD-*.md`
```md
---
id: EVD-YYYYMMDD-XXX
type: evidence
source: user_text | file_path | image_path | table_path
created_at: YYYY-MM-DD
raw_refs:
  - <file-path-1>
  - <file-path-2>
user_sentence: "<用户随口一句原话>"
---
# 原始输入
<尽量原封不动贴用户输入或路径>

# 系统摘要（事实）
- 仅总结可直接从原文/文件看到的事实
- 禁止解释原因（解释应去 Result 的推断区）
```

### 3.2 Task Card（当前任务卡）
文件：`memory/tasks/TSK-*.md`
```md
---
id: TSK-YYYYMMDD-XXX
type: task
mode: ddl | explore
deliverable: sop | ppt_outline | talk_track | progress_note
created_at: YYYY-MM-DD
evidence_ids: [EVD-...]
---
# 目标交付
- <明确输出物>

# 事实区（来自证据/用户原话）
- <每条事实后写 trace:EVD-...>

# 推断区（待验证）
- <用“可能/待确认/需验证”表达，不下定论>

# next_request（最多2条）
- <还缺什么证据/用户下一步只需要补什么>
```

### 3.3 Result Card（交付结果卡）
文件：`memory/results/RES-*.md`
```md
---
id: RES-YYYYMMDD-XXX
type: result
created_at: YYYY-MM-DD
confidence: low | medium | high
trace:
  - statement: "<某条关键结论/建议>"
    evidence: [EVD-...]
assumptions:
  - "<明确写推断前提>"
---
# 交付物正文
<例如 PPT 大纲 / SOP 检查单 / 话术>

# 事实区
- <只放可追溯事实，每条带 trace>

# 推断区
- <建议/原因桶/下一步，每条带 trace 或标记缺证据>

# 检查单（1-3步，带验收标准）
1) 做什么
   - 观察什么
   - 结果分别意味着什么
   - 验收标准（可配置）
```

---

## 4. Router 与 Worker（可编辑 prompt 文件）

### 4.1 `prompts/router.md`（路由器）
必须完成：
- 从用户第一句话提取：
  - deliverable（交付物类型）
  - stuck_point（卡点现象）
- 发起一次轻量试探 A/B 并决定 mode
- 决定下一步需要什么证据（最多 2 条）

### 4.2 `prompts/worker.md`（执行器）
必须完成：
- 读取 memory/ 下相关 evidence/task
- 产出 result：
  - 交付物正文
  - 事实区 vs 推断区
  - 每条推断建议尽量 trace 到 evidence（做不到必须显式标记“缺证据”）
- 输出 confidence 与 assumptions

---

## 5. 用例剧本（真实 user story，作为 Golden Tests）

> 下面两条剧本要写入 `scripts/demo1_ddl.jsonl` 与 `scripts/demo2_explore.jsonl`。  
> JSONL 每行一条事件：`{"role":"user|system","content":"..."}`。  
> 实现时可先不真的跑 LLM，允许用 stub 产出固定结构以验证落盘与格式。

---

### Demo 1：DDL/托管型（今晚组会，马上要 PPT + 明日 SOP）
**用户一句话开场（new）**
- “我今晚组会要汇报 Ce 负载那批材料的进展，但我现在脑子完全乱。之前 10 月做过一批数据放着没整理，现在又觉得结果怪怪的。我怕讲不清会被怼。”

**系统轻量试探（必须出现）**
- “你现在更想要：A 直接给你下一步动作 + PPT 大纲，还是 B 先把原因想清楚再动？”

**用户选择**
- “A。我先活过今晚。”

**系统最少追问（最多2条证据请求）**
- “你说怪怪的具体怪在哪一句话能描述清楚？”
- “先丢一个最有代表性的材料：照片/csv/xlsx/pdf 都行”

**用户给证据（add-evidence）**
- user_sentence: “Ce 加多了以后某个峰反而不稳定，重复性差。”
- path: `/photos/notebook/2025-10-batch.jpg`
- path: `/data/xrd/ce-loading-series.csv`

**系统输出（run --deliverable ppt_outline）**
- 生成：EVD-001、TSK-001、RES-001
- RES 必含：
  - PPT 大纲（10 分钟）
  - “下一步计划”两页（Plan A/Plan B）
  - 明日 SOP 检查单（1-3步，带验收标准）
  - 事实/推断分区 + trace 回指 evidence

---

### Demo 2：认知流动型（被 challenge 到不自信，先要原因桶 + 两步验证）
**用户一句话开场（new）**
- “我最近特别不自信。导师每次都 challenge 我，说我这个现象讲不清楚。我甚至怀疑是不是我根本不会做科研。”

**系统轻量试探**
- “A 直接下一步动作（像 RA 带做） / B 先帮你把原因想清楚再动？”

**用户选择**
- “B。我想知道到底是哪种问题。”

**系统要两句输入（不让用户整理）**
- “现象随口一句”
- “任何一个证据（照片/表格/文献）丢一个就行”

**用户给证据（add-evidence）**
- “DPD 显色漂、重复性很差。”
- `/photos/dpd_color_1.jpg`
- “纸上时间点我没整理，但我记得取样到显色间隔不稳定。”

**系统输出（run --deliverable sop）**
- 必含：
  - 原因桶（3桶，每桶只给一个最小验证动作）
  - 两步验证检查单（桶1优先：操作/时间窗）
  - “对导师可说的话术（证据版）”
  - 事实/推断分区 + trace + assumptions + confidence

---

## 6. Golden Checks（验收标准，写入 scripts/golden_checks.md）

实现完成需满足：

1) **落盘完整**：每次 run 必须生成 1 个 Task + 1 个 Result；Evidence 至少 1 个  
2) **事实/推断分离**：Result 中必须有两个标题区块  
3) **trace 可用**：Result 的关键建议至少 60% 带 evidence 引用；其余必须标记“缺证据”  
4) **用户只回忆**：系统追问不得超过 2 条证据请求（Demo 内）  
5) **timeline 可回放**：timeline 输出能看见历史卡片列表（时间、id、deliverable、简短摘要）  
6) **prompt 可编辑生效**：修改 prompts/router.md 或 prompts/worker.md 后再次 run 有可观察差异（哪怕只是措辞变化）

---

## 7. config.yml（交付物按钮，最小可用）

```yml
deliverables:
  - id: sop
    label: "实验 SOP 草案"
  - id: ppt_outline
    label: "组会 PPT 大纲"
  - id: talk_track
    label: "成果汇报话术"
  - id: progress_note
    label: "进展小短文"
checks:
  max_followup_questions: 2
  confidence_rules:
    high: "证据充足+变量可控"
    medium: "有证据但仍缺关键对照"
    low: "主要靠推断，缺证据"
```

---

## 8. 后续迭代路线（可选，不要在 MVP 里做）

- OCR：只在 Evidence 的 source 扩展（image_path → extracted_text），不要改三卡结构
- Subagent：用 bash/进程隔离直接 spawn 子进程（例如“读 pdf 总结”），主进程只收摘要回写 evidence 或 result  
- 向量库/RAG：等三卡闭环稳定后再加，否则会让“信任链”变模糊

---

## 9. 你写给 Claude Code 的执行提示（直接复制）

> 把下面这段作为 Claude Code 的主任务提示词（可以放在 repo 根目录 README 或 tasks.md）。

```text
实现一个 Traceable Loop Demo（可追溯闭环 demo）CLI。
目标：一句话输入科研卡点 -> 问一个A/B -> 落盘三张Markdown卡（evidence/task/result） -> 输出一个交付物（默认 sop 或 ppt_outline）。
硬约束：
1) 本地优先，不用数据库；所有状态写入 memory/ 目录的md文件
2) 每条建议必须分为【事实区】和【推断区】，并在推断后标注 trace 到 evidence id
3) 三类卡片都有frontmatter，且提供 memory/index.md 索引
4) 提供 timeline 命令按时间列出历史卡片
5) prompts/ 下的 router.md 和 worker.md 必须是可编辑配置（用户改了就生效）
交付：
- 可运行CLI，命令：new, add-evidence, run, timeline
- scripts/ 下提供 demo1_ddl.jsonl 与 demo2_explore.jsonl 两条真实用例剧本
- scripts/golden_checks.md 验收标准
注意：先做最小闭环，不要加入OCR/向量库/复杂多agent编排。
```

---

## 10. 你现在可以怎么用它（无脑操作）

1) 把本文件放进 repo（例如 `SPEC_traceable_loop_demo.md`）  
2) 让 Claude Code 按“执行提示”实现 CLI  
3) 用 demo1/demo2 跑通 golden checks  
4) 跑通后你再决定接不接前端 v0（此时后端是一个稳定黑盒）

