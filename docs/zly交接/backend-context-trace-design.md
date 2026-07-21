# backend context_trace 设计梳理

> 目的：梳理本项目 `backend/` 中 `context_trace` 的实际实现、设计目标、数据流，以及如何在另一个项目中复用一套类似能力。
>
> 这份文档只基于当前代码库中已经存在的实现，不脑补目标态。

---

## 1. 一句话概括

这个项目里的 `context_trace` 本质上不是一个独立的“日志系统”，而是一个**和会话文件共用存储载体的轻量审计层**：

- `messages` 负责保存会话消息
- `traces` 负责保存本轮真实发生的工具调用轨迹
- 两者共同写入同一个 session envelope 文件：`context_trace/{session_id}.json`

也就是说，它的定位更像：

> **面向 Agent 回合执行的真实工具调用审计，而不是通用业务日志平台。**

---

## 2. 相关代码文件

### 2.1 核心实现文件

- [backend/api/chat.py](../../backend/api/chat.py)
- [backend/graph/agent.py](../../backend/graph/agent.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)
- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)

### 2.2 上下文注入与“真实性约束”文件

- [backend/graph/context_orchestrator.py](../../backend/graph/context_orchestrator.py)
- [backend/graph/prompt_builder.py](../../backend/graph/prompt_builder.py)
- [backend/.openclaw/workspace-default/AGENTS.md](../../backend/.openclaw/workspace-default/AGENTS.md)
- [backend/.openclaw/workspace-default/SOUL.md](../../backend/.openclaw/workspace-default/SOUL.md)
- [backend/.openclaw/workspace-default/USER.md](../../backend/.openclaw/workspace-default/USER.md)
- [backend/.openclaw/workspace-default/BOOTSTRAP.md](../../backend/.openclaw/workspace-default/BOOTSTRAP.md)
- [backend/.openclaw/workspace-default/MEMORY.md](../../backend/.openclaw/workspace-default/MEMORY.md)

### 2.3 约束与验证文件

- [backend/tests/test_chat_write_file_flow.py](../../backend/tests/test_chat_write_file_flow.py)
- [backend/tests/test_system_prompt_contract.py](../../backend/tests/test_system_prompt_contract.py)
- [docs/phase3-4-dev-log.md](../阶段/phase3-4-dev-log.md)
- [docs/trace_collection_fix_log.md](../分析/trace_collection_fix_log.md)

### 2.4 安全边界相关

- [backend/graph/path_utils.py](../../backend/graph/path_utils.py)
- [backend/api/agents.py](../../backend/api/agents.py)
- [backend/config.py](../../backend/config.py)

---

## 3. context_trace 到底解决什么问题

从当前实现看，`context_trace` 主要解决 4 个问题。

### 3.1 让 Agent 的“文件操作声明”可核验

这个项目特别强调：

- 不能把“建议写入”说成“已经写入”
- 不能把 system prompt 预加载说成“我已经读过文件”
- 不能在没有工具证据的情况下声称完成了文件操作

这些约束体现在：

- [backend/graph/prompt_builder.py:90-98](../../backend/graph/prompt_builder.py#L90-L98)
- [backend/.openclaw/workspace-default/AGENTS.md:31-35](../../backend/.openclaw/workspace-default/AGENTS.md#L31-L35)
- [backend/.openclaw/workspace-default/SOUL.md:31-35](../../backend/.openclaw/workspace-default/SOUL.md#L31-L35)
- [backend/.openclaw/workspace-default/USER.md:19-24](../../backend/.openclaw/workspace-default/USER.md#L19-L24)
- [backend/.openclaw/workspace-default/BOOTSTRAP.md:13-15](../../backend/.openclaw/workspace-default/BOOTSTRAP.md#L13-L15)
- [backend/.openclaw/workspace-default/MEMORY.md:9-12](../../backend/.openclaw/workspace-default/MEMORY.md#L9-L12)

所以 `context_trace` 的第一目标不是统计，而是：

> **给“是否真的执行过工具”提供事实依据。**

### 3.2 把工具执行过程沉淀到会话文件中

聊天接口是流式 SSE，工具调用在流过程中发生。如果不落盘，前端只能“看见当下”，无法回放。

`context_trace` 通过把工具事件写进 session 文件中的 `traces[]`，让一次回合执行在结束后可被回看。

见：

- [backend/api/chat.py:68-141](../../backend/api/chat.py#L68-L141)
- [backend/graph/trace_writer.py:23-57](../../backend/graph/trace_writer.py#L23-L57)

### 3.3 兼容“消息上下文”和“审计上下文”共存

这个项目没有把聊天消息和审计日志拆成两个文件，而是统一用 envelope schema：

```json
{
  "messages": [...],
  "traces": [...]
}
```

这样做的好处是：

- 一个 session 只有一个主文件
- 聊天和审计天然绑定
- 前端按 `session_id` 查一次即可获取回合历史和工具轨迹

见：

- [backend/graph/session_manager.py:1-9](../../backend/graph/session_manager.py#L1-L9)
- [backend/graph/session_manager.py:63-87](../../backend/graph/session_manager.py#L63-L87)
- [backend/graph/trace_writer.py:42-57](../../backend/graph/trace_writer.py#L42-L57)

### 3.4 支持并发工具调用的正确配对

这部分是本轮链路里最关键的工程点。

LangChain 流式输出工具调用时：

- tool args 可能被拆成多个 chunk
- 多个工具可能并发调用
- 同名工具也可能并发执行

如果只靠 `tool` 名称配对，会错乱。

因此当前实现改成：

- 在 `agent.py` 中按 `tool_call_id` 聚合 `tool_call_chunks`
- 只有 args 拼成完整 JSON 之后才发出 `tool_start`
- 在 `tool_end` 里显式传回 `tool_call_id`
- 在 `chat.py` 里按 `tool_call_id` 跟踪 active tool calls

见：

- [backend/graph/agent.py:130-183](../../backend/graph/agent.py#L130-L183)
- [backend/graph/agent.py:193-211](../../backend/graph/agent.py#L193-L211)
- [backend/api/chat.py:68-128](../../backend/api/chat.py#L68-L128)
- [docs/trace_collection_fix_log.md:77-192](../分析/trace_collection_fix_log.md#L77-L192)

这说明它不是简单地“记个工具名”，而是在认真处理**事件关联性**。

---

## 4. 当前实现的核心设计

## 4.1 存储模型：session envelope

当前 session 文件路径：

- `context_trace/{session_id}.json`

文件格式：

```json
{
  "messages": [...],
  "traces": [...]
}
```

其中：

- `messages` 由 `SessionManager` 负责
- `traces` 由 `TraceWriter` 负责

关键实现：

- [backend/graph/session_manager.py:63-87](../../backend/graph/session_manager.py#L63-L87)
- [backend/graph/trace_writer.py:42-57](../../backend/graph/trace_writer.py#L42-L57)

### 为什么这样设计

这是一个典型的“最小可用审计设计”：

1. 不引入数据库
2. 不拆多份文件
3. 不额外建立复杂 trace schema
4. 只围绕 session 做闭环

非常适合原型期或单工作区 Agent 系统。

---

## 4.2 TraceWriter 的职责边界很窄

`TraceWriter` 非常克制，只做一件事：

> **把收集好的工具调用列表 append 到 session envelope 的 `traces` 字段中。**

它不负责：

- 解析 SSE
- 识别工具开始/结束
- 推断 read/write 是否成功
- 构造 system prompt
- 维护 session index

见：

- [backend/graph/trace_writer.py:15-57](../../backend/graph/trace_writer.py#L15-L57)

这个拆分很合理，因为：

- `chat.py` 已经拥有完整事件流上下文
- `TraceWriter` 只做持久化，便于复用和测试
- session/messages 与 traces 分工明确，不会互相覆盖

---

## 4.3 chat.py 才是 trace 汇总中心

真正的审计聚合逻辑不在 `TraceWriter`，而在 [backend/api/chat.py](../../backend/api/chat.py)。

它在一次 `/api/chat` 请求里做了这几步：

1. 确保 session 存在
2. 生成 Memory Map
3. 构建 system prompt
4. 加载历史消息
5. 流式消费 Agent 输出
6. 在流式过程中收集工具事件
7. 对话流结束后持久化 messages
8. 再将本轮 tool calls 写入 `traces`
9. 最后发送 `done`

主链路见：

- [backend/api/chat.py:35-155](../../backend/api/chat.py#L35-L155)

### 这个顺序的意义

先流式执行，再落 messages，再落 traces，再发 done，意味着：

- 前端看到的 done 是“本轮数据已完成持久化”后的 done
- `done` 不只是 LLM 停止输出，而是“一轮执行闭环结束”

这在工程上很重要，因为它让前端或其他模块可以把 `done` 当成真正的回合完成信号。

---

## 4.4 agent.py 输出的是“标准化事件”而不是直接写 trace

[backend/graph/agent.py](../../backend/graph/agent.py) 的设计也很关键。

它没有直接操作 trace 文件，而是把底层 LangChain/LangGraph 事件转换成统一格式：

- `token`
- `tool_start`
- `tool_end`
- `new_response`
- `error`

见：

- [backend/graph/agent.py:103-120](../../backend/graph/agent.py#L103-L120)

这层抽象的价值是：

1. 上层 `chat.py` 不需要理解 LangChain chunk 细节
2. trace 收集逻辑可以独立于模型供应商细节
3. 前端 SSE 协议也更稳定

所以这里的实际分层是：

- `agent.py`：底层事件标准化
- `chat.py`：回合级聚合与落盘
- `trace_writer.py`：最终持久化

这是一个很清晰的责任拆分。

---

## 4.5 ContextOrchestrator 和 PromptBuilder 与 trace 的关系

严格来说，`context_trace` 当前**并没有把“本轮读了哪些上下文文件”作为结构化 trace 写进去**。

现状是：

- `ContextOrchestrator` 负责扫描 memory/assets，生成 `memory_map`
- `PromptBuilder` 负责把控制层文件、memory map、metadata 注入 system prompt
- 它们对 Agent 的行为形成“约束”和“导航”
- 但它们自己并没有把“注入了什么上下文”落成专门的 trace 结构

见：

- [backend/graph/context_orchestrator.py:20-47](../../backend/graph/context_orchestrator.py#L20-L47)
- [backend/graph/prompt_builder.py:24-59](../../backend/graph/prompt_builder.py#L24-L59)

所以当前 `context_trace` 名字虽然叫 context trace，实际上更准确地说是：

> **tool execution trace，外加一套强约束 prompt 体系。**

它还没有完整做到目标态 TAD 里说的 `context_read plan` / `budget_report` / patch 审计。

见目标态描述：

- [docs/experimental-research-openclaw-TAD.md:236-260](../架构/experimental-research-openclaw-TAD.md#L236-L260)

---

## 5. 端到端数据流

下面按一次 `/api/chat` 请求来讲。

### Step 1：创建/确认 session

`chat.py` 先确保 session 存在：

- [backend/api/chat.py:41-45](../../backend/api/chat.py#L41-L45)

底层会创建：

- `context_trace/{session_id}.json`
- `_sessions_index.json`

见：

- [backend/graph/session_manager.py:100-117](../../backend/graph/session_manager.py#L100-L117)

### Step 2：生成上下文导航信息

`ContextOrchestrator.generate_memory_map(message)` 生成：

- `layer1`
- `layer2`
- `layer3`
- `assets`
- `recommended`

见：

- [backend/graph/context_orchestrator.py:20-47](../../backend/graph/context_orchestrator.py#L20-L47)

### Step 3：构建 system prompt

`PromptBuilder.build()` 注入：

- 工具说明
- workspace 规则
- execution contract
- metadata
- 控制层文件内容
- memory map

见：

- [backend/graph/prompt_builder.py:24-59](../../backend/graph/prompt_builder.py#L24-L59)

### Step 4：Agent 开始流式执行

`AgentManager.astream()` 用统一格式输出事件：

- token
- tool_start
- tool_end
- new_response
- error

见：

- [backend/graph/agent.py:103-218](../../backend/graph/agent.py#L103-L218)

### Step 5：chat.py 收集 tool events

`chat.py` 维护：

- `tool_calls = []`
- `active_tool_calls = {}`

规则：

- 收到 `tool_start`：登记 running 状态
- 收到 `tool_end`：按 `tool_call_id` 配对并补上 result
- 配对成功后 append 到 `tool_calls`

见：

- [backend/api/chat.py:68-128](../../backend/api/chat.py#L68-L128)

### Step 6：落消息

Agent 流结束后：

- 保存 user message
- 保存 assistant 聚合文本

见：

- [backend/api/chat.py:133-136](../../backend/api/chat.py#L133-L136)
- [backend/graph/session_manager.py:173-187](../../backend/graph/session_manager.py#L173-L187)

### Step 7：落 trace

如果本轮产生了工具调用：

- `TraceWriter.write_trace(session_id, tool_calls)`

见：

- [backend/api/chat.py:138-141](../../backend/api/chat.py#L138-L141)
- [backend/graph/trace_writer.py:23-57](../../backend/graph/trace_writer.py#L23-L57)

### Step 8：发送 done

最后才发：

- `event: done`

见：

- [backend/api/chat.py:143-145](../../backend/api/chat.py#L143-L145)

---

## 6. 当前 trace 数据长什么样

根据当前代码，单条 trace 大致长这样：

```json
{
  "tool_call_id": "call_abc123",
  "tool": "write_file",
  "args": {
    "path": "memory/concepts/hello.md",
    "content": "# hello\n"
  },
  "timestamp": "2026-03-10T10:00:15.123456",
  "status": "completed",
  "result": "File written successfully: memory/concepts/hello.md"
}
```

字段来源：

- `tool_call_id/tool/args/timestamp/status` 来自 [backend/api/chat.py:82-98](../../backend/api/chat.py#L82-L98)
- `result` 在收到 `tool_end` 时补齐，见 [backend/api/chat.py:93-99](../../backend/api/chat.py#L93-L99)

兼容态还支持：

- `completed_unmatched`

用于兜底老事件格式或异常配对失败。

见：

- [backend/api/chat.py:100-128](../../backend/api/chat.py#L100-L128)

---

## 7. 这个设计里最值得复用的点

如果你要在另一个项目里实现类似能力，我认为最值得照搬的不是目录名，而是下面 6 个设计点。

## 7.1 “审计事实”来自工具事件，不来自模型文本

这是当前实现最核心的原则。

测试已经明确验证：

- 真正发生 `write_file` 工具调用时，文件会创建，trace 会记录
- 如果模型只是在文本里说“已写 xxx”，但没有真实工具调用，则既不会创建文件，也不会写 trace

见：

- [backend/tests/test_chat_write_file_flow.py:86-119](../../backend/tests/test_chat_write_file_flow.py#L86-L119)

这意味着：

> **系统把“行为真实性”建立在工具回调上，而不是建立在 LLM 文本自述上。**

这点非常适合迁移。

---

## 7.2 事件标准化层和落盘层分离

`agent.py` 不写文件，`trace_writer.py` 不解析 chunk。

这个分层会让你在换模型框架时更轻松：

- 你可以替换 LangChain → 其他 Agent runtime
- 只要还能产出统一事件，就不用重写上层 trace 汇总逻辑

建议在新项目中保留三层：

1. runtime adapter：把底层模型/工具事件转成统一 event
2. round collector：按回合聚合事件
3. trace store：统一落盘/落库

---

## 7.3 用 `tool_call_id` 做主键，而不是工具名

这个点在并发时很关键。

如果你以后接入：

- 并发读多个文件
- 并发调用多个检索器
- 同时两次 `write_file`

只按 `tool` 名称配对一定会乱。

当前实现已经给了可复用范式：

- `agent.py` 聚合 `tool_call_chunks`
- `chat.py` 用 `active_tool_calls[tool_call_id]`

这部分强烈建议直接复用。

---

## 7.4 session envelope 很适合 MVP

如果你的另一个项目现在还没到要上数据库审计表的阶段，当前这个 envelope 模型很省事：

```json
{
  "messages": [...],
  "traces": [...]
}
```

优点：

- 单文件闭环
- debug 方便
- 前端读取简单
- 不需要联表

缺点：

- 文件会持续增长
- 不适合复杂检索/聚合统计
- traces 和 messages 的生命周期被绑在一起

所以适合：

- 单用户/小团队 Agent 系统
- 本地工作区型应用
- 原型期产品

---

## 7.5 system prompt 里显式写“真实性契约”非常有用

这个项目没有只靠后端兜底，它还在 prompt 层面反复声明：

- 只有真实调用 `read_file` 才能说“已读”
- 只有真实调用 `write_file` 才能说“已写”
- 没有工具调用时不能伪造 context trace / memory patch

见：

- [backend/graph/prompt_builder.py:90-98](../../backend/graph/prompt_builder.py#L90-L98)
- [backend/tests/test_system_prompt_contract.py:17-50](../../backend/tests/test_system_prompt_contract.py#L17-L50)

这相当于：

- 后端做事实校验
- prompt 做行为引导
- 测试做契约防回退

这是一个很完整的组合。

---

## 7.6 测试不是测“模型聪不聪明”，而是测“系统有没有被胡说骗过”

这点我也建议在新项目里复制。

当前测试思路非常对：

- 用 fake agent 模拟真实工具调用
- 用 fake hallucinating agent 模拟“嘴上说做了，实际没做”
- 验证系统最终只信工具事件

见：

- [backend/tests/test_chat_write_file_flow.py:42-75](../../backend/tests/test_chat_write_file_flow.py#L42-L75)
- [backend/tests/test_chat_write_file_flow.py:86-119](../../backend/tests/test_chat_write_file_flow.py#L86-L119)

这类测试对 Agent 系统非常重要。

---

## 8. 当前实现的不足与边界

如果你要迁移，下面这些地方要注意，它们是现状里的“边界”，不是 bug 就是未完成目标态。

## 8.1 它现在主要记录的是工具调用，不是真正完整的 context trace

名字叫 `context_trace`，但当前实际落盘内容主要是：

- tool name
- args
- result
- timestamp
- status

它没有结构化记录：

- 本轮 system prompt 注入了哪些控制层文件
- 推荐了哪些 memory files
- 实际读取了哪些上下文文件
- 为什么选择这些上下文
- token budget / truncation report

所以如果你另一个项目想做真正的“上下文审计”，需要额外补：

- `context_injected[]`
- `context_read[]`
- `selection_reason`
- `budget_report`

---

## 8.2 当前没有显式 failed / cancelled 生命周期闭环

在现有代码里，主状态是：

- `running`
- `completed`
- `completed_unmatched`

但没有完整处理：

- tool 抛错
- tool 超时
- stream 中断
- active_tool_calls 残留清理

这一点在修正日志里也提到了“后续补充错误处理”。

见：

- [docs/trace_collection_fix_log.md:236-260](../分析/trace_collection_fix_log.md#L236-L260)

如果迁移，建议至少补充：

- `failed`
- `cancelled`
- `orphaned_start`
- `orphaned_end`

---

## 8.3 write_file_tool 当前实现和日志描述存在偏差

从 [docs/phase3-4-dev-log.md](../阶段/phase3-4-dev-log.md) 的记录看，`write_file_tool` 设计目标包括路径安全检查；
但当前 [backend/tools/write_file_tool.py](../../backend/tools/write_file_tool.py) 的实现实际上只是：

- 相对路径拼到 workspace 下
- 自动创建父目录
- 直接写入

并没有调用 `resolve_safe_path()`。

而安全工具本身是存在的：

- [backend/graph/path_utils.py](../../backend/graph/path_utils.py#L23-L63)

所以从“迁移参考”的角度，你应该以 **path_utils 的安全边界设计** 为准，而不是完全照搬当前 `write_file_tool.py`。

---

## 8.4 metadata 目前是硬编码/半硬编码

在 [backend/api/chat.py:54-59](../../backend/api/chat.py#L54-L59) 中：

- `platform` 被写死为 `darwin`
- `timezone`、`language` 也是固定值

这对 trace 体系影响不大，但说明当前更偏原型。

如果你要迁移到另一个项目，可以把这些 metadata 真实化，并考虑也写入 trace 或 round summary。

---

## 8.5 TraceWriter 是 append-only，没有回合级摘要

当前 `traces[]` 是平铺的工具调用列表，没有 round-level summary，例如：

- 本轮总共调用了几个工具
- 哪些 read 成功 / write 成功
- 最终是否有文件变更
- 本轮缺口是什么

如果你另一个项目更偏“工作流审计”，建议在 `traces[]` 外再补一个 round summary，例如：

```json
{
  "round_id": "r_001",
  "user_message": "...",
  "assistant_summary": "...",
  "context_read": [...],
  "tool_calls": [...],
  "outputs": [...],
  "status": "completed"
}
```

---

## 9. 迁移到另一个项目时，我建议的最小实现方案

如果你想在另一个项目快速实现“类似功能”，我建议不要一次做成大而全，而是按下面最小闭环来。

## 9.1 第一步：保留三层职责拆分

### A. Runtime Event Adapter

负责把底层 Agent/LLM 框架事件统一成：

- `token`
- `tool_start`
- `tool_end`
- `error`
- `done`

要求：

- 每个工具调用必须尽可能拿到 `tool_call_id`
- 参数不完整时不要过早发 `tool_start`

### B. Round Collector

负责在一次请求中聚合：

- assistant text
- active_tool_calls
- completed_tool_calls
- optional: context_read / recommended_files / patch plan

### C. Trace Store

负责最终持久化。

你可以继续用当前项目这种 envelope 结构，或者落数据库。

---

## 9.2 第二步：先只审计“真实工具行为”

建议先做这 4 个字段：

- `tool_call_id`
- `tool`
- `args`
- `result`
- `timestamp`
- `status`

不要一上来就做复杂 context budget / patch graph。

因为当前项目里最稳定、最有价值的部分，就是这条“真实工具行为审计链”。

---

## 9.3 第三步：再补“上下文注入审计”

当你最小链路跑通后，再考虑增加：

- `preloaded_files[]`
- `recommended_files[]`
- `actually_read_files[]`
- `selection_reason[]`
- `budget_report`

也就是说，把现在这个项目里“ContextOrchestrator + PromptBuilder”的隐式上下文选择，升级成显式 trace 数据。

---

## 9.4 第四步：测试一定要包含“模型胡说但系统不认”

建议你在另一个项目里至少写两类测试：

1. **真实工具调用测试**
   - 确认 trace 里有记录
   - 确认文件/副作用真实存在

2. **纯文本幻觉测试**
   - 模型声称“已写/已读”
   - 但没有工具事件
   - 系统最终不能把它算成完成

这是 Agent 产品里非常值钱的一层防线。

---

## 10. 我对这个设计的总体评价

如果只评价当前代码里已经落地的部分，我会这样看：

### 优点

1. **设计目标明确**：重点不是复杂 observability，而是“真实性审计”
2. **实现轻量**：文件存储、单 session envelope、无额外基础设施
3. **责任拆分清晰**：agent 产事件，chat 聚合，trace_writer 落盘
4. **并发工具调用处理到位**：`tool_call_id` 聚合是关键亮点
5. **测试思路正确**：系统只相信工具证据，不相信模型自述
6. **Prompt 契约 + 后端审计 + 测试回归** 三层闭环完整

### 不足

1. `context_trace` 这个名字比实际能力更大，当前更像 `tool_trace`
2. 还没有真正结构化记录 context selection / budget / patch
3. 工具失败和异常回收状态还不完整
4. 个别实现和文档存在偏差（如 write_file 的安全检查）

### 结论

如果你的另一个项目也需要：

- 防止 Agent 胡说“已执行”
- 回放每轮工具调用
- 给文件读写类 Agent 增加可核验性

那这套设计是很值得迁移的，而且迁移成本不高。

最推荐你复用的是：

- **统一工具事件协议**
- **按 `tool_call_id` 的回合级聚合**
- **session envelope 落盘**
- **真实性 prompt contract + 幻觉防御测试**

---

## 11. 可直接复用到另一个项目的简版设计图

```text
User Request
   ↓
Chat API
   ├─ ensure session
   ├─ build prompt / inject context
   ├─ call Agent runtime
   ↓
Agent runtime stream
   ├─ token
   ├─ tool_start(tool_call_id, tool, args)
   └─ tool_end(tool_call_id, tool, output)
   ↓
Round Collector
   ├─ collect assistant_text
   ├─ active_tool_calls[tool_call_id]
   └─ completed_tool_calls[]
   ↓
Persistence
   ├─ save messages
   └─ append traces
   ↓
Done
```

如果要升级成更完整的 workflow audit，可以扩展成：

```text
Round Audit
   ├─ context_injected[]
   ├─ context_read[]
   ├─ tool_calls[]
   ├─ outputs[]
   ├─ memory_patch[]
   └─ round_status
```

---

## 12. 这份文档对应的代码依据

为了后续你在另一个项目里复刻时方便回看，关键依据文件再列一次：

- [backend/api/chat.py](../../backend/api/chat.py)
- [backend/graph/agent.py](../../backend/graph/agent.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)
- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)
- [backend/graph/context_orchestrator.py](../../backend/graph/context_orchestrator.py)
- [backend/graph/prompt_builder.py](../../backend/graph/prompt_builder.py)
- [backend/tests/test_chat_write_file_flow.py](../../backend/tests/test_chat_write_file_flow.py)
- [backend/tests/test_system_prompt_contract.py](../../backend/tests/test_system_prompt_contract.py)
- [docs/trace_collection_fix_log.md](../分析/trace_collection_fix_log.md)
- [docs/phase3-4-dev-log.md](../阶段/phase3-4-dev-log.md)

---

## 13. 后续如果你要我继续做

我可以继续帮你两种方向：

1. **按你另一个项目的技术栈，直接给你出一版可落地的 context_trace 设计稿**
   - 比如 FastAPI / Node.js / NestJS / Django / Go 都可以

2. **直接在这个仓库里继续补一版“更完整的 workflow audit schema” 设计文档**
   - 把当前的 tool trace 升级成 round audit / context audit / memory patch audit
