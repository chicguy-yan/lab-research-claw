# Phase 5.3 开发日志

> 目标：把 workspace 从全局单例改成请求级上下文，实现多 workspace 运行时切换、命名，并接入 bootstrap 生命周期

## 文件创建/更新记录

### Step A：新建 WorkspaceRuntimeRegistry

- 创建：`backend/runtime/__init__.py`
- 创建：`backend/runtime/workspace_registry.py`
  - `SharedAgentResources`：共享 LLM + FetchURLTool（进程级单例）
  - `WorkspaceRuntime`：per-workspace 隔离的 SessionManager + workspace-scoped tools
  - `WorkspaceRuntimeRegistry`：中央注册表，负责 workspace 生命周期、manifest CRUD、runtime 懒加载
  - 从 `app.py` 迁入：`_migrate_workspace()`、`_normalize_workspace_skills()`、`_normalize_skill_entry()`
  - manifest 读写：`load_manifest()`、`save_manifest()`、`update_bootstrap_status()`
  - workspace provision：`create_workspace()` 写 manifest 并设 `bootstrap_status=pending`
  - default workspace：`ensure_default_workspace()` 为已有 default 补 manifest

### Step B：新建 runtime_context helper

- 创建：`backend/api/runtime_context.py`
  - `get_registry(request)` → 从 app.state 取 registry
  - `resolve_workspace_id(request, body_workspace_id)` → body 优先 > X-Workspace-Id header > default
  - `get_runtime(request, body_workspace_id)` → 返回 WorkspaceRuntime，404 if not found

### Step C：改造 app.py 启动逻辑

- 修改：`backend/app.py`
  - 删除全局 `SessionManager` / `AgentManager` 初始化
  - 删除 `_migrate_workspace` / `_normalize_workspace_skills` 等函数（已迁入 registry）
  - 启动时创建 `WorkspaceRuntimeRegistry`，调用 `initialize_shared()` + `ensure_default_workspace()`
  - 预热 default runtime
  - 挂载 `app.state.workspace_registry`
  - 保留 `app.state.session_manager` 向后兼容（指向 default runtime）
  - 注册 `/api/workspaces` 路由

### Step D：改造现有 API 为 workspace-aware

- 修改：`backend/api/sessions.py`
  - 所有端点改用 `get_runtime(request).session_manager`
- 修改：`backend/api/files.py`
  - `_get_workspace()` 改用 `get_runtime(request).workspace_dir`
- 修改：`backend/api/assets.py`
  - upload/download 改用 `get_runtime(request).workspace_dir`
- 修改：`backend/api/chat.py`
  - `ChatRequest` 新增 `workspace_id` 字段
  - 不再使用 `AgentManager.astream()`
  - 改为每请求用 `shared.llm + all_tools + system_prompt` 构建 agent
  - agent streaming 逻辑从 `graph/agent.py` 内联到 chat.py

### Step E：新建 Workspace 管理 API

- 创建：`backend/api/workspaces.py`
  - `GET /api/workspaces` — 列出所有 workspace（含 bootstrap_status、session_count）
  - `POST /api/workspaces` — provision 新 workspace（bootstrap_status=pending）
  - `PUT /api/workspaces/{workspace_id}` — 重命名（只改 manifest）
  - `GET /api/workspaces/{workspace_id}/manifest` — 读取 manifest
  - `POST /api/workspaces/{workspace_id}/bootstrap/start` — 启动 bootstrap（pending|failed → running）

### Step F：/api/agents 兼容处理

- 修改：`backend/api/agents.py`
  - `GET /api/agents` 内部委托 `registry.list_workspaces()`，映射为 agent 格式
  - `POST /api/agents` 内部委托 `registry.create_workspace()`，额外写 IDENTITY.md
  - 返回中增加 `_note` 字段标记 deprecated

### Step G：更新 workspace-templates/BOOTSTRAP.md

- 覆盖：`backend/workspace-templates/BOOTSTRAP.md`
  - 用 `docs/BOOSTRAP-new.md` 的 v1.0 内容替换旧版
  - 新版明确 preconditions（manifest 存在、bootstrap_status=pending|failed、runtime 可用）
  - 新版明确 manifest 由 bootstrap runner 更新，不由 agent 直接写
  - 新版包含 Phase A-J 完整初始化流程 + guardrails

### Step H：前端改造

- 修改：`frontend/index.html`
  - 顶栏新增 workspace 选择器（下拉框 + 新建 + 重命名按钮）
  - 顶栏新增 session 重命名按钮
  - `state` 新增 `currentWorkspaceId`，持久化到 localStorage
  - `STORAGE_KEYS` 新增 `workspaceId`
  - `apiFetch()` 统一注入 `X-Workspace-Id` header
  - `sendMessage()` body 中新增 `workspace_id` 字段
  - 新增函数：`loadWorkspaces()`、`switchWorkspace()`、`createWorkspace()`、`renameWorkspace()`、`renameSession()`
  - `refreshWorkspace()` 增加 `loadWorkspaces()` 调用
  - `switchWorkspace()` 切换时清空 session/chat/file viewer/trace 状态
  - `loadWorkspaces()` 启动时验证 localStorage 中的 workspace_id 是否仍存在

## 已处理问题

1. **LLM 多实例浪费**
   - 问题：原计划每个 workspace 持有独立 AgentManager，会重复创建 ChatOpenAI
   - 处理：拆分为 SharedAgentResources（共享 LLM + FetchURLTool）和 WorkspaceRuntime（隔离 tools），每请求临时组装 agent

2. **全局单例残留**
   - 问题：app.py 中 `_migrate_workspace` 等函数与 registry 职责重叠
   - 处理：全部迁入 `workspace_registry.py`，app.py 中保留空壳 `ensure_default_workspace()` 待后续清理

3. **已有 workspace 缺少 manifest**
   - 问题：Phase 5.3 之前创建的 workspace 没有 `workspace_manifest.json`
   - 处理：`ensure_default_workspace()` 和 `list_workspaces()` 中自动补写 manifest，default workspace 设为 `completed`

## 测试结果

| # | 测试项 | 命令 | 预期 | 状态 |
|---|--------|------|------|------|
| 1 | 模块导入 | `python -c "from runtime.workspace_registry import ..."` | 无报错 | PASS |
| 2 | API 路由导入 | `python -c "from api.workspaces import router"` | 无报错 | PASS |
| 3 | 全量路由导入 | `python -c "from api.chat import router; ..."` | 所有 router 无报错 | PASS |
| 4 | 启动流程 | `python -c "import app; asyncio.run(app.on_startup())"` | Registry 初始化成功 | PASS |
| 5 | 已有 workspace 识别 | 启动后检查 list_workspaces | 返回 default + 已有 workspace | PASS |
| 6 | default manifest 补写 | 启动后检查 default manifest | bootstrap_status=completed | PASS |

## Phase 5.3 产出汇总

- 新建文件 4 个：`runtime/__init__.py`、`runtime/workspace_registry.py`、`api/runtime_context.py`、`api/workspaces.py`
- 修改文件 6 个：`app.py`、`api/chat.py`、`api/sessions.py`、`api/files.py`、`api/assets.py`、`api/agents.py`
- 更新模板 1 个：`workspace-templates/BOOTSTRAP.md`
- 修改前端 1 个：`frontend/index.html`
- 新增 API 端点 5 个：workspace CRUD + bootstrap start
- 核心架构变更：全局单例 → 请求级 workspace runtime

## Phase 5.3 → Phase 5.4 / 6.0 衔接

| 产出 | 后续依赖 |
|------|----------|
| `WorkspaceRuntimeRegistry` | bootstrap runner 实际执行逻辑（读 BOOTSTRAP.md、执行 scope discovery、写 workspace_scope.md） |
| `POST /api/workspaces/{id}/bootstrap/start` | bootstrap runner 的完整实现（当前只做状态流转，不执行初始化正文） |
| `workspace_manifest.json` + `bootstrap_status` | 前端 bootstrap 引导界面（pending/failed 时阻止进入普通 chat） |
| `X-Workspace-Id` header 机制 | 前端 bootstrap 界面需要在初始化对话中也带此 header |
| `graph/agent.py` AgentManager | ⚠️ 不再被 chat.py 直接使用，但未删除；后续可清理或保留为独立测试入口 |
