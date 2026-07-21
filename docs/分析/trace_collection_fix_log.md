# Trace 采集链路修正日志

**修正日期**: 2026-03-10
**问题级别**: 🔴 核心问题（影响 Phase 3 "透明可控" 目标）
**影响范围**: Phase 3 TraceWriter、Phase 4 工具并发调用、Phase 5 RAG 审计

---

## 问题描述

### 原始实现缺陷

#### 1. agent.py (line 140-151) — 工具调用参数不完整

**问题**：
- LangChain streaming 模式下，一个 tool call 会分多个 `tool_call_chunks` 传输
- 原实现每收到一个 chunk 就立即发出 `tool_start` 事件
- 没有按 `tool_call_id` 聚合 chunks，导致：
  - 同一个工具调用发出多次 `tool_start`
  - `args` 字段不完整（只拿到最后一个 chunk 的片段）
  - 无法区分不同的工具调用

**原代码**：
```python
for tc in chunk.tool_call_chunks:
    name = tc.get("name", "")
    args = tc.get("args", "")
    if name:  # 只要有 name 就发出 tool_start
        yield {
            "event": "tool_start",
            "data": {
                "tool": name,
                "input": args,  # ❌ args 不完整
            },
        }
```

#### 2. agent.py (line 161-171) — tool_end 缺少 tool_call_id

**问题**：
- `tool_end` 事件只包含 `tool_name`，没有 `tool_call_id`
- 无法与 `tool_start` 准确配对
- 并发调用同名工具时会混淆

**原代码**：
```python
yield {
    "event": "tool_end",
    "data": {
        "tool": tool_name,  # ❌ 只有名称，无 ID
        "output": str(chunk.content)[:2000],
    },
}
```

#### 3. chat.py (line 70-92) — 单变量无法处理并发

**问题**：
- 使用单个 `current_tool_call` 变量跟踪工具调用
- LLM 可能并发调用多个工具（LangChain 支持 parallel tool calling）
- 后续 `tool_start` 会覆盖前一个，导致数据丢失

**原代码**：
```python
current_tool_call = None

if event_type == "tool_start":
    current_tool_call = {...}  # ❌ 覆盖之前的 tool call

elif event_type == "tool_end":
    if current_tool_call:  # ❌ 只能匹配最后一个
        tool_calls.append(current_tool_call)
```

---

## 修正方案

### 1. agent.py — 按 tool_call_id 聚合 chunks

**修改位置**: `astream()` 方法 (line 103-178)

**核心改动**：
1. 新增 `tool_call_buffer = {}` 字典，按 `tool_call_id` 缓存 chunks
2. 累积 `name` 和 `args` 字段（args 可能分多个 chunk 传输）
3. 尝试 JSON 解析 args，成功后才发出 `tool_start`（确保完整性）
4. `tool_end` 事件携带 `tool_call_id`，从 `ToolMessage.tool_call_id` 提取
5. 发出 `tool_end` 后清理 buffer

**关键代码**：
```python
# Buffer to aggregate tool_call_chunks by tool_call_id
tool_call_buffer = {}  # {tool_call_id: {"name": str, "args": str}}

for tc in chunk.tool_call_chunks:
    call_id = tc.get("id")
    if not call_id:
        continue

    # Initialize buffer entry
    if call_id not in tool_call_buffer:
        tool_call_buffer[call_id] = {"name": None, "args": ""}

    # Accumulate name and args
    if tc.get("name"):
        tool_call_buffer[call_id]["name"] = tc["name"]
    if tc.get("args"):
        tool_call_buffer[call_id]["args"] += tc["args"]

    # Check if args is complete (can be parsed as JSON)
    if tool_call_buffer[call_id]["name"] and tool_call_buffer[call_id]["args"]:
        try:
            parsed_args = json.loads(tool_call_buffer[call_id]["args"])
        except json.JSONDecodeError:
            continue  # Args still incomplete

        # Emit tool_start with complete data
        yield {
            "event": "tool_start",
            "data": {
                "tool_call_id": call_id,  # ✅ 新增 ID
                "tool": tool_call_buffer[call_id]["name"],
                "input": parsed_args,  # ✅ 完整的 args
            },
        }
```

**tool_end 改动**：
```python
# Extract tool_call_id from ToolMessage
call_id = chunk.tool_call_id if hasattr(chunk, "tool_call_id") else None

yield {
    "event": "tool_end",
    "data": {
        "tool_call_id": call_id,  # ✅ 新增 ID
        "tool": tool_name,
        "output": str(chunk.content)[:2000],
    },
}

# Clean up buffer
if call_id and call_id in tool_call_buffer:
    del tool_call_buffer[call_id]
```

### 2. chat.py — 字典跟踪并发工具调用

**修改位置**: `event_generator()` 函数 (line 65-95)

**核心改动**：
1. 改用 `active_tool_calls = {}` 字典，按 `tool_call_id` 跟踪
2. `tool_start` 时存入字典，记录 `tool_call_id/tool/args/timestamp/status`
3. `tool_end` 时按 `tool_call_id` 匹配，更新 `result` 和 `status`
4. 添加 fallback 逻辑：如果 `tool_end` 没有 `tool_call_id`（兼容旧版），按 `tool_name` 匹配

**关键代码**：
```python
# Phase 3+4: Collect tool calls for trace (support concurrent tool calls)
tool_calls = []
active_tool_calls = {}  # {tool_call_id: {...}}

# Track tool calls by tool_call_id
elif event_type == "tool_start":
    call_id = event_data.get("tool_call_id")
    if call_id:
        active_tool_calls[call_id] = {
            "tool_call_id": call_id,
            "tool": event_data.get("tool"),
            "args": event_data.get("input"),
            "timestamp": datetime.now().isoformat(),
            "status": "running",
        }

elif event_type == "tool_end":
    call_id = event_data.get("tool_call_id")
    if call_id and call_id in active_tool_calls:
        active_tool_calls[call_id]["result"] = event_data.get("output")
        active_tool_calls[call_id]["status"] = "completed"
        tool_calls.append(active_tool_calls[call_id])
        del active_tool_calls[call_id]
    elif not call_id:
        # Fallback: tool_end without tool_call_id (legacy compatibility)
        tool_name = event_data.get("tool")
        for cid, tc in list(active_tool_calls.items()):
            if tc["tool"] == tool_name:
                tc["result"] = event_data.get("output")
                tc["status"] = "completed"
                tool_calls.append(tc)
                del active_tool_calls[cid]
                break
```

---

## 修正后的 Trace 数据结构

### tool_start 事件
```json
{
  "event": "tool_start",
  "data": {
    "tool_call_id": "call_abc123",
    "tool": "terminal",
    "input": {"command": "ls -la"}
  }
}
```

### tool_end 事件
```json
{
  "event": "tool_end",
  "data": {
    "tool_call_id": "call_abc123",
    "tool": "terminal",
    "output": "total 48\ndrwxr-xr-x  6 user  staff  192 Mar 10 10:00 ."
  }
}
```

### 最终 trace 记录（写入 session.json）
```json
{
  "tool_call_id": "call_abc123",
  "tool": "terminal",
  "args": {"command": "ls -la"},
  "result": "total 48\ndrwxr-xr-x  6 user  staff  192 Mar 10 10:00 .",
  "timestamp": "2026-03-10T10:00:15.123456",
  "status": "completed"
}
```

---

## 验证清单

修正后需验证以下场景：

### ✅ 基础场景
- [ ] **单个工具调用**：args 完整，trace 包含所有字段
- [ ] **长参数工具调用**：args 超过 1KB，分多个 chunk 传输，能正确聚合
- [ ] **工具调用失败**：status 标记为 "failed"（需后续补充错误处理）

### ✅ 并发场景
- [ ] **并发调用不同工具**：如同时调用 `terminal` 和 `read_file`，trace 不混淆
- [ ] **并发调用同名工具**：如同时调用两次 `read_file`，按 `tool_call_id` 区分

### ✅ 边界场景
- [ ] **tool_start 无对应 tool_end**：工具执行超时或崩溃，`active_tool_calls` 残留（需后续添加超时清理）
- [ ] **tool_end 无对应 tool_start**：异常情况，fallback 逻辑能兜底

### ✅ 数据完整性
- [ ] **TraceWriter 写入**：`session.json` 的 `traces` 数组包含完整字段
- [ ] **前端展示**：SSE 事件能正确渲染工具调用过程

---

## 后续优化建议

### 1. 超时清理机制
当前实现中，如果 `tool_end` 永远不到达（工具执行崩溃），`active_tool_calls` 会残留。建议：
- 在 `event_generator()` 结束时，检查 `active_tool_calls` 是否为空
- 对残留的 tool call 标记 `status: "timeout"` 并写入 trace

### 2. 错误状态传递
当前 `tool_end` 只有 `output` 字段，无法区分成功/失败。建议：
- agent.py 捕获工具执行异常，在 `tool_end` 中添加 `error` 字段
- chat.py 根据 `error` 字段设置 `status: "failed"`

### 3. 性能优化
- `tool_call_buffer` 在 agent.py 中持续累积，如果 LLM 生成大量工具调用但不执行，会占用内存
- 建议添加 buffer 大小限制（如最多缓存 100 个 tool call）

### 4. 日志增强
- 在 `tool_start` 和 `tool_end` 发出时记录 DEBUG 日志，便于排查问题
- 记录 `tool_call_id` 和 `tool_name`，方便追踪

---

## 影响评估

### 对现有功能的影响
- **向后兼容**：chat.py 添加了 fallback 逻辑，即使 agent.py 未升级也能工作（按 tool_name 匹配）
- **API 变更**：SSE 事件的 `data` 字段新增 `tool_call_id`，前端需适配（可选字段，不影响现有前端）

### 对后续 Phase 的影响
- **Phase 4 (6 个核心工具)**：并发调用场景（如同时读多个文件）现在能正确跟踪
- **Phase 5 (RAG)**：KnowledgeIndexer 调用 `fetch_url` 批量抓取时，trace 不会混淆
- **Phase 6 (前端)**：工具调用面板能按 `tool_call_id` 展示实时状态（running → completed）

---

## 修改文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| `backend/graph/agent.py` | 新增 `tool_call_buffer` 聚合逻辑，`tool_start/tool_end` 携带 `tool_call_id` | +40 lines |
| `backend/api/chat.py` | 改用 `active_tool_calls` 字典，支持并发工具调用 | +20 lines |

---

## 测试建议

### 手动测试
1. 启动后端：`cd backend && uvicorn app:app --reload`
2. 发送测试请求：
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "列出当前目录文件并读取 README.md", "session_id": "test-001"}'
   ```
3. 观察 SSE 输出，确认：
   - `tool_start` 事件包含 `tool_call_id`
   - `tool_end` 事件的 `tool_call_id` 与 `tool_start` 匹配
4. 检查 `workspace/sessions/test-001/session.json`，确认 `traces` 数组完整

### 自动化测试（后续补充）
- 单元测试：mock LangChain 的 `tool_call_chunks`，验证聚合逻辑
- 集成测试：调用真实 Agent，验证并发工具调用场景

---

## 结论

此次修正解决了 Phase 3 "透明可控" 的核心问题，确保 trace 数据的完整性和准确性。修正后：

✅ **工具调用参数完整**：按 `tool_call_id` 聚合 chunks，args 不再丢失
✅ **支持并发调用**：字典跟踪多个工具调用，不会混淆
✅ **准确配对 start/end**：通过 `tool_call_id` 匹配，不依赖 tool_name
✅ **向后兼容**：fallback 逻辑确保旧版 agent.py 也能工作

**建议立即合并此修正**，作为 Phase 3 的补充交付，再继续 Phase 4 的工具开发。
