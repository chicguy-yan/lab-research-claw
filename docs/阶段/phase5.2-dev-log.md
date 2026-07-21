# Phase 5.2 开发日志

> 目标：Assets 智能上传（自动分类 + SHA8 去重 + quick_summary + download）+ 溯源机制（write_file source_assets 强制注入）+ 前端附件上传入口

## 文件创建/更新记录

### Step A：Assets 上传增强

- 修改：`backend/api/assets.py`
  - 重写整个文件（75 行 → 153 行）
  - 新增 `AUTO_CLASSIFY` 字典：扩展名 → 目标子目录映射（14 种扩展名）
  - `target_dir` 默认值从 `"uploads"` 改为 `"auto"`，自动根据扩展名分类
  - 落盘路径从 `{filename}` 改为 `{sha256前8位}_{filename}`，防同名覆盖
  - 新增 `_detect_file_type()` 和 `_quick_summary()` 函数
  - `_quick_summary()` 对 CSV 返回行数+列名，对 PDF 尝试用 pypdf 读页数（try/except 保护），其他类型返回文件大小
  - 返回值新增 `file_type`、`mime_type`、`target_dir`、`quick_summary` 四个字段
  - 新增 `GET /api/assets/download` 端点：返回 `FileResponse`，支持二进制文件预览/下载，仅允许 `assets/` 目录

### Step B：ContextOrchestrator Assets 扫描细化

- 修改：`backend/graph/context_orchestrator.py`
  - `_scan_assets()` 返回类型从 `list[str]`（目录名）改为 `list[dict]`（文件级清单）
  - 每个条目包含 `path`、`type`、`size` 三个字段
  - 遍历 uploads/data/figures/ppt_pack 四个子目录下的所有文件

### Step C：溯源机制

- 修改：`backend/tools/write_file_tool.py`
  - `WriteFileToolInput` 新增 `source_assets: list[str]` 字段
  - 新增 `_inject_source_assets_frontmatter()` 函数：自动注入 YAML frontmatter
  - `_run()` 中当 `source_assets` 非空且路径以 `memory/` 开头时，自动调用注入
  - 支持已有 frontmatter 的合并（不覆盖已有 source_assets）
  - `description` 更新，提示 Agent 写 memory 文件时传入 source_assets

- 修改：`backend/graph/prompt_builder.py`
  - Execution Contract 新增 `Asset Traceability Rule` 章节，含 write_file 示例
  - Memory Map 的 Assets 部分支持 `list[dict]` 格式，显示文件路径+类型+大小
  - 向后兼容：如果 assets 仍是 `list[str]`（旧格式），正常显示

### Step E：ChatRequest Attachments

- 修改：`backend/api/chat.py`
  - 新增 `AttachmentInfo` Pydantic model（saved_path, file_type, summary）
  - `ChatRequest` 新增 `attachments: list[AttachmentInfo]` 字段
  - `_build_prompt_metadata()` 中注入 attachments 到 metadata
  - 消息持久化时，如果有附件，在 user message 前拼接附件上下文

### Step D：前端附件上传

- 修改：`frontend/index.html`
  - CSS：新增 `.attach-btn`、`.attachment-chip`、`.drop-overlay` 等样式
  - HTML：composer 区域新增 📎 按钮、隐藏 file input、附件预览条、拖拽覆盖层
  - JS：新增 `pendingFiles` 数组、`handleFileSelect()`、`addPendingFiles()`、`removePendingFile()`、`renderAttachmentBar()`、`uploadPendingFiles()` 函数
  - `sendMessage()` 中发送前先上传附件，将 attachments 注入 POST body
  - 拖拽上传：composer-bar 支持 dragover/dragleave/drop 事件

### 测试修复

- 修改：`backend/tests/test_write_file_tool.py`
  - `test_schema_exposes_cwd` 的 schema 字段集合从 `{"path", "content", "cwd"}` 更新为 `{"path", "content", "cwd", "source_assets"}`

## 已处理问题

1. **上传同名文件覆盖**
   - 问题：原实现直接用 `{filename}` 落盘，两次上传同名文件会静默覆盖
   - 处理：落盘路径改为 `{sha256前8位}_{filename}`，同内容幂等，不同内容不覆盖

2. **前端无法预览二进制文件**
   - 问题：`GET /api/files` 只支持 UTF-8 文本，图片/PDF 会报 400
   - 处理：新增 `GET /api/assets/download` 端点，返回 FileResponse

3. **write_file schema 测试失败**
   - 问题：新增 `source_assets` 字段后，`test_schema_exposes_cwd` 断言字段集合不匹配
   - 处理：更新测试断言包含 `source_assets`

## 测试结果

| # | 测试项 | 状态 |
|---|--------|------|
| 1-5 | Phase 4 原有测试（chat_write_file_flow） | ✅ PASS |
| 6-8 | fetch_url_tool 测试 | ✅ PASS |
| 9-11 | python_repl_tool 测试 | ✅ PASS |
| 12-14 | read_file_tool 测试 | ✅ PASS |
| 15-21 | skill_loader 测试（含 PromptBuilder 向后兼容） | ✅ PASS |
| 22-24 | system_prompt_contract 测试 | ✅ PASS |
| 25-29 | terminal_tool 测试 | ✅ PASS |
| 30-34 | write_file_tool 测试（含 source_assets schema） | ✅ PASS |

执行命令：
```bash
PYTHONPYCACHEPREFIX=/tmp/pycache backend/.venv/bin/python -m unittest discover -s backend/tests -v
```
结果：34/34 全部通过。

## Phase 5.2 产出汇总

| 指标 | 值 |
|------|-----|
| 新建文件 | 0 个 |
| 修改文件 | 6 个（assets.py, context_orchestrator.py, prompt_builder.py, write_file_tool.py, chat.py, index.html） |
| 修改测试 | 1 个（test_write_file_tool.py） |
| 新增 API 端点 | 1 个（GET /api/assets/download） |
| 修改 API 端点 | 1 个（POST /api/assets/upload：auto 分类 + SHA8 + quick_summary） |
| 新增 Python 依赖 | 0 个 |
| 回归测试 | 34/34 通过 |

## 关键设计决策

1. **深度解析交给 Agent，不建 parsers/ 层**
   - 官方 skill（pdf/docx/pptx）是给 Agent 看的指令文档
   - Agent 已有 python_repl + terminal，读完 SKILL.md 后自己就能解析
   - 后端只做轻量 quick_summary，不重复实现 Agent 已有的能力

2. **source_assets 在 WriteFileTool 中强制注入**
   - 不依赖 Agent 手动写 frontmatter（不可靠）
   - 工具层自动注入，只要 Agent 传了 source_assets 参数就生效
   - 仅对 memory/ 路径生效，assets/ 和 skills/ 不注入

3. **SHA8 命名去重**
   - 同内容同名 = 同路径（幂等）
   - 不同内容同名 = 不同路径（不覆盖）
   - 保护溯源稳定性

## Phase 5.2 → Phase 6 衔接

| Phase 5.2 提供 | Phase 6 如何使用 |
|----------------|-----------------|
| `POST /api/assets/upload`（auto + SHA8 + quick_summary） | 前端附件上传已对接，Phase 6 可在 UI 中展示上传历史 |
| `GET /api/assets/download` | Phase 6 可在文件查看器中预览图片/PDF |
| ContextOrchestrator 文件级 assets 清单 | Phase 6 可在左侧面板展示 assets 文件树 |
| WriteFileTool source_assets 注入 | Phase 6 Trace 审计可检查 source_assets 完整性 |
| ChatRequest.attachments | Phase 6 可在 trace 中记录每轮附件信息 |
| 前端 📎 附件按钮 + 拖拽上传 | Phase 6 可增强为批量上传 + 进度条 |

### Phase 5.2 已知限制

1. **quick_summary 对 PDF 依赖 pypdf**：如果未安装，只返回文件大小，不返回页数
2. **前端附件预览较简单**：只显示文件名+大小的 chip，未做图片缩略图内联显示
3. **溯源依赖 Agent 传参**：如果 Agent 不传 source_assets，工具层不会自动推断来源
4. **未做上传大小限制**：plan 中提到 50MB 上限，当前未实现
5. **attachments 未进入 trace schema**：附件信息通过 metadata 间接进入 prompt，但未作为独立字段进入 trace

---

**开发完成日期**：2026-03-16
