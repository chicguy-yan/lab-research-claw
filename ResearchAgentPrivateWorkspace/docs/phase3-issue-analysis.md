# Phase 3 Issue Analysis: PromptBuilder user_prompt 未使用问题

## 问题描述

**高优先级**：PromptBuilder 设计出的 `user_prompt` 实际不会被用到，导致 `selected_files` / `[untrusted]` metadata 这两条输入通道在方案里存在、在落地链路里不存在。

## 问题定位

### 1. 设计层面（phase3-dev-plan.md）

**PromptBuilder.build() 设计**（line 203-212）：
```python
def build(
    self,
    context_result: ContextResult,
    user_message: str,
    metadata: dict | None = None,
) -> tuple[str, str]:
    """
    返回 (system_prompt, user_prompt)
    """
```

设计返回了 `(system_prompt, user_prompt)` 两个值。

**User Prompt 结构设计**（line 268-273）：
```
[可选] <untrusted> JSON 代码块（上传文件路径等）
用户正文
```

这表明设计意图是将 metadata（如上传文件路径）和用户消息组装成 user_prompt。

**ContextOrchestrator.select_context() 设计**（line 97-101）：
```python
def select_context(
    self,
    message: str,
    selected_files: list[str] | None = None,
) -> ContextResult:
```

设计接受 `selected_files` 参数，用于用户指定文件直接注入（line 178）。

### 2. 实现层面

**chat.py 当前实现**（line 48）：
```python
async for event in am.astream(body.message, history, SYSTEM_PROMPT):
```

问题：
1. 直接使用 `body.message` 作为用户消息
2. 使用硬编码的 `SYSTEM_PROMPT`
3. **没有调用 PromptBuilder**
4. **没有使用 PromptBuilder 返回的 user_prompt**

**agent.py 的 astream 接口**（line 76-81）：
```python
async def astream(
    self,
    message: str,
    history: list[dict],
    system_prompt: str,
) -> AsyncGenerator[dict, None]:
```

接口只接受：
- `message: str` - 单个用户消息字符串
- `system_prompt: str` - 系统提示

**agent.py 的消息构建**（line 98-99）：
```python
# Build messages list: history + current user message
messages = list(history) + [{"role": "user", "content": message}]
```

直接将 `message` 作为用户消息内容，没有任何预处理。

### 3. 数据流断裂点

```
设计流程：
ChatRequest.message
  → ContextOrchestrator.select_context(message, selected_files)  ← selected_files 从哪来？
  → PromptBuilder.build(context_result, message, metadata)       ← metadata 从哪来？
  → (system_prompt, user_prompt)
  → AgentManager.astream(user_prompt, history, system_prompt)    ← 需要修改接口

实际流程：
ChatRequest.message
  → AgentManager.astream(message, history, SYSTEM_PROMPT)
  → 直接使用原始 message
```

**断裂点**：
1. `ChatRequest` 没有 `selected_files` 字段
2. `ChatRequest` 没有 `metadata` 字段
3. `chat.py` 没有调用 `ContextOrchestrator` 和 `PromptBuilder`
4. `AgentManager.astream()` 接口不支持接收预处理后的 user_prompt

## 影响范围

### 功能缺失

1. **selected_files 通道不可用**
   - 用户无法通过前端指定要注入的文件
   - ContextOrchestrator 的 `selected_files` 参数永远为 None

2. **untrusted metadata 通道不可用**
   - 上传文件路径无法传递给 Agent
   - User Prompt 中的 `<untrusted>` JSON 块永远不会生成

3. **PromptBuilder 的 user_prompt 构建逻辑无效**
   - 设计的 User Prompt 结构（metadata + 用户正文）不会被使用
   - PromptBuilder.build() 返回的第二个值被浪费

### 架构问题

1. **设计与实现不一致**
   - phase3-dev-plan 描述的流程与实际代码不符
   - 验收标准无法通过（trace 中不会有 selected_files / metadata 信息）

2. **扩展性受限**
   - Phase 5 的上传功能无法将文件路径传递给 Agent
   - 前端无法实现"选择文件注入上下文"功能

## 根本原因

**设计假设错误**：设计假设 AgentManager 可以接收预处理后的 user_prompt，但实际上：

1. LangChain 的 Agent 接口期望的是原始用户消息
2. 将 metadata 注入到 user message 中会污染对话历史
3. 当前架构中，system_prompt 是每轮重建的，但 user message 应该保持原始性

**正确的架构应该是**：
- System Prompt：包含所有上下文、规则、metadata
- User Message：保持用户原始输入，不做修改

## 修复方案

### 方案 A：将 metadata 注入 system_prompt（推荐）

**原理**：将 selected_files 和 untrusted metadata 作为 system_prompt 的一部分注入，而不是修改 user message。

**修改点**：

1. **ChatRequest 扩展**（api/chat.py）：
```python
class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True
    selected_files: list[str] | None = None  # NEW
    metadata: dict | None = None             # NEW (上传文件路径等)
```

2. **PromptBuilder.build() 修改**（graph/prompt_builder.py）：
```python
def build(
    self,
    context_result: ContextResult,
    user_message: str,  # 仅用于日志/trace，不修改
    metadata: dict | None = None,
) -> str:  # 只返回 system_prompt
    """
    返回 system_prompt（包含 metadata 块）
    """
```

System Prompt 新增 Block 4.5：
```
Block 4: ## Inbound Context (trusted metadata)
  JSON: 平台/时区/语言/会话类型/当前日期/intent_hint

Block 4.5: ## User Context (untrusted)  ← NEW
  [如果有 metadata]
  JSON: 上传文件路径、用户选择的文件等

Block 5: # Memory Map
  ...
```

3. **chat.py 集成修改**：
```python
async def chat(body: ChatRequest, request: Request):
    # ...
    async def event_generator():
        history = sm.load_session_for_agent(body.session_id)

        # NEW: 调用 ContextOrchestrator
        co = request.app.state.context_orchestrator
        context_result = co.select_context(
            body.message,
            selected_files=body.selected_files  # 传递用户选择的文件
        )

        # NEW: 调用 PromptBuilder
        pb = request.app.state.prompt_builder
        system_prompt = pb.build(
            context_result,
            body.message,
            metadata=body.metadata  # 传递 metadata
        )

        # 使用构建的 system_prompt，message 保持原样
        async for event in am.astream(body.message, history, system_prompt):
            # ...
```

4. **agent.py 不需要修改**：
   - 接口保持不变
   - message 参数仍然是用户原始输入
   - system_prompt 包含所有上下文信息

**优点**：
- 符合 LangChain 最佳实践（system prompt 包含上下文，user message 保持原始）
- 不污染对话历史
- 最小化修改范围
- 对话历史中的 user message 仍然是用户原始输入

**缺点**：
- 需要修改 phase3-dev-plan.md 中的 User Prompt 结构设计

### 方案 B：在 history 中注入 metadata（不推荐）

将 metadata 作为一条 system 消息插入到 history 中。

**缺点**：
- 污染对话历史
- 每轮都会累积 metadata 消息
- 不符合 LangChain 消息模型

### 方案 C：修改 AgentManager 接口支持 user_prompt（不推荐）

修改 `astream(user_prompt, history, system_prompt)` 接受预处理后的 user_prompt。

**缺点**：
- 对话历史中保存的是修改后的消息，不是用户原始输入
- 回放时会看到被注入 metadata 的消息
- 违反单一职责原则（AgentManager 不应该关心 prompt 构建）

## 推荐行动

1. **采用方案 A**：将 metadata 注入 system_prompt
2. **修改 phase3-dev-plan.md**：
   - 删除 "User Prompt 结构" 章节（line 268-273）
   - 修改 PromptBuilder.build() 签名为只返回 system_prompt
   - 在 System Prompt Block 4 后增加 Block 4.5: User Context (untrusted)
3. **更新 chat.py 集成流程**（line 372-384）
4. **更新验收标准**：trace 中应记录 selected_files 和 metadata

## 验证方式

修复后，应能通过以下测试：

```bash
# 测试 selected_files
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这些文件",
    "session_id": "test_selected",
    "selected_files": ["memory/tasks/TASK_exp_003.md"],
    "stream": true
  }'

# 检查 trace
curl "http://localhost:8002/api/traces/test_selected/latest" | jq '.context_read'
# 预期：包含 TASK_exp_003.md，why 字段标注 "用户指定"

# 测试 metadata
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这个上传的文件",
    "session_id": "test_metadata",
    "metadata": {"uploaded_files": ["assets/uploads/XRD_sample_03.pdf"]},
    "stream": true
  }'

# 检查 system prompt 是否包含 metadata
# （需要在 trace 中记录 system_prompt 或通过日志验证）
```

## 时间估算

- 修改 ChatRequest：5 分钟
- 修改 PromptBuilder：15 分钟
- 修改 chat.py 集成：10 分钟
- 更新 phase3-dev-plan.md：10 分钟
- 测试验证：20 分钟

**总计**：约 1 小时

## 优先级

**高**：这是 Phase 3 的核心功能缺失，影响：
- Phase 5 上传功能的数据流
- 前端文件选择功能
- 验收标准的通过

建议在开始 Phase 3 实现前先修复此设计问题。
