# CC Pairing + Debug Logging + Spec Evolution（补丁版工程规范，避免重复）

> 这份文档是 **对你现有两份规格的“增量补丁”**：  
> - `Traceable_Loop_Demo_SPEC_for_ClaudeCode.md`（产品/落盘/用例/验收：主 spec）  
> - `agent_ENGINEERING_SPEC_for_CC.md`（工程原则/目录/边界：工程 spec）  
>
> 这里 **只**定义你刚刚要的三件事：  
> 1) 结对编程流程（cc 怎么和你协作）  
> 2) 细致的 log & debug 日志规范  
> 3) spec 文档如何持续迭代（补丁机制）  
>
> 目标：**减少 cc 上下文压力**，避免把主 spec 全重复塞进对话。

---

## 0) 单一事实源（Source of Truth）

- 产品/行为/用例/验收：看 `Traceable_Loop_Demo_SPEC_for_ClaudeCode.md`
- 工程原则/边界：看 `agent_ENGINEERING_SPEC_for_CC.md`
- **本文件只管协作、日志、spec 演进**，不要写三卡 schema/目录/命令细节（避免重复）。

---

## 1) cc 上下文长度控制（硬规则）

### 1.1 永远“引用文件”，不要“粘贴全文”
当需要 cc 理解某段实现：
- 只给文件路径 + 行号区间
- 用终端命令截取片段，不复制整个文件

**建议命令：**
```bash
# 只展示指定行
sed -n '120,220p' src/core/worker.py

# 搜索关键字，给出行号
rg -n "trace" src/core/worker.py

# 只看差异（最省上下文）
git diff --stat
git diff
```

### 1.2 每次给 cc 的输入限制在“3块内容”
每次发给 cc 的消息最多包含：
1) 本次目标（1-2 句）
2) 涉及文件列表
3) 关键片段

> 其余信息写进 repo 文件（见下节），让 cc 去读文件。

### 1.3 增量状态摘要（让 cc 不靠记忆）
新增一个文件：`docs/STATE.md`（滚动更新）
- 当前实现到哪
- 已通过的 golden checks
- 当前最痛的 bug / TODO
- 最近一次决策（为何这么做）

每次 session 结束，cc 必须更新 `docs/STATE.md`。

---

## 2) 结对编程（Pairing）流程：每次只跑一个“小闭环”

### 2.1 Session 开始（5 行以内）
在 `docs/PAIRING_LOG.md` 追加一条：

```md
## 2026-02-04 16:30
- 目标：让 demo1 跑通 trace>=60%
- 范围：worker.py, schema.py
- 验收：golden_checks #2/#3 通过
```

### 2.2 Session 中（强制“边做边记”）
每完成一个最小改动，立刻记录：
- 改了什么（1 句）
- 为什么（1 句）
- 怎么验证（1 条命令）
- 结果（pass/fail + 关键输出路径）

> 记录位置：`docs/DEVLOG.md`（你面试/复盘会用）。

### 2.3 Session 结束（强制“收口”）
1) 跑一次 `scripts/golden_checks.md` 对应的最小验证  
2) 更新 `docs/STATE.md`  
3) 如果引入了新规则，走 spec 补丁流程（第 4 节）

---

## 3) 日志系统（Logs）：你要的“细致 log + 可 debug”统一标准

### 3.1 目录结构
新增：
```
logs/
  2026-02-04/
    run_demo1.log
    run_demo2.log
    timeline.log
    exception.txt
```

### 3.2 运行日志（每次 run 都必须落盘）
每次执行 `run` 命令：
- 把“输入摘要 + 读了哪些 evidence/task + 写了哪些文件 + 关键决策”写进 log

**最低信息集（必须包含）：**
- timestamp
- command + args
- mode (ddl/explore)
- deliverable
- evidence_ids
- 生成文件路径列表
- trace 覆盖率（例如 8/12 = 66.7%）
- confidence + assumptions 条数

### 3.3 Debug 日志模板（遇到 bug 必须用）
在 `docs/DEBUG_DIARY.md` 追加条目：

```md
## BUG-2026-02-04-01 trace 丢失
- 现象：RES 中推断区没有 trace，golden_check #3 fail
- 复现命令：python src/cli.py run --deliverable ppt_outline
- 期望：推断建议 >=60% 带 evidence 引用；否则标记“缺证据”
- 实际：trace 字段为空列表
- 初步假设：
  1) worker 没把 evidence_ids 传进去
  2) schema 序列化丢字段
- 排查步骤：
  - rg -n "trace" src/core/worker.py
  - sed -n '...' src/core/schema.py
- 结论：xxx
- 修复：xxx
- 验证：运行 demo1；golden_check #3 pass
- 防回归：新增测试/新增日志字段/新增断言（选一）
```

### 3.4 “可追溯调试”的最小断言（建议加）
- 每次写 Result 卡时，若 `trace_coverage < 0.6`，必须在 log 中写：
  - 哪些 statement 没有 trace
  - 是否标了“缺证据”
- 每次出现异常，写 `logs/<date>/exception.txt`（含堆栈）

---

## 4) Spec 演进机制（关键：补丁而不是重写）

你要的是：**不断迭代进最初 spec 文档**，但不让 cc 每次背一大坨上下文。

### 4.1 新增文件：`docs/SPEC_PATCHES.md`
所有 spec 改动先以 patch 形式落在这里，确认有效后再合并回主 spec。

**Patch 模板：**
```md
## PATCH-2026-02-04-01 增加 trace_coverage 日志字段
- 背景：golden_check #3 需要可度量 trace 覆盖
- 变更：
  - logs/run*.log 增加 trace_coverage: x/y
  - worker 在写 RES 前计算覆盖率
- 影响文件：
  - src/core/worker.py
  - src/core/logger.py（如有）
  - docs/golden_checks.md（如需）
- 验收标准：
  - demo1 输出日志包含 trace_coverage
  - demo1 #3 通过
- 回滚方式：删字段不影响三卡 schema
```

### 4.2 合并回主 spec 的规则（避免膨胀）
当某个 patch 连续 2 次 session 都稳定通过（golden checks pass）：
- 把 patch 内容合并进主 spec 的对应章节
- 在主 spec 顶部追加一行 Changelog：
  - `- 2026-02-04 PATCH-... merged: trace_coverage logging`

> 原则：主 spec 只保留“长期稳定的规则”。短期探索全部留在 PATCHES。

### 4.3 spec 变更的“最小差异”要求
- 每个 patch 修改文本尽量 <= 50 行
- 如果超过 50 行，拆成多个 patch（按主题拆：logging / schema / CLI 等）

---

## 5) 给 Claude Code 的“结对执行提示”（尽量短，省上下文）

> 复制给 cc 使用。它会自动按本文件的日志/补丁规范来做。

```text
从现在起按“结对+日志+补丁”规范开发：
- 主 spec 见 Traceable_Loop_Demo_SPEC_for_ClaudeCode.md，工程边界见 agent_ENGINEERING_SPEC_for_CC.md，本次不要重复抄这些内容。
- 你每次只做一个小闭环：改动 -> 运行最小复现 -> 记 DEVLOG -> 更新 STATE。
- 所有运行过程写入 logs/YYYY-MM-DD/*.log；遇到 bug 用 docs/DEBUG_DIARY.md 模板记录。
- 如果发现需要新增/修改规范，先写 docs/SPEC_PATCHES.md 的 PATCH 条目，连续两次通过后再合并回主 spec。
- 注意上下文长度：引用文件路径+行号，不要粘贴长代码；每次消息最多目标/文件列表/关键片段三块。
```

---

## 6) 你要的“细致 log”到底细到哪（边界）

- 细致 ≠ 全量输出。  
- 你要的是：**可复现 + 可定位 + 可归因**。

因此日志重点记录：
- 输入摘要（用户句子、evidence ids）
- 关键决策（mode/deliverable/缺证据处理）
- 输出路径（生成了哪些 md）
- 指标（trace_coverage、confidence）
- 异常（stacktrace）

不需要记录：
- LLM 全量中间思维（会爆上下文，也不利于审计）

---

## 7) 落地清单（你现在就能让 cc 做的 3 件事）

1) 在 repo 新增：`docs/STATE.md`, `docs/PAIRING_LOG.md`, `docs/DEBUG_DIARY.md`, `docs/SPEC_PATCHES.md`, `logs/`  
2) 让 CLI 每次 run 自动写 `logs/YYYY-MM-DD/run_<demo>.log`  
3) 把 `trace_coverage` 作为第一条 patch（最能立刻提升可审计性）

