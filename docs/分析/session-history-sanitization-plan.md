# Session History Sanitization Plan

> 主题：解决 `SessionManager.load_session_for_agent()` 将高风险 assistant 历史原样回灌给模型，导致 tool call 参数协议被污染的问题。

## 1. 问题定义

当前实现中，`SessionManager.load_session_for_agent()` 会把会话历史中的 `messages` 基本原样返回给 agent，仅做“连续 assistant 消息合并”。

这在普通聊天里问题不大，但在 tool-calling agent 场景中会放大以下风险：

1. assistant 历史里包含伪工具调用示例，例如：
   - `terminal("ls ...")`
   - `read_file("foo.md")`
   - `write_file("bar.md", "...")`
2. 用户会把 assistant 旧回答整段复制回下一轮，导致这些伪代码再次进入 history。
3. 这些内容会和新的 system prompt 工具 schema 同时出现，形成协议冲突：
   - 一边是结构化参数对象
   - 一边是函数式伪代码调用
4. 最终表现为模型在真实 tool call 时串字段，例如：
   - 给 `terminal` 传 `path`
   - 给 `read_file` 传 `command`

结论：问题不只是 prompt 文案，而是“历史回灌策略缺少面向 tool-calling 的清洗层”。

## 2. 非目标

本方案不做以下事情：

- 不删除用户可见的历史记录
- 不改写 `context_trace/{session_id}.json` 中已有的审计快照
- 不改变前端 `GET /api/sessions/{id}/history` 的展示内容

目标是：

- 只改变“喂给模型的 history”
- 保留“给用户展示的 history”

## 3. 推荐方案

推荐采用“双轨历史”策略。

### 3.1 Display History

继续保留当前 `messages`，用于：

- 前端展示
- 会话回放
- 审计追踪

### 3.2 Model History

新增一层“清洗后的历史视图”，专门给 agent 使用：

- 过滤或改写高风险 assistant 文本
- 删除会污染 tool schema 的伪工具调用示例
- 尽量保留对话语义、任务上下文和最终结论

换句话说：

- `display_messages`：保真
- `model_messages`：安全

## 4. 三档实现方案

### 方案 A：最小改动

只在 `load_session_for_agent()` 中对 assistant 历史做规则过滤。

处理规则示例：

- 删除包含以下模式的行：
  - `terminal("`
  - `read_file("`
  - `write_file("`
  - `python_repl("`
  - `fetch_url("`
- 删除整段代码块中出现上述伪调用格式的代码块

优点：

- 改动最小
- 风险较低
- 很快能降低字段串错概率

缺点：

- 规则比较脆
- 对 `Context Trace / Memory Patch` 这类冗余文本处理不够

### 方案 B：推荐方案

在 `load_session_for_agent()` 中，将 assistant 历史转换为“摘要化的安全版本”。

规则：

1. 保留 user 消息原文
2. assistant 消息执行以下清洗：
   - 去掉 `Context Trace`
   - 去掉 `Memory Patch`
   - 去掉带有伪工具调用示例的代码块
   - 去掉旧 prompt/工具签名长段引用
   - 保留：
     - 任务结论
     - 建议动作
     - 关键信息摘要
3. 对超长 assistant 消息做长度压缩

优点：

- 对 tool-calling 场景最稳
- 明显降低历史污染
- 不影响前端展示和审计

缺点：

- 需要明确定义清洗规则
- 需要补测试

### 方案 C：结构升级

在存储层正式拆分两类消息：

- `messages`: 展示/审计用
- `model_messages`: 推理用

优点：

- 语义清晰
- 后续最易维护

缺点：

- 改动面大
- 会影响 SessionManager、Chat API、历史接口、测试

## 5. 推荐落地路线

建议按两步走：

### 第一步：落地方案 B

原因：

- 成本可控
- 对当前问题最直接
- 不需要改动前端协议

### 第二步：视效果决定是否升级到方案 C

如果后续仍有：

- 历史过长
- 历史摘要不稳定
- 多轮 tool pollution

再考虑在存储层引入显式的 `model_messages`

## 6. 具体改动点

### 6.1 SessionManager

文件：`backend/graph/session_manager.py`

新增私有方法建议：

- `_sanitize_assistant_message_for_model(content: str) -> str`
- `_strip_pseudo_tool_calls(content: str) -> str`
- `_strip_trace_sections(content: str) -> str`
- `_compress_assistant_message(content: str, max_chars: int = 1200) -> str`

修改：

- `load_session_for_agent()`

新逻辑：

1. 读取原始 `messages`
2. 合并连续 assistant 消息
3. 对 assistant 消息做清洗
4. 丢弃清洗后为空的 assistant 消息
5. 返回清洗后的 history 给 agent

### 6.2 Chat API

文件：`backend/api/chat.py`

无需修改对外接口，但建议增加 DEBUG 日志：

- 记录原始 history 条数
- 记录清洗后 history 条数
- 记录被剔除的 assistant 片段数量

### 6.3 测试

建议新增文件：

- `backend/tests/test_session_history_sanitization.py`

覆盖点：

1. assistant 含 `terminal("ls")` 时，模型历史中应被清掉
2. assistant 含 `Context Trace` / `Memory Patch` 时，模型历史中应被裁掉或摘要化
3. user 原文必须完整保留
4. 前端读取 history 的原始消息不受影响
5. 连续 assistant 合并后仍能正确清洗

## 7. 规则细节建议

### 必删内容

- 伪工具调用示例
- 长段旧 system prompt 引用
- `Context Trace` 标题块
- `Memory Patch` 标题块

### 建议保留内容

- 用户任务目标
- assistant 的结论性摘要
- 文件路径、实验名、缺口清单
- 真实业务语义，不保留伪执行样式

### 建议压缩内容

- 表格
- 长 checklist
- 重复的工具说明

## 8. 成功标准

实施后应达到：

1. 新会话中，assistant 旧回答即使被用户复制回下一轮，也不再显著污染 tool call 参数选择
2. `terminal(path=...)`、`read_file(command=...)` 这类错误频率明显下降
3. 前端历史展示、trace 审计、会话回放保持不变
4. agent 输入 history 更短、更干净、更稳定

## 9. 风险与注意事项

1. 清洗过度可能丢失对话语义
2. 规则太弱则无法降低污染
3. 不能把“清洗模型输入”误做成“篡改审计历史”

所以推荐原则是：

- 存储层保真
- 推理层清洗

## 10. 建议结论

建议立即执行方案 B：

- 不删除历史文件
- 不改前端 history 展示
- 只清洗喂给 agent 的 assistant 历史

这是当前最符合工程现实、风险最低、收益最高的修复路径。
