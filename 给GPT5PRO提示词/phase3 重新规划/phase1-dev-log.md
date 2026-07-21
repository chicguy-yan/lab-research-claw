# Phase 1 开发日志

> 目标：完成后端最小可用链路（`POST /api/chat` SSE）

## 文件创建/更新记录

### Step 0 文档同步
- 更新：`docs/architecture-summary.md`
  - 明确 done 仅由 `api/chat.py` 发送
  - 明确 Session 消息文件格式（后经 Step 10 改为 envelope schema `{"messages": [...], "traces": []}`）
  - 明确会话端点为 5 个（含 history）
  - 补充 `create_agent` 版本锁定说明
- 更新：`docs/phase1-dev-plan.md`
  - 覆盖为修正后的 Phase 1 正式计划

### Step 1 依赖与环境
- 创建：`backend/.env.example`
- 更新：`backend/requirements.txt`

### Step 2-4 核心模块
- 创建：`backend/config.py`
- 创建：`backend/graph/session_manager.py`
- 创建：`backend/graph/agent.py`

### Step 5-7 API 与入口
- 创建：`backend/api/__init__.py`
- 创建：`backend/api/sessions.py`
- 创建：`backend/api/chat.py`
- 创建：`backend/app.py`

### Step 8 Bug 修复（2026-03-07）
- 修复：`backend/graph/agent.py`
  - **Bug 7**: `stream_mode` + `node_name` 不匹配导致无 token 输出
  - **Bug 8**: 配置文件 base_url 与 API key 来源不匹配
  - 详见下方 Bug 7、Bug 8 记录

### Step 9 文档输出（2026-03-07）
- 创建：`docs/phase1-architecture.html` — Phase 1 架构可视化（可浏览器直接打开）

### Step 10 风险修复（2026-03-07）
- 修复：**依赖版本策略**（高风险 → 已解决）
  - `requirements.txt` 收窄范围：`langchain>=1.1.1,<1.2`（避开 v1.1.0 的 create_agent 消失问题）
  - 新增 `requirements.lock`：精确版本锁（langchain==1.1.3 等），已通过 SSE 端到端验证
- 修复：**Session/Trace schema 冲突**（中风险 → 已解决）
  - `context_trace/{session_id}.json` 从纯数组改为 envelope schema：`{"messages":[], "traces":[]}`
  - SessionManager 仅读写 `messages`，TraceWriter（Phase 3）仅读写 `traces`，互不污染
  - 自动兼容旧版纯数组格式（`isinstance(data, list)` 检测并迁移）
- 更新：`docs/phase1-dev-plan.md` — 关键决策同步
- 更新：`docs/architecture-summary.md` — 风险汇总同步（6.2 / 6.10 标记已解决）

## 已处理问题（Bug/风险）

1. **done 事件重复风险**
   - 问题：Agent 层与 API 层可能重复发 done。
   - 处理：`graph/agent.py` 不发 done，统一在 `api/chat.py` 流结束后发送。

2. **Session schema 与架构不一致风险**
   - 问题：把消息和元数据混在同一对象会影响后续 TraceWriter。
   - 处理：`context_trace/{session_id}.json` 使用 envelope schema `{"messages": [...], "traces": []}`（Step 10 修正），SessionManager 读写 `messages` 字段。元数据进 `_sessions_index.json`。

3. **LangChain API 兼容风险**
   - 问题：`create_agent` 在部分版本路径变化。
   - 处理：依赖范围锁定 `langchain>=1.0,<1.2`，并保留异常事件透传。

4. **依赖冲突（langgraph 版本）**
   - 问题：`langchain>=1.0` 依赖 `langgraph>=1.0.2`，与旧约束 `langgraph<0.4` 冲突。
   - 处理：`requirements.txt` 调整为 `langgraph>=1.0.2,<1.1`。

5. **启动失败（SOCKS 代理依赖缺失）**
   - 问题：环境启用了 SOCKS proxy，缺少 `socksio` 导致 `ChatOpenAI` 初始化失败。
   - 处理：依赖新增 `httpx[socks]>=0.28,<0.29`。

6. **启动失败（未配置 OPENAI_API_KEY）**
   - 问题：本地未配置 key 时，`ChatOpenAI` 初始化抛错，服务无法启动。
   - 处理：`AgentManager.initialize()` 加入 key 判空保护，不阻断服务启动；`/api/chat` 返回 `error` 事件提示配置。

7. **SSE 无 token 输出（stream_mode + node_name 不匹配）**
   - 问题：`agent.py` 使用 `stream_mode="updates"` + `node_name == "agent"` 判断，但 `create_agent`（LangChain v1.1.3）返回的节点名为 `"model"`，导致所有流式输出被跳过。同时 `stream_mode="updates"` 只返回完整 node 输出，不支持逐 token 流式。
   - 处理：改为 `stream_mode="messages"`，返回 `(AIMessageChunk, metadata)` 元组；通过 `metadata["langgraph_node"]` 判断节点名（`"model"` 或 `"tools"`）。实现了真正的逐 token SSE 推送。
   - 影响：这是 Phase 1 的关键 Bug，修复后 SSE 链路完全跑通。

8. **API key 配置不匹配**
   - 问题：`.env.example` 默认 `OPENAI_BASE_URL=https://api.xiaomimimo.com/v1`，但实际使用 Kimi（Moonshot AI）的 API key，导致 401 鉴权失败。
   - 处理：`.env` 需根据实际 API 提供方配置正确的 base_url 和 model。Kimi 的正确配置为 `OPENAI_BASE_URL=https://api.moonshot.cn/v1`，`OPENAI_MODEL=kimi-k2-turbo-preview`。

## 测试方法

### 1) 启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

### 2) 会话 CRUD
```bash
curl -X POST http://localhost:8002/api/sessions -H "Content-Type: application/json" -d '{"title":"test"}'
curl http://localhost:8002/api/sessions
curl http://localhost:8002/api/sessions/{id}/history
curl -X PUT http://localhost:8002/api/sessions/{id} -H "Content-Type: application/json" -d '{"title":"renamed"}'
curl -X DELETE http://localhost:8002/api/sessions/{id}
```

### 3) SSE
```bash
curl -N -X POST http://localhost:8002/api/chat -H "Content-Type: application/json" -d '{"message":"你好","session_id":"test","stream":true}'
```

## 结果

- [x] 服务可启动（在未配置 `OPENAI_API_KEY` 情况下仍可启动）
- [x] 会话 CRUD 正常（create/list/rename/delete/history 全部验证通过）
- [x] SSE token 逐字流式正常（Kimi API, 2026-03-07 验证通过）
- [x] done 仅发送一次（已验证）
- [x] 对话持久化写入正确（user + assistant 消息均写入 messages 数组）

### 第一次 smoke test（2026-03-06，无 API key）

- `GET /` → `{"status":"ok","service":"experimental-research-openclaw-backend"}`
- `POST /api/sessions` → 成功返回 session 元数据（示例 id: `526da66cf1f8`）
- `GET /api/sessions` → 返回会话列表，按 `updated_at` 排序
- `GET /api/sessions/{id}/history` → 返回 `messages: []`（新会话）
- `POST /api/chat`（无 API key）→
  - 收到 `event: error`（提示配置 OPENAI_API_KEY）
  - 收到 `event: done`（仅一次）
  - 会话文件 `context_trace/{id}.json` 写入 user 消息

### 第二次 smoke test（2026-03-07，Kimi API key, Bug 7/8 修复后）

**环境配置**:
```
OPENAI_API_KEY=sk-k3bQ...VWHP
OPENAI_BASE_URL=https://api.moonshot.cn/v1
OPENAI_MODEL=kimi-k2-turbo-preview
```

**测试结果**:

1. `GET /` → `{"status":"ok","service":"experimental-research-openclaw-backend"}` ✅
2. `POST /api/sessions {"title":"Phase1 SSE Test"}` → 返回 `id: bff99281ab77` ✅
3. `GET /api/sessions` → 返回会话列表，按 `updated_at` 倒序 ✅
4. `GET /api/sessions/bff99281ab77/history` → `messages: []` ✅
5. `PUT /api/sessions/bff99281ab77 {"title":"Renamed Test"}` → title 更新成功 ✅
6. `DELETE /api/sessions/bff99281ab77` → 删除成功 ✅
7. `POST /api/chat {"message":"请用一句话介绍你自己"}` → **SSE 逐 token 流式正常** ✅
   ```
   event: token  data: {"content": "我是"}
   event: token  data: {"content": "Open"}
   event: token  data: {"content": "Cl"}
   event: token  data: {"content": "aw"}
   event: token  data: {"content": "里"}
   event: token  data: {"content": "随时"}
   event: token  data: {"content": "待命"}
   ...
   event: token  data: {"content": "。"}
   event: done   data: {"session_id": "ca3335c66327"}
   ```
8. 持久化验证 → `context_trace/ca3335c66327.json` 包含完整 user + assistant 消息 ✅
9. `_sessions_index.json` 元数据正确更新 ✅

## workspace-templates 对齐检查报告（2026-03-07）

### 对照 PRD §4.8.3 验收标准

| 要求 | 状态 | 说明 |
|------|------|------|
| Prompt 组件（SOUL/IDENTITY/USER/AGENTS/BOOTSTRAP/MEMORY/TOOLS/README.md） | ✅ 完整 | 8 个文件均存在于模板根目录 |
| `memory/identity/`（user.md / project.md / lab_context.md / context_budget.md） | ✅ 完整 | Layer 1 四个文件齐全 |
| `memory/timeline/180d_index.md` | ✅ 存在 | |
| `memory/timeline/phases/`（P01-P05） | ✅ 完整 | 5 个阶段文件齐全 |
| `memory/timeline/weeks/` | ✅ 存在 | `_WEEK_TEMPLATE.md` 模板 |
| `memory/timeline/days/` | ✅ 存在 | `_DAY_TEMPLATE.md` 模板 |
| `memory/timeline/stage_reports/` | ✅ 存在 | `_STAGE_REPORT_TEMPLATE.md` 模板 |
| `memory/concepts/CONCEPT_TEMPLATE.md` | ✅ 存在 | |
| `memory/tasks/TASK_TEMPLATE.md` | ✅ 存在 | |
| `memory/packs/PACK_TEMPLATE.md` | ✅ 存在 | |
| `assets/data/` | ✅ 存在 | README.md 占位 |
| `assets/figures/` | ✅ 存在 | README.md 占位 |
| `assets/ppt_pack/` | ✅ 存在 | README.md 占位 |
| **`assets/uploads/`** | **❌ 缺失** | PRD §4.8.3 要求，模板中未创建 |
| `context_trace/`（README + TRACE_TEMPLATE.json） | ✅ 完整 | |

### 结论

- 29/30 项对齐，仅 `assets/uploads/` 目录缺失
- 需在 Phase 2 补充该目录（在 workspace-templates 中添加 `assets/uploads/README.md`）
- Prompt 组件文件放在模板根目录（而非 `workspace/` 子目录），与 TAD 项目结构一致
