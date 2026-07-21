# 自动化评测系统设计 PRD

## 0. 文档信息
- 文档名称：`eval_system_design_prd.md`
- 面向对象：Benchmark 设计者、模型开发者、后端工程师、Codex 实现者
- 目标版本：v1（HTTP 优先、零侵入 / 低侵入）
- 适用范围：材料科研智能体全生命周期闭环评测，覆盖 B/C/D/E 四类场景

---

## 1. 背景与问题定义

当前材料科研智能体已经具备完整的 workspace / session / chat / files / assets / trace 能力，且前端能浏览真实工作区、会话历史与 `memory/*` 文件。但是，现有系统还缺少一套**与业务后端解耦**的、可自动运行的闭环评测系统，导致下面几个问题长期存在：

1. 评测仍偏人工，难以稳定复现。
2. 只能看最终回答，难以系统检查 trace、artifact、source-layer honesty、binary grounding 等关键能力。
3. 长时评测（单次运行 1 小时左右）缺少清晰的实时进度可视化，执行者无法知道当前卡在哪个 session / turn / tool。
4. 虽然 backend 已经能保存真实会话，但缺少统一的 run 级结果视图、评分结果、hallucination 子指标、失败样例归档。
5. 每个闭环场景（literature / experiment / writing / bridge）评测逻辑都不一样，缺少统一的插件基类与加载机制。

本 PRD 要解决的问题是：**设计一套自动化评测系统，在尽量不改动既有 backend 代码的前提下，通过 HTTP API（主路径）或类实例化（可选路径）驱动真实 workspace，执行 B/C/D/E 四类全生命周期场景，对每个 turn 进行规则评测、trace 评测、artifact 评测与 LLM-judge 评测，并把结果实时展示在终端，同时可在前端稍后查看。**

---

## 2. 产品目标

### 2.1 总目标
在现有后端之外新增一层“评测编排与评分系统”，实现以下四件事：

- **像真实用户一样发起问题**：真实创建 workspace、真实上传文件、真实创建 session、真实通过 `/api/chat` 获得回复。
- **像评审专家一样打分**：对每个 turn 执行规则检查、trace 检查、artifact 检查、LLM-judge 检查，并汇总成 session / scenario / run 级分数。
- **像运维面板一样实时展示**：在终端实时显示当前 run、session、turn、SSE token/tool 流、阶段耗时、临时分数、错误信息与 checkpoint。
- **像普通用户一样事后回看**：让真实会话保留在前端；同时把 run 级总结写入 `memory/packs/`，保证用户稍后可以在前端直接打开查看。

### 2.2 成功标准
v1 达成下面这些条件即视为产品成功：

1. 支持 4 个场景、40 个 session、120 个 turn、不少于 360 条评分细则。
2. 评测系统主路径不要求修改 backend 代码。
3. 运行中可实时看到进度、tool 调用、阶段耗时、已完成 / 待完成评测项。
4. 每个 scenario 结束后能自动产出 summary markdown；整个 run 结束后能产出 run index / scoreboard。
5. 支持断点恢复：至少按“已完成 turn”粒度恢复。
6. 支持 scenario 插件化：不同场景能挂接自己的问题集、prompt、评分规则、artifact 检查逻辑。
7. 输出 hallucination 子指标，不只给一个平均分。

---

## 3. 非目标

本期明确不做以下事情：

- 不重构既有 agent graph / prompt / tool 实现。
- 不要求在 backend 内部新增专用 evaluator 路由。
- 不要求前端新增复杂的评测大盘页面；v1 只要求“真实 workspace 可看”与 “summary markdown 可看”。
- 不追求全自动判定所有科研正确性；允许部分复杂问题使用 LLM-judge + 审慎 prompt 的组合。
- 不在本期解决跨模型并行对比、A/B dashboard、长期趋势 BI 等二期能力。

---

## 4. 目标用户与核心使用场景

### 4.1 用户角色

| 角色 | 主要诉求 |
|---|---|
| Benchmark 设计者 | 能快速定义新场景、新问题集、新评分规则 |
| 模型开发者 | 能看到某次 run 究竟输在哪个 turn、哪类 hallucination 指标掉分 |
| 后端工程师 | 希望评测系统尽量解耦，不侵入既有服务逻辑 |
| 研究负责人 / 业务 owner | 希望像看真实用户会话一样回放 benchmark，并看到结构化评分结论 |

### 4.2 核心使用场景

#### 场景 A：启动一次完整 benchmark
用户执行 `eval run`，系统自动跑完 B/C/D/E 四个 scenario，期间终端实时展示当前 session / turn / token / tool / score，结束后输出 JSON、Markdown、HTML 报告，并把 summary 写回真实 workspace。

#### 场景 B：只跑某一个 scenario
用户只想看 experiment closure 的效果，于是指定 `scenario_C`。系统只创建 C 对应 workspace，执行 10 个 session、30 个 turn，并输出专门的 scenario 结果。

#### 场景 C：中断后恢复
运行到第 63 个 turn 机器断开。用户重新执行 `eval run --resume <run_id>`，系统从最近 checkpoint 继续，不重复已完成的 turn。

#### 场景 D：在前端复盘
评测结束后，用户进入前端 workspace 列表，可以像普通用户一样打开 `[EVAL][B]...`、`[EVAL][C]...` 等 workspace，查看真实 session 历史；同时在 `memory/packs/` 下打开 `EVAL_RUN_..._SUMMARY.md` 等 summary 文件。

---

## 5. 核心设计原则

### 5.1 HTTP 优先，零侵入主路径
评测系统优先通过现有 HTTP API 运行，而不是改造后端内部 graph。这样可最大限度降低耦合，也更接近真实用户路径。

### 5.2 Session 清空上下文，Workspace 保留记忆
每个新 session 代表清空对话上下文，但同一 scenario 的 session 共享同一个 workspace，因此 `memory/concepts`、`memory/tasks`、`memory/packs` 会成为“长期记忆层”。

### 5.3 评分与业务解耦
评分逻辑、LLM-judge prompt、artifact 规则全部放在 evaluator 侧，通过 scenario plugin 加载，而不是塞进 backend 业务代码。

### 5.4 实时可见优先
由于单次长跑可能持续约一小时，系统必须优先解决“当前在做什么、卡在哪里、目前得分怎样”的可见性问题。终端 TUI 是 v1 的核心产品能力之一。

### 5.5 结果要能回到真实工作区
最终 summary 不只保存在本地 run 目录，也要镜像到真实 workspace 的 `memory/packs/`，确保前端可以稍后查看。

---

## 6. 关键现状与产品机会

基于现有代码，已经有以下基础设施可直接复用：

1. `/api/chat` 已支持 SSE，且有 `token / tool_start / tool_end / done / error` 事件。
2. `/api/workspaces`、`/api/workspaces/{id}/bootstrap/start`、`/api/sessions`、`/api/files`、`/api/assets/upload` 都已可用。
3. `context_trace/{session_id}.json` 会在 turn 完成后落盘，可用于事后 trace 检查。
4. `write_file` 会为 `memory/` 下的文件注入 `source_assets` frontmatter，可用作 artifact 溯源评测点。
5. 前端可以查看 session history、trace panel、`memory/concepts|tasks|packs` 等目录。

这意味着 v1 的评测系统本质上只需要新增一层**编排、评分、报告与可视化**，而不是重做整个后端。

---

## 7. 功能需求

### FR1. Scenario Package Loader
系统必须能加载 scenario 包。每个 scenario 至少包括：

- `{B/C/D/E}_scenario_questions.json`
- `eval_detailed_tad_{B/C/D/E}.md`
- scenario 专属 Python 评分模块（本次交付共 28 个原型文件）

loader 要能识别：

- scenario 级元信息
- session 列表
- turn 列表
- user_upload 清单
- route / bootstrap 语义
- expected_artifacts
- key_terms / forbidden_terms / llm_focus / trace_focus
- binary_grounding_required
- 是否需要 prior workspace memory

### FR2. Workspace Orchestrator
系统必须为每个 scenario 创建独立 workspace，并驱动完整生命周期：

1. 创建 workspace
2. 启动 bootstrap
3. 依次执行 10 个 session
4. 每个 session 新建真实会话
5. 每个 turn 上传文件 / 复用 cached asset metadata
6. 调用 chat 获得回复
7. turn 完成后读取 history / trace / artifact
8. 打分并写 run store
9. 结束后写 scenario summary pack

### FR3. Asset Upload & Reuse
系统必须支持两种模式：

- **声明式上传**：按 scenario JSON 中的 `user_upload` 列表逐 turn 上传
- **缓存复用**：如果同一 workspace 内同一文件已上传过，可直接复用 `saved_path` / `quick_summary`，减少重复 I/O

但无论采用何种优化，都必须满足：**scenario 中列出的所有源文件至少被 upload 一次**。

### FR4. Turn Executor
turn 执行器必须支持：

- route=bootstrap 与 route=default 的切换
- SSE 流式消费
- 实时记录 token / tool_start / tool_end / done / error
- turn 完成后抓取：
  - session history
  - `context_trace/{session_id}.json`
  - expected_artifact 文件
  - 本地 run 级事件日志

### FR5. 实时终端 TUI
这是本产品的强制需求。终端需要实时展示：

- 当前 run/scenario/session/turn
- 已完成/总数
- 当前 SSE token 预览
- 最近 tool 调用（名称、开始/结束、耗时）
- 当前 turn 的 provisional score（规则/trace/artifact/LLM-judge）
- 当前错误、重试、checkpoint
- 各 scenario 的 pass/fail / avg score / hallucination summary

### FR6. 场景插件化评分
系统必须有一个统一的评分基类，例如：

- `ScenarioPluginBase`
- `CriterionSpec`
- `CriterionRunner`
- `TurnEvaluationContext`

不同 scenario 通过子类/插件挂入自己的：

- turn 级规则检查
- trace 检查
- artifact 检查
- LLM-judge prompt
- hallucination 子指标

### FR7. LLM-Judge
系统必须支持 per-turn LLM-judge：

- 至少 1/3 评分项来自 LLM-judge
- 每个场景至少 30 个 LLM-judge 细则
- prompt 必须场景化、专家化、长度充足、输出结构化 JSON
- LLM-judge 可异步并发执行，但 turn 本身仍按会话顺序串行执行

### FR8. 结果归档与报告
系统必须在本地 run store 中保留：

- `run_manifest.json`
- `events.jsonl`
- `turn_results/*.json`
- `scenario_summary.json`
- `overall_summary.json`
- `terminal_replay.html`
- `report.md`

同时还必须镜像到 workspace 中，至少写入：

- `memory/packs/EVAL_RUN_<run_id>_INDEX.md`
- `memory/packs/EVAL_RUN_<run_id>_B_SUMMARY.md`
- `memory/packs/EVAL_RUN_<run_id>_C_SUMMARY.md`
- `memory/packs/EVAL_RUN_<run_id>_D_SUMMARY.md`
- `memory/packs/EVAL_RUN_<run_id>_E_SUMMARY.md`

### FR9. Checkpoint / Resume
系统必须支持：

- 每完成一个 turn 落一次 checkpoint
- 恢复时跳过已完成 turn
- 支持 `--resume <run_id>`
- 支持 `--rerun-turn scenario_B:session_004:turn_2` 这种细粒度重跑（可二期，但接口预留）

### FR10. Hallucination 子指标
除了总分，系统还必须输出多维幻觉指标，例如：

- binary grounding compliance
- source-layer honesty
- unsupported specificity rate
- condition fabrication rate
- version authority integrity
- cross-system / cross-closure transfer safety

这类指标要按 turn、scenario、overall 三层汇总。

---

## 8. 非功能需求

### 8.1 解耦性
主路径不得依赖修改 backend 代码。评测系统应作为独立工程运行。

### 8.2 可恢复性
出现网络抖动、LLM judge 失败、单 turn 报错时，不应导致整次 run 直接报废。

### 8.3 可观察性
所有关键阶段都必须有事件化记录；任何失败都应能定位到 scenario / session / turn / criterion。

### 8.4 可扩展性
以后新增 scenario_F、scenario_G 时，不应改动核心 runner，只新增 scenario 包与插件。

### 8.5 真实度
运行路径尽量贴近真实用户：真实 workspace、真实 assets、真实 session、真实 chat SSE、真实 trace、真实 memory file。

### 8.6 可读性
终端输出和最终 markdown 报告都要可读，不允许只有 raw json。

---

## 9. 关键交互与用户体验要求

### 9.1 命令行入口
建议至少提供三个命令：

- `eval run`
- `eval watch`
- `eval report`

### 9.2 终端面板布局（v1）
建议布局：

1. 顶部：run id / backend url / elapsed / completion
2. 左侧：scenario & session 进度树
3. 中间：当前 turn 的 assistant 流式文本
4. 右侧：最近 tool event + provisional score
5. 底部：errors / warnings / checkpoint / last artifact

### 9.3 前端回看体验
用户无需学习新 UI，直接用既有前端即可：

- 在 workspace 列表里看到 `[EVAL]` 前缀的真实 workspace
- 在 session 列表里看到 10 个真实 session
- 在 trace panel 里看到真实 trace
- 在 `memory/packs/` 里看到 run 级 summary markdown

---

## 10. 验收标准

### 10.1 功能验收
- 能完整运行 B/C/D/E 四个 scenario
- 每个 scenario 有 10 个 session、每个 session 3 个 turn
- 总 turn 数 = 120
- 总评分细则数 >= 360
- 每个 scenario 至少 30 个 LLM-judge 细则
- 每个 scenario 的所有源文件都至少 upload 一次
- 能输出本地 run 报告和 workspace summary pack

### 10.2 技术验收
- 主路径仅依赖既有 HTTP API
- 能在 turn 级 checkpoint 后恢复
- 中途失败不会丢失已完成结果
- 终端 TUI 能看到实时 token/tool/progress
- `memory/packs/` summary 能在前端直接打开

### 10.3 评测质量验收
- 每个 turn 至少 3 条评分细则
- 至少 1/3 评分项为 LLM-judge
- 幻觉指标不少于 5 个大类
- 至少覆盖内容、trace、artifact、hallucination 四个维度

---

## 11. 风险与缓解

### 风险 1：二进制文件 quick_summary 太浅，模型容易“看文件名作答”
**缓解**：在 scenario JSON 中显式标记 `binary_grounding_required`；评分时检查 trace 是否真的调用 `terminal` / `python_repl` 或在回答中诚实声明不确定性。

### 风险 2：LLM-judge 变成新的噪声源
**缓解**：使用结构化 prompt + JSON 输出；对每个 scenario 固定 prompt template；保留 rule-based/trace-based 基线分数。

### 风险 3：长跑中断导致结果丢失
**缓解**：turn 级 checkpoint、事件日志、scenario summary 增量写入、本地 run store + workspace mirror 双写。

### 风险 4：前端 summary 太深看不到
**缓解**：summary 文件固定写在 `memory/packs/` 浅层目录，不写到更深子目录。

### 风险 5：评测逻辑与业务逻辑耦合过高
**缓解**：场景评分代码放在 scenario 包；核心 runner 只认识统一接口，不认识具体科研内容。

---

## 12. 推荐版本切分

### v1
- HTTP runner
- 终端 TUI
- scenario plugin
- run store
- workspace mirror
- checkpoint / resume
- B/C/D/E 四个 scenario 全量跑通

### v1.1
- `eval watch` 独立观测命令
- 更细粒度 rerun
- 场景间对比报告
- 失败 turn 自动聚合

### v2
- web dashboard
- 多模型对比
- 回归趋势分析
- 更丰富的 CI 集成

---

## 13. 最终交付物（本次设计阶段）

本轮设计最终交付：

1. `eval_system_design_prd.md`
2. `eval_system_design_tad.md`
3. `B_questions_and_eval_methods.zip`
4. `C_questions_and_eval_methods.zip`
5. `D_questions_and_eval_methods.zip`
6. `E_questions_and_eval_methods.zip`

其中 4 个 scenario zip 共包含：
- 4 个 scenario questions json
- 4 个 detailed TAD markdown
- 28 个 Python 评测原型模块
- 共 120 个 turn、360 条评分细则

---

## 14. 一句话结论

这套评测系统的产品定位不是“再造一个后端”，而是**在现有 backend 之上增加一层可编排、可评分、可恢复、可回放、可前端查看的 benchmark OS**：它让 B/C/D/E 四条科研闭环都能被稳定、透明、长时可观察地评测。
