# Phase 3+4 修订开发计划 (基于对齐分析)

**版本**: v2.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## ⚠️ 关键约定（必须遵守）

### 1. 会话文件格式（Phase 1 已确立）
- 路径：`context_trace/{session_id}.json`
- Schema：**envelope 格式** `{"messages": [...], "traces": []}`
- 职责分离：
  - `messages` 字段 → SessionManager 读写（聊天历史）
  - `traces` 字段 → TraceWriter 读写（工具调用审计）
- **严禁直接覆盖文件**：必须先读取完整 envelope，只更新对应字段，再写回

参考实现：[session_manager.py:63-87](../../backend/graph/session_manager.py#L63-L87)

### 2. Skills 处理策略（Phase 3 vs Phase 5）
- **Phase 3 职责**：只注入静态控制层文件（AGENTS/SOUL/IDENTITY/USER/TOOLS/BOOTSTRAP/MEMORY/project.md）
- **Phase 5 职责**：动态加载和注入 skills（读取 skills/registry.json，根据用户消息匹配技能）
- **理由**：职责分离 + 按需加载 + 节省上下文

### 3. Memory Map Layer 2 必须包含 stage_reports/
- 路径：`memory/timeline/stage_reports/Rxx_*.md`
- 用途：阶段汇报文件（组会 PPT、阶段总结）
- 扫描策略：最近 5 个阶段汇报

---

## 一、核心意图回顾

基于你的核心意图:
1. ✅ **Tool-Driven Memory Access**: LLM 通过工具主动访问 memory
2. ✅ **Assets 溯源**: Memory 文件嵌入 assets 路径,便于用户溯源
3. ✅ **完整工具集**: 必须包含 terminal 和 python_repl
4. ✅ **简化架构**: 移除复杂的 ContextOrchestrator 预注入逻辑
5. ✅ **用户上传流程**: 文件先搬运到 assets,然后 LLM 触发 context-engineering

---

## 二、Phase 3+4 合并方案 (修订版)

### 2.1 核心架构

```
System Prompt 结构:
├── Block 1-5: 控制层完整注入 (AGENTS/SOUL/IDENTITY/USER/TOOLS/BOOTSTRAP/MEMORY/project.md)
├── Block 6: Memory Map (仅目录结构,不注入内容)
└── Block 7: Tools 说明 (terminal/python_repl/read_file/write_file/fetch_url)

注意: Skills 的加载和注入由 Phase 5 的 skill load 模块负责，Phase 3 不处理 skills。

LLM 工作流:
1. 看到 Memory Map → 了解有哪些文件
2. 根据需要 → 调用 read_file 读取
3. 处理完成 → 调用 write_file 写入 (带 assets 路径)
4. 数据分析 → 调用 python_repl
5. 系统操作 → 调用 terminal
6. 网络信息 → 调用 fetch_url 获取网页内容
```

### 2.2 与原 Phase3-4 Plan 的关键差异

| 维度 | 原 Plan | 修订版 |
|------|---------|--------|
| **ContextOrchestrator** | 移除 | **保留简化版** (仅生成 Memory Map) |
| **工具集** | 3个 (read/write/list) | **5个** (+ terminal + python_repl + fetch_url) |
| **Assets 处理** | 未明确 | **明确上传流程和溯源机制** |
| **Context 注入** | 仅目录列表 | **目录列表 + 推荐文件提示** |

---

## 三、Phase 3: Context Orchestrator + Prompt Builder

### 3.1 ContextOrchestrator (简化版)

**职责**: 生成 Memory Map,不预先注入文件内容

**文件**: `backend/graph/context_orchestrator.py`

```python
class ContextOrchestrator:
    """简化版 Context Orchestrator - 只生成 Memory Map"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def generate_memory_map(self, user_message: str = None) -> dict:
        """
        生成 Memory Map (目录结构 + 可选的推荐文件)

        Returns:
            {
                "layer1": ["memory/identity/user.md", ...],
                "layer2": ["memory/timeline/180d_index.md", ...],
                "layer3": ["memory/concepts/CONCEPT_*.md", ...],
                "assets": ["assets/uploads/", ...],
                "recommended": ["memory/identity/project.md", ...]  # 可选
            }
        """
        memory_map = {
            "layer1": self._scan_layer1(),
            "layer2": self._scan_layer2(),
            "layer3": self._scan_layer3(),
            "assets": self._scan_assets(),
        }

        # 可选: 基于用户消息推荐文件
        if user_message:
            memory_map["recommended"] = self._recommend_files(user_message)

        return memory_map

    def _scan_layer1(self) -> list[str]:
        """扫描 Layer1 文件"""
        layer1_dir = self.workspace_dir / "memory" / "identity"
        return [str(f.relative_to(self.workspace_dir))
                for f in layer1_dir.glob("*.md")]

    def _scan_layer2(self) -> list[str]:
        """扫描 Layer2 文件"""
        layer2_dir = self.workspace_dir / "memory" / "timeline"
        files = []
        # 180d_index
        files.extend(layer2_dir.glob("180d_index.md"))
        # phases
        files.extend((layer2_dir / "phases").glob("*.md"))
        # 最近的 weeks (最多5个)
        weeks = sorted((layer2_dir / "weeks").glob("*.md"), reverse=True)[:5]
        files.extend(weeks)
        # 最近的 days (最多10个)
        days = sorted((layer2_dir / "days").glob("*.md"), reverse=True)[:10]
        files.extend(days)
        # stage_reports (阶段汇报，最近5个)
        stage_reports = sorted((layer2_dir / "stage_reports").glob("*.md"), reverse=True)[:5]
        files.extend(stage_reports)
        return [str(f.relative_to(self.workspace_dir)) for f in files]

    def _scan_layer3(self) -> list[str]:
        """扫描 Layer3 文件"""
        layer3_dir = self.workspace_dir / "memory"
        files = []
        files.extend((layer3_dir / "concepts").glob("*.md"))
        files.extend((layer3_dir / "tasks").glob("*.md"))
        files.extend((layer3_dir / "packs").glob("*.md"))
        return [str(f.relative_to(self.workspace_dir)) for f in files]

    def _scan_assets(self) -> list[str]:
        """扫描 Assets 目录"""
        assets_dir = self.workspace_dir / "assets"
        dirs = ["uploads/", "data/", "figures/", "ppt_pack/"]
        return [f"assets/{d}" for d in dirs]

    def _recommend_files(self, user_message: str) -> list[str]:
        """基于用户消息推荐文件 (简单关键词匹配)"""
        recommended = []

        # 总是推荐 project.md
        recommended.append("memory/identity/project.md")

        # 关键词匹配
        if "汇报" in user_message or "R0" in user_message:
            recommended.append("memory/timeline/180d_index.md")
            # 查找最近的 stage_report
            stage_reports = sorted(
                (self.workspace_dir / "memory/timeline/stage_reports").glob("*.md"),
                reverse=True
            )
            if stage_reports:
                recommended.append(str(stage_reports[0].relative_to(self.workspace_dir)))

        if "合成" in user_message or "checklist" in user_message:
            recommended.append("memory/identity/lab_context.md")

        if "机理" in user_message or "证据链" in user_message:
            # 查找 mechanism 相关的 packs
            mechanism_packs = (self.workspace_dir / "memory/packs").glob("PACK_mechanism_*.md")
            recommended.extend([str(f.relative_to(self.workspace_dir)) for f in mechanism_packs])

        return recommended
```

### 3.2 PromptBuilder (修订版)

**职责**: 构建 System Prompt,注入控制层 + Memory Map

**文件**: `backend/graph/prompt_builder.py`

```python
class PromptBuilder:
    """构建 System Prompt (OpenClaw 风格)"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def build(self, memory_map: dict, metadata: dict = None) -> str:
        """
        构建 System Prompt

        Args:
            memory_map: ContextOrchestrator 生成的 Memory Map
            metadata: 元数据 (platform/timezone/language/current_date)

        Returns:
            完整的 System Prompt
        """
        blocks = []

        # Block 1: Identity
        blocks.append("You are a personal assistant running inside OpenClaw.")

        # Block 2: Tooling
        blocks.append(self._build_tooling_block())

        # Block 3: Workspace
        blocks.append(self._build_workspace_block())

        # Block 4: Inbound Context
        if metadata:
            blocks.append(self._build_metadata_block(metadata))

        # Block 5: Control Plane Files
        blocks.append(self._build_control_plane_block())

        # Block 6: Memory Map
        blocks.append(self._build_memory_map_block(memory_map))

        return "\n\n".join(blocks)

    def _build_tooling_block(self) -> str:
        return """## Tooling

Available tools:
- **terminal(command)**: 执行 Shell 命令 (受限环境)
- **python_repl(code)**: 执行 Python 代码
- **read_file(path)**: 读取文件内容
- **write_file(path, content)**: 写入文件到 memory/ 目录
- **fetch_url(url)**: 获取网页内容 (返回 Markdown 格式)

Tool usage guidelines:
1. Use terminal for system operations and file listing (e.g., ls, find)
2. Use python_repl for data analysis and visualization
3. Use read_file to access memory and assets
4. Use write_file to persist insights to memory (必须在 memory/ 目录下)
5. Use fetch_url to retrieve web content for research"""

    def _build_workspace_block(self) -> str:
        return f"""## Workspace

工作目录: {self.workspace_dir}

规则:
- **Memory Map 是你的导航**: 下面的 Memory Map 列出了所有可用文件
- **信息不足时**: 使用 read_file 读取相关文件
- **需要沉淀时**: 使用 write_file 写入 memory (必须包含 assets 溯源路径)
- **禁止脑补**: 必须基于实际文件内容,不要编造信息
- **Assets 溯源**: 写入 memory 时,必须包含原始 assets 文件路径"""

    def _build_metadata_block(self, metadata: dict) -> str:
        import json
        return f"""## Inbound Context (trusted metadata)

```json
{json.dumps(metadata, indent=2, ensure_ascii=False)}
```"""

    def _build_control_plane_block(self) -> str:
        """读取并注入控制层文件"""
        blocks = ["# Project Context"]

        # 控制层文件列表（不包含 skills，skills 由 Phase 5 处理）
        control_files = [
            "AGENTS.md",
            "SOUL.md",
            "IDENTITY.md",
            "USER.md",
            "TOOLS.md",
            "BOOTSTRAP.md",
            "MEMORY.md",
            "memory/identity/project.md",
        ]

        for file in control_files:
            file_path = self.workspace_dir / file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                blocks.append(f"## {file}")
                blocks.append(content)

        return "\n\n".join(blocks)

    def _build_memory_map_block(self, memory_map: dict) -> str:
        """构建 Memory Map 块"""
        lines = ["# Memory Map", ""]

        # Layer 1
        lines.append("## Layer 1 — Identity (长期稳定)")
        for file in memory_map.get("layer1", []):
            lines.append(f"- {file}")
        lines.append("")

        # Layer 2
        lines.append("## Layer 2 — Timeline (时间轴)")
        for file in memory_map.get("layer2", []):
            lines.append(f"- {file}")
        lines.append("")

        # Layer 3
        lines.append("## Layer 3 — Atom Notes (原子资产)")
        for file in memory_map.get("layer3", []):
            lines.append(f"- {file}")
        lines.append("")

        # Assets
        lines.append("## Assets (原始资产)")
        for dir in memory_map.get("assets", []):
            lines.append(f"- {dir}")
        lines.append("")

        # Recommended files (如果有)
        if memory_map.get("recommended"):
            lines.append("## 💡 Recommended Files (推荐阅读)")
            lines.append("Based on your query, you may want to read:")
            for file in memory_map["recommended"]:
                lines.append(f"- {file}")
            lines.append("")

        lines.append("**提示**: 使用 read_file(path) 读取任何你需要的文件")

        return "\n".join(lines)
```

### 3.3 TraceWriter

**职责**: 记录工具调用到 trace

**文件**: `backend/graph/trace_writer.py`

```python
class TraceWriter:
    """记录工具调用到 trace"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.trace_dir = workspace_dir / "context_trace"
        self.trace_dir.mkdir(exist_ok=True)

    def write_trace(self, session_id: str, tool_calls: list[dict]):
        """
        写入 trace（遵循 Phase 1 envelope schema）

        Args:
            session_id: 会话 ID
            tool_calls: 工具调用列表
                [
                    {
                        "tool": "read_file",
                        "args": {"path": "..."},
                        "result": "...",
                        "timestamp": "..."
                    },
                    ...
                ]
        """
        trace_file = self.trace_dir / f"{session_id}.json"

        # 读取完整 envelope（遵循 Phase 1 schema）
        if trace_file.exists():
            envelope = json.loads(trace_file.read_text())
            # 兼容旧格式
            if isinstance(envelope, dict) and "messages" not in envelope:
                envelope = {"messages": [], "traces": []}
        else:
            envelope = {"messages": [], "traces": []}

        # 只更新 traces 字段，保留 messages
        if "traces" not in envelope:
            envelope["traces"] = []
        envelope["traces"].extend(tool_calls)

        # 写回完整 envelope
        trace_file.write_text(json.dumps(envelope, indent=2, ensure_ascii=False))
```

---

## 四、Phase 4: 完整工具集

### 4.1 工具列表

| # | 工具 | 文件 | 优先级 |
|---|------|------|--------|
| 1 | terminal | `backend/tools/terminal_tool.py` | P0 |
| 2 | python_repl | `backend/tools/python_repl_tool.py` | P0 |
| 3 | read_file | `backend/tools/read_file_tool.py` | P0 |
| 4 | write_file | `backend/tools/write_file_tool.py` | P0 |
| 5 | fetch_url | `backend/tools/fetch_url_tool.py` | P0 |

### 4.2 工具实现要点

**terminal**:
- ✅ 黑名单拦截危险命令
- ✅ CWD 限制在 workspace
- ✅ 30 秒超时
- ✅ 输出截断 (10000 字符)
- 技术选型：直接使用 LangChain 内置工具 `langchain_community.tools.ShellTool`

**python_repl**:
- ✅ 隔离环境
- ✅ workspace_dir 自动添加到 sys.path
- ✅ 异常捕获
- ✅ 输出截断 (10000 字符)
- 技术选型：直接使用 LangChain 内置工具 `langchain_experimental.tools.PythonREPLTool`

**read_file**:
- ✅ 路径安全检查 (resolve_safe_path)
- ✅ 自动截断 (20000 字符)
- ✅ 支持多种编码
- 技术选型：直接使用 LangChain 内置工具 `langchain_community.tools.file_management.ReadFileTool`

**write_file**:
- ✅ 限制只能写入 memory/ 目录
- ✅ 自动创建父目录
- ✅ 路径安全检查
- 技术选型：基于 LangChain 的 `WriteFileTool` 封装，添加 memory/ 目录限制

**fetch_url**:
- ✅ 获取网页内容
- ✅ HTML 转 Markdown (使用 BeautifulSoup 或 html2text)
- ✅ 内容截断 (避免 Token 过多)
- 技术选型：基于 LangChain 的 `langchain_community.tools.RequestsGetTool` 封装，添加内容清洗
- ✅ 隔离环境
- ✅ workspace_dir 自动添加到 sys.path
- ✅ 异常捕获
- ✅ 输出截断 (10000 字符)

---

## 五、Assets 上传与溯源流程

### 5.1 上传流程

```
1. 用户上传文件 → POST /api/assets/upload
2. 后端保存到 assets/uploads/{filename}
3. 返回文件路径给前端
4. 前端将路径附加到用户消息
5. LLM 收到消息 + 文件路径
6. LLM 使用 read_file 读取文件
7. LLM 处理后使用 write_file 写入 memory (带溯源路径)
```

### 5.2 溯源格式

**Memory 文件示例** (`memory/tasks/TASK_exp_005.md`):

```markdown
---
task_id: TASK_exp_005
created_at: 2025-11-23T10:00:00
updated_at: 2025-11-23T10:30:00
---

# 实验 005: XRD 表征

## 数据来源

**原始数据**: [XRD 数据](assets/data/exp_005_xrd.csv)
**谱图**: [XRD 谱图](assets/figures/exp_005_xrd.png)
**实验照片**: [样品照片](assets/uploads/20251123_sample.jpg)

## 分析结果

根据 XRD 数据分析,Co(IV) 特征峰在 2θ=31.2°...

## 结论

...
```

### 5.3 Assets Upload API

**文件**: `backend/api/assets.py`

```python
from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import hashlib

router = APIRouter(prefix="/api/assets", tags=["assets"])

@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    target_dir: str = "uploads"
):
    """
    上传文件到 assets

    Args:
        file: 上传的文件
        target_dir: 目标目录 (uploads/data/figures/ppt_pack)

    Returns:
        {
            "saved_path": "assets/uploads/filename.csv",
            "sha256": "...",
            "size": 12345
        }
    """
    # 验证 target_dir
    allowed_dirs = ["uploads", "data", "figures", "ppt_pack"]
    if target_dir not in allowed_dirs:
        raise HTTPException(400, f"Invalid target_dir: {target_dir}")

    # 保存文件
    workspace_dir = get_current_workspace()
    target_path = workspace_dir / "assets" / target_dir / file.filename
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    content = await file.read()
    target_path.write_bytes(content)

    # 计算 SHA256
    sha256 = hashlib.sha256(content).hexdigest()

    return {
        "saved_path": str(target_path.relative_to(workspace_dir)),
        "sha256": sha256,
        "size": len(content)
    }
```

---

## 六、开发步骤

### Step 1: 实现 ContextOrchestrator (简化版)
- [ ] 创建 `backend/graph/context_orchestrator.py`
- [ ] 实现 `generate_memory_map()`
- [ ] 实现 `_scan_layer1/2/3()` 和 `_scan_assets()`
- [ ] 实现 `_recommend_files()` (简单关键词匹配)

### Step 2: 修改 PromptBuilder
- [ ] 修改 `backend/graph/prompt_builder.py`
- [ ] 实现 `_build_memory_map_block()`
- [ ] 更新 `_build_tooling_block()` (添加 terminal/python_repl)
- [ ] 更新 `_build_workspace_block()` (添加溯源规则)

### Step 3: 实现 TraceWriter
- [ ] 创建 `backend/graph/trace_writer.py`
- [ ] 实现 `write_trace()`

### Step 4: 实现 5 个核心工具
- [ ] `backend/tools/terminal_tool.py`
- [ ] `backend/tools/python_repl_tool.py`
- [ ] `backend/tools/read_file_tool.py`
- [ ] `backend/tools/write_file_tool.py`
- [ ] `backend/tools/fetch_url_tool.py`

### Step 5: 实现 Assets Upload API
- [ ] 创建 `backend/api/assets.py`
- [ ] 实现 `POST /api/assets/upload`

### Step 6: 集成到 AgentManager
- [ ] 修改 `backend/graph/agent.py`
- [ ] 注册 5 个工具
- [ ] 集成 ContextOrchestrator 和 PromptBuilder

### Step 7: 修改 Chat API
- [ ] 修改 `backend/api/chat.py`
- [ ] 集成 ContextOrchestrator → PromptBuilder → Agent → TraceWriter 流程

### Step 8: 端到端测试
- [ ] 测试场景 1: 数据分析 (python_repl)
- [ ] 测试场景 2: 合成 checklist (read + write)
- [ ] 测试场景 3: 阶段汇报 (read + list + write)
- [ ] 测试场景 4: Assets 上传与溯源

---

## 七、验收标准

### Phase 3 验收

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **ContextOrchestrator** | 能生成完整的 Memory Map | ⏳ |
| **PromptBuilder** | 能构建包含 Memory Map 的 System Prompt | ⏳ |
| **TraceWriter** | 能记录工具调用到 trace | ⏳ |
| **Memory Map 推荐** | 能基于关键词推荐文件 | ⏳ |

### Phase 4 验收

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **terminal** | 能执行命令,拦截危险命令 | ⏳ |
| **python_repl** | 能执行 Python 代码,支持数据分析 | ⏳ |
| **read_file** | 能读取 memory 和 assets 文件 | ⏳ |
| **write_file** | 能写入 memory,拦截非法路径 | ⏳ |
| **fetch_url** | 能获取网页内容并转换为 Markdown | ⏳ |
| **Assets Upload** | 能上传文件到 assets | ⏳ |
| **溯源机制** | Memory 文件包含 assets 路径 | ⏳ |

### 端到端验收

| 场景 | 验收标准 | 状态 |
|------|---------|------|
| **数据分析** | 上传 CSV → python_repl 分析 → 写入 Task (带溯源) | ⏳ |
| **合成 checklist** | 读取 lab_context → 生成 checklist → 写入 day | ⏳ |
| **阶段汇报** | 读取多个文件 → 生成 Pack (带溯源) | ⏳ |
| **网络研究** | 使用 fetch_url 获取网页内容 → 分析 → 写入 memory | ⏳ |

---

## 八、与原 Phase3-4 Plan 的对比

| 维度 | 原 Plan | 修订版 | 理由 |
|------|---------|--------|------|
| **ContextOrchestrator** | 移除 | **保留简化版** | 需要生成 Memory Map 和推荐文件 |
| **工具数量** | 3 个 | **5 个** | 必须支持数据分析和网络访问场景 |
| **Assets 处理** | 未明确 | **明确流程** | 用户核心需求 |
| **溯源机制** | 未明确 | **明确格式** | 用户核心需求 |
| **Context 注入** | 仅目录 | **目录 + 推荐** | 提高 LLM 效率 |
| **Skills 处理** | Phase 3 注入 | **Phase 5 处理** | 职责分离 + 按需加载 |
| **控制层文件** | 包含 SKILLS_SNAPSHOT.md | **移除 SKILLS_SNAPSHOT.md** | 该文件不存在，skills 由 Phase 5 处理 |
| **Layer 2 扫描** | 未包含 stage_reports | **包含 stage_reports** | 阶段汇报是重要交付物 |

---

## 九、关键设计决策

### 决策 1: 保留简化版 ContextOrchestrator

**理由**:
- 需要生成 Memory Map (目录结构)
- 需要基于关键词推荐文件
- 不预先注入文件内容,保持灵活性

### 决策 2: 5 个核心工具（包含网络访问能力）

**理由**:
- JSON 用户示例中大量数据分析场景
- PRD 明确要求核心工具
- 这是最小 MVP 的必要能力
- fetch_url 提供基础的网络信息获取能力，支持研究场景

### 决策 3: 明确 Assets 溯源机制

**理由**:
- 用户明确要求"memory 文件带 assets 路径"
- 便于用户溯源和审计
- 支持多模态 (CSV/图片/PDF)

### 决策 4: Phase 3 不处理 skills，完全由 Phase 5 负责

**理由**:
- **职责分离**：Phase 3 负责静态控制层，Phase 5 负责动态技能加载
- **按需加载**：避免每次都注入所有 8 个技能，节省上下文
- **可扩展性**：未来可以实现更复杂的技能匹配逻辑（语义匹配、优先级排序）
- **避免冲突**：移除不存在的 SKILLS_SNAPSHOT.md，使用真实的 skills/registry.json

### 决策 5: Layer 2 必须包含 stage_reports/

**理由**:
- 阶段汇报是重要的交付物（组会 PPT、阶段总结）
- 模板明确定义了 `memory/timeline/stage_reports/` 路径
- 与 AGENTS.md 的规范保持一致

---

## 十、开始开发

准备开始开发 Phase 3+4,按照以下顺序:

1. **Step 1**: ContextOrchestrator (简化版)
2. **Step 2**: PromptBuilder (修订版)
3. **Step 3**: TraceWriter
4. **Step 4**: 5 个核心工具 (terminal/python_repl/read_file/write_file/fetch_url)
5. **Step 5**: Assets Upload API
6. **Step 6**: 集成到 AgentManager
7. **Step 7**: 修改 Chat API
8. **Step 8**: 端到端测试

---

## 十一、Phase 3+4 → Phase 5 衔接

### Phase 3+4 产出（供 Phase 5 使用）

| 产出 | 文件路径 | 说明 |
|------|---------|------|
| **ContextOrchestrator** | `backend/graph/context_orchestrator.py` | 生成 Memory Map（目录结构 + 推荐文件） |
| **PromptBuilder** | `backend/graph/prompt_builder.py` | 构建 System Prompt（控制层 + Memory Map + Tools） |
| **TraceWriter** | `backend/graph/trace_writer.py` | 记录工具调用到 trace |
| **5 个核心工具** | `backend/tools/*.py` | terminal / python_repl / read_file / write_file / fetch_url |
| **Assets Upload API** | `backend/api/assets.py` | POST /api/assets/upload |

### Phase 5 需要实现的 Skills 模块

**职责**：动态加载和匹配技能，将技能注入到 LLM 上下文

#### 5.1 SkillLoader (新建)

**文件**：`backend/graph/skill_loader.py`

**职责**：
1. 读取 `skills/registry.json`
2. 根据用户消息匹配相关技能（通过 triggers 关键词匹配）
3. 动态加载匹配到的 `skills/<skill_id>/SKILL.md`
4. 返回技能内容供 PromptBuilder 注入

**接口设计**：
```python
class SkillLoader:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        """加载 skills/registry.json"""
        registry_path = self.workspace_dir / "skills" / "registry.json"
        if registry_path.exists():
            return json.loads(registry_path.read_text())
        return {"skills": []}

    def match_skills(self, user_message: str, max_skills: int = 3) -> list[dict]:
        """
        根据用户消息匹配技能

        Returns:
            [
                {
                    "id": "synthesis_checklist",
                    "name": "按时间顺序合成 checklist",
                    "content": "... SKILL.md 内容 ..."
                },
                ...
            ]
        """
        matched = []
        for skill in self.registry.get("skills", []):
            # 检查 triggers 是否匹配
            if any(trigger in user_message for trigger in skill.get("triggers", [])):
                skill_path = self.workspace_dir / skill["entry"]
                if skill_path.exists():
                    matched.append({
                        "id": skill["id"],
                        "name": skill["name"],
                        "content": skill_path.read_text(encoding='utf-8')
                    })
                if len(matched) >= max_skills:
                    break
        return matched
```

#### 5.2 修改 PromptBuilder（Phase 5）

**修改点**：添加 `_build_skills_block()` 方法

```python
def build(self, memory_map: dict, matched_skills: list[dict] = None, metadata: dict = None) -> str:
    """
    构建 System Prompt

    Args:
        memory_map: ContextOrchestrator 生成的 Memory Map
        matched_skills: SkillLoader 匹配的技能列表（Phase 5 新增）
        metadata: 元数据
    """
    blocks = []

    # Block 1-4: Identity + Tooling + Workspace + Metadata
    # ... (Phase 3 已实现)

    # Block 5: Control Plane Files
    blocks.append(self._build_control_plane_block())

    # Block 6: Skills (Phase 5 新增)
    if matched_skills:
        blocks.append(self._build_skills_block(matched_skills))

    # Block 7: Memory Map
    blocks.append(self._build_memory_map_block(memory_map))

    return "\n\n".join(blocks)

def _build_skills_block(self, matched_skills: list[dict]) -> str:
    """构建 Skills 块（Phase 5 新增）"""
    if not matched_skills:
        return ""

    lines = ["# Available Skills", ""]
    lines.append("以下技能已根据你的请求加载：")
    lines.append("")

    for skill in matched_skills:
        lines.append(f"## Skill: {skill['name']}")
        lines.append(skill['content'])
        lines.append("")

    return "\n".join(lines)
```

#### 5.3 修改 Chat API（Phase 5）

**修改点**：在调用 PromptBuilder 前先调用 SkillLoader

```python
# backend/api/chat.py (Phase 5 修改)

from backend.graph.skill_loader import SkillLoader

@router.post("/chat")
async def chat_stream(...):
    # ... 前置逻辑 ...

    # Phase 3: 生成 Memory Map
    orchestrator = ContextOrchestrator(workspace_dir)
    memory_map = orchestrator.generate_memory_map(user_message)

    # Phase 5: 匹配技能（新增）
    skill_loader = SkillLoader(workspace_dir)
    matched_skills = skill_loader.match_skills(user_message, max_skills=3)

    # Phase 3: 构建 System Prompt（Phase 5 传入 matched_skills）
    prompt_builder = PromptBuilder(workspace_dir)
    system_prompt = prompt_builder.build(
        memory_map=memory_map,
        matched_skills=matched_skills,  # Phase 5 新增参数
        metadata=metadata
    )

    # ... 后续逻辑 ...
```

### Phase 5 验收标准

| 验收项 | 标准 | 依赖 Phase 3+4 |
|-------|------|---------------|
| **SkillLoader** | 能读取 registry.json 并匹配技能 | ✅ PromptBuilder 接口 |
| **技能注入** | 匹配的技能能正确注入到 System Prompt | ✅ PromptBuilder.build() |
| **技能触发** | 用户消息包含 trigger 关键词时能加载对应技能 | - |
| **技能限制** | 最多加载 3 个技能，避免上下文过长 | - |

### 关键设计决策

**决策：Phase 3 不处理 skills，完全由 Phase 5 负责**

**理由**：
1. **职责分离**：Phase 3 负责静态控制层，Phase 5 负责动态技能加载
2. **灵活性**：按需加载技能，避免每次都注入所有 8 个技能
3. **上下文优化**：只加载相关技能，节省 token
4. **可扩展性**：未来可以实现更复杂的技能匹配逻辑（如语义匹配、优先级排序）

---

**文档完成** | 2026-03-09

**准备开始开发!**
