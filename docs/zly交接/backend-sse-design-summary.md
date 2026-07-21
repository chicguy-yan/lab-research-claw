# 当前项目 SSE 设计总结

> 目的：总结当前项目里 `/api/chat` 的 SSE 设计是如何完成的，重点说明：
> 1. 后端如何主动把“模型现在调用了什么 tool”实时推给前端
> 2. 为什么前端能在流式过程中看到这些信息，而不是等整轮结束
> 3. 当前实现里哪些是已经落地的，哪些还是 PRD/TAD 里的目标态

---

## 1. 一句话结论

当前项目已经把 **SSE 作为对话主通道** 落地在后端 `/api/chat` 上，并且不是只推文本 token，而是推一组**标准化的执行事件**：

- `token`
- `tool_start`
- `tool_end`
- `new_response`
- `error`
- `done`

其中最关键的是：

> **后端会在 Agent 真实开始调用工具时立刻发 `tool_start`，工具执行完再发 `tool_end`，所以前端可以实时看到“模型现在在调用什么 tool、参数是什么、返回了什么”。**

这正是当前这套 SSE 设计最有价值的地方：**不仅流文本，还流执行过程。**

---

## 2. 这套设计在 PRD / TAD 里的定位

### 2.1 PRD 的要求

PRD 明确把系统定位为“透明可控”，要求：

- 工具调用要可回放
- 记忆读写与缺口追问要可追溯
- 不能做黑盒 Agent

参考：

- [experimental-research-openclaw-PRD.md:16-18](../架构/experimental-research-openclaw-PRD.md#L16-L18)
- [experimental-research-openclaw-PRD.md:199-205](../架构/experimental-research-openclaw-PRD.md#L199-L205)

### 2.2 TAD 的要求

TAD 明确写了后端技术栈是：

- FastAPI
- 异步 HTTP
- SSE 流式推送

并且在 `graph/agent.py` 这一层，把“流式事件序列”定义成：

- `token`
- `tool_start`
- `tool_end`
- `new_response`
- `done`

参考：

- [experimental-research-openclaw-TAD.md:35](../架构/experimental-research-openclaw-TAD.md#L35)
- [experimental-research-openclaw-TAD.md:207-217](../架构/experimental-research-openclaw-TAD.md#L207-L217)

也就是说，**“把工具调用过程一起流给前端”并不是额外补丁，而是这套架构从设计上就想实现的核心能力。**

---

## 3. 当前实际代码里，SSE 是怎么跑起来的

当前真实落地链路可以概括成：

```text
前端 sendMessage()
  -> POST /api/chat
  -> FastAPI StreamingResponse(text/event-stream)
  -> chat.py 的 async generator 持续 yield 事件
  -> AgentManager.astream() 把 LangChain/LangGraph 流转换成标准事件
  -> 前端 fetch + ReadableStream 逐行解析 SSE
  -> 实时渲染 token / tool_start / tool_end
  -> 回合结束后后端落盘 messages + traces
  -> 最后发送 done
```

关键文件：

- [backend/api/chat.py](../../backend/api/chat.py)
- [backend/graph/agent.py](../../backend/graph/agent.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)
- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)
- [frontend/index.html](../../frontend/index.html)

---

## 4. 后端核心：`/api/chat` 用 `StreamingResponse` 持续推事件

SSE 入口在：

- [backend/api/chat.py:35-155](../../backend/api/chat.py#L35-L155)

这里的关键点有 3 个。

### 4.1 使用 `StreamingResponse`

后端返回：

- `media_type="text/event-stream"`
- `Cache-Control: no-cache`
- `Connection: keep-alive`
- `X-Accel-Buffering: no`

对应代码：

- [backend/api/chat.py:147-154](../../backend/api/chat.py#L147-L154)

这说明后端不是等所有内容生成完再一次性返回，而是保持连接，边生成边发。

### 4.2 用 `async def event_generator()` 作为事件源

`chat.py` 内部定义了一个异步生成器 `event_generator()`，在里面：

1. 生成本轮 Memory Map
2. 构建 system prompt
3. 读取历史消息
4. 调用 `am.astream(...)`
5. 一边收到事件，一边立刻 `yield` 成 SSE 格式

关键代码：

- [backend/api/chat.py:47-73](../../backend/api/chat.py#L47-L73)
- [backend/api/chat.py:130-145](../../backend/api/chat.py#L130-L145)

SSE 输出格式就是标准文本：

```text
event: token
data: {"content": "..."}

```

对应代码：

- [backend/api/chat.py:130-131](../../backend/api/chat.py#L130-L131)

### 4.3 `done` 不是模型结束时发，而是“持久化完成后”发

当前实现里，`done` 不是 `AgentManager` 发的，而是 `chat.py` 在以下动作都完成后再发：

1. agent stream 完成
2. `messages` 写入 session 文件
3. `traces` 写入 session 文件

对应：

- [backend/api/chat.py:133-145](../../backend/api/chat.py#L133-L145)
- [backend/graph/agent.py:4-5](../../backend/graph/agent.py#L4-L5)

这意味着：

> 前端拿到 `done` 时，可以把它理解成“这一轮不仅输出完了，而且会话和审计也已经落盘完毕”。

这个设计对前端很友好，因为 `done` 是一个真正的“闭环完成信号”。

---

## 5. AgentManager 做的事：把底层 LangChain 流转成统一事件

真正把“模型流”和“工具流”转成前端可消费事件的核心在：

- [backend/graph/agent.py:103-217](../../backend/graph/agent.py#L103-L217)

它并不直接操作前端，也不直接写 trace，而是负责做一层**事件标准化**。

### 5.1 它输出哪些事件

`AgentManager.astream()` 当前只输出：

- `token`
- `tool_start`
- `tool_end`
- `new_response`
- `error`

定义见：

- [backend/graph/agent.py:109-120](../../backend/graph/agent.py#L109-L120)

这层抽象很重要，因为这样前端不需要理解 LangChain 的内部 chunk 格式，只需要理解项目自己的统一事件协议。

### 5.2 `token`：文本流

当 LangChain 返回普通文本 chunk 时，后端立即发：

```json
{
  "event": "token",
  "data": {"content": "..."}
}
```

对应代码：

- [backend/graph/agent.py:184-191](../../backend/graph/agent.py#L184-L191)

### 5.3 `tool_start`：工具开始时立刻通知前端

这是本项目 SSE 设计的关键。

当模型在流式输出中产生 tool call 时，`agent.py` 不会直接把半截参数发出去，而是：

1. 按 `tool_call_id` 聚合 `tool_call_chunks`
2. 累积工具名和参数字符串
3. 只有在参数能成功解析成完整 JSON 后，才发出 `tool_start`

对应代码：

- [backend/graph/agent.py:130-183](../../backend/graph/agent.py#L130-L183)

发出的事件结构是：

```json
{
  "event": "tool_start",
  "data": {
    "tool_call_id": "call_xxx",
    "tool": "write_file",
    "input": {...}
  }
}
```

这带来两个直接收益：

1. **前端能马上知道当前调的是哪个工具**
2. **前端拿到的是完整参数，而不是拼到一半的残缺 JSON**

### 5.4 `tool_end`：工具结束后把结果继续推给前端

工具执行完成后，`AgentManager` 会从 `ToolMessage` 中提取：

- `tool_call_id`
- `tool`
- `output`

然后发：

```json
{
  "event": "tool_end",
  "data": {
    "tool_call_id": "call_xxx",
    "tool": "write_file",
    "output": "..."
  }
}
```

对应代码：

- [backend/graph/agent.py:193-211](../../backend/graph/agent.py#L193-L211)

这就让前端不仅知道“开始调了什么工具”，还知道“这个工具返回了什么”。

---

## 6. 为什么说“现在后端可以主动发送模型调用了什么 tool，而且不会阻塞前端观察”

这个问题要分两层理解。

## 6.1 “主动发送”体现在哪

不是前端轮询，不是等整轮结束回查，而是后端在流式执行中**主动 yield SSE 事件**。

也就是：

- 模型一旦形成完整 tool call → 后端立刻发 `tool_start`
- 工具一旦执行完成 → 后端立刻发 `tool_end`
- 不需要等 assistant 最终回答全部生成完
- 更不需要等 trace 文件被前端二次读取后才知道工具发生了什么

因此这里的“主动发送”本质上是：

> **事件在执行时刻直接从后端流到前端，而不是执行完成后再做离线查询。**

## 6.2 “不会阻塞”具体指什么

这里更准确的说法应该是：

> **前端对工具调用的可见性不会被“整轮回答完成”或“最终落盘完成”阻塞。**

也就是说，前端不必等到：

- 最终文本回答全部输出完
- session 写盘完
- trace 写盘完
- `done` 发出

才知道工具调用情况。

它在流进行中就能看到：

- 当前开始了哪个工具
- 这个工具的输入参数是什么
- 工具什么时候结束
- 工具输出预览是什么

当然，严格说模型在等待工具执行时，文本 token 的继续生成会暂停，这本来就是 tool-call Agent 的正常行为；但**UI 不会处于“什么都看不到”的黑盒等待状态**，因为 SSE 已经把工具状态推出来了。

---

## 7. 并发工具调用为什么也能正确显示

这部分是当前实现里非常关键、也非常工程化的一点。

相关文件：

- [backend/graph/agent.py:130-183](../../backend/graph/agent.py#L130-L183)
- [backend/api/chat.py:68-128](../../backend/api/chat.py#L68-L128)
- [trace_collection_fix_log.md:77-232](../分析/trace_collection_fix_log.md#L77-L232)

### 7.1 问题背景

LangChain 流式 tool calling 有两个典型难点：

1. 一个 tool call 的参数可能被拆成多个 chunk
2. 多个工具可能并发调用
3. 同名工具也可能并发执行

如果只按工具名匹配，很容易乱。

### 7.2 当前项目的做法

#### 在 `agent.py` 里

- 用 `tool_call_buffer` 按 `tool_call_id` 缓存 chunk
- name 和 args 都按同一个 `tool_call_id` 聚合
- 只有 args 可以成功解析为完整 JSON 后，才发 `tool_start`

#### 在 `chat.py` 里

- 用 `active_tool_calls = {tool_call_id: ...}` 跟踪本轮正在执行的工具
- 收到 `tool_start` 时登记为 running
- 收到 `tool_end` 时按 `tool_call_id` 精确匹配并补上 result
- 最终形成可持久化的 trace 记录

这意味着：

> 当前系统不是简单地“显示一个工具名”，而是已经具备了**按调用实例精确跟踪工具生命周期**的能力。

这也是为什么前端适合直接把它展示成“工作流审计”。

---

## 8. `chat.py` 为什么既负责流式推送，又负责 trace 汇总

当前链路里，`chat.py` 是真正的回合编排中心：

- 它知道本轮何时开始
- 它拿得到所有 SSE 事件
- 它能积累 assistant 文本
- 它能收集 tool calls
- 它能在结尾统一落盘

相关代码：

- [backend/api/chat.py:65-141](../../backend/api/chat.py#L65-L141)

它在一个请求内完成：

1. 把 agent 输出的事件流转发给前端
2. 同时在服务端把工具调用整理成 `tool_calls[]`
3. 回合结束后保存 `messages`
4. 再写入 `traces`
5. 最后发 `done`

所以当前架构可以理解成：

- `agent.py`：事件标准化
- `chat.py`：事件转发 + 本轮聚合 + 闭环控制
- `trace_writer.py`：只负责 append traces
- `session_manager.py`：只负责 messages envelope

这个分层比较清晰，而且不重。

---

## 9. Trace 持久化设计：SSE 是实时层，`context_trace` 是回放层

当前项目不是只做“实时可见”，还做了“事后可回放”。

### 9.1 存储格式

session 文件路径：

- `context_trace/{session_id}.json`

当前使用 envelope schema：

```json
{
  "messages": [...],
  "traces": [...]
}
```

对应：

- [backend/graph/session_manager.py:1-9](../../backend/graph/session_manager.py#L1-L9)
- [backend/graph/session_manager.py:63-87](../../backend/graph/session_manager.py#L63-L87)
- [backend/graph/trace_writer.py:23-57](../../backend/graph/trace_writer.py#L23-L57)

### 9.2 为什么这个设计配合 SSE 很合适

可以把它理解成两层：

#### 第一层：SSE 实时层

负责“当前正在发生什么”：

- token 正在输出
- 哪个 tool 开始了
- 哪个 tool 结束了

#### 第二层：trace 回放层

负责“这轮最终到底发生了什么”：

- 本轮完整工具调用列表
- 参数、结果、时间戳、状态
- 和消息历史一起保存在同一个 session envelope 中

这样前端既能在**当下看到过程**，也能在**事后回看审计**。

---

## 10. 前端是怎么消费这套 SSE 的

前端主实现当前在：

- [frontend/index.html:1641-1745](../../frontend/index.html#L1641-L1745)

这里有两个重点。

### 10.1 当前前端不是 `EventSource`，而是 `fetch + ReadableStream`

当前实现里，前端对 `/api/chat` 发 POST：

- [frontend/index.html:1665-1673](../../frontend/index.html#L1665-L1673)

然后直接拿：

- `response.body.getReader()`
- `TextDecoder()`
- 手动逐行解析 `event:` / `data:`

对应：

- [frontend/index.html:1679-1699](../../frontend/index.html#L1679-L1699)

所以虽然协议层是 SSE（`text/event-stream`），但消费方式不是浏览器原生 `EventSource`，而是更灵活的 **fetch streaming**。

这在当前项目里是合理的，因为：

- `/api/chat` 是 POST 请求
- 浏览器原生 `EventSource` 更适合 GET
- 这里需要携带 JSON body（message / session_id / stream）

### 10.2 前端实时渲染 tool 事件

当前事件处理逻辑：

- `token` → 追加到 assistant 气泡
- `tool_start` → 在“本轮工作流审计”区域插入一条“调用工具”记录
- `tool_end` → 插入一条“工具返回”记录
- `error` → 追加错误信息

对应：

- [frontend/index.html:1710-1718](../../frontend/index.html#L1710-L1718)
- [frontend/index.html:1626-1639](../../frontend/index.html#L1626-L1639)

也就是说，前端当前已经具备这种用户体验：

```text
用户发消息
  -> 看到 assistant 文本逐字出现
  -> 同时看到“调用工具 · read_file”
  -> 再看到“工具返回 · read_file”
  -> 再继续看到 assistant 后续文本
```

这正是“后端主动发工具状态，前端非阻塞可见”的直接体现。

---

## 11. `new_response` 的状态：后端已支持，当前前端主逻辑还没重点使用

后端支持 `new_response`：

- [backend/graph/agent.py:186-187](../../backend/graph/agent.py#L186-L187)

它的作用是：

> 工具调用后，如果 Agent 重新开始生成一段新的 assistant 文本，可以通知前端创建新的响应段。

这是 TAD 里“多段响应”的设计点：

- [experimental-research-openclaw-TAD.md:216-217](../架构/experimental-research-openclaw-TAD.md#L216-L217)

不过从当前 `frontend/index.html` 的主聊天逻辑看，前端现在主要显式处理的是：

- `token`
- `tool_start`
- `tool_end`
- `error`

并没有对 `new_response` 做单独分段渲染。

所以更准确的表述是：

- **后端事件协议已经预留了多段 assistant response 能力**
- **当前前端主要已经充分利用的是 token/tool_start/tool_end 这三类核心实时事件**

---

## 12. 当前 SSE 设计最值得前端使用的点

如果只看“给前端展示”这件事，当前设计最有价值的是下面 4 点。

### 12.1 文本流和工具流走同一条连接

不用：

- 一条请求拿文本
- 另一条请求轮询工具状态
- 第三条请求拉 trace

而是一条 `/api/chat` 就能同时拿到：

- assistant token
- tool_start
- tool_end
- error
- done

这让前端状态机简单很多。

### 12.2 tool 事件是标准化结构，不是字符串日志

前端拿到的是结构化数据：

- `tool_call_id`
- `tool`
- `input`
- `output`

所以它可以：

- 做卡片展示
- 做状态标记
- 做折叠展开
- 做 tool timeline
- 后续做更细粒度工作流 UI

### 12.3 `done` 是强语义信号

因为 `done` 发生在落盘之后，所以前端可以在 `done` 之后安全地：

- 重新读取 envelope
- 刷新 trace 计数
- 渲染本轮审计卡片

当前前端就是这么做的：

- [frontend/index.html:1734-1744](../../frontend/index.html#L1734-L1744)

### 12.4 历史回放与实时展示天然衔接

前端可以：

- 流式过程中显示 tool_start / tool_end
- 回合结束后再从 `context_trace/{session_id}.json` 读取完整 envelope
- 展示会话累计审计和本轮 trace 摘要

对应：

- [frontend/index.html:1488-1502](../../frontend/index.html#L1488-L1502)
- [frontend/index.html:1748-1805](../../frontend/index.html#L1748-L1805)

---

## 13. 当前实现与 TAD 目标态的差异

为了避免总结时把“目标态”和“现状”混在一起，这里单独说明一下。

### 13.1 已经落地的

已经真实落地的部分：

- `/api/chat` 基于 SSE 流式输出
- 后端推 `token/tool_start/tool_end/error/done`
- 工具调用按 `tool_call_id` 做精确配对
- 并发工具调用可以正确采集
- 前端可以实时看到工具开始和结束
- session 与 traces 共用一个 envelope 文件
- 回合结束后前端可读取持久化 trace

### 13.2 文档里提到、但当前代码里还不是主链路的

从当前代码看，下面这些还更偏文档目标态或后续阶段内容：

- 独立 `traces.py` API（TAD 里有提到，但当前 `backend/api/` 中没有该文件）
- `retrieval` SSE 事件的完整主链路展示
- 更完整的 skills 流式执行显示
- 前端对 `new_response` 的分段展示
- TAD 里提到的更完整 context_read 审计结构

所以如果要向别人介绍当前项目，最准确的说法是：

> **SSE 主链路和 tool 实时可见已经落地，且这是现在最好用、最清晰的一部分；更完整的 trace / retrieval / skills 展示能力仍有继续扩展空间。**

---

## 14. 总结：现在这套 SSE 设计到底解决了什么问题

如果把价值压缩成一句话：

> **它把 Agent 从“只会吐最终答案的黑盒”变成了“会边思考边把工具执行过程实时暴露给前端的透明工作流”。**

更具体地说，它解决了 4 个实际问题：

1. **前端不再只能等最终答案**
   - 工具一触发就能看到

2. **模型调用什么 tool 变得可视化**
   - `tool_start` / `tool_end` 直接展示

3. **并发 tool 调用不会乱**
   - 通过 `tool_call_id` 做精确配对

4. **实时过程和事后审计打通了**
   - SSE 做实时显示
   - `context_trace/{session_id}.json` 做持久化回放

所以从产品体验上看，当前项目的 SSE 不是简单的“流式输出文本”，而是：

> **把“回答内容”和“执行过程”一起流给前端。**

这也是为什么它特别适合实验研究场景：用户不只关心答案，还关心“你查了什么、读了什么、写了什么、调用了什么工具”。

---

## 15. 可直接复述给前端/产品同学的版本

可以直接用下面这段话对外解释：

> 当前项目的 SSE 设计不是只流模型文本，而是把 Agent 执行过程也作为事件一起流出来。后端 `/api/chat` 会通过 `text/event-stream` 持续推送 `token`、`tool_start`、`tool_end`、`done` 等事件。这样前端在模型真正调用工具的当下，就能立刻看到“现在调了哪个 tool、参数是什么、返回了什么”，而不需要等整轮结束或轮询后端。回合完成后，这些工具调用还会被写入 `context_trace/{session_id}.json`，所以同一套数据既能支持实时展示，也能支持历史审计回放。

---

## 16. 参考文件

### 后端

- [backend/api/chat.py](../../backend/api/chat.py)
- [backend/graph/agent.py](../../backend/graph/agent.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)
- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)
- [backend/graph/prompt_builder.py](../../backend/graph/prompt_builder.py)
- [backend/tests/test_chat_write_file_flow.py](../../backend/tests/test_chat_write_file_flow.py)

### 前端

- [frontend/index.html](../../frontend/index.html)

### 设计文档

- [experimental-research-openclaw-PRD.md](../架构/experimental-research-openclaw-PRD.md)
- [experimental-research-openclaw-TAD.md](../架构/experimental-research-openclaw-TAD.md)
- [trace_collection_fix_log.md](../分析/trace_collection_fix_log.md)
- [backend-context-trace-design.md](./backend-context-trace-design.md)
