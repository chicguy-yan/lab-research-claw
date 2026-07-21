# backend bootstrap 重构交接说明

## 1. 变更目标

这次 bootstrap 重构的目标有两个：

1. 删掉旧版 bootstrap 的“硬分类 / 分意图 / 生成固定 plan”状态机。
2. 改成 OpenClaw 风格的一次性 onboarding：
   - 新 workspace 生成 `BOOTSTRAP.md`
   - 前端读取并展示固定首问
   - 用户首答仍走正常 `/api/chat`
   - 后端把首答写回 `BOOTSTRAP.md`
   - 然后复用正常 agent 主链路更新 `IDENTITY.md / USER.md / SOUL.md`
   - bootstrap 完成后删除 `BOOTSTRAP.md`

---

## 2. 旧逻辑和新逻辑的差异

### 2.1 旧逻辑

旧版 bootstrap 是一个独立状态机，核心问题是：

- 先做 `semantic_scope / time_mode / primary_object` 这类硬分类
- 先输出模板化确认稿和 bootstrap plan
- 用户必须沿着确认流程走
- 很容易压过用户真正的问题
- 不适合材料化学实验这种“先问任务入口、再逐步沉淀记忆”的场景

旧状态机核心文件是：
- `backend/runtime/bootstrap_runner.py`（旧版）

### 2.2 新逻辑

新版 bootstrap 不再做分类，而是：

1. `/bootstrap/start` 只负责读取 `BOOTSTRAP.md` 里的首问，并创建 `__bootstrap__` 会话。
2. 用户回复首问时，前端仍调用普通 `/api/chat`，但 `route=bootstrap`。
3. 后端先把这次首答写回 `BOOTSTRAP.md` 的 QA 占位区。
4. 然后直接进入正常 agent 主链路：
   - `ContextOrchestrator`
   - `PromptBuilder`
   - `create_agent`
   - `agent.astream(...)`
5. 正常主链路跑完后：
   - 删除 `BOOTSTRAP.md`
   - manifest 标记为 `completed`

这意味着 bootstrap 不再是一套平行于 chat 的特殊任务流，而是：

> 用一个一次性的 bootstrap 文件，引导第一次对话；第一次对话本身仍然复用正常 agent 主链路。

---

## 3. 当前 bootstrap 运行流程

### 3.1 workspace 创建阶段

`WorkspaceRuntimeRegistry` 现在会根据 manifest 的 `bootstrap_status` 自动同步 `BOOTSTRAP.md`：

- `pending / running / failed`：如果缺失则补回 `BOOTSTRAP.md`
- `completed`：删除 `BOOTSTRAP.md`

对应改动文件：
- `backend/runtime/workspace_registry.py`
- `backend/runtime/bootstrap_runner.py`

### 3.2 bootstrap start 阶段

接口：
- `POST /api/workspaces/{workspace_id}/bootstrap/start`

行为：
- 检查 workspace manifest
- 把 `bootstrap_status` 改成 `running`
- 读取 workspace 下的 `BOOTSTRAP.md`
- 提取首问块
- 重建 `__bootstrap__` session
- 往 bootstrap history 写入一条 assistant 首问
- 返回：
  - `session_id="__bootstrap__"`
  - `bootstrap_prompt`
  - 最新 manifest

对应文件：
- `backend/api/workspaces.py`
- `backend/runtime/bootstrap_runner.py`

### 3.3 chat 阶段

接口仍然是：
- `POST /api/chat`

区别只在于：
- 如果 `route=bootstrap`
- 且 `session_id=__bootstrap__`
- 且 manifest 状态是 `running`

后端会先执行：
- `bootstrap_runner.record_first_answer(...)`

然后就进入正常主链路：
- 生成 memory map
- build prompt
- create agent
- stream 输出
- 记录 session 和 trace

如果 bootstrap 这轮成功结束：
- `bootstrap_runner.complete()` 删除 `BOOTSTRAP.md`
- `registry.update_bootstrap_status(..., "completed")`

对应文件：
- `backend/api/chat.py`

---

## 4. BOOTSTRAP.md 的作用

新版 bootstrap 的核心不是一个 Python 状态机，而是一个控制文件：

- 文件路径：`backend/workspace-templates/BOOTSTRAP.md`
- 会被复制进每个需要 bootstrap 的 workspace
- 里面包含两类关键块：

### 4.1 首问块

通过 marker 提取：
- `<!-- BOOTSTRAP_QUESTION_START -->`
- `<!-- BOOTSTRAP_QUESTION_END -->`

用于前端展示给用户的第一问。

### 4.2 首答记录块

通过 marker 替换：
- `<!-- BOOTSTRAP_QA_START -->`
- `<!-- BOOTSTRAP_QA_END -->`

用于把用户第一次简短回答回写进 bootstrap 文件。

这样做的好处是：
- bootstrap 提示词固定、可编辑
- 首次问答有文件留痕
- 主链路不用再理解一套额外状态机

---

## 5. 前端行为变化

### 5.1 之前的问题

前端原先有两个问题：

1. workspace 在 `pending/failed` 时，只会显示 gate，不会自动调用 `/bootstrap/start`
2. bootstrap 完成后，界面会立刻切到普通 chat 分支，看起来像“跳走了”

### 5.2 现在的行为

在 `frontend/src/app/App.tsx` 中已经改为：

1. 当 manifest 状态为 `pending/failed` 时，前端会自动调用 `/bootstrap/start`
2. 启动成功后把 `bootstrap_prompt` 直接塞进 bootstrap history cache
3. 当 manifest 状态为 `running` 时，显示 bootstrap 专属 `ChatPanel`
4. 当 manifest 状态变成 `completed` 后：
   - 如果当前 session 仍然是 `__bootstrap__`
   - 前端继续停留在“初始化完成 / 初始化会话”界面
   - 不会强制跳到一个新的普通会话
5. 用户可以手动新建正式会话，也可以继续在初始化会话里追问

对应文件：
- `frontend/src/app/App.tsx`
- `frontend/src/shared/types/api.ts`
- `frontend/src/app/App.test.tsx`

---

## 6. write_file 白名单修复

### 6.1 问题

bootstrap prompt 里要求 agent 更新：
- `IDENTITY.md`
- `USER.md`
- `SOUL.md`

但旧版路径白名单只允许写这些目录：
- `memory/`
- `assets/`
- `context_trace/`
- `skills/`
- `temporary_dir/`

导致 agent 想写 workspace 根目录控制文件时，会直接触发 path security violation。

### 6.2 修复

现在在 `backend/graph/path_utils.py` 中新增了：
- `ROOT_WRITABLE_FILES`

允许直接写这些根目录控制文件：
- `AGENTS.md`
- `BOOTSTRAP.md`
- `IDENTITY.md`
- `MEMORY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`

修复后：
- `write_file("IDENTITY.md", ...)` 已可正常写入
- 非白名单根目录文件仍然会被拒绝

对应文件：
- `backend/graph/path_utils.py`
- `backend/tests/test_write_file_tool.py`
- `backend/graph/prompt_builder.py`

---

## 7. 主要改动文件

### 后端

- `backend/runtime/bootstrap_runner.py`
  - 重写为轻量 bootstrap 文件生命周期管理器
- `backend/api/workspaces.py`
  - `/bootstrap/start` 返回首问和 bootstrap session
- `backend/api/chat.py`
  - bootstrap 改为先记录首答，再复用正常主链路
- `backend/runtime/workspace_registry.py`
  - 按 manifest 状态自动同步 `BOOTSTRAP.md`
- `backend/workspace-templates/BOOTSTRAP.md`
  - 固定首问模板 + 首答占位块
- `backend/graph/path_utils.py`
  - 放开根目录控制文件写入白名单
- `backend/graph/prompt_builder.py`
  - 更新 write_file 可写范围提示

### 前端

- `frontend/src/app/App.tsx`
  - 自动 start bootstrap
  - running/completed/bootstrap-session 三态处理
- `frontend/src/shared/types/api.ts`
  - 增加 `bootstrap_prompt`
- `frontend/src/app/App.test.tsx`
  - 补充 bootstrap 自动进入与完成后保留会话测试

### 测试

- `backend/tests/test_bootstrap_runner.py`
- `backend/tests/test_system_prompt_contract.py`
- `backend/tests/test_write_file_tool.py`
- `frontend/src/app/App.test.tsx`

---

## 8. 已完成验证

### 后端测试

已跑：

```bash
python -m pytest backend/tests/test_write_file_tool.py backend/tests/test_bootstrap_runner.py backend/tests/test_system_prompt_contract.py
```

结果：
- `13 passed`

### 前端测试

已跑：

```bash
npm run test:run -- src/app/App.test.tsx
npm run build
```

结果：
- App bootstrap flow 测试通过
- 前端 build 通过

### Playwright 验证

已做两类验证：

1. 真实页面验证 bootstrap 首问能够显示、前端会自动进入 bootstrap 会话
2. 在 `bootstrap_status=completed + currentSessionId=__bootstrap__` 条件下，页面会停留在“初始化完成 / 初始化会话”，不会自动跳走

另外还直接烟测了：
- `WriteFileTool._run("IDENTITY.md", ...)`
- 返回 `File written successfully: IDENTITY.md`

---

## 9. 当前已知问题

### 9.1 真实 bootstrap 首轮有时会卡很久

在一次真实 Playwright 测试中，bootstrap 首答发出后，SSE 长时间停留在“发送中”，模型流未及时结束。

这说明现在还存在一个未完全解决的问题：
- 首轮 bootstrap 复用正常主链路后，模型在某些情况下响应过慢或没有及时结束

这不是前端跳转问题，也不是 `write_file` 白名单问题，而是 live bootstrap 首轮执行时长/收敛性的问题，需要后续单独继续查。

### 9.2 手工改 workspace JSON 时需要注意 UTF-8 BOM

调试过程中，如果手工用 PowerShell 改：
- `workspace_manifest.json`
- `_sessions_index.json`
- `context_trace/*.json`

要注意不要写出 UTF-8 BOM，否则 Python 的 `json.load()` 会报：
- `Unexpected UTF-8 BOM`

这个不是业务逻辑 bug，而是调试时手工改文件的编码问题。

---

## 10. 建议后续工作

### P0

继续定位 live bootstrap 首轮为什么会长时间卡住，重点看：
- LLM 响应是否在 bootstrap prompt 下过长
- 是否有工具调用循环
- 是否首轮要求更新多个控制文件导致模型收敛慢

### P1

如果后续想进一步稳定 bootstrap，建议在 `BOOTSTRAP.md` 中继续压缩首轮任务：
- 首轮只要求提炼 workspace identity
- 不要在首轮同时要求过多额外交付

### P2

如果后续想把 bootstrap 结束后的体验做得更顺，可以考虑：
- 在“初始化完成 / 初始化会话”界面增加一个明确按钮
  - “进入正式会话”
  - “继续留在初始化会话”

---

## 11. 一句话结论

这次 bootstrap 重构已经把旧的分类状态机拆掉了，变成了“`BOOTSTRAP.md` 驱动的一次性首问 + 正常 chat 主链路复用”的方案；同时修掉了前端 bootstrap 完成后跳走的问题，以及根目录控制文件无法通过 `write_file` 更新的问题。