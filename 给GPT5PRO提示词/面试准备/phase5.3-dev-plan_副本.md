# Phase 5.3 开发计划：Workspace 运行时切换 + Workspace/Session 命名

> 目标：把当前“只能创建多个 workspace 目录，但运行时永远绑定 `workspace-default`”的架构，改成“前端可切换当前 workspace，后端按请求进入对应 runtime，且 workspace 与内部 session 都可以命名”。

---

## 0. 先说结论

这个问题不能靠“新增一个切换按钮”解决，必须先改后端的运行时绑定方式。

当前真正的瓶颈不是 `/api/agents`，而是：

1. `SessionManager` 在启动时固定绑定 `DEFAULT_WORKSPACE_DIR`
2. `AgentManager` 在启动时固定初始化到 `DEFAULT_WORKSPACE_DIR`
3. `chat/files/assets/sessions` 等接口都通过全局单例去拿当前 workspace
4. 前端只有 session 选择器，没有 workspace 作用域

所以 5.3 的核心不是“多建几个目录”，而是“把 workspace 从全局状态，改成请求级上下文”。

---

## 1. 范围判断

### 1.1 推荐范围

Phase 5.3 推荐只落下面 3 件事：

1. 前端可创建、选择、重命名 workspace
2. 每个 workspace 下有自己独立的 session 列表，session 可创建、重命名、切换
3. 后端所有和运行时相关的接口都按“当前选中的 workspace”执行

5.3 不纳入的内容：

- bootstrap 自动判断 workspace 的语义边界
- 基于 bootstrap 自动生成 workspace 类型 / scope statement
- 按语义边界自动初始化 route / memory 模板

这些能力是合理的，但属于比“运行时切换 + 命名”更大一层的产品编排问题，建议后续单独做 Phase 5.4 或 6.0。

### 1.1.1 与 Bootstrap 初始化协议的关系

Phase 5.3 和 bootstrap 不是同一层问题。

- Phase 5.3 解决的是：workspace 如何成为真正可切换、可隔离、可命名的运行时作用域
- bootstrap 解决的是：一个新 workspace 在首次创建时，如何被定义成什么语义容器

也就是说：

- 5.3 管“这个 workspace 怎么跑”
- bootstrap 管“这个 workspace 到底是什么”

结合当前 [boostrap-index.md](/Users/fenke/projects/study_ai/2-未完成项目存档/zly%20规划-0219/ResearchAgentPrivateWorkspace/docs/boostrap-index.md) 的方向，后续合理的生命周期应是：

1. `POST /api/workspaces` 创建 workspace 目录与基础元数据
2. 触发 first-run bootstrap
3. bootstrap 基于“用户意图 + 初始材料”形成最小 scope decision
4. bootstrap 形成 generation plan
5. bootstrap 生成与 scope 相称的初始化骨架
6. 后续所有对话与文件操作，再交由 5.3 的 workspace runtime routing 接管

因此 5.3 只需要为 bootstrap 预留 hook 和生命周期位置，不应在本阶段直接吞下 bootstrap 的语义定界与初始化编排。

### 1.2 不建议在 5.3 同时做“真正独立的 agent 与 workspace 双实体”

按当前代码，`agent` 本质上就是 `workspace-{agent_id}` 这一套目录和运行时。也就是说，今天的 `agent` 和 `workspace` 是同一个东西，不是两个概念。

如果 5.3 强行拆成两个独立选择器：

- `agent` = 人格 / prompt profile / 工具配置
- `workspace` = memory / assets / sessions / trace 的数据根目录

那就不是“小修”，而是一次模型重构，范围会从运行时切换扩大到 prompt/source-of-truth 设计，风险明显变大。

### 1.3 5.3 的产品建议

5.3 先把产品语义定成：

- `workspace`：真正可切换的工作空间，也是运行时作用域
- `agent`：前端文案上可作为 workspace 的别名展示，但后端暂不拆成独立实体

如果界面上一定要出现 “Agent / Workspace”，建议先做一个合并选择器，而不是两个独立下拉框。

---

## 2. 当前代码中的卡点

### 2.1 启动阶段把 runtime 固定到了 default

`backend/app.py` 当前在启动时做了两件硬绑定：

- `SessionManager(cfg.DEFAULT_WORKSPACE_DIR)`
- `agent_manager.initialize(workspace_dir=cfg.DEFAULT_WORKSPACE_DIR)`

这意味着后续所有请求，如果没有额外 runtime 分发层，天然只会落到 `workspace-default`。

### 2.2 各 API 默认都从全局单例拿 workspace

当前 workspace 来源基本都是：

- `request.app.state.session_manager._workspace_dir`

这在这些接口里都存在：

- `backend/api/chat.py`
- `backend/api/files.py`
- `backend/api/assets.py`
- `backend/api/sessions.py`

这说明即使 `/api/agents` 已经能创建出多个目录，运行时入口还是单点的。

### 2.3 前端只有 session 视角，没有 workspace 视角

`frontend/index.html` 目前只有：

- session 下拉框
- 新建 session
- 刷新 workspace 目录树

但没有：

- workspace 选择器
- workspace 新建 / 重命名
- 基于 workspace 重新加载 session/tree/chat 的逻辑

---

## 3. 5.3 的目标状态

完成后，系统应该变成下面的行为：

1. 用户在前端选择某个 workspace
2. 前端之后发出的 `chat/files/assets/sessions` 请求都显式带上该 `workspace_id`
3. 后端为该 `workspace_id` 解析到对应目录，并拿到该 workspace 专属 runtime
4. 该 workspace 下的 session 列表、聊天历史、memory、assets、trace 都完全隔离
5. workspace 有可编辑的展示名，session 也有可编辑的标题

一句话：从“全局 default runtime”切到“每个请求都显式指向一个 workspace runtime”。

---

## 4. 核心设计决策

### 4.1 不做“全局切换当前 workspace”的后端状态

不建议新增类似：

- `POST /api/agents/switch`
- `app.state.current_workspace = xxx`

这种做法在单用户 demo 看起来简单，但一旦：

- 两个浏览器标签页同时打开
- 后续支持多人
- 并发上传 / 并发聊天

就会出现串 workspace 的问题。

### 4.2 改成“请求级 workspace 选择”

推荐把 `workspace_id` 作为每个请求的显式上下文传给后端。

推荐顺序：

1. 前端统一通过 Header 传 `X-Workspace-Id`
2. 对于 `POST /api/chat` 这类核心接口，body 中也保留 `workspace_id`，便于 trace 和调试
3. 若未传，则回退到 `default`

这样：

- 前端切换 workspace 只是切换本地状态
- 后端不保存“当前选中的 workspace”
- 并发安全

### 4.3 runtime 要按 workspace 懒加载，但不要把 LLM 客户端按 workspace 复制

推荐新增一层 registry：

```python
@dataclass
class WorkspaceRuntime:
    workspace_id: str
    workspace_dir: Path
    session_manager: SessionManager
    workspace_tools: list


@dataclass
class SharedAgentResources:
    llm: ChatOpenAI | None
    fetch_url_tool: FetchURLTool
    config_error: str


class WorkspaceRuntimeRegistry:
    def get_runtime(self, workspace_id: str) -> WorkspaceRuntime:
        ...

    def get_shared_resources(self) -> SharedAgentResources:
        ...
```

职责：

1. `workspace_id -> workspace_dir` 解析
2. 启动时只初始化一份共享 `llm`
3. 第一次访问某个 workspace 时，懒初始化 `SessionManager` 和该 workspace 专属 tools
4. 缓存 workspace runtime，避免每个请求重复建对象
5. 请求到来时，用“共享 llm + 当前 workspace tools + system prompt”临时组装 agent
6. 对新建 workspace 做模板迁移与技能注册归一化

这里要明确区分两类资源：

1. 共享资源：
   - `ChatOpenAI`
   - `FetchURLTool()`
   - API key / provider 配置检查结果
2. workspace 隔离资源：
   - `SessionManager(workspace_dir)`
   - `TerminalTool(workspace_dir)`
   - `PythonREPLTool(workspace_dir)`
   - `ReadFileTool(workspace_dir)`
   - `WriteFileTool(workspace_dir)`
   - 以及其他未来依赖 `workspace_dir` 的 tool

原因很直接：对当前项目来说，`llm` 和 `fetch_url` 基本不依赖 workspace，而 file/exec 类 tools 明确依赖 `workspace_dir`。如果每个 workspace 都持有一个完整 `AgentManager`，就会重复创建多个 `ChatOpenAI` 实例，甚至重复创建本可共享的无状态网络工具，属于无必要复制。

---

## 5. 数据模型与命名方案

### 5.1 workspace 标识与展示名分离

每个 workspace 都应该有两个字段：

- `workspace_id`：稳定、机器可用、不可轻易改动
- `display_name`：前端展示名，可编辑

继续保留现有目录命名：

- `.openclaw/workspace-{workspace_id}/`

### 5.2 新增 `workspace_manifest.json`

建议在每个 workspace 根目录新增：

- `workspace_manifest.json`

格式：

```json
{
  "workspace_id": "chlorite_mainline",
  "display_name": "亚氯酸盐主线",
  "description": "Co3O4 / Ce 掺杂机理闭环",
  "bootstrap_status": "pending",
  "created_at": "2026-03-16T10:00:00+00:00",
  "updated_at": "2026-03-16T10:00:00+00:00"
}
```

原因：

1. 不要继续把 workspace 命名语义塞进 `IDENTITY.md`
2. 前端列表展示需要稳定元数据
3. bootstrap 生命周期状态需要有机器可读锚点
4. 重命名 workspace 时，只改 manifest，不改目录名，风险最低

建议把 `bootstrap_status` 设计成显式状态，而不是布尔值，至少支持：

- `pending`
- `running`
- `completed`
- `failed`

语义分工建议：

- `workspace_manifest.json`：机器可读元数据与生命周期状态
- `memory/identity/workspace_scope.md`：agent 可读的语义边界说明

### 5.3 session 继续按 workspace 隔离

这一点当前天然成立，因为 `SessionManager` 的数据都落在：

- `context_trace/_sessions_index.json`
- `context_trace/{session_id}.json`

只要 `SessionManager` 改成按 workspace 取实例，session 就会自动被隔离到各自 workspace 下，不需要额外加数据库表。

---

## 6. 后端改造步骤

### Step A：新增 workspace service / runtime registry

新增一个集中层，建议文件：

- `backend/runtime/workspace_registry.py`

提供能力：

1. `resolve_workspace_dir(workspace_id)`
2. `ensure_workspace_exists(workspace_id)`
3. `load_manifest(workspace_id)`
4. `list_workspaces()`
5. `create_workspace(workspace_id, display_name, description)`
6. `rename_workspace(workspace_id, display_name)`
7. `get_runtime(workspace_id)`
8. `get_shared_resources()`

这里要把 `app.py` 里与 workspace 生命周期相关的逻辑收进来，包括：

- 默认 workspace 初始化
- 模板缺项迁移
- skills registry 归一化

### Step B：启动阶段改成初始化 registry，而不是初始化 default 单例

`backend/app.py` 改成：

1. 启动时只确保 default workspace 存在
2. 初始化共享资源：
   - 一份共享 `llm`
   - 一份共享 `fetch_url_tool`
3. 创建 `WorkspaceRuntimeRegistry`
4. 挂到 `app.state.workspace_registry`
5. 删除或停止依赖：
   - `app.state.session_manager`
   - `app.state.agent_manager`

可以保留 default runtime 的预热，但不能再把它作为全局唯一 runtime。预热内容应是：

- default workspace 的 `SessionManager`
- default workspace 的 file/exec tools

而不是再创建一份只属于 default 的独占 `llm` 或独占 `fetch_url`。

### Step C：统一加 `get_runtime(request)` helper

建议新增一个通用 helper，例如：

- `backend/api/runtime_context.py`

职责：

1. 从 `X-Workspace-Id` 或 body/query 解析 `workspace_id`
2. 调 `request.app.state.workspace_registry.get_runtime(workspace_id)`
3. 返回 `WorkspaceRuntime`

这样 `chat/files/assets/sessions` 都走同一条入口。

### Step D：让现有 API 全部 workspace-aware

#### D1. `chat`

`POST /api/chat` 新增：

- `workspace_id: str = "default"`

调用链改为：

1. 先拿 runtime
2. 再从 runtime 取 `session_manager`
3. 再从 registry 取共享 `llm`
4. 再从 registry 取共享 `fetch_url_tool`
5. 用共享 `llm + 共享 fetch_url + runtime.workspace_tools + system_prompt` 组装当前请求的 agent
6. `ContextOrchestrator` / `PromptBuilder` / `SkillLoader` / `TraceWriter` 全部基于 runtime 的 `workspace_dir`

#### D2. `sessions`

保留现有接口路径，但都按 workspace 作用域执行：

- `GET /api/sessions`
- `POST /api/sessions`
- `PUT /api/sessions/{session_id}`
- `DELETE /api/sessions/{session_id}`
- `GET /api/sessions/{session_id}/history`

这些接口通过 header/body/query 解析 `workspace_id`。

这样前端切换 workspace 后，请求同一路径，也能拿到不同的 session 集合。

#### D3. `files` / `assets`

这两个接口必须同步改，不然会出现：

- session 在 workspace-A
- 文件树却读的还是 workspace-default

改造要求：

1. 文件树、文件读取、文件保存按选中 workspace 执行
2. 上传附件写到选中 workspace 的 `assets/`
3. 下载附件只允许下载该 workspace 下的文件

### Step E：新增真正的 workspace API

当前 `/api/agents` 的职责其实更接近 `workspace` 管理。

5.3 建议新增：

- `GET /api/workspaces`
- `POST /api/workspaces`
- `PUT /api/workspaces/{workspace_id}`

接口建议：

#### `GET /api/workspaces`

返回：

```json
{
  "workspaces": [
    {
      "workspace_id": "default",
      "display_name": "Default Workspace",
      "description": "",
      "workspace_dir": "...",
      "session_count": 12
    }
  ]
}
```

#### `POST /api/workspaces`

请求：

```json
{
  "workspace_id": "chlorite_mainline",
  "display_name": "亚氯酸盐主线",
  "description": "Co3O4 / Ce 掺杂机理闭环"
}
```

行为：

1. copy `workspace-templates`
2. 写 `workspace_manifest.json`
3. 将 `bootstrap_status` 标记为 `pending`
4. 确保模板内已包含 `BOOTSTRAP.md`
5. 对 skills registry 做归一化
6. 为该 workspace 建立 bootstrap runner 上下文
7. 返回 workspace 元数据

这里要明确：`POST /api/workspaces` 只完成 **provision**，不等于初始化已经完成。

它负责的是：

- 创建技术作用域
- 写基础元数据
- 建立 bootstrap runner 所需的最小上下文
- 让 workspace 进入可被 bootstrap 的状态

它不负责：

- 定义 workspace 的语义边界
- 直接生成最终的 `workspace_scope.md`
- 在创建接口里一次性跑完 bootstrap

#### `PUT /api/workspaces/{workspace_id}`

请求：

```json
{
  "display_name": "亚氯酸盐主线 v2",
  "description": "更新后的描述"
}
```

行为：

1. 只改 manifest
2. 不改目录名
3. 不迁移 session 文件

### Step E.1：Workspace Lifecycle + Bootstrap Runner Contract

5.3 需要把 workspace 生命周期和 bootstrap runner 一起定义清楚，否则 `bootstrap_status` 只有状态，没有执行闭环。

#### lifecycle states

建议把 workspace 生命周期显式拆成：

1. `provision`
   - 目录已创建
   - 模板已复制
   - manifest 已写入
   - `bootstrap_status = pending`
2. `bootstrap`
   - workspace 已 provision，但尚未 active
   - bootstrap runner 显式启动 first-run 初始化
   - agent 按 `BOOTSTRAP.md` 执行语义初始化正文
   - 生成 `workspace_scope.md` 与最小初始化骨架
3. `active`
   - bootstrap 已完成
   - `bootstrap_status = completed`
   - 后续所有请求都按正常 workspace runtime 流程处理

#### when bootstrap is needed

- 当前端切换到某个 workspace 后，先读取该 workspace 的 `bootstrap_status`
- 若状态是 `completed`，直接进入普通 chat 界面
- 若状态是 `pending` 或 `failed`，不要进入普通 chat，而是先进入 bootstrap 初始化入口

也就是说，workspace 是否进入正常聊天，不由“是否切换成功”决定，而由“是否完成 bootstrap 初始化”决定。

这样设计的原因，不只是为了 first-run 初始化。

更重要的是，workspace 在真实科研业务中会持续承接大量非结构化、异构、不断变化的用户源文件。
因此，5.3 必须先把 workspace 做成真正独立、可隔离、可切换的运行时容器，
后续 bootstrap、初始材料 intake、自动同步、memory 沉淀、上下文选择，才能围绕同一个 workspace 稳定发生。

#### who starts bootstrap

5.3 采用 **方案 A：独立 Bootstrap Runner 服务**。

它的定位是：

- 生命周期上独立于普通 chat
- 职责上只负责 first-run 初始化编排
- 未来可扩展到更复杂的初始材料处理、自动同步与大体量非结构化文件 intake
- 当前 MVP 只实现最小闭环，不引入复杂异步工作流

MVP 形态建议是：

- 创建 workspace 时，先建立该 workspace 的 bootstrap runner 上下文
- 前端切换到新 workspace 后，由显式入口启动该 runner

显式 start 入口例如：

- `POST /api/workspaces/{workspace_id}/bootstrap/start`

推荐它的原因是：

- 不把 bootstrap 逻辑本体混进 `POST /api/workspaces`
- 不把 bootstrap 混进普通 `POST /api/chat`
- 不依赖全局 current workspace
- 方便前端在 `pending|failed` 状态下做明确引导与 retry

#### who updates manifest

- `workspace_manifest.json` 的生命周期更新由 workspace runtime / bootstrap runner 负责
- 不由 BOOTSTRAP agent 通过普通 `write_file` 工具直接回写
- 当前路径安全约束默认不允许 agent/tool 直接写 workspace 根目录，因此 `workspace_manifest.json` 应被视为系统级状态文件，而不是普通 memory 文件

#### retry and completed rules

- 只有 `pending` 或 `failed` 状态允许进入 bootstrap 主流程
- 启动前：`pending|failed -> running`
- 成功后：`running -> completed`
- 失败后：`running -> failed`
- `failed` 状态允许 retry，且 retry 仍走同一 runner
- `completed` workspace 不应再次进入 bootstrap 主流程
- 普通 chat 请求不负责隐式接管 bootstrap

因此 5.3 之后合理的链路应是：

1. 前端 `POST /api/workspaces`
2. 后端完成 provision，并建立 bootstrap runner 上下文
3. 前端切换到新建 workspace
4. 前端先读取该 workspace 的 `bootstrap_status`
5. 若状态为 `pending` 或 `failed`，前端直接进入 bootstrap 初始化流
6. 前端通过显式 bootstrap start 入口触发初始化
7. bootstrap 完成后写入：
   - `workspace_manifest.json` 状态更新
   - `memory/identity/workspace_scope.md`
   - 其他初始化骨架
8. 只有当状态变为 `completed` 后，前端才进入普通 chat 界面

### Step F：`/api/agents` 的处理策略

5.3 不建议继续扩展 `/api/agents`，建议：

1. 新前端只使用 `/api/workspaces`
2. `/api/agents` 保留兼容一版
3. 返回里增加字段说明它等价于 workspace

如果一定要兼容老逻辑，可以让 `/api/agents` 复用 `/api/workspaces` 的 service。

---

## 7. 前端改造步骤

### Step A：顶栏新增 workspace 选择区

在当前 session 选择区旁边增加：

1. workspace 下拉框
2. 新建 workspace 按钮
3. 重命名 workspace 按钮

推荐交互：

- 切换 workspace 后，立即刷新：
  - session 列表
  - chat history
  - memory tree
  - atom tree
  - trace 面板状态

新建 workspace 后的交互也要明确：

1. 调 `POST /api/workspaces`
2. 创建成功后立即切换到该 workspace
3. 切换后先读取该 workspace 的 `bootstrap_status`
4. 若状态是 `completed`，直接进入普通 chat 界面
5. 若状态是 `pending` 或 `failed`，则前端直接进入 bootstrap 初始化界面
6. 前端通过独立 bootstrap runner 入口触发初始化
7. bootstrap 完成前，不进入普通 chat 主流程
8. bootstrap 完成后，再进入正常 workspace 界面

### Step B：前端 state 新增 `currentWorkspaceId`

当前前端只有：

- `currentSessionId`

需要新增：

```js
const state = {
  currentWorkspaceId: "default",
  currentSessionId: null,
  ...
}
```

并持久化到 `localStorage`。

### Step C：统一给 API 请求带上 workspace 上下文

推荐做法是在 `apiFetch` / `apiJson` 这一层统一补：

- `X-Workspace-Id: state.currentWorkspaceId`

这样不用在每个请求点重复拼接 query 参数。

`sendMessage()` 则额外在 body 里补一份 `workspace_id`，方便后端 trace。

对于 bootstrap 初始化流，前端也应把当前 `workspace_id` 带入显式 start 入口与后续初始化对话请求，确保整个 first-run 过程始终落在同一个 workspace runtime 内。

### Step D：workspace 切换后的前端行为

切换 workspace 时必须做的事情：

1. 清空当前消息区
2. 释放当前左右文件预览
3. 重置 trace 计数
4. 重新请求该 workspace 的 session 列表
5. 自动选中该 workspace 最近更新的 session；若没有则允许用户新建
6. 重新加载文件树

否则 UI 会出现 “session 属于 A，文件树属于 B” 的错位。

### Step E：暴露 session 命名能力

后端已经有：

- `PUT /api/sessions/{session_id}`

前端 5.3 只需要把它做出来。

推荐最小交互：

1. 在 session 下拉框旁边新增 “重命名会话”
2. 点击后弹 prompt/modal
3. 调 `PUT /api/sessions/{session_id}`
4. 刷新 session 列表并保留当前选中项

### Step F：workspace 命名能力

workspace 的重命名不应通过改目录名实现，而是：

1. 编辑 `workspace_manifest.json` 中的 `display_name`
2. 前端列表展示 `display_name`
3. 下拉框 value 仍然用 `workspace_id`

---

## 8. 建议的实施顺序

### 第 1 阶段：先打通后端 runtime

目标：哪怕前端还没改，只要手工带 header，也能切 workspace。

任务：

1. `WorkspaceRuntimeRegistry`
2. `get_runtime(request)`
3. `chat/files/assets/sessions` 全部改成按 workspace 运行
4. 加最基本的 `GET /api/workspaces`

### 第 2 阶段：补 workspace 管理 API

任务：

1. `POST /api/workspaces`
2. `PUT /api/workspaces/{workspace_id}`
3. manifest 读写
4. `/api/agents` 兼容策略

### 第 3 阶段：补前端 workspace selector

任务：

1. workspace 下拉框
2. 新建 / 重命名 workspace
3. 切换后重载 session/tree/chat

### 第 4 阶段：补 session 命名 UI

任务：

1. session rename 按钮
2. session 作用域跟随 workspace
3. 切 workspace 后回收旧 session 状态

---

## 9. 验收标准

### 9.1 workspace 级隔离

1. 在前端创建 workspace-A 和 workspace-B
2. 在 workspace-A 中新建 session，发一轮对话，上传一个文件
3. 切到 workspace-B
4. 预期：
   - 看不到 workspace-A 的 session
   - 看不到 workspace-A 的 memory/assets/context_trace
5. 再切回 workspace-A
6. 预期所有内容完整恢复

### 9.2 命名能力

1. 新建 workspace 时可填写展示名
2. workspace 重命名后，下拉框展示立即更新
3. 新建 session 后可重命名
4. 刷新页面后，workspace 名和 session 名都能正确恢复

### 9.3 运行时正确性

1. 在 workspace-A 调 `POST /api/chat`
2. trace 应写到 `workspace-A/context_trace/`
3. 在 workspace-B 调 `GET /api/files/tree`
4. 返回必须来自 workspace-B 根目录

### 9.4 并发安全

1. 浏览器标签页 1 选 workspace-A
2. 浏览器标签页 2 选 workspace-B
3. 同时发消息
4. 不应出现互串 session、互串 trace、互串 assets

---

## 10. 风险与控制

### 风险 1：继续依赖全局 `app.state.session_manager`

如果只在前端加 selector，不拆全局单例，功能表面上能跑，实际一定会串 workspace。

控制：

- 5.3 明确移除“全局唯一 SessionManager / AgentManager”依赖

### 风险 2：workspace 切换后 UI 状态未清空

如果切换 workspace 后还保留旧 chat/history/tree，就会出现错位感。

控制：

- workspace change 事件里显式 reset 当前页面状态

### 风险 3：把重命名做成目录 rename

目录 rename 会影响：

- 路径引用
- trace 历史
- 潜在缓存

控制：

- 只改 `display_name`
- `workspace_id` 和目录路径保持稳定

---

## 11. 5.3 完成后的系统边界

5.3 完成后，系统会升级为：

- 多 workspace 可创建
- 多 workspace 可切换
- 每个 workspace 有自己独立 runtime
- 每个 workspace 下的 session 独立、可命名
- 前端具备真正的 workspace/session 作用域

但 5.3 仍然**不包含**：

- 真正独立的 agent profile 系统
- 一个 agent 绑定多个 workspace 的复用模型
- 跨 workspace 的 session 迁移 / 克隆

这些如果后续要做，建议放到 5.4 或 6.0，再正式拆 `agent` 与 `workspace`。

---

## 12. 一句话的落地建议

5.3 不要做“切一个全局 current workspace”，而要做“每个请求都带 `workspace_id`，后端按 `workspace_id` 取 runtime”；在这个基础上，把 workspace 展示名和 session 标题暴露给前端，就能把“多目录假象”升级成真正可用的多 workspace 系统。


### 9.5 bootstrap 生命周期验收

1. 创建新 workspace
2. 检查 `workspace_manifest.json.bootstrap_status = pending`
3. 切换到该 workspace
4. 前端不进入普通 chat 主流程，而进入 bootstrap entry
5. 调用 bootstrap start 后，manifest 变为 `running`
6. 完成初始化后：
   - `workspace_scope.md` 已生成
   - `bootstrap_status = completed`
7. 再次进入该 workspace：
   - 不再重复进入 bootstrap
   - 直接进入正常 workspace 界面
8. 若中途失败：
   - `bootstrap_status = failed`
   - 可通过同一入口 retry