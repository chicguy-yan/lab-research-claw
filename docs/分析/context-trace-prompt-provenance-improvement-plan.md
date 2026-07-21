# Context Trace Prompt Provenance Improvement Plan

> 主题：修正 `context_trace` 中 prompt 的来源可追溯性、回放粒度和历史污染问题，使 trace 真正可用于 prompt 审计与调试。

## 1. 背景

当前后端已经具备基础的 prompt trace 能力：

- `backend/api/chat.py` 会生成 `system_prompt`、拼接 `history + user message`
- `backend/graph/prompt_builder.py` 负责 system prompt 组装
- `backend/graph/trace_writer.py` 会把最终 `prompt` 写入 `context_trace/{session_id}.json`

这套链路已经能回答“模型最后收到了什么 prompt”，但还不能稳定回答以下问题：

1. 本轮 prompt 是由哪些上下文块拼出来的
2. 为什么选这些块，而不是别的块
3. 哪些内容被裁剪、跳过、降级
4. 当前看到的 `prompt` 是哪一轮的，而不是整个 session 的最新覆盖结果
5. 历史 assistant 文本里哪些是可信事实，哪些只是错误叙述或伪工具调用

结论：当前实现适合作为 MVP，不足以支撑严格的 prompt provenance 审计。

## 2. 现状问题

### 2.1 Trace 粒度不对

设计目标是“每回合一份 trace”，但当前自动实现实际上是“每个 session 一个文件”：

- `context_trace/{session_id}.json`
- `prompt` 字段每轮被最新值覆盖
- 无法精确回放任意历史轮次的 prompt

直接后果：

- 只能看到最近一轮 prompt
- 很难定位“哪一轮引入了错误上下文”
- 前端回放与设计文档不一致

### 2.2 只有最终 prompt，没有上下文选择过程

当前 trace 里有：

- `prompt.system_prompt`
- `prompt.messages`
- `traces[]` 工具调用

但没有：

- `context_read[]`
- `context_candidates[]`
- `selection_reason`
- `truncated/skipped` 记录

这意味着系统只能展示结果，不能解释来源链路。

### 2.3 Project Context 注入过薄

当前 `PromptBuilder` 真实注入的正文主要是：

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `TOOLS.md`
- `BOOTSTRAP.md`
- `MEMORY.md`
- `memory/identity/project.md`

Layer1/Layer2/Layer3 的大部分内容并没有正文注入，只是通过 `Memory Map` 做目录导航。

直接后果：

- prompt 的事实基础偏弱
- 模型仍需自己调用 `read_file`
- trace 虽然显示了 `Memory Map`，但无法说明“本轮真正依赖了哪些记忆正文”

### 2.4 Memory Map 推荐逻辑过于简化

`ContextOrchestrator` 当前是：

- 扫描目录
- 做少量关键词匹配
- 生成推荐文件列表

问题在于：

- 推荐规则召回率低
- 文件命名稍有偏差就匹配不到
- 无权重、无排序依据、无命中证据

### 2.5 Assistant 历史会污染下一轮 prompt

当前 session 存储采用：

- `messages` 用于展示
- 同一份 `messages` 也会回灌给模型

如果 assistant 曾错误声称：

- “已写入某文件”
- “已读取某文件”
- 伪造 `Context Trace`
- 输出伪工具调用示例

这些文本会进入下一轮 `prompt.messages`，造成 provenance 污染。

### 2.6 自动 trace 与人工 trace 混在同一目录

当前 `context_trace/` 里同时存在：

- 自动生成的 session envelope
- agent 手工 `write_file` 生成的任务型 trace

两者 schema 完全不同，但目录混用，容易误判来源。

## 3. 改造目标

本方案要实现的目标分三层：

### 3.1 审计目标

让开发者能稳定回答：

1. 本轮 prompt 的 system/user/history 分别来自哪里
2. 哪些文件被注入正文，哪些只是推荐项
3. 为什么选了这些文件
4. 哪些内容被截断、跳过、降级
5. 本轮 assistant 是否引用了未真实读取的文件

### 3.2 产品目标

让前端可以稳定展示：

- 每回合 prompt 快照
- 上下文选择树
- 读取与注入的区别
- 历史污染告警

### 3.3 工程目标

在不一次性重构过大的前提下，优先修正：

1. trace 粒度
2. provenance 字段
3. model history 清洗

## 4. 非目标

本计划暂不处理以下事项：

- 不更换底层 LLM 或 agent 框架
- 不做复杂 RAG 检索器接入
- 不在第一阶段引入向量库
- 不重写前端所有 trace 展示逻辑
- 不删除现有 `messages` 展示数据

## 5. 推荐方案

推荐分三阶段落地。

### Phase A: 修正 Trace 粒度与基础 provenance

优先级：P0

目标：

- 每回合生成独立 trace
- 不再只保留 session 最新 prompt
- 为 prompt 增加最小 provenance 字段

建议新增 trace envelope：

```json
{
  "trace_id": "T20260315_0001",
  "session_id": "213b5d63c615",
  "turn_index": 7,
  "timestamp": "2026-03-15T17:01:42+08:00",
  "user_message": "...",
  "prompt": {
    "system_prompt": "...",
    "messages": [...]
  },
  "prompt_provenance": {
    "system_blocks": [...],
    "history_summary": {...},
    "context_read": [...],
    "context_recommended": [...],
    "skills_snapshot_used": true
  },
  "tool_calls": [...]
}
```

同时保留 session 级 envelope，但它不再承担“完整 prompt 回放”的职责，只保留：

- 展示消息
- 轮次索引
- trace 文件列表

### Phase B: 建立上下文选择可解释链路

优先级：P1

目标：

- 让 `ContextOrchestrator` 输出的不只是 `memory_map`
- 还要输出“候选集 + 选择原因 + 裁剪状态”

建议把当前返回结构升级为：

```json
{
  "memory_map": {...},
  "context_read": [
    {
      "path": "memory/identity/project.md",
      "layer": "memory_identity",
      "mode": "injected",
      "why": "default_required",
      "status": "full"
    }
  ],
  "context_recommended": [
    {
      "path": "memory/packs/PACK_skill_mechanism_evidence_chain_reference.md",
      "why": "keyword:机理",
      "score": 0.82
    }
  ],
  "selection_notes": []
}
```

这里最关键的是区分三类状态：

- `injected`: 正文已进入 system prompt
- `recommended`: 仅作为导航提示
- `skipped`: 本可选但因预算或规则被跳过

### Phase C: 历史消息双轨化

优先级：P1

目标：

- 展示历史与模型历史分离
- 阻断 assistant 错误陈述污染下一轮 prompt

推荐策略：

- `messages`: 原始展示历史，保真
- `model_messages`: 清洗后历史，仅供模型使用

第一步可以不改存储 schema，先在 `SessionManager.load_session_for_agent()` 中生成清洗视图。

后续若验证有效，再正式拆分持久化结构。

## 6. 具体改动点

### 6.1 `backend/graph/trace_writer.py`

改造目标：

- 支持按 turn 写入独立 trace 文件
- session 文件不再覆盖最新 `prompt`
- 增加 `trace_id / turn_index / session_id`

建议新增方法：

- `write_turn_trace(...)`
- `append_session_trace_index(...)`

建议目录结构：

```text
context_trace/
  sessions/
    213b5d63c615.json
  turns/
    T20260315_0001.json
    T20260315_0002.json
```

如果不想改目录，也至少要改成：

- `context_trace/{session_id}/T0001.json`

### 6.2 `backend/api/chat.py`

改造目标：

- 在写 trace 前收集本轮 provenance 信息
- 明确区分 display history 与 model history

建议新增：

- `prompt_provenance` 组装函数
- `turn_index` 生成逻辑
- 调试日志：记录原始 history 条数、清洗后 history 条数、context 注入数量

### 6.3 `backend/graph/prompt_builder.py`

改造目标：

- 返回结构化 block 信息，而不只是最终大字符串

建议新增接口：

```python
build_result = prompt_builder.build(...)

{
  "system_prompt": "...",
  "blocks": [
    {"name": "identity", "source": "builtin", "chars": 58},
    {"name": "tooling", "source": "builtin", "chars": 1024},
    {"name": "project_context", "source": "files", "files": [...]}
  ]
}
```

这样 trace 可以直接记录：

- block 顺序
- 每块来源
- 每块字符数

而不是事后对大字符串做反向分析。

### 6.4 `backend/graph/context_orchestrator.py`

改造目标：

- 从“目录扫描器”升级为“上下文选择器”

建议新增能力：

1. 输出候选文件与命中原因
2. 区分默认注入、推荐、跳过
3. 记录预算裁剪结果
4. 提供稳定排序依据

建议规则优先级：

1. workspace 固定协议文件
2. Layer1 长期稳定文件
3. route 命中的 phase/timeline 文件
4. query 命中的 task/pack/concept
5. 技能强相关引用文件

### 6.5 `backend/graph/session_manager.py`

改造目标：

- 对 assistant 历史做模型侧清洗

建议新增方法：

- `_sanitize_assistant_message_for_model()`
- `_strip_trace_sections()`
- `_strip_false_completion_claims()`
- `_strip_pseudo_tool_call_examples()`
- `_compress_long_assistant_message()`

清洗原则：

- 保留用户消息原文
- assistant 消息保留结论、文件路径、缺口
- 删除 `Context Trace` / `Memory Patch` 口径性文本
- 删除伪工具调用示例
- 删除长段旧 prompt 引用

### 6.6 `backend/workspace-templates/context_trace/*`

改造目标：

- 模板文档与真实实现对齐

需要同步更新：

- `README.md`
- `TRACE_TEMPLATE.json`

避免继续出现“文档写每回合一份，实际却是 session 覆盖”的偏差。

## 7. 数据结构建议

### 7.1 Turn Trace

```json
{
  "trace_id": "T20260315_0007",
  "session_id": "213b5d63c615",
  "turn_index": 7,
  "timestamp": "2026-03-15T17:01:42+08:00",
  "request": {
    "route": "mechanism_closure",
    "user_message": "请你分析..."
  },
  "prompt": {
    "system_prompt": "...",
    "messages": [...]
  },
  "prompt_provenance": {
    "metadata": {...},
    "blocks": [...],
    "context_read": [...],
    "context_recommended": [...],
    "history": {
      "raw_count": 10,
      "model_count": 6,
      "removed_sections": [
        "assistant_context_trace",
        "pseudo_tool_calls"
      ]
    }
  },
  "tool_calls": [...],
  "warnings": []
}
```

### 7.2 Session Index

```json
{
  "session_id": "213b5d63c615",
  "title": "研究会话 03/15 16:52",
  "created_at": "...",
  "updated_at": "...",
  "turns": [
    {
      "trace_id": "T20260315_0006",
      "user_message_preview": "请你将 pack 中的 skill mechanism...",
      "timestamp": "..."
    }
  ]
}
```

## 8. 分阶段实施计划

### Stage 1: P0 最小闭环

目标：

- 让每回合 prompt 可回放

改动：

1. turn 级 trace 文件落盘
2. session 文件只做索引
3. `TraceWriter` 新 schema
4. 补基础测试

验收标准：

- 任意 session 至少能回放最近 10 轮的独立 prompt
- 最新轮不会覆盖旧轮

### Stage 2: P1 provenance 补齐

目标：

- 解释 prompt 是怎么选出来的

改动：

1. `PromptBuilder` 返回结构化 blocks
2. `ContextOrchestrator` 记录 `context_read/context_recommended`
3. trace 增加 `prompt_provenance`

验收标准：

- 前端或开发者可以看到：
  - 哪些文件被注入
  - 哪些文件只是推荐
  - 哪些文件被跳过
  - 跳过原因是什么

### Stage 3: P1 历史清洗

目标：

- 阻断 assistant 历史污染

改动：

1. `SessionManager.load_session_for_agent()` 引入清洗逻辑
2. 补针对伪工具调用、伪完成声称、冗长 trace 文本的测试

验收标准：

- 错误 assistant 回复不会再被完整回灌给模型
- 展示历史不变，模型历史变安全

### Stage 4: P2 规则升级

目标：

- 提高推荐与注入质量

改动：

1. route-aware 规则
2. skill-aware 推荐
3. 文件预算与裁剪策略
4. `skipped/truncated` 记录

验收标准：

- 推荐文件命中率提升
- trace 能解释预算裁剪行为

## 9. 测试计划

建议新增测试文件：

- `backend/tests/test_turn_trace_writer.py`
- `backend/tests/test_prompt_provenance.py`
- `backend/tests/test_context_orchestrator_selection.py`
- `backend/tests/test_session_history_sanitization.py`

核心覆盖点：

1. 同一 session 多轮对话会产生多个 turn trace
2. turn trace 不会覆盖旧 prompt
3. `prompt_provenance.blocks` 顺序与最终 prompt 顺序一致
4. `context_read` 能区分 `injected/recommended/skipped`
5. assistant 伪造“已写入”文本不会进入 model history
6. 手工 trace 与自动 trace 不会再混淆

## 10. 风险与权衡

### 10.1 存储量上升

每回合独立 trace 会增加 JSON 文件数量。

应对：

- session 只保留索引
- turn trace 可按时间清理或归档

### 10.2 实现复杂度上升

`PromptBuilder` 和 `ContextOrchestrator` 将从“字符串拼接器”升级为“结构化构建器”。

应对：

- 先保留向后兼容接口
- 新增结构化返回，不立即移除旧接口

### 10.3 前后端协议要同步

trace schema 调整后，前端展示需要适配。

应对：

- 先支持双 schema 读取
- 旧字段保留一段时间

## 11. 最终建议

建议按以下优先顺序执行：

1. 先修 trace 粒度，不再覆盖历史 prompt
2. 再补 `prompt_provenance`，把“结果”变成“可解释结果”
3. 再做 session history sanitization，阻断污染链
4. 最后升级上下文选择规则与预算策略

原因很直接：

- 不先修 turn trace，就没有稳定回放基础
- 不补 provenance，就只能看到大字符串，不能解释来源
- 不做历史清洗，错误 assistant 文本还会继续污染后续 prompt

## 12. 建议的首批交付

如果只做一轮迭代，建议把范围控制在以下 4 项：

1. turn 级 trace 文件
2. session 索引文件
3. `prompt_provenance.blocks + context_read`
4. `load_session_for_agent()` 的 assistant 清洗

这是投入产出比最高的一组改动，能显著提升 prompt trace 的可靠性和可审计性。
