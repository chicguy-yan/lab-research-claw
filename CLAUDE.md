# CLAUDE.md — Experimental-Research-OpenClaw 项目规范

## 项目概述

Experimental-Research-OpenClaw 是一个科研 AI Agent 后端系统，采用分阶段（Phase 1-6）迭代开发。

- **后端目录**：`backend/`
- **文档目录**：`docs/`
- **Phase 计划**：`docs/phase{N}-dev-plan.md`
- **Phase 日志**：`docs/phase{N}-dev-log.md`
- **Phase 架构 HTML**：`docs/phase{N}-architecture.html`

## Phase 开发前置检查流程（必须执行）

**每次开始开发一个新的 Phase 前，必须自动执行以下步骤：**

### Step 1：扫描开发进度

1. 读取 `docs/phase{N}-dev-plan.md`（当前要开发的 Phase 计划）
2. 读取前一个 Phase 的日志 `docs/phase{N-1}-dev-log.md` 确认已完成
3. 检查 `backend/` 目录结构，确认代码实现状态：
   - 计划中列出的新建文件是否已存在
   - 计划中列出的修改文件是否已更新
   - `app.py` 路由注册是否完成
4. 输出进度报告：列出每个子任务的完成状态

### Step 2：写开发日志

开发完成（或发现已完成）后，创建 `docs/phase{N}-dev-log.md`，格式参照 `docs/phase1-dev-log.md`：

```markdown
# Phase {N} 开发日志
> 目标：{一句话描述}
## 文件创建/更新记录
### Step X {步骤名}
- 创建/修改：`{文件路径}`
  - {具体变更说明}
## 已处理问题
1. **{问题标题}**
   - 问题：{描述}
   - 处理：{解决方案}
## 测试结果
| # | 测试项 | 命令 | 预期 | 状态 |
## Phase {N} 产出汇总
## Phase {N} → Phase {N+1} 衔接
```

### Step 3：生成架构 HTML

创建 `docs/phase{N}-architecture.html`，格式参照 `docs/phase1-architecture.html`：

- 使用相同的 GitHub Dark 主题 CSS 变量
- 必须包含的章节：
  1. **Phase 目标与验收** — 表格列出所有验证项及 PASS/FAIL 状态
  2. **文件清单** — 文件树视图，新建文件用绿色 `.new`，Phase 1 文件用灰色 `.phase1`
  3. **API 端点** — 累计端点列表（含之前 Phase）
  4. **核心模块职责** — 卡片网格展示每个模块
  5. **请求流程** — 流程图展示关键 API 的调用链路
  6. **关键决策记录** — callout 样式记录架构决策
  7. **模块依赖关系** — ASCII 依赖图
  8. **Phase 路线图** — 表格标记各 Phase 状态
  9. **Phase 衔接表** — 当前 Phase 产出与后续 Phase 依赖

- CSS badge 类命名：`.badge-done`（绿色已完成），`.badge-phase{N}`（当前 Phase 颜色），`.badge-later`（灰色待开发）
- 可浏览器直接打开，无外部依赖

## 文档纪律

- **只写已实现的内容**：验证矩阵的 PASS 必须有实测支撑，未跑通的标 FAIL 或待验证
- **区分现状与目标态**：`architecture-summary.md` 是目标态文档（标注了实现状态声明），各 Phase 的 dev-log 才是交付依据
- **已知限制必须标注**：如 Agent CRUD 仅创建目录、不切换上下文，必须在衔接表中标 ⚠️
- **Bug 修复记入日志**：代码审查发现的 bug 修复需追加到对应 Phase 的 dev-log（如 Step 6 Bug 修复）
- **Prompt 组件位置**：workspace 根目录（SOUL.md / IDENTITY.md 等），**非** `workspace/` 子目录
- **会话文件格式**：envelope schema `{"messages": [...], "traces": []}`（Phase 1 Step 10 修正）

## 代码规范

- 后端框架：FastAPI + Pydantic v2
- Agent 框架：LangChain `create_agent` + LangGraph
- API 风格：Pydantic body + HTTPException，路由前缀 `/api`
- 文件操作：必须通过 `resolve_safe_path()` 安全检查（使用 `Path.relative_to()` 做边界检查，禁止 `str.startswith()`）
- 依赖策略：双文件 `requirements.txt`（范围）+ `requirements.lock`（精确锁）
- 新 Phase 不修改前序 Phase 核心模块，除非有明确的 bug 修复需求
- workspace 迁移：`app.py` 启动时对已有 workspace 补齐模板新增文件（`_migrate_workspace()`）

## Phase 状态

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 后端基础骨架：SSE chat + 会话 CRUD | DONE |
| Phase 2 | 文件系统 API + Agent CRUD + 路径安全 | DONE |
| Phase 3+4 | Context Orchestrator + PromptBuilder + TraceWriter + 5 核心工具 + Assets | DONE |
| Phase 5 | Skills 渐进式披露（SkillLoader + Agent 自主读取） | DONE |
| Phase 6 | 前端三栏 UI 增强 + route 选择器 + 技能面板 | Next |
