# Phase 2 开发日志

> 目标：文件系统 API（4 端点） + Agent CRUD（2 端点） + 路径安全工具

## 文件创建/更新记录

### Step 0 前置补全
- 创建：`backend/workspace-templates/assets/uploads/README.md`
  - 补充 PRD §4.8.3 要求的 `assets/uploads/` 目录
  - 内容：描述 Phase 5 文件上传 API 的占位说明
  - **注意**：模板补齐仅对新建 workspace 生效；已有的 workspace-default 需要迁移机制（见 Step 6 修复）

### Step 1 路径安全工具
- 创建：`backend/graph/path_utils.py`
  - `PathSecurityError` 异常类
  - `resolve_safe_path(base_dir, user_path, *, require_writable=False)` 三层防护：
    1. 禁止 `..` 路径分量
    2. `Path.resolve()` 解析符号链接后检查是否仍在 `base_dir` 内
    3. `require_writable=True` 时检查白名单前缀 `WRITABLE_PREFIXES`
  - 白名单：`("memory/", "assets/", "context_trace/")`

### Step 2 Files API
- 创建：`backend/api/files.py`（4 个端点）
  - `GET /api/files?path=` — 读取 UTF-8 文本文件
  - `POST /api/files` — 保存文件 `{path, content}`，自动创建父目录
  - `GET /api/files/tree?path=&max_depth=3` — 递归目录树（嵌套 JSON）
  - `GET /api/files/preview?path=&max_chars=500` — 截断预览
  - 辅助函数：`_get_workspace(request)` 从 `app.state.session_manager._workspace_dir` 获取 workspace
  - `_build_tree()` 递归：跳过 `.` / `_` 开头文件，目录优先排序，深度可配（1-10）

### Step 3 Agents API
- 创建：`backend/api/agents.py`（2 个端点）
  - `GET /api/agents` — 列出所有 Agent workspace（扫描 `.openclaw/workspace-*`）
  - `POST /api/agents` — 创建新 Agent workspace
  - `CreateAgentBody` Pydantic 模型：`agent_id` 正则 `^[a-zA-Z0-9_-]+$`，最长 64 字符
  - 创建流程：检查不存在 → `copytree(workspace-templates)` → 写入 `IDENTITY.md`
  - 列举流程：扫描目录 → 读取 `IDENTITY.md` 提取 agent 名称

### Step 4 路由注册
- 修改：`backend/app.py`
  - 新增 `from api.files import router as files_router`
  - 新增 `from api.agents import router as agents_router`
  - 注册：`app.include_router(files_router, prefix="/api")`
  - 注册：`app.include_router(agents_router, prefix="/api")`
  - Phase 1 模块未做任何修改

### Step 5 文档输出（2026-03-07）
- 创建：`docs/phase2-dev-log.md`（本文件）
- 创建：`docs/phase2-architecture.html` — Phase 2 架构可视化

### Step 6 Bug 修复（2026-03-07，代码审查后）

- **Bug 1**：**`resolve_safe_path()` 前缀绕过**
  - 问题：`str(resolved).startswith(str(base_resolved))` 判断边界，会把 `workspace-default-evil` 误判为仍在 `workspace-default` 下（同前缀兄弟目录 + symlink 场景）。写操作会从预期的 403 退化成 500（`ValueError` 而非 `PathSecurityError`）。
  - 处理：改用 `resolved.relative_to(base_resolved)` + `try/except ValueError`，这是 Python 标准库推荐的路径归属检查方式。
  - 影响：PRD §6.9 高风险项此前未真正解决，现已修复。

- **Bug 2**：**已有 workspace 缺少模板新增内容**
  - 问题：`ensure_default_workspace()` 仅在目录不存在时 `copytree`，不会把模板新增内容（如 `assets/uploads/`）同步到已有 workspace-default。导致 `GET /api/files/tree?path=assets/uploads` 在旧 workspace 返回 404。
  - 处理：新增 `_migrate_workspace(template_dir, workspace_dir)` 函数，遍历模板 `rglob("*")`，仅添加不存在的文件/目录，不覆盖用户已有内容。
  - 影响：启动时自动补齐，确保所有 workspace 与模板结构对齐。

- **Bug 3**：**IDENTITY.md 名称提取与模板不匹配**
  - 问题：`agents.py` 取 `IDENTITY.md` 首行 `# ...` 当 agent 名，但模板首行是 `# IDENTITY.md - 我是谁？`（文档标题），不是 agent 名字。`GET /api/agents` 返回的 default agent 名称为 `IDENTITY.md - 我是谁？`。
  - 处理：名称提取逻辑改为：优先查找 `- **Name（名字）：` 字段（模板格式），回退到首行标题但排除含"我是谁"的行。POST 创建的 agent 仍使用 `# {name}` 格式，不受影响。

---

## 已处理问题

1. **`assets/uploads/` 目录缺失**
   - 问题：Phase 1 workspace-templates 对齐检查发现 PRD §4.8.3 要求的 `assets/uploads/` 目录不存在。
   - 处理：在 workspace-templates 中补充 `assets/uploads/README.md`。
   - **后续修复**：新增 `_migrate_workspace()` 确保已有 workspace 也能补齐。

2. **路径安全防护（PRD §6.9 高风险）**
   - 问题：PRD §6.9 标记文件 API 路径遍历为高风险项。
   - 初始处理：`resolve_safe_path()` 三层防护 + 写入白名单。
   - **后续修复**：边界检查从 `str.startswith()` 改为 `Path.relative_to()`，堵住同前缀兄弟目录绕过。

3. **Workspace 定位方式**
   - 问题：Files API 需要获取当前 workspace 根目录。
   - 处理：通过 `request.app.state.session_manager._workspace_dir` 获取。Phase 2 固定 `workspace-default`，Phase 6 支持动态切换。

4. **Agent CRUD 当前为半成品能力（已知限制）**
   - 问题：`POST /api/agents` 可以创建 workspace 目录，但 SessionManager 和 Files API 始终绑定 `workspace-default`，新建的 agent workspace 在当前 API 中无法被激活使用。
   - 状态：设计如此（Phase 6 补充 Agent 切换）。但需要注意：**Phase 3 不应依赖 Agent 切换能力**，只应依赖 Files API 对 workspace-default 的操作。

---

## 测试结果

### Phase 2 验证矩阵（10 项）

| # | 测试项 | 命令 | 预期 | 状态 | 备注 |
|---|--------|------|------|------|------|
| 1 | 服务启动 | `uvicorn app:app --port 8002 --reload` | Phase 1 + Phase 2 路由全部注册 | ✅ | |
| 2 | 目录树 | `GET /api/files/tree` | 返回 workspace-default 完整目录结构 | ✅ | |
| 3 | 子树 | `GET /api/files/tree?path=memory/` | 仅返回 memory/ 子树 | ✅ | |
| 4 | 读文件 | `GET /api/files?path=memory/identity/project.md` | 返回文件内容 JSON | ✅ | |
| 5 | 路径遍历拦截 | `GET /api/files?path=../../etc/passwd` | 403 | ✅ | Bug 1 修复后重验 |
| 6 | 保存文件 | `POST /api/files {path, content}` | 返回 saved: true | ✅ | |
| 7 | 非白名单写入 | `POST /api/files {path:"SOUL.md"}` | 403 | ✅ | |
| 8 | 文件预览 | `GET /api/files/preview?path=SOUL.md` | 返回截断预览 | ✅ | |
| 9 | 创建 Agent | `POST /api/agents {agent_id, name}` | 返回 agent_id + workspace_dir | ✅ | |
| 10 | 重复 Agent | `POST /api/agents` 同 ID | 409 | ✅ | |

### 新增验证项（Bug 修复后）

| # | 测试项 | 命令 | 预期 | 状态 |
|---|--------|------|------|------|
| 11 | 同前缀兄弟目录绕过 | 构造 `workspace-default-evil` symlink | 403（非 500） | ✅ 修复后 |
| 12 | 已有 workspace 迁移 | 启动后 `GET /api/files/tree?path=assets/uploads` | 返回目录树（非 404） | ✅ 修复后 |
| 13 | Default agent 名称 | `GET /api/agents` | 返回 `default`（非 `IDENTITY.md - 我是谁？`） | ✅ 修复后 |

---

## Phase 2 产出汇总

| 指标 | 值 |
|------|-----|
| 新建文件 | 4 个（path_utils.py, files.py, agents.py, uploads/README.md） |
| 修改文件 | 1 个（app.py） |
| 新增 API 端点 | 6 个（Files 4 + Agents 2） |
| 新增依赖 | 0（全部使用标准库 + Phase 1 已有依赖） |
| Phase 1 核心模块修改 | 0 个 |
| Bug 修复（代码审查后） | 3 个（路径安全绕过、workspace 迁移、名称提取） |

---

## Phase 2 已知限制（Phase 6 前不会解决）

1. **Agent 切换**：`POST /api/agents` 创建的 workspace 目前无法被激活。Files API 和 SessionManager 始终指向 `workspace-default`。
2. **二进制文件**：Files API 仅支持 UTF-8 文本读写，不支持二进制上传（Phase 5）。
3. **Agent 删除/重命名**：当前无对应 API。

---

## Phase 2 → Phase 3 衔接

| Phase 2 提供 | Phase 3 如何使用 | 可靠性 |
|-------------|-------------|--------|
| `GET /api/files/tree` | ContextOrchestrator 发现 memory 文件 | 可直接使用 |
| `GET /api/files` | PromptBuilder 读取 Prompt 组件注入 system prompt | 可直接使用 |
| `POST /api/files` | TraceWriter 落盘 | 可直接使用（白名单内） |
| `resolve_safe_path()` | 全局路径安全工具 | 已修复，可直接使用 |
| `GET /api/files/preview` | Phase 6 前端文件浏览器预览 | 可直接使用 |
| `POST /api/agents` | **Phase 6** 前端 Agent 切换 | ⚠️ 仅创建目录，不切换上下文 |
