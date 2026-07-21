# Phase 5.2 开发计划：Assets 智能上传 + 文件解析 + 溯源链路

> 目标：让用户上传的任意类型文件（表格、PPT、图片、PDF）自动存入 assets，后端提供统一的文件解析能力，Agent 生成的 memory 文件（TASK/PACK/原子笔记等）自动携带 `source_assets` 溯源路径，前端提供上传入口。

---

## 0. 问题定义

当前系统的 assets 上传（`POST /api/assets/upload`）只做了"存文件 + 返回路径"，存在以下缺口：

1. **前端无上传入口** — `frontend/index.html` 没有文件上传 UI，用户无法在对话中附带文件
2. **无文件解析** — 上传后 Agent 只能用 `read_file` 读文本，无法解析 PDF/PPTX/DOCX/Excel/图片
3. **无溯源** — Agent 生成的 memory 文件不会自动记录"这个笔记是基于哪个 asset 生成的"
4. **Agent 无法主动触发上传** — 当 Agent 判断用户需要上传文件时，没有机制引导用户上传

---

## 1. 设计原则

- **assets 是唯一的文件落盘点** — 所有用户上传的原始文件都进 `assets/` 子目录
- **深度解析交给 Agent** — Agent 读 skill 文档后自行用 python_repl/terminal 解析，结果直接写入 memory
- **memory 文件必须溯源** — 任何基于 asset 生成的 TASK/PACK/笔记，frontmatter 中必须包含 `source_assets` 字段
- **前端上传 = chat 附件** — 上传入口集成在聊天输入框，上传后自动注入当前对话上下文
- **Agent 可感知 assets** — 通过 ContextOrchestrator 的 Memory Map 和新增的 `parse_asset` tool

---

## 2. 架构变更概览

```
用户上传文件
    │
    ▼
前端 Chat 输入框 [📎 附件按钮]
    │
    ▼
POST /api/assets/upload  ──→  assets/{target_dir}/{sha8}_{filename}
    │                              (SHA256 前 8 位前缀，防同名覆盖)
    │  返回 saved_path + quick_summary + metadata
    ▼
Chat 消息自动注入附件上下文:
  "[附件: {filename}] 路径: {saved_path} 摘要: {quick_summary}"
    │
    ▼
Agent 读 skill 文档 → 自己用 python_repl / terminal 深度解析
Agent 生成 memory 文件时 write_file 自动注入 source_assets
```

**关键设计决策：深度解析交给 Agent，不建 parsers/ 层**

Phase 5.1 下载的官方 skill（pdf/docx/pptx）本质上是给 Agent 看的指令文档。Agent 读完 SKILL.md 后，自己就能在 `python_repl` 或 `terminal` 里调用 `pypdf`、`pandoc`、`markitdown` 等工具做深度解析。

因此 Phase 5.2 不再新建 `backend/parsers/` 目录和 `parse_asset` tool。上传端点只做轻量 quick_summary（文件类型 + 大小 + 页数/行数），深度解析完全由 Agent + skill + python_repl 完成。这样：
- 不重复实现 Agent 已有的能力
- 减少 8 个新文件 → 0 个
- 减少 7 个新 Python 依赖 → 0 个（依赖由 Agent 按需 pip install）
- Phase 5.2 范围大幅收窄，可落地性显著提升

---

## 3. 实施步骤

### Step A：后端 — Assets 上传增强 + 自动分类

#### A1. 增强 `backend/api/assets.py`

**当前状态**：只支持 `uploads/data/figures/ppt_pack` 四个固定目录，无文件类型检测。

**变更**：

1. 新增 `parsed` 到 `allowed_dirs`（存放解析结果）
2. 新增 `auto` 模式：根据文件扩展名自动分类到对应子目录
3. 返回值增加 `file_type` 和 `mime_type` 字段
4. **文件命名去重**：落盘路径改为 `assets/{target_dir}/{sha256前8位}_{原始文件名}`，避免同名覆盖破坏溯源

```python
# 自动分类规则
AUTO_CLASSIFY = {
    # 表格
    ".csv": "data", ".xlsx": "data", ".xls": "data", ".tsv": "data",
    # PDF
    ".pdf": "uploads",
    # PPT
    ".pptx": "ppt_pack", ".ppt": "ppt_pack",
    # Word
    ".docx": "uploads", ".doc": "uploads",
    # 图片
    ".png": "figures", ".jpg": "figures", ".jpeg": "figures",
    ".tif": "figures", ".tiff": "figures", ".svg": "figures", ".bmp": "figures",
    # 其他
    ".md": "uploads", ".txt": "uploads", ".json": "data",
}
```

**新增返回格式**：
```json
{
  "saved_path": "assets/data/a1b2c3d4_experiment_01.csv",
  "sha256": "abc123...",
  "size": 12345,
  "file_type": "csv",
  "mime_type": "text/csv",
  "target_dir": "data"
}
```

#### A2. upload 端点内置 `_quick_summary()` — 轻量摘要

**不新建独立的 parse 端点**。在 `POST /api/assets/upload` 返回值中直接附带 `quick_summary`。

**`_quick_summary()` 实现**（约 20 行，纯标准库 + 少量轻依赖）：

```python
def _quick_summary(file_path: Path, file_type: str) -> str:
    """轻量摘要，只做文件级元信息，不做深度解析。"""
    size_kb = file_path.stat().st_size / 1024
    if file_type in ("csv", "tsv"):
        lines = sum(1 for _ in open(file_path, encoding="utf-8", errors="ignore"))
        first_line = open(file_path, encoding="utf-8", errors="ignore").readline().strip()
        return f"CSV, {lines} 行, 列: {first_line[:100]}"
    if file_type == "pdf":
        # 仅用 pypdf 读页数（如果已安装），否则只返回大小
        try:
            from pypdf import PdfReader
            return f"PDF, {len(PdfReader(str(file_path)).pages)} 页, {size_kb:.0f}KB"
        except ImportError:
            return f"PDF, {size_kb:.0f}KB"
    if file_type in ("png", "jpg", "jpeg", "tif", "tiff", "svg", "bmp"):
        return f"图片 (.{file_type}), {size_kb:.0f}KB"
    return f".{file_type} 文件, {size_kb:.0f}KB"
```

**新增返回格式**（在原有基础上加 `quick_summary`）：
```json
{
  "saved_path": "assets/data/a1b2c3d4_experiment_01.csv",
  "sha256": "abc123...",
  "size": 12345,
  "file_type": "csv",
  "mime_type": "text/csv",
  "target_dir": "data",
  "quick_summary": "CSV, 340 行, 列: Time,Abs_420nm,Concentration..."
}
```

深度解析（提取全文、表格、图表）交给 Agent 在对话中通过 `python_repl` / `terminal` + skill 文档自行完成。

#### A3. 深度解析策略：Agent + Skill 文档 + python_repl

**不新建 `backend/parsers/` 目录**。深度解析完全由 Agent 自主完成：

```
用户上传 PDF → upload 返回 quick_summary("PDF, 12页, 2.3MB")
    → 附件信息注入 chat 消息
    → Agent 读 skills/pdf/SKILL.md，学会用 pypdf/pdfplumber
    → Agent 在 python_repl 中写代码提取文本和表格
    → Agent 用 write_file 写入 TASK_*.md（自动注入 source_assets）
```

**Agent 可用的解析工具链**（通过 skill 文档指导）：

| 文件类型 | Agent 读的 skill | Agent 用的工具 |
|---------|-----------------|---------------|
| PDF | `skills/pdf/SKILL.md` | `python_repl`: pypdf + pdfplumber |
| DOCX | `skills/docx/SKILL.md` | `terminal`: pandoc file.docx -o output.md |
| PPTX | `skills/pptx/SKILL.md` | `terminal`: python -m markitdown file.pptx |
| CSV/Excel | 内置知识 | `python_repl`: pandas |
| 图片 | 内置知识 | `python_repl`: Pillow |

**依赖安装策略**：Agent 首次使用某个库时，如果 import 失败，可通过 `terminal` 执行 `pip install pypdf` 等命令自行安装。这比在 requirements.txt 中预装所有可能用到的库更灵活。

---

### Step B：后端 — ContextOrchestrator 增强（不新增 tool）

**不新增 parse_asset tool，不修改 agent.py**。Agent 已有 `python_repl` + `terminal` + `read_file`，配合 skill 文档足以完成任何文件解析。工具数保持 5 个不变。

#### B1. 增强 `backend/graph/context_orchestrator.py` — Assets 扫描细化

**当前状态**：`_scan_assets()` 只返回目录名（`assets/uploads/`），不返回具体文件。

**变更**：返回具体文件列表 + 文件类型标注，让 Agent 知道 workspace 里有哪些可用 assets。

```python
def _scan_assets(self) -> list[dict]:
    """扫描 Assets 目录，返回文件级清单"""
    # 返回格式：
    # [
    #   {"path": "assets/uploads/paper.pdf", "type": "pdf", "size": 123456},
    #   {"path": "assets/data/exp01.csv", "type": "csv", "size": 7890},
    #   ...
    # ]
```

同时在 Memory Map 的 assets 部分注入文件清单，让 PromptBuilder 能把它写进 system prompt。

---

### Step C：后端 — 溯源机制（source_assets）

#### C1. 定义溯源规范

所有由 Agent 基于 asset 生成的 memory 文件（TASK/PACK/CONCEPT/日志等），必须在文件头部包含 `source_assets` 字段：

```markdown
---
source_assets:
  - path: assets/uploads/paper_heterojunction.pdf
    sha256: abc123...
    role: primary_input
  - path: assets/data/PMSO_kinetics.csv
    sha256: def456...
    role: data_source
created: 2026-03-15
skill_used: literature_pdf_4block
---

# TASK_literature_heterojunction_mechanism

...正文...
```

#### C2. 修改 PromptBuilder — 注入溯源指令

在 `prompt_builder.py` 的 execution contract 或 tooling block 中，追加溯源指令：

```
## Asset Traceability Rule

When you create or update any file in memory/ (TASK_*, PACK_*, CONCEPT_*, day logs, etc.)
that is derived from one or more assets, you MUST include a YAML frontmatter block with:

- source_assets: list of {path, sha256 (if known), role}
- role values: primary_input / data_source / reference / figure_source
- created: ISO date
- skill_used: skill id if applicable

This ensures every piece of knowledge can be traced back to its source material.
```

#### C3. 修改 `backend/tools/write_file_tool.py` — 溯源强制注入（必须）

**必须实现**：在 WriteFileTool 中增加 `source_assets` 参数。当 Agent 写入 `memory/` 下的文件且 `source_assets` 非空时，工具自动在文件头部注入 YAML frontmatter。这是溯源闭环的强制写入点，不是可选增强。

```python
class WriteFileToolInput(BaseModel):
    path: str
    content: str
    cwd: str = "."
    source_assets: list[str] = Field(default_factory=list,
        description="List of asset paths this file is derived from")
```

当 `source_assets` 非空时：
1. 检查 content 是否已有 `---` frontmatter
2. 如果没有，自动在头部插入包含 `source_assets` + `created` 的 YAML frontmatter
3. 如果已有 frontmatter，将 `source_assets` 合并进去（不覆盖已有字段）
4. 仅对 `memory/` 路径下的文件生效，`assets/` 和 `skills/` 不注入

---

### Step D：前端 — 上传入口 + 附件预览

#### D1. Chat 输入框增加附件按钮

在 `frontend/index.html` 的聊天输入区域添加：

1. 📎 按钮（或拖拽区域）
2. 点击后弹出文件选择器，支持多文件
3. 选中文件后显示附件预览条（文件名 + 类型图标 + 大小 + ❌ 移除）
4. 发送消息时：
   - 先调用 `POST /api/assets/upload` 上传每个文件（返回值已含 quick_summary）
   - 将附件信息（路径 + quick_summary）注入到 chat 消息中发送

#### D2. 消息注入格式

上传完成后，在用户消息前自动拼接附件上下文：

```
[附件已上传]
- 📄 paper_heterojunction.pdf → assets/uploads/paper_heterojunction.pdf (PDF, 2.3MB)
  解析摘要: 12页，主题：异质结催化剂的高价钴生成机制...
- 📊 PMSO_kinetics.csv → assets/data/PMSO_kinetics.csv (CSV, 45KB)
  解析摘要: 12列 x 340行，列名：Time, Abs_420nm, ...

用户消息：帮我分析这两个文件...
```

#### D3. 附件预览组件 + 二进制文件下载端点

**前置问题**：当前 `GET /api/files` 只支持 UTF-8 文本读取，非文本文件（图片/PDF/PPTX）会直接报 400 错误。前端附件预览需要一个能返回二进制文件的端点。

**新增端点**：`GET /api/assets/download?path=assets/figures/xxx.png`

```python
@router.get("/download")
async def download_asset(request: Request, path: str = Query(...)):
    """下载/预览 asset 文件（支持二进制）"""
    workspace = request.app.state.session_manager._workspace_dir
    resolved = resolve_safe_path(workspace, path)
    # 仅允许 assets/ 目录下的文件
    if not str(resolved.relative_to(workspace.resolve())).startswith("assets/"):
        raise HTTPException(403, "Only assets/ files can be downloaded")
    return FileResponse(resolved, filename=resolved.name)
```

**前端附件预览**：
- 图片类型：通过 `/api/assets/download?path=...` 获取，直接 `<img src="...">` 显示缩略图
- PDF：通过下载端点获取，用浏览器内置 PDF 查看器或 `<iframe>` 预览
- 其他类型：显示文件图标 + 名称，点击触发下载

#### D4. 拖拽上传支持

聊天区域支持拖拽文件上传，拖入时显示高亮提示区域。

---

### Step E：ChatRequest 扩展 — 附件字段

#### E1. 修改 `backend/api/chat.py` — ChatRequest 增加 attachments

```python
class AttachmentInfo(BaseModel):
    saved_path: str          # assets/uploads/paper.pdf
    # 无 parsed_path — 深度解析由 Agent 自行完成
    file_type: str = ""      # pdf / csv / docx / pptx / image
    summary: str = ""        # 解析摘要

class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True
    route: str = ""
    prompt_context: dict[str, Any] = Field(default_factory=dict)
    attachments: list[AttachmentInfo] = Field(default_factory=list)  # 新增
```

#### E2. 附件信息注入 system prompt

在 `chat.py` 的 `event_generator()` 中，如果 `body.attachments` 非空：
1. 将附件路径列表加入 metadata
2. PromptBuilder 在 workspace/metadata block 中注入当前对话的附件清单
3. Agent 可据此决定是否调用 `parse_asset` 或 `read_file` 读取详细内容

---

## 4. 文件变更清单

### 新建（0 个文件）

无新建文件。不再需要 `backend/parsers/` 目录和 `parse_asset_tool.py`。

### 修改（6 个文件）
1. `backend/api/assets.py` — 自动分类 + SHA8 命名去重 + quick_summary + download 端点
2. `backend/graph/context_orchestrator.py` — assets 扫描返回文件级清单
3. `backend/graph/prompt_builder.py` — 注入溯源指令 + 附件上下文
4. `backend/tools/write_file_tool.py` — source_assets 强制注入（必须）
5. `backend/api/chat.py` — ChatRequest 增加 attachments 字段
6. `frontend/index.html` — 附件按钮 + 拖拽上传 + 预览 + 消息注入

---

## 5. workspace 模板变更

无新增目录。不再需要 `assets/parsed/`——解析结果由 Agent 直接写入 `memory/tasks/` 或 `memory/packs/`。

---

## 6. 依赖变更

**Phase 5.2 不新增 Python 依赖到 requirements.txt**。

解析所需的库（pypdf、pdfplumber、markitdown、pandas 等）由 Agent 在对话中按需通过 `terminal` 执行 `pip install` 安装。这比预装所有可能用到的库更灵活，也避免了 requirements.txt 膨胀。

`_quick_summary()` 函数对 pypdf 做了 `try/except ImportError` 保护——如果未安装，只返回文件大小，不会报错。

| 依赖 | 安装方式 | 说明 |
|------|----------|------|
| `pypdf` | Agent 按需 `pip install` | PDF 页数/文本提取 |
| `pdfplumber` | Agent 按需 `pip install` | PDF 表格提取 |
| `markitdown[pptx]` | Agent 按需 `pip install` | PPTX 文本提取 |
| `pandas` + `openpyxl` | Agent 按需 `pip install` | CSV/Excel 分析 |
| `pandoc`（系统工具） | 需预装：`brew install pandoc` | DOCX → Markdown |

唯一建议预装的系统工具是 `pandoc`（DOCX 解析的主路径）。

---

## 7. 验证方式

### 自动化测试

新建 `backend/tests/test_asset_upload_enhanced.py`：
1. 自动分类正确（.csv → data, .pdf → uploads, .png → figures）
2. SHA8 命名去重：同文件上传两次路径相同，不同文件同名路径不同
3. quick_summary 返回正确的文件类型 + 元信息
4. download 端点能返回二进制文件
5. attachments 字段正确传入 ChatRequest
6. WriteFileTool source_assets 参数自动注入 frontmatter

### 手动集成验证

**场景 1：上传 CSV 并分析**
> 用户在前端附件按钮上传 experiment.csv → 自动存入 assets/data/ → 自动解析 → Agent 看到附件信息 → 调用 parse_asset 读取详细内容 → 生成 TASK 文件（含 source_assets 溯源）

**场景 2：上传 PDF 文献并拆解**
> 用户上传 3 篇 PDF → 自动存入 assets/uploads/ → 解析提取文本 → Agent 调用 literature_pdf_4block skill → 生成 TASK_literature_*.md（frontmatter 含 source_assets 指向 3 篇 PDF 路径）

**场景 3：上传 PPT 并整理**
> 用户上传旧版组会 PPT → 解析提取逐 slide 文本 → Agent 调用 results_to_report_structuring skill → 生成新的汇报结构（溯源到原 PPT）

---

## 8. 开发顺序

建议顺序：

| 顺序 | Step | 原因 |
|------|------|------|
| 1 | Step A（upload 增强 + quick_summary + download） | 核心上传能力 |
| 2 | Step B（ContextOrchestrator assets 细化） | 让 Agent 感知 assets |
| 3 | Step C（溯源：WriteFileTool + PromptBuilder） | 让产出可追溯 |
| 4 | Step E（ChatRequest attachments） | 前后端对接协议 |
| 5 | Step D（前端 UI） | 最后做 UI |

---

## 9. 风险点与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 大文件解析耗时 | PDF/PPTX 解析可能 >5s | 解析异步化，前端显示进度；设置 50MB 上传上限 |
| Agent 解析依赖缺失 | Agent 首次用 pypdf 时可能 import 失败 | Agent 可自行 pip install；quick_summary 对缺失依赖做了 try/except 保护 |
| Agent context 爆炸 | 大文件解析文本过长 | Agent 自行控制截断；skill 文档中已有截断建议 |
| 溯源 frontmatter 被 Agent 遗漏 | Agent 不一定每次都写 source_assets | PromptBuilder 强指令 + 后续 Phase 6 trace 审计补充 |
| 前端上传与 chat 消息时序 | 上传未完成就发送消息 | 前端 disable 发送按钮直到所有上传完成 |
| 图片 OCR 需求 | 部分用户上传扫描件/手写笔记 | Phase 5.2 不做 OCR，仅提取元信息；OCR 留作后续扩展 |
| ~~上传同名覆盖~~ | ~~旧 asset 被替换，溯源失真~~ | **已解决**：落盘路径改为 `{sha8}_{filename}`，同内容同名 = 同路径（幂等），不同内容同名 = 不同路径（不覆盖） |

---

## 10. Phase 边界提醒

**本 Phase 只做**：
- 文件上传自动分类 + SHA8 去重 + quick_summary + download 端点
- ContextOrchestrator assets 文件级扫描
- WriteFileTool source_assets 强制注入 + PromptBuilder 溯源指令
- 前端上传入口 + 附件预览
- ChatRequest attachments 字段
- 深度解析完全交给 Agent + skill 文档 + python_repl

**不做（留给后续 Phase）**：
- Phase 6：Trace 审计自动检查 source_assets 完整性
- Phase 6：从 trace 中自动提取 asset → memory 的溯源关系图
- Phase 7：assets 管理 UI（搜索、标签、批量操作）
- 后续：OCR 支持、音视频解析、在线协作上传
