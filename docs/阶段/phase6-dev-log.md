# Phase 6 开发日志

> 目标：把前端从单文件 HTML 升级为 React + Vite + TypeScript 正式工程，落地 bootstrap gate、workspace-aware API client、三栏工作台，并建立前端测试体系

## 变更纪律

从本轮需求开始，Phase 6 采用新的执行约束：

1. 任何新的交互、架构、测试或状态流改动
2. 在正式执行代码实现前
3. 必须先写入 `docs/phase6-dev-plan.md` 和 `docs/phase6-dev-log.md`

本条用于保证后续每次改动都能先留痕，再实施。

## 新增需求记录

### 2026-03-17：Markdown 渲染 + 覆盖式文件预览

用户新增要求：

1. 左右两边文件以及 Layer 1 文件查看时支持 Markdown 渲染
2. 文件查看不再只停留在侧栏或底部 preview card
3. 改为以“可关闭的、覆盖在 chatbot 上方”的方式打开

本轮结论：

1. 需求合理
2. 具体交互不采用传统阻塞 modal
3. 改为在聊天区上方打开 `drawer / sheet` 风格的覆盖式预览层
4. `.md` 文件默认 Markdown 渲染，保留原文切换
5. 该决策已同步写入 `phase6-dev-plan.md`

### 2026-03-18：Chat 独立滚动 + Markdown 文件前端编辑

用户新增要求：

1. chat 内容过长时，中间区域需要更明确的滚动设计
2. 用户与 assistant 仍保持两边对齐
3. 左右两边的 `.md` 文件不仅可看，还要能直接在前端编辑

本轮结论：

1. chat 区采用独立内部滚动容器，而不是依赖页面整体滚动
2. 用户消息继续靠右，assistant 靠左，形成稳定对话轴
3. Markdown 文件的编辑入口放在覆盖式预览层内
4. 编辑保存直接走 `/api/files`
5. 该决策已同步写入 `phase6-dev-plan.md`

### 2026-03-18：Markdown 编辑器架构定稿 + assistant 审计折叠

用户新增要求：

1. 由我直接选定最适合的 Markdown 编辑架构
2. assistant 对话框支持 Markdown 渲染
3. `Context Trace（可公开版）` 和 `Rationale（可公开版）` 不直接占据主回答区
4. 工具调用 trace 不必全部默认展示，改为折叠在本轮工作流审计组件中

本轮结论：

1. 选用 `@uiw/react-codemirror + @codemirror/lang-markdown`
2. 编辑模式用 CodeMirror
3. 渲染模式继续使用 `react-markdown`
4. assistant 正文改为 Markdown 渲染
5. `Context Trace / Rationale / tool trace` 统一进入折叠式工作流审计组件
6. 该决策已同步写入 `phase6-dev-plan.md`

## 文件创建/更新记录

### Step A：建立前端工程骨架

- 创建：`frontend/package.json`
  - React 18 + Vite 6 + TypeScript 5.7
  - 依赖：react, react-dom, zustand, @tanstack/react-query
  - devDependencies：vitest, @testing-library/react, msw, @playwright/test
- 创建：`frontend/vite.config.ts`
  - @vitejs/plugin-react 插件
  - `@/` 路径别名指向 `./src`
  - vitest 配置（jsdom 环境，排除 tests/ 目录）
- 创建：`frontend/tsconfig.json`
  - target: ES2022, lib: ES2022 + DOM
  - jsx: react-jsx, paths: `@/*` → `./src/*`
- 创建：`frontend/tsconfig.node.json`
  - target: ES2022, moduleResolution: bundler, skipLibCheck: true
- 创建：`frontend/index.html`
  - 最小入口，挂载 `#root`，引用 `src/main.tsx`
- 创建：`frontend/src/main.tsx`
  - React.StrictMode + QueryClientProvider 包裹 App
- 创建：`frontend/src/styles.css`
  - GitHub Dark 风格主题，540 行全局 CSS
  - 三栏响应式布局（1220px 断点折叠为单栏）

### Step B：建立类型与 API client

- 创建：`frontend/src/shared/types/api.ts`
  - 完整类型定义：WorkspaceInfo, WorkspaceManifest, SessionMeta, ChatMessage, TraceEntry, TraceEnvelope, FileTreeNode, StreamEvent 等 18 个类型/接口
  - StreamEvent 联合类型覆盖 token/tool_start/tool_end/new_response/error/done
- 创建：`frontend/src/shared/api/client.ts`
  - `createApiClient()` 工厂函数，统一注入 `X-Workspace-Id` header
  - 封装全部后端 API：probe/workspaces/sessions/files/assets/chat
  - ApiError 类携带 HTTP status
- 创建：`frontend/src/shared/api/sse.ts`
  - `streamSse()` 独立 SSE 解析模块，从 ReadableStream 解析 event/data 行
- 创建：`frontend/src/shared/utils/format.ts`
  - formatDateTime, formatPreview, countTreeFiles, inferAssetIcon
- 创建：`frontend/src/shared/utils/storage.ts`
  - STORAGE_KEYS 常量、defaultApiBase()、safeLocalStorageGet()

### Step C：建立全局状态层

- 创建：`frontend/src/features/app/store.ts`
  - Zustand store + persist 中间件
  - `resetWorkspaceScope()` 切换 workspace 时清空 session/preview/trace
- 创建：`frontend/src/app/queryClient.ts`

### Step D：实现 workspace 与 bootstrap gate

- 创建：`frontend/src/features/workspace/BootstrapGate.tsx`
  - 根据 bootstrap_status 显示不同文案和操作按钮
  - data-testid="bootstrap-gate" 供测试定位
- 创建：`frontend/src/features/workspace/WorkspaceDialogs.tsx`
  - CreateWorkspaceDialog + RenameDialog

### Step E：实现 session 与 chat 流式能力

- 创建：`frontend/src/features/chat/ChatPanel.tsx`
  - 历史消息 + 实时流式消息（liveTurn）
  - SSE 事件处理：token/tool_start/tool_end/done/error
  - 附件上传队列 + route 参数 hash 解析

### Step F：实现文件树、预览、trace

- 创建：`frontend/src/features/files/FileTreePanel.tsx`
  - 递归 TreeNodeView + 分 section 展示
- 创建：`frontend/src/features/files/DocumentPreviewOverlay.tsx`
  - 覆盖在聊天区上方的文件预览层
  - `.md` 文件支持 Markdown 渲染
  - 支持“渲染 / 原文”切换
  - 支持遮罩关闭、按钮关闭、Esc 关闭
- 创建：`frontend/src/features/trace/TracePanel.tsx`
  - 固定定位浮层，按时间倒序展示工具审计记录
- 创建：`frontend/src/app/App.tsx`
  - 顶部控制栏 + 三栏布局（memory / chat or gate / atoms）
  - 10+ useQuery + 4 useMutation
  - bootstrap gate 条件渲染
  - 文件点击后统一在聊天区上方打开 `DocumentPreviewOverlay`
- 修改：`frontend/src/features/app/store.ts`
  - 预览状态从 `leftPreview/rightPreview` 收敛为单一 `documentPreview`
- 修改：`frontend/package.json`
  - 新增依赖：`react-markdown`、`remark-gfm`

### Step G：补齐测试体系

- 创建：`frontend/src/test/setup.ts` — MSW 生命周期 + jest-dom matchers
- 创建：`frontend/src/test/server.ts` — MSW setupServer
- 创建：`frontend/src/shared/api/client.test.ts` — X-Workspace-Id 注入验证
- 创建：`frontend/src/shared/api/sse.test.ts` — SSE parser 解析验证（2 tests）
- 创建：`frontend/src/features/app/store.test.ts` — resetWorkspaceScope 验证
- 创建：`frontend/src/features/workspace/BootstrapGate.test.tsx` — pending 状态渲染
- 创建：`frontend/src/features/files/DocumentPreviewOverlay.test.tsx`
  - Markdown 渲染
  - 原文切换
  - 关闭行为
- 创建：`frontend/src/app/App.test.tsx` — pending workspace 触发 gate（MSW 全链路）
- 创建：`frontend/tests/smoke.spec.ts` — Playwright E2E smoke

### Step H：构建修复（验收阶段）

- 修改：`frontend/tsconfig.json` — target/lib ES2020 → ES2022
- 修改：`frontend/tsconfig.node.json` — 新增 target/skipLibCheck/moduleResolution:bundler
- 修改：`frontend/vite.config.ts` — defineConfig 改用 vitest/config + exclude tests/
- 修改：`frontend/src/app/App.test.tsx` — mock URL 127.0.0.1 → localhost
- 新增 devDependency：`@types/node`

## 已处理问题

1. **TypeScript 构建失败：Array.at() 不存在**
   - 问题：代码使用了 ES2022 的 `.at()` 方法，但 tsconfig target/lib 设为 ES2020
   - 处理：升级 target 和 lib 到 ES2022

2. **TypeScript 构建失败：Cannot find module 'rollup/parseAst'**
   - 问题：tsconfig.node.json 的 moduleResolution 为 "Node"，无法解析 vite 6 的 rollup 子路径导出
   - 处理：改为 "bundler"

3. **TypeScript 构建失败：Private identifiers 需要 ES2015+**
   - 问题：tsconfig.node.json 未指定 target，vitest 类型文件中的 `#private` 语法报错
   - 处理：新增 target: ES2022 + skipLibCheck: true

4. **vitest 收集 Playwright 测试文件导致报错**
   - 问题：`tests/smoke.spec.ts` 被 vitest 错误收集，`@playwright/test` 的 `test.beforeEach` 在 vitest 环境下抛出 runtime 错误
   - 处理：vite.config.ts test.exclude 新增 `tests/**`

5. **App.test.tsx MSW mock URL 不匹配**
   - 问题：mock 使用 `http://127.0.0.1:8002`，但 jsdom 环境下 `window.location.hostname` 为 `localhost`，请求未被拦截
   - 处理：mock URL 统一改为 `http://localhost:8002`

6. **zustand persist 在测试环境下触发 localStorage 报错**
   - 问题：jsdom 环境中的 localStorage 行为与 persist 默认实现不一致，导致 `storage.setItem is not a function`
   - 处理：为 store 增加安全 storage fallback，并在 test setup 中注入内存版 localStorage mock

7. **Markdown 预览测试初次断言失败**
   - 问题：原文模式下换行文本在 Testing Library 中做精确匹配不稳定
   - 处理：改用函数型 matcher 验证关键文本片段

### Step I：Assistant Markdown 与审计折叠收口

- 修改：`frontend/package.json`
  - 新增依赖：`@uiw/react-codemirror`
  - 新增依赖：`@codemirror/lang-markdown`
- 新增：`frontend/src/features/chat/audit.ts`
  - 提取 assistant 回答中的：
    - `Context Trace（可公开版）`
    - `Rationale（可公开版）`
  - 主回答与审计信息拆分渲染
- 新增：`frontend/src/features/chat/AuditDisclosure.tsx`
  - 统一承接：
    - 工具调用 trace
    - Context Trace
    - Rationale
  - 默认折叠，点击后展开
- 修改：`frontend/src/features/chat/ChatPanel.tsx`
  - assistant 消息改为 `react-markdown` 渲染
  - 历史消息与流式消息都支持 Markdown
  - `Context Trace / Rationale` 不再直接占据主回答区
  - 本轮工具调用 trace 收口到折叠式“本轮工作流审计”
- 修改：`frontend/src/features/files/DocumentPreviewOverlay.tsx`
  - Markdown 编辑器由 `textarea` 升级为 `CodeMirror`
- 修改：`frontend/src/styles.css`
  - 增加 assistant markdown、审计折叠、CodeMirror 编辑器样式
- 新增：`frontend/src/features/chat/audit.test.ts`
- 新增：`frontend/src/features/chat/ChatPanel.test.tsx`
- 修改：`frontend/src/features/files/DocumentPreviewOverlay.test.tsx`
  - 用 mock CodeMirror 保证 jsdom 环境下编辑保存测试稳定

## 本轮处理问题

8. **assistant 主回答中 Context Trace / Rationale 冗余**
   - 问题：审计信息与主结论混排，阅读负担过高
   - 处理：解析 assistant 回答，将两类内容移入默认折叠的审计组件

9. **工具调用 trace 默认展开，长回合过于嘈杂**
   - 问题：SSE 回合中的工具调用会直接占据主聊天区
   - 处理：工具调用 trace 改为折叠在“本轮工作流审计”中，用户点击才展开

10. **Markdown 文件编辑器能力不足**
   - 问题：`textarea` 不适合 Phase 6 的 Markdown 文件直接编辑
   - 处理：采用 `@uiw/react-codemirror + @codemirror/lang-markdown`

11. **CodeMirror 在 jsdom 中触发布局测量报错**
   - 问题：测试环境缺少 `getClientRects()` 等真实布局能力
   - 处理：在组件测试中 mock CodeMirror，保留保存链路验证

### Step J：左栏 Skills 收敛

- 需求：左侧 skills 展示过长，影响与右栏的信息平衡
- 决策：
  - 左栏不再展示完整 `skills/` 目录树
  - 仅保留 `SkillSnapshot` 快捷入口
  - 快捷入口打开 `skills/SKILLS_SNAPSHOT.md`
- 目标：
  - 左右 bar 的信息密度更接近
  - 左栏主信息仍然保持在 control plane / identity / timeline
  - 技能系统仍可快速访问，但不再主导左栏长度

### Step K：前端研发文案清理

- 需求：前端不应显示与开发阶段、技术选型、内部架构直接相关的说明文字
- 决策：
  - 品牌区去掉 `Phase 6`
  - 去掉 `React + Vite + TypeScript`、`phase5.3`、`workspace runtime` 等描述
  - bootstrap 引导文案改为纯用户视角表达

### Step L：莫兰迪主题改色

- 需求：前端改为“莫兰迪多色系”
- 决策：
  - 主题根变量改为低饱和多色体系
  - 颜色语言包括灰调绿、陶土、雾蓝、灰紫、沙米色
  - 移除当前“单一棕色主导”的方向
  - 保持现有布局，仅替换主题语义色

## 测试结果

| # | 测试项 | 命令 | 预期 | 状态 |
|---|--------|------|------|------|
| 1 | TypeScript 编译 | `tsc -b` | 零错误 | PASS |
| 2 | Vite 生产构建 | `npm run build` | 输出 dist/ | PASS |
| 3 | API client 单元测试 | `npm run test:run` | X-Workspace-Id 注入正确 | PASS |
| 4 | SSE parser 单元测试 | `npm run test:run` | token/done 解析正确 | PASS |
| 5 | Store 单元测试 | `npm run test:run` | resetWorkspaceScope 清空状态 | PASS |
| 6 | BootstrapGate 组件测试 | `npm run test:run` | pending 状态渲染正确 | PASS |
| 7 | DocumentPreviewOverlay 组件测试 | `npm run test:run` | Markdown 渲染/关闭正确 | PASS |
| 8 | assistant 审计分流单元测试 | `npm run test:run` | 主回答与审计区拆分正确 | PASS |
| 9 | ChatPanel 组件测试 | `npm run test:run` | assistant Markdown + 折叠审计正确 | PASS |
| 10 | App bootstrap flow 集成测试 | `npm run test:run` | pending workspace 触发 gate | PASS |
| 11 | Playwright smoke | `npm run test:e2e` | 需后端运行 | 待验证 |

```
 Test Files  8 passed (8)
      Tests  11 passed (11)
```

## Phase 6 产出汇总

- 23 个前端源文件（含 7 个测试文件 + 1 个 Playwright spec）
- React 18 + Vite 6 + TypeScript 5.7 工程化前端
- Zustand 持久化 store + TanStack React Query 服务端状态
- workspace-aware API client（自动注入 X-Workspace-Id）
- Bootstrap gate（pending/failed/running 阻止进入 chat）
- 三栏工作台：memory tree / chat + SSE / atom tree
- 覆盖式文件预览层：聊天区上方 drawer + Markdown 渲染
- 附件上传 + trace envelope 查看
- Vitest + RTL + MSW 测试体系（8 files, 11 tests, all passed）

## Phase 6 → Phase 7 衔接

| Phase 6 产出 | 后续依赖 | 备注 |
|-------------|---------|------|
| BootstrapGate 组件 | bootstrap runner 完整实现后自动放行 | 当前 start 只做状态流转 |
| App.tsx ~430 行 | 建议拆分 custom hooks | ⚠️ 可维护但已接近上限 |
| 全局 CSS 540 行 | 建议迁移 CSS Modules 或 Tailwind | ⚠️ 类名冲突风险 |
| ChatPanel assistant Markdown 已接入 | 后续可补语法高亮或代码块复制 | 当前已支持主回答 Markdown 与审计折叠 |
| route 参数（hash 解析） | route 选择器 UI | 当前仅内部读取 |
| Playwright smoke.spec.ts | 需后端运行环境 | 未纳入 CI |
