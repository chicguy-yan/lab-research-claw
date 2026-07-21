# Phase 2 开发计划：文件系统 API + Agent CRUD

> 基于 PRD v0.2 + TAD v0.2 + architecture-summary.md
> **前置**：Phase 1 已完成（SSE chat + 会话 CRUD，2026-03-07 验证通过）
> **目标**: `curl GET /api/files/tree` → 返回 workspace 目录树；`curl POST /api/agents` → 创建新 Agent workspace
> **最后更新**: 2026-03-07

---

## Phase 1 → Phase 2 衔接

| Phase 1 提供 | Phase 2 如何使用 |
|-------------|-------------|
| `app.py` 路由注册模式（`include_router`） | 新增 `files_router` + `agents_router` |
| `config.py` 路径常量（`OPENCLAW_DIR` / `WORKSPACE_TEMPLATES_DIR`） | Files API 解析 workspace 路径；Agents API 定位模板目录 |
| `SessionManager._workspace_dir` | Files API 通过 `request.app.state.session_manager._workspace_dir` 获取当前 workspace 根目录 |
| `sessions.py` API 风格（Pydantic body + HTTPException） | Phase 2 复用相同 router + Pydantic 风格 |
| `ensure_default_workspace()` | Phase 2 Agents API 扩展为多 workspace（`workspace-{agent_id}`） |

| Phase 2 产出 | Phase 3+ 依赖方 | 可靠性 |
|-------------|-------------|--------|
| `GET /api/files/tree` | Phase 3 ContextOrchestrator 发现 memory 文件 | ✅ 可直接使用 |
| `GET /api/files` 读文件 | Phase 3 PromptBuilder 读取 Prompt 组件注入 system prompt | ✅ 可直接使用 |
| `POST /api/files` 写文件 | Phase 3 TraceWriter 落盘 / Phase 6 Monaco 编辑器保存 | ✅ 可直接使用 |
| `GET /api/files/preview` | Phase 6 前端文件浏览器预览 | ✅ 可直接使用 |
| `POST /api/agents` 创建 Agent | **Phase 6** 前端 Agent 切换 | ⚠️ 仅创建目录，不切换运行上下文（Phase 3 不应依赖此能力） |
| `resolve_safe_path()` | 全局路径安全工具，解决 PRD §6.9 高风险 | ✅ 已修复前缀绕过 |

---

## 关键决策（已确认）

1. **路径安全策略** — `resolve_safe_path(base_dir, user_path)` 三层防护：
   - 禁止 `..` 路径分量
   - `Path.resolve()` 解析符号链接后检查是否仍在 `base_dir` 内
   - 写入操作仅允许 `memory/`、`assets/`、`context_trace/` 三个前缀
   - 违规返回 HTTP 403，解决 PRD §6.9 高风险

2. **Workspace 定位** — Files API 通过 `request.app.state.session_manager._workspace_dir` 获取当前 workspace 根目录。Phase 2 暂为 `workspace-default`，Phase 6 支持 Agent 切换后动态变更。

3. **Agent workspace 命名** — `.openclaw/workspace-{agent_id}`，每个 Agent 独立一套完整的 workspace-templates 副本。`workspace-default` 为默认 Agent。

4. **Agent 身份** — `POST /api/agents` 创建时写入 `IDENTITY.md`（`# {name}`）。列举时优先从 `Name（名字）：` 字段提取，回退到首行标题（排除模板标题）。模板默认 workspace 的 IDENTITY.md 首行为文档标题，非 agent 名。

5. **目录树过滤** — 隐藏 `.` 和 `_` 开头的文件/目录（避免暴露 `_sessions_index.json` 等内部文件）。目录优先排序，默认深度 3 层。

6. **无新依赖** — Phase 2 不引入新的 Python 包，全部使用标准库 + Phase 1 已有依赖。

---

## 新建/修改文件清单

### 新建（4 个）

```
backend/
├── graph/
│   └── path_utils.py             # 路径安全工具（resolve_safe_path）
├── api/
│   ├── files.py                  # 文件 CRUD + tree + preview（4 个端点）
│   └── agents.py                 # Agent CRUD（2 个端点）
└── workspace-templates/
    └── assets/
        └── uploads/
            └── README.md         # 补充 PRD §4.8.3 缺失目录
```

### 修改（1 个）

```
backend/
└── app.py                        # 注册 files_router + agents_router
```

共 5 个文件变更。不修改 Phase 1 核心模块（`agent.py` / `session_manager.py` / `chat.py`）。

---

## API 端点（6 个）

### Files API（4 个）

| 方法 | 端点 | 功能 | 路径安全 |
|------|------|------|----------|
| GET | `/api/files?path=...` | 读取文件内容（UTF-8 文本） | `resolve_safe_path` 读模式 |
| POST | `/api/files` | 保存文件 `{path, content}`，自动创建父目录 | `resolve_safe_path` 写模式（白名单） |
| GET | `/api/files/tree?path=&max_depth=3` | 递归目录树，嵌套 JSON | `resolve_safe_path` 读模式 |
| GET | `/api/files/preview?path=&max_chars=500` | 文件内容截断预览 | `resolve_safe_path` 读模式 |

### Agents API（2 个）

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/agents` | 列出所有 Agent workspace（扫描 `.openclaw/workspace-*`） |
| POST | `/api/agents` | 创建新 Agent workspace（`copytree` + 写 `IDENTITY.md`） |

---

## 核心模块说明

### `graph/path_utils.py`

```python
WRITABLE_PREFIXES = ("memory/", "assets/", "context_trace/")

class PathSecurityError(Exception): ...

def resolve_safe_path(base_dir, user_path, *, require_writable=False) -> Path:
    # 1. 禁止 ".." 分量
    # 2. resolve() 解析符号链接
    # 3. 检查结果仍在 base_dir 下
    # 4. require_writable=True 时检查白名单前缀
```

### `api/files.py`

- `_get_workspace(request)` — 从 `app.state.session_manager._workspace_dir` 获取 workspace
- 所有端点统一 `try/except PathSecurityError → 403`
- 目录树递归函数 `_build_tree()` 跳过 `.` / `_` 开头文件，目录优先排序

### `api/agents.py`

- `agent_id` 校验：正则 `^[a-zA-Z0-9_-]+$`，最长 64 字符
- 创建流程：检查不存在 → `copytree(workspace-templates)` → 写入 `IDENTITY.md`
- 列举流程：扫描 `.openclaw/workspace-*` 目录，从 `IDENTITY.md` 提取 agent 名称（优先 `Name（名字）` 字段，回退到非模板标题行）

---

## 实现顺序

1. 补充 `workspace-templates/assets/uploads/README.md`（PRD §4.8.3 缺失项）
2. 创建 `graph/path_utils.py`
3. 创建 `api/files.py`（4 个端点）
4. 创建 `api/agents.py`（2 个端点）
5. 修改 `app.py`（注册 2 个新 router）
6. 启动 + curl 验证全部端点
7. 输出 docs（`phase2-dev-plan.md` + `phase2-dev-log.md` + `phase2-architecture.html`）

---

## 验证方式

### 测试 1：服务启动
```bash
cd backend && python3 -m uvicorn app:app --port 8002 --reload
# 预期：无报错，Phase 1 + Phase 2 路由全部注册
```

### 测试 2：目录树
```bash
curl http://localhost:8002/api/files/tree
# 预期：返回 workspace-default 完整目录结构

curl "http://localhost:8002/api/files/tree?path=memory/"
# 预期：仅返回 memory/ 子树
```

### 测试 3：读文件
```bash
curl "http://localhost:8002/api/files?path=memory/identity/project.md"
# 预期：返回 {"path": "memory/identity/project.md", "content": "..."}
```

### 测试 4：路径安全（应返回 403）
```bash
curl "http://localhost:8002/api/files?path=../../etc/passwd"
# 预期：403 + "Path traversal detected"
```

### 测试 5：保存文件
```bash
curl -X POST http://localhost:8002/api/files \
  -H "Content-Type: application/json" \
  -d '{"path":"memory/identity/project.md","content":"# Test Project\n\nPhase 2 验证"}'
# 预期：{"path": "memory/identity/project.md", "saved": true}
```

### 测试 6：保存到非白名单目录（应返回 403）
```bash
curl -X POST http://localhost:8002/api/files \
  -H "Content-Type: application/json" \
  -d '{"path":"SOUL.md","content":"hack"}'
# 预期：403 + "Path is not in a writable directory"
```

### 测试 7：文件预览
```bash
curl "http://localhost:8002/api/files/preview?path=SOUL.md&max_chars=200"
# 预期：{"path": "SOUL.md", "preview": "...", "truncated": true/false, "total_chars": N}
```

### 测试 8：创建 Agent
```bash
curl -X POST http://localhost:8002/api/agents \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test-agent","name":"测试Agent","description":"Phase 2 验证用"}'
# 预期：返回 agent_id + workspace_dir + created_at
```

### 测试 9：列出 Agent
```bash
curl http://localhost:8002/api/agents
# 预期：{"agents": [{"agent_id": "default", ...}, {"agent_id": "test-agent", ...}]}
```

### 测试 10：重复创建 Agent（应返回 409）
```bash
curl -X POST http://localhost:8002/api/agents \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test-agent","name":"Duplicate"}'
# 预期：409 + "Agent workspace already exists"
```

---

## Phase 2 不做的事（明确边界）

- Context Orchestrator / PromptBuilder / TraceWriter（Phase 3）
- tools/ 6 个核心工具（Phase 4）
- KnowledgeIndexer / RAG（Phase 5）
- 前端（Phase 6）
- Agent 切换（当前 Files API 固定指向 workspace-default，Phase 6 支持动态切换）
- 文件上传二进制流（Phase 5，当前仅支持 UTF-8 文本写入）
- Agent 删除/重命名 API（可在 Phase 6 补充）
