# Phase 6 开发计划：React + Vite 前端重构 + Bootstrap Gate + 前端测试体系

> 目标：把当前基于单文件 `frontend/index.html` 的前端，升级为 `React + Vite + TypeScript` 的正式前端工程，完整承接 Phase 5.3 的 workspace-aware runtime，并建立可持续回归的前端测试体系。

---

## 0. 先说结论

Phase 6 的核心不是“把静态页换成 React”，而是把当前已经在后端完成的 `workspace runtime` 架构，真正落成一个：

1. 可切换 workspace
2. 可阻止未 bootstrap 完成的 workspace 进入普通 chat
3. 可稳定承接 SSE、文件树、附件、trace
4. 可被测试验证的前端系统

当前系统已经具备了做这件事的后端前提：

- `WorkspaceRuntimeRegistry` 已完成
- `/api/workspaces` 已完成
- `X-Workspace-Id` 请求级上下文已完成
- `chat/files/assets/sessions` 已是 workspace-aware

但前端仍然存在两个根本问题：

1. 当前实现仍然是单文件 HTML + 原生脚本，状态、请求、SSE、DOM 操作耦合过高
2. `bootstrap` 引导界面仍是 stub，无法支撑 Phase 5.3 设计要求中的 first-run 流程

因此 Phase 6 的合理边界应该是：

- 前端重构
- bootstrap gate 落地
- 测试体系补齐

而不是顺手吞掉 Phase 5.4 的 bootstrap runner 正文逻辑。

---

## 1. 问题定义

### 1.1 当前前端的主要问题

当前 `frontend/index.html` 虽然已经承接了部分 Phase 5.3 的能力，但仍有以下结构性问题：

1. **前端仍是单文件实现**
   - HTML、CSS、JS 混在一个文件内
   - workspace/session/chat/tree/trace/attachment 全部耦合在一处
   - 不适合组件测试和长期迭代

2. **bootstrap gate 未真正实现**
   - 当前 UI 只会把 `bootstrap_status` 显示在 workspace 文案里
   - 没有真正阻止 `pending / failed` workspace 进入普通 chat
   - 这与 Phase 5.3 的设计要求不一致

3. **SSE 处理逻辑不可测试**
   - chat 流式逻辑直接写在页面脚本里
   - token/tool_start/tool_end/done 等事件没有独立抽象
   - 后续一旦扩展 retrieval/title/bootstrap stream，会进一步失控

4. **没有正式前端测试体系**
   - 缺少单元测试
   - 缺少组件测试
   - 缺少基于 mock API 的 E2E smoke

### 1.2 Phase 6 的定位

Phase 6 解决的是“前端系统如何稳定承接 Phase 5.3 的运行时模型”。

它不解决：

- bootstrap runner 的完整执行正文
- `running -> completed` 的真实后端自动闭环
- 独立 agent profile 系统
- Monaco/IDE 级复杂编辑体验

---

## 2. 目标状态

完成后，前端应具备以下行为：

1. 用户打开前端后，自动探测后端连接状态
2. 用户可创建、切换、重命名 workspace
3. 切换 workspace 后，所有请求都自动带上 `X-Workspace-Id`
4. 若 workspace 的 `bootstrap_status != completed`，前端进入 bootstrap gate，而不是普通 chat
5. 只有 `completed` 的 workspace 才显示正常三栏工作台
6. 用户可在 workspace 内创建、切换、重命名 session
7. 中间聊天区支持 SSE token、tool_start、tool_end、done
8. 左侧可浏览 memory/skills，右侧可浏览 concepts/tasks/packs
9. 支持附件上传并注入当前聊天请求
10. 支持读取 trace envelope 并展示工具审计
11. 以上能力都有对应测试覆盖

一句话：从“可演示页面”升级为“真正可持续开发的前端应用”。

---

## 3. 范围判断

### 3.1 纳入 Phase 6 的内容

1. `React + Vite + TypeScript` 工程化重构
2. 三栏工作台布局重建
3. workspace 选择、新建、重命名
4. session 选择、新建、重命名
5. bootstrap gate UI 与流程拦截
6. chat 流式 SSE 接入
7. 文件树、文件预览、附件上传、trace 面板
8. API client / SSE parser / store 抽象
9. `Vitest + React Testing Library + MSW + Playwright`

### 3.2 不纳入 Phase 6 的内容

1. bootstrap runner 完整后端实现
2. `workspace_scope.md` 的真实自动生成逻辑
3. agent/workspace 双实体拆分
4. Monaco 编辑器和复杂 IDE 布局
5. SSR / Next.js

### 3.3 关键边界说明

Phase 6 前端必须承认并显式处理一个事实：

- 当前 `POST /api/workspaces/{id}/bootstrap/start` 只完成状态流转，不执行完整 runner 正文

这意味着：

- 前端可以实现 bootstrap gate
- 前端可以实现 start 按钮与 retry 入口
- 但不能伪造“bootstrap 已完整完成”

因此 Phase 6 的职责是“正确表达现状并阻止错误路径”，不是“掩盖后端未完成的逻辑”。

---

## 4. 技术决策

### 4.1 前端框架

使用：

- `React 18`
- `Vite`
- `TypeScript`

理由：

1. 这是当前阶段最轻量、最快速、最适合前后端分离的组合
2. 不需要 SSR
3. 更适合做本地开发、mock API 测试和后续 Playwright

### 4.2 状态管理

使用：

- `TanStack Query`：管理服务端数据
- `Zustand`：管理 UI 层状态

理由：

1. workspace/session/history/tree/manifest 适合 query 管理
2. file preview、trace drawer、apiBase、当前选中项适合 lightweight store
3. 比单纯 Context 更利于拆分和测试

### 4.3 测试栈

使用：

- `Vitest`
- `React Testing Library`
- `MSW`
- `Playwright`

分工：

1. `Vitest`：测纯逻辑与工具函数
2. `RTL`：测组件与状态联动
3. `MSW`：mock API，保证组件测试不依赖真实后端
4. `Playwright`：跑完整 smoke 流程

### 4.4 API 设计约束

前端统一遵守以下约束：

1. 统一由 `apiClient` 注入 `X-Workspace-Id`
2. `POST /api/chat` body 中仍显式带 `workspace_id`
3. 新前端只使用 `/api/workspaces`
4. `/api/agents` 仅保留兼容，不再作为新前端主入口

### 4.5 SSE 设计约束

前端必须把 SSE 解析独立成模块，至少支持：

- `token`
- `tool_start`
- `tool_end`
- `new_response`
- `done`
- `error`

并且要对 `done` 事件做兼容：

- 若返回 `trace_path`，优先使用
- 若未返回，fallback 读取 `context_trace/{session_id}.json`

### 4.6 文件预览与 Markdown 渲染决策

Phase 6 新增一条明确交互决策：

1. 左右两栏以及 Layer 1 文件在被点击查看时，不再以内嵌底部 preview card 为主形态
2. 改为在中间聊天区上方打开一个**可关闭的覆盖式文件预览层**
3. 该预览层优先采用 `drawer / sheet` 风格，而不是传统阻塞式 modal
4. `.md` 文件默认走 Markdown 渲染，同时保留“原文 / 渲染”切换
5. 非 Markdown 文件继续走文本预览

这样设计的原因是：

- Markdown 文件（如 `AGENTS.md`、`SOUL.md`、`project.md`、`workspace_scope.md`）是当前系统的核心内容载体
- 原始文本预览可读性不足
- 将预览覆盖在聊天区上方，既能保证阅读集中，又不会永久挤压左右栏
- drawer 比传统 modal 更适合“边看文档边继续聊天”的研究工作流

因此，Phase 6 中关于文件查看的推荐交互统一收敛为：

- 树结构仍然保留在左右两栏
- 文件内容在中间区以覆盖式预览层打开
- 预览层必须可关闭
- 预览层应支持 `Esc` 关闭、关闭按钮、点击遮罩关闭

### 4.8 Chat 滚动与消息对齐决策

Phase 6 再新增一条聊天区交互约束：

1. 中间 chat 区必须使用独立滚动容器，而不是依赖整页滚动
2. 当消息过长时，滚动应只发生在 chat 内容区内部
3. 用户消息与 assistant 消息维持两边对齐：
   - user 在右
   - assistant 在左
4. 工具审计卡、系统提示和长文本不应破坏消息对齐关系

这样设计的原因是：

- 当前研究型对话内容明显长于普通客服聊天
- 若没有明确滚动区，页面会被长消息和预览层拖得过长
- 用户在“边看文档边聊天”时，需要一个稳定的中间滚动上下文

因此 Phase 6 聊天区的推荐形态是：

- `chat-stage` 保持固定高度
- `chat-scroll` 负责内部滚动
- 新消息到来时自动滚动到底部
- 左右消息气泡保持清晰的视觉对齐

### 4.9 Markdown 文件前端编辑决策

Phase 6 新增一条内容编辑决策：

1. 左右两边树中的 `.md` 文件，打开后应支持直接在前端编辑
2. 编辑入口放在覆盖式预览层内，而不是跳转到独立页面
3. 编辑完成后通过 `POST /api/files` 直接保存回当前 workspace
4. 仅对 `.md` 文件开放编辑；非 Markdown 文件仍保持只读预览

这样设计的原因是：

- 左右两栏展示的很多核心文件本质上就是工作中的可编辑文档
- 用户常见需求不是“只看”，而是快速修 `project.md`、`AGENTS.md`、`TASK_*.md`
- 在预览层内直接编辑，能保持当前聊天上下文不丢失

### 4.10 Markdown 编辑器架构选择

在“自建 textarea 编辑”和“接入通用 Markdown 编辑组件”之间，Phase 6 选用：

- `@uiw/react-codemirror`
- `@codemirror/lang-markdown`

选择理由：

1. 当前前端已经有自定义的覆盖式预览层与 Markdown 渲染层
2. 需求重点是“在当前 overlay 中编辑并保存”，而不是引入一个重量级、强侵入的整套 Markdown IDE
3. CodeMirror 6 更适合保留现有布局、样式和保存链路
4. 它比 Monaco 更轻，比整套 md-editor 更容易与现有 `react-markdown` 预览模式共存

因此 Phase 6 的最终方案是：

- 预览层继续由自定义 overlay 承担
- 渲染模式继续使用 `react-markdown`
- 编辑模式切换为 CodeMirror Markdown 编辑器

### 4.11 Assistant Markdown 与审计折叠决策

Phase 6 再新增一条 assistant 消息渲染约束：

1. assistant 正文支持 Markdown 渲染
2. 若回答中包含：
   - `Context Trace（可公开版）`
   - `Rationale（可公开版）`
3. 这两部分不应直接占据主回答区域
4. 它们应和工具调用 trace 一起进入统一的“本轮工作流审计”折叠组件
5. 工具调用 trace 默认折叠，不默认全部展开

这样设计的原因是：

- 主回答区域应优先承载“用户真正要读的答案”
- `Context Trace` 和 `Rationale` 更像审计信息，而不是主结论
- 工具 trace 全展开会让科研型回答显得过长、噪声过高

因此推荐交互是：

- assistant 正文只显示精简后的 Markdown 主回答
- 审计组件默认折叠
- 用户点击后再展开查看：
  - tool trace
  - Context Trace（可公开版）
  - Rationale（可公开版）

### 4.7 开发流程约束

从本次需求开始，Phase 6 采用以下变更纪律：

1. 任何新的交互、架构、数据流或测试要求
2. 在正式执行代码改动前
3. 必须先写入对应的开发计划和开发日志

也就是说，后续每次改动都遵循：

1. 先更新 `docs/phase6-dev-plan.md`
2. 再更新 `docs/phase6-dev-log.md`
3. 然后才执行实现

这条约束用于避免：

- 口头决策与实际实现脱节
- 交互变更没有被文档追踪
- 后续复盘时无法还原“为什么这样改”

---

## 5. 前端架构规划

### 5.1 目标目录结构

```text
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── playwright.config.ts
├── src/
│   ├── main.tsx
│   ├── styles.css
│   ├── app/
│   │   ├── App.tsx
│   │   └── queryClient.ts
│   ├── features/
│   │   ├── app/
│   │   │   └── store.ts
│   │   ├── workspace/
│   │   │   ├── BootstrapGate.tsx
│   │   │   └── WorkspaceDialogs.tsx
│   │   ├── chat/
│   │   │   └── ChatPanel.tsx
│   │   ├── files/
│   │   │   └── FileTreePanel.tsx
│   │   └── trace/
│   │       └── TracePanel.tsx
│   ├── shared/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── sse.ts
│   │   ├── types/
│   │   │   └── api.ts
│   │   └── utils/
│   │       ├── format.ts
│   │       └── storage.ts
│   └── test/
│       ├── server.ts
│       └── setup.ts
└── tests/
    └── smoke.spec.ts
```

### 5.2 组件层划分

1. `App`
   - 负责全局 query 和 layout 装配

2. `WorkspaceSelector + WorkspaceDialogs`
   - 负责 workspace 创建、切换、重命名

3. `BootstrapGate`
   - 负责阻止未初始化 workspace 进入普通 chat

4. `ChatPanel`
   - 负责历史、输入、SSE、附件、流式消息
   - assistant Markdown 渲染
   - 工作流审计折叠组件

5. `FileTreePanel`
   - 负责左/右两栏文件树

6. `DocumentPreviewOverlay`
   - 负责覆盖式文件预览层
   - 支持 Markdown 渲染、原文切换、前端编辑与保存

7. `TracePanel`
   - 负责 trace envelope 展示

---

## 6. 状态设计

### 6.1 服务端状态

使用 Query 管理：

1. `workspaces`
2. `workspace manifest`
3. `sessions`
4. `history`
5. `trace envelope`
6. `memory tree`
7. `atom tree`

### 6.2 本地 UI 状态

使用 Zustand 管理：

1. `apiBase`
2. `connection`
3. `currentWorkspaceId`
4. `currentSessionId`
5. `leftPreview`
6. `rightPreview`
7. `tracePanelOpen`

### 6.3 切换 workspace 的前端行为

切换 workspace 时必须同时做：

1. 重置 `currentSessionId`
2. 关闭左右文件预览
3. 关闭 trace panel
4. 清理当前聊天临时态
5. 重新拉取 manifest / sessions / tree / trace

否则会出现“session 属于 A，文件树属于 B”的状态错位。

---

## 7. 实施步骤

### Step A：建立前端工程骨架

产出：

1. `frontend/package.json`
2. `vite.config.ts`
3. `tsconfig.json`
4. `src/main.tsx`
5. `src/styles.css`

目标：

- 前端从单文件脚本切换到正式工程
- 能运行 `npm run dev`
- 能运行 `npm run build`

### Step B：建立类型与 API client

产出：

1. `shared/types/api.ts`
2. `shared/api/client.ts`
3. `shared/api/sse.ts`

目标：

- 把后端接口收敛成统一类型
- 统一注入 `X-Workspace-Id`
- 把 SSE 解析从组件里抽离

### Step C：建立全局状态层

产出：

1. `features/app/store.ts`
2. `app/queryClient.ts`

目标：

- 管理 apiBase / workspace / session / preview / trace panel
- 支撑后续组件拆分

### Step D：实现 workspace 与 bootstrap gate

产出：

1. workspace 选择器
2. 新建/重命名 dialog
3. `BootstrapGate`

目标：

- `pending / failed / running` workspace 不进入普通 chat
- `completed` workspace 才进入主界面

### Step E：实现 session 与 chat 流式能力

产出：

1. session 下拉与操作按钮
2. `ChatPanel`
3. SSE token/tool 审计渲染

目标：

- 会话可创建、选择、重命名
- 聊天可流式显示
- 当前回合可看到工具调用记录

### Step F：实现文件树、预览、附件、trace

产出：

1. 左栏 memory tree
2. 右栏 atom tree
3. 覆盖式文件预览层
4. Markdown 渲染
5. Markdown 文件前端编辑与保存
6. assistant Markdown 渲染
7. 审计信息折叠展示
8. 附件上传
9. Trace panel

目标：

- 三栏工作流完整闭环
- 可从聊天区发起上传
- 可查看会话 envelope
- 可在聊天区上方查看 Markdown 文件
- 可直接在前端修改左右栏 Markdown 文件
- assistant 主回答支持 Markdown 渲染
- `Context Trace / Rationale / 工具 trace` 收口到折叠审计组件

### Step G：补齐测试体系

产出：

1. 单元测试
2. 组件测试
3. Playwright smoke

目标：

- Phase 6 后续开发不再依赖“手点页面试试看”

---

## 8. 测试计划

### 8.1 单元测试

覆盖内容：

1. `apiClient` 是否正确注入 `X-Workspace-Id`
2. SSE parser 是否能正确解析 `token`、`done`
3. store 是否能在切换 workspace 时清空 session / preview / trace

### 8.2 组件测试

覆盖内容：

1. `BootstrapGate` 在 `pending` 时显示正确文案与按钮
2. App 在 `pending workspace` 下不进入普通 chat
3. workspace/session 基础 UI 渲染是否正确
4. Markdown 文件点击后以覆盖式预览层打开
5. 预览层可关闭，且不破坏当前 chat 状态
6. Markdown 文件可在预览层中编辑并保存
7. assistant Markdown 主回答渲染正确
8. 审计组件默认折叠，点击后可展开查看

### 8.3 E2E smoke

至少覆盖两条链路：

1. `pending workspace`
   - 打开页面
   - 读取 manifest
   - 进入 bootstrap gate

2. `completed workspace`
   - 打开页面
   - 进入 chat 工作台
   - 发送一条消息
   - 收到 token
   - 收到 done

### 8.4 测试执行命令

```bash
npm run build
npm run test:run
npm run test:e2e
```

---

## 9. 交付物清单

Phase 6 完成后应至少产出：

1. 新的 `frontend` React 工程
2. workspace-aware API client
3. bootstrap gate
4. session/chat/files/assets/trace 主界面
5. 单元测试
6. 组件测试
7. E2E smoke

---

## 10. 风险与限制

### 10.1 bootstrap runner 尚未闭环

当前后端只实现了：

- `pending|failed -> running`

尚未实现：

- `running -> completed` 的完整自动闭环

因此前端必须诚实表达这个现状。

### 10.2 `done` 事件契约可能与文档存在差异

当前前端实现必须对 `trace_path` 做兼容 fallback，不能完全依赖文档理想态。

### 10.3 当前重点不是视觉升级

Phase 6 主要目标是结构、契约和测试，不是大规模做视觉设计实验。

---

## 11. 验收标准

Phase 6 完成的最低验收标准：

1. 前端已迁移到 React + Vite + TypeScript
2. 所有请求自动带 `X-Workspace-Id`
3. `pending / failed` workspace 无法进入普通 chat
4. workspace 切换后 session/tree/trace 不串
5. chat SSE 可显示 token 与工具事件
6. 支持附件上传
7. Markdown 文件支持渲染预览
8. 文件查看以可关闭覆盖层形式出现
9. Chat 内容区具备独立滚动能力，长会话不破坏整体布局
10. 左右栏 Markdown 文件支持前端直接编辑与保存
11. assistant 主回答支持 Markdown 渲染
12. `Context Trace / Rationale / 工具 trace` 默认折叠展示
13. 支持 trace envelope 查看
14. `npm run build` 通过
15. `npm run test:run` 通过
16. 至少 1 条 Playwright smoke 通过

### 11.1 左栏 Skills 收敛规则

为避免左栏信息密度明显高于右栏，Phase 6 前端将不再在左栏展开完整 `skills/` 目录树，而采用以下收敛规则：

1. 左栏标题回归“记忆层”
2. `skills/` 不再完整展开到与 `memory/*` 并列
3. 左栏只保留一个 `SkillSnapshot` 快捷入口
4. 快捷入口实际打开文件为：
   - `skills/SKILLS_SNAPSHOT.md`
5. 设计目标：
   - 左右两侧信息节奏更对齐
   - 避免 system/workspace skills 树过长压缩记忆层可读性
   - 保留技能系统可达性，但不让它主导左栏结构

### 11.2 前端文案约束

产品界面中的说明文案不应暴露研发阶段、技术选型或内部架构背景。

因此前端展示层需要遵守：

1. 不显示 `Phase 6`、`phase5.3` 之类的阶段标识
2. 不显示 `React + Vite + TypeScript`、`workspace runtime` 之类的实现说明
3. bootstrap、空状态、说明文字都应改写为用户视角的产品文案

### 11.3 视觉主题约束

当前前端主色调从冷青科技感收敛为“莫兰迪多色系”方向。

设计约束：

1. 主题不采用单一主色，而采用多种低饱和颜色共存
2. 主色语言包括灰调绿、陶土、雾蓝、灰紫、沙米色
3. 面板、按钮、提示块应共享同一套莫兰迪语义色，而不是单一棕色覆盖全局

---

## 12. 一句话落地建议

Phase 6 不要再继续堆叠 `frontend/index.html` 的原生脚本，而应一次性切换到 `React + Vite`，并以 `bootstrap gate + workspace-aware API + 测试体系` 为核心交付，这样才能真正把 Phase 5.3 的运行时重构，变成一个可持续开发的前端系统。
