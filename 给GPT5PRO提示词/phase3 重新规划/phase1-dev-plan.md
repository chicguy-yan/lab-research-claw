# Phase 1 开发计划：后端基础骨架

> 基于 PRD v0.2 + TAD v0.2 + architecture-summary.md
> **目标**: `curl POST /api/chat` → 收到 SSE token 流
> **最后更新**: 2026-03-07

---

## 关键决策（已确认）

1. **`create_agent` API** — 确认存在于 `langchain>=1.1.1`，签名 `from langchain.agents import create_agent`，返回 `CompiledStateGraph`。锁定 `langchain>=1.1.1,<1.2`（v1.1.0 的 `create_agent` 从 `__init__.py` 消失，已避开）。验证版本：1.1.3。
2. **Session 文件格式** — `context_trace/{session_id}.json` 使用 **envelope schema**：`{"messages": [...], "traces": []}`。messages 为 OpenAI messages 数组（SessionManager 读写），traces 为审计信息数组（TraceWriter 读写，Phase 3 填充）。会话元数据存储在 `context_trace/_sessions_index.json`。支持自动迁移旧版纯数组格式。
3. **done 事件归属** — AgentManager 只产出 `token`/`tool_start`/`tool_end`/`new_response` 事件，**不产出 `done`**。`done` 由 `api/chat.py` 统一发送。
4. **无降级路径** — 严禁 `AgentExecutor`，严禁 `langgraph.prebuilt.create_react_agent`（对齐 PRD §1.2 禁令）。
5. **会话端点** — 5 个（含 history），PRD §5.2 原文即为 5 个。
6. **流式模式** — 使用 `stream_mode="messages"` 实现逐 token SSE（非 `"updates"`）。`create_agent` 返回的 LLM 节点名为 `"model"`（非 `"agent"`）。
7. **依赖策略** — 双文件：`requirements.txt`（收窄范围约束）+ `requirements.lock`（精确版本锁，已验证）。可复现安装用 lock 文件。

## 依赖版本

范围约束（`requirements.txt`）：
```
langchain>=1.1.1,<1.2
langchain-openai>=0.3.34,<0.4
langchain-community>=0.3.31,<0.4
langgraph>=1.0.10,<1.1
fastapi>=0.115,<0.116
uvicorn>=0.34,<0.35
pydantic>=2.10,<3.0
python-dotenv>=1.0,<2.0
tiktoken>=0.7,<1.0
httpx[socks]>=0.28,<0.29
```

精确版本锁（`requirements.lock`，已验证）：
```
langchain==1.1.3
langchain-core==1.2.17
langchain-openai==0.3.34
langchain-community==0.3.31
langgraph==1.0.10
fastapi==0.115.14
uvicorn==0.34.3
pydantic==2.12.5
python-dotenv==1.2.2
tiktoken==0.12.0
httpx[socks]==0.28.1
```

## 新建文件清单

```
backend/
├── app.py                    # FastAPI 入口
├── config.py                 # 环境变量 + config.json 读写
├── .env.example              # 环境变量模板
├── requirements.txt          # 依赖（pin 范围）
├── api/
│   ├── __init__.py
│   ├── chat.py               # POST /api/chat (SSE 流式)
│   └── sessions.py           # 会话 CRUD (5 个端点)
└── graph/
    ├── __init__.py
    ├── agent.py               # AgentManager
    └── session_manager.py     # SessionManager
```

共 10 个文件。不修改现有 `skills/` 和 `workspace-templates/`。

---

## 验证方式

### 测试 1：服务启动
```bash
cd backend && uvicorn app:app --port 8002 --reload
# 预期：无报错，.openclaw/workspace-default/ 自动创建
```

### 测试 2：会话 CRUD
```bash
curl -X POST http://localhost:8002/api/sessions -H "Content-Type: application/json" -d '{"title":"test"}'
curl http://localhost:8002/api/sessions
curl http://localhost:8002/api/sessions/{id}/history
curl -X PUT http://localhost:8002/api/sessions/{id} -H "Content-Type: application/json" -d '{"title":"renamed"}'
curl -X DELETE http://localhost:8002/api/sessions/{id}
```

### 测试 3：SSE 对话流
```bash
curl -N -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","session_id":"test","stream":true}'
# 预期：event: token（多条）+ event: done（仅一条）
```

### 测试 4：对话持久化
```bash
cat backend/.openclaw/workspace-default/context_trace/test.json
# 预期：envelope 格式 {"messages": [...], "traces": []}
cat backend/.openclaw/workspace-default/context_trace/_sessions_index.json
# 预期：sessions 列表含 test 条目
```

---

## Phase 1 不做的事（明确边界）

- Context Orchestrator（Phase 3）
- TraceWriter（Phase 3）
- KnowledgeIndexer / RAG（Phase 5）
- tools/ 6 个核心工具（Phase 4）
- 前端（Phase 6）
- assets 上传（Phase 5）
- skills 扫描（Phase 4）
- Agent CRUD API（Phase 2）
