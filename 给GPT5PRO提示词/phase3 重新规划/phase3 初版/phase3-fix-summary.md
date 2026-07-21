# Phase 3 设计问题修复总结

## 问题核心

PromptBuilder 设计返回 `(system_prompt, user_prompt)` 两个值，但实际实现中：
1. **user_prompt 永远不会被使用**
2. **selected_files 参数无法传递**（ChatRequest 没有此字段）
3. **metadata 参数无法传递**（ChatRequest 没有此字段）

这导致两条关键输入通道失效：
- 用户指定文件（selected_files）
- 不可信元数据（untrusted metadata，如上传文件路径）

## 根本原因

**架构假设错误**：设计假设可以修改 user message 来注入 metadata，但这违反了：
1. LangChain 最佳实践（user message 应保持原始）
2. 对话历史的完整性（不应污染用户原始输入）
3. 单一职责原则（AgentManager 不应关心 prompt 构建细节）

## 推荐修复方案

### 将 metadata 注入 system_prompt（而非 user_prompt）

**核心思路**：
- System Prompt：包含所有上下文、规则、metadata、selected_files
- User Message：保持用户原始输入，不做任何修改

### 具体修改

#### 1. ChatRequest 扩展（api/chat.py）

```python
class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True
    selected_files: list[str] | None = None  # NEW：用户指定文件
    metadata: dict | None = None             # NEW：不可信元数据（上传文件路径等）
```

#### 2. PromptBuilder.build() 签名修改（graph/prompt_builder.py）

```python
def build(
    self,
    context_result: ContextResult,
    user_message: str,  # 仅用于日志/trace，不修改
    metadata: dict | None = None,
) -> str:  # 只返回 system_prompt，不返回 user_prompt
    """
    返回 system_prompt（包含 metadata 块）
    """
```

#### 3. System Prompt 结构调整

在 Block 4 后增加 Block 4.5：

```
Block 4: ## Inbound Context (trusted metadata)
  JSON: 平台/时区/语言/会话类型/当前日期/intent_hint

Block 4.5: ## User Context (untrusted)  ← NEW
  [如果有 metadata]
  JSON: {
    "uploaded_files": ["assets/uploads/XRD_sample_03.pdf"],
    "selected_files": ["memory/tasks/TASK_exp_003.md"],
    ...
  }

Block 5: # Memory Map
  ...
```

#### 4. chat.py 集成修改

```python
async def chat(body: ChatRequest, request: Request):
    async def event_generator():
        history = sm.load_session_for_agent(body.session_id)

        # NEW: 调用 ContextOrchestrator（传递 selected_files）
        co = request.app.state.context_orchestrator
        context_result = co.select_context(
            body.message,
            selected_files=body.selected_files  # 用户指定文件
        )

        # NEW: 调用 PromptBuilder（传递 metadata）
        pb = request.app.state.prompt_builder
        system_prompt = pb.build(
            context_result,
            body.message,
            metadata=body.metadata  # 不可信元数据
        )

        # 使用构建的 system_prompt，message 保持原样
        async for event in am.astream(body.message, history, system_prompt):
            # ...
```

#### 5. agent.py 不需要修改

接口保持不变：
```python
async def astream(
    self,
    message: str,        # 用户原始输入
    history: list[dict],
    system_prompt: str,  # 包含所有上下文和 metadata
) -> AsyncGenerator[dict, None]:
```

### 文档修改

#### phase3-dev-plan.md 需要修改的地方

1. **删除 User Prompt 结构章节**（line 268-273）
2. **修改 PromptBuilder.build() 签名**（line 203-212）：
   ```python
   def build(
       self,
       context_result: ContextResult,
       user_message: str,
       metadata: dict | None = None,
   ) -> str:  # 只返回 system_prompt
   ```
3. **在 System Prompt 六块结构中增加 Block 4.5**（line 215-266）
4. **修改 chat.py 集成流程**（line 372-390）：
   - 增加 ContextOrchestrator 调用
   - 增加 PromptBuilder 调用
   - 传递 selected_files 和 metadata

## 数据流对比

### 修复前（设计但未实现）

```
ChatRequest.message
  → PromptBuilder.build()
  → (system_prompt, user_prompt)  ← user_prompt 包含 metadata
  → AgentManager.astream(user_prompt, ...)  ← 需要修改接口
```

问题：
- ChatRequest 缺少 selected_files 和 metadata 字段
- user_prompt 污染对话历史
- AgentManager 接口需要大改

### 修复后（推荐）

```
ChatRequest {
  message: str
  selected_files: list[str] | None
  metadata: dict | None
}
  → ContextOrchestrator.select_context(message, selected_files)
  → PromptBuilder.build(context_result, message, metadata)
  → system_prompt  ← 包含所有上下文和 metadata
  → AgentManager.astream(message, history, system_prompt)
```

优点：
- message 保持原始，不污染历史
- system_prompt 包含所有上下文信息
- AgentManager 接口无需修改
- 符合 LangChain 最佳实践

## 验证方式

### 测试 1：selected_files 通道

```bash
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
```

### 测试 2：metadata 通道

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这个上传的文件",
    "session_id": "test_metadata",
    "metadata": {"uploaded_files": ["assets/uploads/XRD_sample_03.pdf"]},
    "stream": true
  }'

# 检查 trace 中是否记录了 metadata
curl "http://localhost:8002/api/traces/test_metadata/latest" | jq '.metadata'
```

### 测试 3：组合使用

```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "基于这些材料分析实验结果",
    "session_id": "test_combined",
    "selected_files": ["memory/tasks/TASK_exp_003.md"],
    "metadata": {
      "uploaded_files": ["assets/uploads/XRD_sample_03.pdf"],
      "context": "实验闭环"
    },
    "stream": true
  }'
```

## 影响范围

### 直接影响

1. **Phase 3 实现**：
   - ChatRequest 数据模型
   - PromptBuilder 接口和实现
   - chat.py 集成逻辑
   - phase3-dev-plan.md 文档

2. **Phase 3 验收**：
   - 验收标准需要增加 selected_files 和 metadata 测试
   - trace 结构需要记录这两个字段

### 后续 Phase 影响

1. **Phase 5（上传功能）**：
   - 上传文件后，通过 metadata.uploaded_files 传递路径
   - Agent 可以在 system prompt 中看到上传文件信息

2. **Phase 6（前端）**：
   - 前端可以实现"选择文件注入上下文"功能
   - 文件选择器 → selected_files 参数 → ContextOrchestrator

## 时间估算

- 修改 ChatRequest：5 分钟
- 修改 PromptBuilder 设计：15 分钟
- 修改 chat.py 集成：10 分钟
- 更新 phase3-dev-plan.md：15 分钟
- 测试验证：20 分钟

**总计**：约 1 小时

## 优先级

**高**：这是 Phase 3 的核心功能缺失，必须在实现前修复，否则：
- Phase 5 上传功能无法工作
- 前端文件选择功能无法实现
- 验收标准无法通过
- 设计与实现严重不一致

## 建议

1. **立即修复 phase3-dev-plan.md**，明确 PromptBuilder 只返回 system_prompt
2. **在开始实现前**，先完成 ChatRequest 扩展和 chat.py 集成设计
3. **在 trace 结构中**，增加 selected_files 和 metadata 字段记录
4. **在验收标准中**，增加这两条输入通道的测试用例
