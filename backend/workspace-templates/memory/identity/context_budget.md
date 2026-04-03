# Layer1 / context_budget.md — 上下文预算与裁剪策略（File-first）

> 目标：避免单回合把上下文塞爆，同时保持可追溯。  
> 原则：**宁可少读文件，也不要粗暴总结“丢证据”。**

## 1) 默认预算（可按模型能力调整）

- `totalMaxChars`（Project Context 合计）：120_000
- `perFileMaxChars`（单文件）：20_000
- `always_full`：
  - `AGENTS.md`
  - `memory/identity/user.md`
  - `memory/identity/project.md`

## 2) 裁剪规则（推荐）

当文件过长时：
1. 优先保留：标题、字段、表格、结论段、对照/判据段
2. 其余段落可截断尾部，用 `…` 表示
3. 必须在 trace 里记录：`truncated: true` + `kept_sections`

## 3) 摘要落盘（而不是“脑内摘要”）

如果某文件长期过长（比如阶段汇报累计、文献笔记）：
- 生成一个 **摘要文件**（如 `*_summary.md`），并写明：
  - 摘要覆盖范围
  - 原文件路径
  - 摘要生成时间
  - 丢弃了哪些细节（如具体图号）

下次优先注入 summary，再按需注入原文件局部片段。

## 4) “本轮必读” vs “按需读”

- 必读：Layer1（身份与判据）
- 按需：Layer2/3（根据用户请求类型选择）

