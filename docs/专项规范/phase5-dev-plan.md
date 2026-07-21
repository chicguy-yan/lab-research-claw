# Phase 5 开发计划（Agent 自主按需读取技能）

**版本**: v2.1 | **日期**: 2026-03-12（审查后修订）
**项目**: Experimental-Research-OpenClaw

---

## 一、Phase 5 目标

实现服务科研闭环的 Skills 渐进式披露机制：后端生成技能菜单摘要，Agent 根据用户消息和 route 上下文自主判断并按需读取完整技能内容；同时支持跨 workspace 的 `system skill`、workspace 自定义 skill，以及一个跨 workspace 常驻的科研版 `skill_creator`。

**核心原则**：
- 职责分离：Phase 3 负责静态控制层，Phase 5 负责技能菜单生成和文件准备；SkillLoader 不负责 route 决策、memory 决策、trace 决策、技能匹配
- 渐进式披露：每轮只注入 SKILLS_SNAPSHOT.md（菜单摘要），Agent 自主通过 read_file 读取完整 SKILL.md
- Agent 自主决策：后端不做 trigger 匹配、route 排序，决策权完全在 Agent
- 服务闭环：技能集合覆盖机理闭环、实验闭环、阶段汇报三条核心科研路径
- route 是工作语境：用于 context selection、atom_decision、trace，不用于技能匹配
- 多来源共存：运行时同时加载 `system` / `workspace` 两类 skill，不能只保留 backend 单一来源
- 用户可定制：workspace 允许沉淀自己的 skill，且不应被 backend 模板隐式覆盖

### 1.1 审查修订说明

本次修订纳入三类新增信息：

1. **代码现状**：当前实现已完成单来源 `backend/skills/` → `workspace/skills/` 的 snapshot 注入链路。
2. **审查发现**：
   - `route` 目前只实际进入 `metadata`，尚未进入 `ContextOrchestrator` 和 `TraceWriter`
   - `test_skill_loader.py` 中 “SKILL.md 复制验证” 使用了错误的 `src` 拼接方式，测试覆盖不足
   - 文档中的 block 顺序描述需要统一到真实实现：`Control Plane -> Skills Snapshot -> Execution Contract -> Memory Map`
   - `BOOTSTRAP.md` 对 `SKILLS_SNAPSHOT` 的常驻控制面描述与当前 Phase 5 注入方式存在漂移
3. **新增需求**：
   - 支持 backend system skill 与 workspace 自定义 skill 同时可用
   - 新增一个跨 workspace 常驻的科研版 `research_skill_creator`
   - 为用户自主创建 skill 提供安全的 `skills/` 写入路径

---

## 二、核心架构

### 2.1 技能来源分层（v2.1 新增）

运行时 skill 来源分为两层：

| 层级 | 位置 | 作用 | 生命周期 |
|------|------|------|---------|
| `system` | `backend/skills/` | 跨 workspace 常驻技能，既包含通用科研 skill，也包含 `research_skill_creator` | 跟随产品版本 |
| `workspace` | `workspace/skills/` | 用户在当前 workspace 内定制和沉淀的 skill | 跟随具体 workspace |

**运行时原则**：
- 两层 skill 都应出现在合并后的 snapshot 中
- Agent 仍然只通过 `read_file` 读取 workspace 内的运行时副本
- 运行时副本建议使用命名空间路径，避免冲突：
  - `skills/_system/<skill_id>/SKILL.md`
  - `skills/<skill_id>/SKILL.md`
- 不允许 backend 模板无提示覆盖用户 workspace skill
- 若存在同名 skill，默认并存而非隐式覆盖；如需覆盖，必须显式声明 `overrides`

### 2.2 Skills 注入流程

```
用户消息 + route
    ↓
SkillLoader.get_snapshot()
    ↓ 读取并合并 system/workspace 两个 registry
    ↓ 生成 SKILLS_SNAPSHOT.md（包含所有可用技能的元信息 + source + runtime_path）
    ↓ 确保 backend skill 的运行时副本已同步到 workspace 命名空间目录
    ↓
PromptBuilder.build(memory_map, skills_snapshot, metadata)
    ↓ Block 1: Identity
    ↓ Block 2: Tooling
    ↓ Block 3: Workspace / Metadata
    ↓ Block 4: Control Plane
    ↓ Block 5: Skills Snapshot（菜单，Agent 据此判断需要哪些技能）
    ↓ Block 6: Execution Contract
    ↓ Block 7: Memory Map
    ↓ [User Message]
    ↓
System Prompt → Agent
    ↓
Agent 读 SKILLS_SNAPSHOT（已在 prompt 中）
    ↓ 根据 user_message 和 route 上下文自主判断需要哪些技能
    ↓ 通过 read_file 工具读取 snapshot 给出的 runtime_path
    ↓ TraceWriter 记录 Agent 实际读取了哪些技能
```

### 2.3 PromptBuilder Block 顺序（冻结）

| Block | 内容 | 注入条件 |
|-------|------|----------|
| 1 | Identity | 必选 |
| 2 | Tooling | 必选 |
| 3 | Workspace / Metadata | 必选 |
| 4 | Control Plane | 必选 |
| 5 | Skills Snapshot | 每轮必注入（菜单摘要，Agent 据此自主决策） |
| 6 | Execution Contract | 必选 |
| 7 | Memory Map | 必选 |
| — | User Message | 用户消息（不在 system prompt 中） |

**约束**：
- 不允许每轮全量注入全部技能的完整内容
- Agent 通过 read_file 工具按需读取 snapshot 提供的 `runtime_path`
- 后端不做 trigger 匹配和 route 排序，决策权在 Agent

### 2.4 与 Phase 3+4 的集成

Phase 3+4 已提供：
- ✅ ContextOrchestrator - 生成 Memory Map
- ✅ PromptBuilder - 构建 System Prompt（需扩展 skills_snapshot 参数）
- ✅ TraceWriter - 记录工具调用（可记录 Agent 读取了哪些技能）
- ✅ 5 个核心工具（包括 read_file）

Phase 5 新增：
- SkillLoader - 生成 SKILLS_SNAPSHOT.md，确保 SKILL.md 在 workspace 可访问
- PromptBuilder 扩展 - 添加 `_build_skills_snapshot_block()` 方法
- Chat API 扩展 - 集成 SkillLoader，传入 route（用于 trace，不用于匹配）

**SkillLoader 职责边界**：只负责菜单生成、registry 合并和运行时文件准备。不负责 route 决策、memory 决策、trace 决策、技能匹配。

---

## 三、开发步骤

### Step 1: 实现 SkillLoader

**文件**: `backend/graph/skill_loader.py`

**职责**：
1. 读取 `backend/skills/registry.json`
2. 生成 SKILLS_SNAPSHOT.md 菜单摘要（包含所有技能的元信息）
3. 确保所有 SKILL.md 从 backend/skills/ 复制到 workspace/skills/，供 Agent 通过 read_file 按需读取
4. **不负责**：trigger 匹配、route 排序、自动注入完整 SKILL.md

**接口设计**：
```python
class SkillLoader:
    """Skills 管理：生成 snapshot 菜单，确保 SKILL.md 在 workspace 可访问。不做匹配逻辑。"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.registry = self._load_registry()
        self._ensure_skills_in_workspace()

    def _load_registry(self) -> dict:
        """加载 backend/skills/registry.json"""
        from config import SKILLS_DIR
        registry_path = SKILLS_DIR / "registry.json"
        if registry_path.exists():
            return json.loads(registry_path.read_text(encoding='utf-8'))
        return {"skills": []}

    def _ensure_skills_in_workspace(self) -> None:
        """
        确保所有 SKILL.md 从 backend/skills/ 复制到 workspace/skills/<skill_id>/SKILL.md。

        复制策略（克制，尊重用户定制）：
        - 若 workspace 中不存在，则从 backend 模板复制
        - 若 workspace 已存在同名 skill，默认不覆盖（保护用户定制版本）
        """
        from config import SKILLS_DIR
        import shutil

        for skill in self.registry.get("skills", []):
            src = SKILLS_DIR / skill["entry"]
            dst = self.workspace_dir / "skills" / skill["id"] / "SKILL.md"
            if src.exists() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    def get_snapshot(self) -> str:
        """
        生成菜单型技能摘要（SKILLS_SNAPSHOT），每轮注入 prompt。
        包含所有技能的 id / name / category / triggers / use_cases / preferred_routes。
        不含完整 SKILL.md 内容。Agent 据此自主决策需要读取哪些技能。

        写盘策略（克制）：
        - 每轮生成 snapshot 文本并返回（用于注入 prompt）
        - 只在 workspace/skills/SKILLS_SNAPSHOT.md 不存在时写盘
        - 不每轮强制写盘，避免不必要的 I/O

        Returns:
            摘要文本字符串
        """
        lines = ["# Skills Snapshot", ""]
        lines.append("以下技能可通过 read_file 工具读取：`workspace/skills/<skill_id>/SKILL.md`")
        lines.append("")
        by_category: dict[str, list] = {}
        for skill in self.registry.get("skills", []):
            cat = skill.get("category", "misc")
            by_category.setdefault(cat, []).append(skill)
        for cat, skills in by_category.items():
            lines.append(f"## {cat}")
            for s in skills:
                lines.append(f"### `{s['id']}` — {s['name']}")
                if s.get("triggers"):
                    lines.append(f"- **triggers**: {', '.join(s['triggers'])}")
                if s.get("use_cases"):
                    lines.append(f"- **use_cases**: {s['use_cases']}")
                if s.get("preferred_routes"):
                    lines.append(f"- **preferred_routes** (仅供参考): {', '.join(s['preferred_routes'])}")
                lines.append("")
        snapshot = "\n".join(lines)

        # 只在文件不存在时写盘
        snapshot_path = self.workspace_dir / "skills" / "SKILLS_SNAPSHOT.md"
        if not snapshot_path.exists():
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(snapshot, encoding="utf-8")

        return snapshot
```

**关键点**：
- 删除 match_skills 方法
- Agent 通过 read_file 工具自主读取 workspace/skills/<skill_id>/SKILL.md
- snapshot 包含 triggers / use_cases / preferred_routes 作为描述信息，供 Agent 理解，**backend 不得基于这些字段做过滤、排序、自动选择**
- 复制策略克制：只在 workspace 不存在时复制，不覆盖用户定制版本
- 写盘策略克制：snapshot 只在首次不存在时写盘，不每轮强制写入

### Step 1.1: 扩展为多来源 SkillLoader（v2.1 新增）

**目标**：将当前单来源 `backend/skills/` 扩展为 `system + workspace` 两层合并。

**新增职责**：
1. 合并多个 registry：
   - `backend/skills/registry.json`
   - `workspace/skills/registry.json`
2. 为每个 skill 生成稳定的运行时路径 `runtime_path`
3. 在 snapshot 中显式标记 `source`
4. 对 backend 来源的 skill 同步到 workspace 命名空间目录
5. 对 workspace 自定义 skill 直接纳入 catalog，不做覆盖

**合并输出结构（建议）**：

```python
{
    "id": "mechanism_evidence_chain",
    "name": "...",
    "source": "system",   # system | workspace
    "runtime_path": "skills/_system/mechanism_evidence_chain/SKILL.md",
    "entry": "skills/mechanism_evidence_chain/SKILL.md",
    "category": "analysis",
    "triggers": [...],
    "use_cases": "...",
    "preferred_routes": [...]
}
```

**冲突规则**：
- 默认不覆盖：同名 skill 保留多份并在 snapshot 中区分 `source`
- 若未来支持覆盖，需引入显式 `overrides` 字段，Phase 5 先不做隐式 shadow

---

### Step 2: 修改 PromptBuilder

**文件**: `backend/graph/prompt_builder.py`

**修改点**：
1. `build()` 新增 `skills_snapshot` 参数
2. 实现 `_build_skills_snapshot_block()`
3. **不注入**完整 SKILL.md 内容

**向后兼容**：新参数有默认值（`skills_snapshot=""`），已有调用 `build(memory_map=..., metadata=...)` 的测试无需修改签名，行为不变。

**代码修改**：
```python
def build(
    self,
    memory_map: dict,
    skills_snapshot: str = "",
    metadata: dict = None
) -> str:
    blocks = []
    # Block 1: Identity
    blocks.append("You are a personal assistant running inside OpenClaw.")
    # Block 2: Tooling
    blocks.append(self._build_tooling_block())
    # Block 3: Workspace / Metadata
    blocks.append(self._build_workspace_block())
    if metadata:
        blocks.append(self._build_metadata_block(metadata))
    # Block 4: Control Plane
    blocks.append(self._build_control_plane_block())
    # Block 5: Skills Snapshot（菜单，Agent 据此自主决策）
    if skills_snapshot:
        blocks.append(self._build_skills_snapshot_block(skills_snapshot))
    # Block 6: Memory Map
    blocks.append(self._build_memory_map_block(memory_map))
    return "\n\n".join(blocks)

def _build_skills_snapshot_block(self, snapshot: str) -> str:
    return f"# Skills Menu\n\n{snapshot}"
```

---

### Step 3: 修改 Chat API

**文件**: `backend/api/chat.py`

**修改点**：
1. `ChatRequest` 新增可选字段 `route: str = ""`（用于 trace 和上下文，不用于技能匹配）
2. 调用 SkillLoader.get_snapshot()，不调用 match_skills
3. 传入 snapshot 给 PromptBuilder

**`ChatRequest` 修改**：
```python
class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True
    route: str = ""   # Phase 5 新增：工作语境，用于 trace 和上下文，不用于技能匹配
```

**前端 route 输入来源（Phase 5 范围内的最小方案）**：

Phase 5 不做前端 UI 改造（那是 Phase 6 的事），但 route 必须能传入。采用以下最小方案：

> `frontend/index.html` 在发 `/api/chat` 时，从 URL hash 或 `<select>` 读取当前 route 值并附加到请求 body。

具体做法（在 `frontend/index.html` 里）：
```javascript
// 在发送 /api/chat 前，读取页面上已有的 route 选择器（或 URL 参数）
const route = document.getElementById('route-select')?.value ?? '';
// ...
body: JSON.stringify({ message, session_id: sessionId, route })
```

如果 Phase 5 开发期间前端还没有 route 选择器，可用以下临时方案保证可测试性：
- URL hash：`#route=mechanism_closure` → JS 解析 `location.hash`
- 或在聊天输入框支持前缀语法：`[mechanism_closure] 帮我看证据链` → 后端在 `chat.py` 里解析并填充 `route`

**Phase 5 验收要求**：至少有一种方式能让前端传入非空 route，使 route 上下文可被端到端测试覆盖。

**`event_generator` 修改**：
```python
from graph.skill_loader import SkillLoader

async def event_generator():
    # Phase 3: Generate Memory Map
    orchestrator = ContextOrchestrator(workspace_dir)
    memory_map = orchestrator.generate_memory_map(body.message)

    # Phase 5: 生成 Skills Snapshot（不做匹配）
    skill_loader = SkillLoader(workspace_dir)
    skills_snapshot = skill_loader.get_snapshot()

    # Phase 3+5: 构建 System Prompt
    prompt_builder = PromptBuilder(workspace_dir)
    metadata = {
        "platform": "darwin",
        "timezone": "Asia/Shanghai",
        "language": "zh-CN",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "route": body.route  # Phase 5 新增：route 作为工作语境注入 metadata
    }
    system_prompt = prompt_builder.build(
        memory_map=memory_map,
        skills_snapshot=skills_snapshot,
        metadata=metadata
    )

    # ... 后续逻辑 ...

    # Phase 3+4: Write trace（Phase 5 扩展：记录 route）
    if tool_calls:
        trace_writer = TraceWriter(workspace_dir)
        trace_writer.write_trace(body.session_id, tool_calls)
        # 注：可选扩展 write_trace 接口支持 route 参数，用于记录工作语境
```

**route 的实际用途**：
- 注入到 metadata 中，供 Agent 作为工作语境参考
- 可选：在 trace 中记录当前 route（需扩展 TraceWriter 接口）
- 未来可用于 context selection、atom_decision
- **不用于**技能匹配（后端不做匹配逻辑）

**审查说明（v2.1）**：
- 当前代码已实现 `route -> metadata`
- 当前代码**尚未实现** `route -> ContextOrchestrator`
- 当前代码**尚未实现** `route -> TraceWriter`
- 因此文档中凡是写 “route 已用于 context selection / trace” 的说法，都应理解为 **目标状态**，不是当前已完成状态

---

### Step 4: 补充测试

**已有测试兼容性说明**：

| 测试文件 | 影响 | 处理方式 |
|---------|------|----------|
| `tests/test_system_prompt_contract.py` | 调用 `PromptBuilder.build(memory_map, metadata=...)` | **无需修改**：新参数有默认值，签名向后兼容 |
| `tests/test_chat_write_file_flow.py` | POST `/api/chat` body 无 `route` 字段 | **无需修改**：`route` 默认为 `""`，行为与现在一致 |

**Phase 5 新增测试**（新建 `tests/test_skill_loader.py`）：

```python
# 以下为测试要点，非完整代码

# 1. get_snapshot 返回包含所有技能 id/name/triggers/use_cases/preferred_routes 的摘要文本，不含 SKILL.md 内容
# 2. _ensure_skills_in_workspace 只在 workspace 不存在时复制 SKILL.md，不覆盖已存在的文件
# 3. get_snapshot 只在 SKILLS_SNAPSHOT.md 不存在时写盘，不每轮强制写入
# 4. registry.json 不存在时，get_snapshot() 返回空字符串
# 5. Agent 可通过 read_file 工具读取 workspace/skills/<skill_id>/SKILL.md
# 6. preferred_routes 仅作为描述信息，backend 不基于此做任何过滤或排序
```

**测试补强（v2.1 新增）**：
- 修复 `test_skills_copied_to_workspace()` 中对 `src` 路径的错误拼接，不能再用 `cfg.SKILLS_DIR / skill["entry"]`
- 新增多来源测试：
  - system/workspace 两个 registry 的合并结果
  - snapshot 中包含 `source` 和 `runtime_path`
  - workspace skill 与 system skill 同名时默认并存
  - `research_skill_creator` 出现在 system 层并能被 snapshot 感知
  - route 仅进入 metadata，不应被误测为已进入 trace/context selection

### Step 5: 支持 workspace 自定义 skill（v2.1 新增）

**目标**：让当前 workspace 能沉淀自己的 skill，并在运行时与 backend skill 同时可用。

**需要补充**：
1. 初始化空的 `workspace/skills/registry.json`
2. 允许 workspace skill 只存在于当前 workspace，不需要回写 backend
3. `SkillLoader` 在每轮合并 workspace registry
4. `SKILLS_SNAPSHOT.md` 需要展示 skill 来源和运行时路径

**验收点**：
- 用户手工在 `workspace/skills/` 新建一个 skill 后，重启或重载后可在 snapshot 中看到
- 该 skill 不会被 backend 同名模板覆盖

### Step 6: 新增科研版 `research_skill_creator`（v2.1 新增）

**定位**：跨 workspace 常驻的 system skill，用于帮助用户在科研场景下自己构建 skill。

**建议位置**：
- `backend/skills/research_skill_creator/SKILL.md`
- `backend/skills/registry.json`

**职责**：
1. 访谈用户，明确 skill 的 `when_to_use / reads / writes / outputs`
2. 基于 `_skill_template/SKILL.md` 生成科研场景 skill
3. 将生成结果写入 `workspace/skills/<skill_id>/SKILL.md`
4. 更新 `workspace/skills/registry.json`
5. 明确告诉用户该 skill 是 workspace 私有 skill 还是建议沉淀为 system skill

**边界**：
- `research_skill_creator` 负责“帮用户造 skill”
- 不负责自动把 workspace skill 发布回 backend 模板库

### Step 7: 写入权限与安全收口（v2.1 新增）

要支持用户在 workspace 内自主创建 skill，仅有 `research_skill_creator` 不够，还需要收口路径策略：

1. 明确允许写入 `workspace/skills/`
2. `write_file` 写 skill 时必须经过与 `read_file` 一致的安全校验
3. 防止通过 skill 创建能力写出 workspace 边界

**说明**：
- 当前 `read_file` 已限制在 workspace 内
- 当前 skill 创建能力要真正开放前，需补齐 `skills/` 写入白名单和统一路径安全策略

---

## 四、验收标准

### Phase 5 验收

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **get_snapshot** | 每轮生成菜单摘要，写入 SKILLS_SNAPSHOT.md；包含所有技能，不按 route 过滤 | ⏳ 待实现 |
| **SKILL.md 复制** | 所有 SKILL.md 从 backend/skills/ 复制到 workspace/skills/<skill_id>/SKILL.md | ⏳ 待实现 |
| **route 字段落地** | `ChatRequest` 有 `route` 字段；前端至少有一种方式传入非空 route（URL hash / 前缀语法 / select） | ⏳ 待实现 |
| **snapshot 注入** | PromptBuilder 注入 snapshot，不注入完整 SKILL.md | ⏳ 待实现 |
| **Agent 自主读取** | Agent 可通过 read_file 读取 workspace/skills/<skill_id>/SKILL.md | ⏳ 待实现 |
| **block 顺序** | PromptBuilder 按冻结顺序组装：Control Plane → Skills Snapshot → Execution Contract → Memory Map | ⏳ 待实现 |
| **降级处理** | registry.json 不存在时不影响基础功能 | ⏳ 待实现 |
| **多来源技能** | system/workspace 两类 skill 同时出现在 snapshot 中 | ⏳ 待实现 |
| **workspace 自定义 skill** | workspace 私有 skill 可被加载，且不被 backend 模板隐式覆盖 | ⏳ 待实现 |
| **research_skill_creator** | 作为 system skill 常驻存在，并能帮助用户创建 workspace skill | ⏳ 待实现 |
| **写入安全** | 允许写入 `workspace/skills/`，同时保持路径安全边界 | ⏳ 待实现 |

### 端到端验收

| 场景 | 验收标准 | 状态 |
|------|---------|------|
| **snapshot 全量展示** | 无论 route 是什么，SKILLS_SNAPSHOT 始终包含所有技能 | ⏳ 待测试 |
| **Agent 自主判断** | Agent 根据 user_message 和 route 上下文，自主决定读取哪些技能 | ⏳ 待测试 |
| **read_file 可用** | Agent 通过 read_file 工具成功读取 workspace/skills/<skill_id>/SKILL.md | ⏳ 待测试 |
| **trace 记录** | TraceWriter 记录 Agent 实际读取了哪些技能文件 | ⏳ 待测试 |
| **无后端匹配** | 后端不做 trigger 匹配和 route 排序，所有决策在 Agent | ⏳ 待测试 |
| **多来源共存** | backend system skill 与 workspace 自定义 skill 同时可见、同时可读 | ⏳ 待测试 |
| **system skill 常驻** | `research_skill_creator` 无论 workspace 如何都可被 snapshot 展示 | ⏳ 待测试 |

---

## 五、Skills Registry 格式

**文件**: `backend/skills/registry.json`（即 `config.SKILLS_DIR / "registry.json"`，不在 workspace 下）

**字段说明**：
- `id`: 技能唯一标识
- `name`: 技能名称
- `category`: 通用能力类别（literature / analysis / figure / experiment / spectroscopy / ppt / word 等），不是 route 名
- `entry`: 技能文件路径（相对于 SKILLS_DIR，即 backend/skills/）
- `triggers`: 触发关键词列表（描述信息，供 Agent 理解，不作为后端硬逻辑）
- `use_cases`: 使用场景描述（可选，供 Agent 理解）
- `preferred_routes`: 优先推荐的 route 列表（**仅作为描述信息供 Agent 参考，backend 不得基于此做过滤、排序、自动选择**）

**格式示例**：
```json
{
  "skills": [
    {
      "id": "evidence_chain_pack",
      "name": "证据链整理",
      "category": "analysis",
      "entry": "skills/evidence_chain_pack/SKILL.md",
      "triggers": ["证据链", "文献整合", "汇报结构"],
      "use_cases": "整理机理证据链，生成汇报结构",
      "preferred_routes": ["mechanism_closure", "stage_progress", "writing_closure"]
    },
    {
      "id": "literature_extract",
      "name": "文献整理与证据提取",
      "category": "literature",
      "entry": "skills/literature_extract/SKILL.md",
      "triggers": ["文献", "evidence", "证据"],
      "preferred_routes": ["mechanism_closure"]
    },
    {
      "id": "figure_reading",
      "name": "图表解读",
      "category": "figure",
      "entry": "skills/figure_reading/SKILL.md",
      "triggers": ["图", "figure", "数据图"],
      "preferred_routes": ["experiment", "writing_closure"]
    },
    {
      "id": "xps_analysis",
      "name": "XPS 谱图分析",
      "category": "spectroscopy",
      "entry": "skills/xps_analysis/SKILL.md",
      "triggers": ["XPS", "谱图", "价态"],
      "preferred_routes": ["experiment"]
    },
    {
      "id": "stage_report",
      "name": "阶段汇报生成",
      "category": "ppt",
      "entry": "skills/stage_report/SKILL.md",
      "triggers": ["汇报", "R0", "组会"],
      "preferred_routes": ["stage_progress"]
    },
    {
      "id": "writing_outline",
      "name": "论文大纲生成",
      "category": "word",
      "entry": "skills/writing_outline/SKILL.md",
      "triggers": ["大纲", "outline", "论文结构"],
      "preferred_routes": ["writing_closure"]
    }
  ]
}
```

---

## 六、关键设计决策

### 决策 1: Agent 自主决策，后端不做匹配

**选择**: 删除后端 match_skills 逻辑，Agent 通过 read_file 自主读取技能

**理由**：
- 决策权在 Agent：Agent 可根据对话上下文做更智能的判断，不受后端硬编码的 trigger 匹配限制
- 架构更清晰：后端只提供"菜单"和"文件准备"能力，不做业务逻辑
- 更灵活：Agent 可以根据需要读取任意数量的技能，不受 max_skills=3 限制
- 可追溯：通过 TraceWriter 记录 Agent 实际读取了哪些技能，比后端匹配更透明

### 决策 2: 渐进式披露——snapshot 常驻，完整内容按需

**选择**: 每轮注入 SKILLS_SNAPSHOT.md 菜单摘要；Agent 通过 read_file 按需读取完整 SKILL.md

**理由**：
- snapshot 体积小（每条约 3-5 行），不影响上下文预算
- 完整 SKILL.md 可能较长，按需加载节省 token
- 符合渐进式披露原则，Agent 能感知有哪些技能而不被全量内容淹没
- Agent 可以根据实际需要决定读取顺序和数量

### 决策 3: route 是工作语境，不是匹配条件

**选择**: route 用于 context selection、atom_decision、trace，不用于技能匹配

**理由**：
- route 是"工作语境"，不是"准入门槛"
- 技能跨场景存在：同一技能可能在多个 route 下使用
- preferred_routes 只是描述信息，供 Agent 参考，**backend 不得基于 preferred_routes 做过滤、排序、自动选择**
- 避免硬过滤导致技能被错误排除

### 决策 4: SKILL.md 复制到 workspace 控制平面（克制策略）

**选择**: 启动时将 backend/skills/ 下的 SKILL.md 复制到 workspace/skills/<skill_id>/SKILL.md，但只在不存在时复制

**理由**：
- 所有控制平面文件都在 workspace/ 下，架构一致
- Agent 用现有的 read_file 工具就能读，不需要新工具
- backend/skills/ 是"模板库"，workspace/skills/ 是"运行时实例"
- **尊重用户定制**：若 workspace 已存在同名 skill，默认不覆盖，保护用户定制版本
- 不因 backend 更新时间更新就自动覆盖

### 决策 4.1: 技能来源分层 + 运行时命名空间（v2.1 新增）

**选择**：保留 backend system skill 作为模板源，同时允许 workspace skill 独立存在；运行时统一映射到 workspace 内的命名空间目录。

**理由**：
- 满足“跨 workspace 共享 skill + workspace 定制 skill”同时存在的需求
- Agent 仍然只需要 `read_file` 一个工具即可读取 skill
- 命名空间路径能避免 system/workspace 同名 skill 互相覆盖
- 后续 system skill（如 `research_skill_creator`）也能无缝加入 catalog

### 决策 5: SKILLS_SNAPSHOT.md 写盘策略（克制）

**选择**: 每轮生成 snapshot 文本用于注入 prompt，但只在文件不存在时写盘

**理由**：
- 避免不必要的 I/O 开销
- snapshot 主要用途是注入 prompt，写盘只是为了调试和前端展示
- 若需要更新 snapshot 文件，用户可手动删除后重启服务

---

## 七、Phase 5 → Phase 6 衔接

| Phase 5 提供 | Phase 6 如何使用 | 可靠性 |
|-------------|-------------|--------|
| **SkillLoader** | 前端可展示当前 Agent 读取的技能名称（通过 trace） | 可直接使用 |
| **SKILLS_SNAPSHOT.md**（workspace/skills/） | 前端可展示技能菜单面板；路径在 workspace 控制平面 | 可直接使用 |
| **registry.json（含 category/preferred_routes）** | 前端按闭环分组展示技能选择器；preferred_routes 可用于 UI 提示"推荐场景" | 可扩展 |
| **workspace/skills/<skill_id>/SKILL.md** | 前端可提供技能预览功能 | 可直接使用 |

---

## 八、已知限制

1. **Agent 决策质量**：依赖 LLM 的理解能力，可能出现漏读或误读技能的情况
2. **文件复制开销**：每次启动时检查并复制 SKILL.md，对于大量技能可能有性能影响
3. **动态更新**：修改 registry.json 后需重启服务（未实现热重载）
4. **route 落地不完整**：当前 route 虽然可进入 `/api/chat` 和 metadata，但尚未真正进入 `ContextOrchestrator` 与 `TraceWriter`
5. **测试覆盖缺口**：现有 `test_skill_loader.py` 中 “SKILL.md 复制验证” 需要修复路径拼接后才算有效
6. **文档漂移**：`BOOTSTRAP.md` 等模板文档仍需同步到 Phase 5 的实际注入方式
7. **多来源 skill 尚未实现**：当前代码仍以 `backend/skills/` 单来源为主，system/workspace registry 合并属于本次修订新增范围
8. **skill 创建安全策略未收口**：在允许用户通过 `research_skill_creator` 写入 `workspace/skills/` 之前，需明确写入白名单和路径安全边界

---

## 九、未来扩展方向

1. **技能推荐**：在 snapshot 中根据 route 和历史使用频率，标注"推荐"技能
2. **技能依赖**：支持技能之间的依赖关系（如技能 A 依赖技能 B）
3. **热重载**：监听 registry.json 变化，自动重新加载
4. **技能版本管理**：支持技能的版本控制和回滚

---

## 十、v2.1 详细开发方案

本节将 v2.1 的新增方向收敛成一套可按步骤实现的落地方案，目标是把当前单来源 `SkillLoader` 升级为双来源 `SkillLoader`，同时支持 workspace 自定义 skill 和跨 workspace 常驻的科研版 `research_skill_creator`。

### 10.1 目标状态

运行时要同时满足这 4 个条件：

1. backend system skill 可用
2. workspace 自定义 skill 可用
3. system skill 可常驻可用
4. Agent 仍然只通过 `read_file` 读取 workspace 内的运行时副本

### 10.2 技能目录约定

#### 模板源目录

```text
backend/
├─ skills/
│  ├─ registry.json                  # system skills
│  ├─ mechanism_evidence_chain/
│  ├─ stage_report_ppt/
│  ├─ research_skill_creator/
│  └─ ...
```

#### workspace 运行时目录

```text
workspace/
└─ skills/
   ├─ registry.json                  # workspace 自定义 skills
   ├─ SKILLS_SNAPSHOT.md
   ├─ _system/
   │  └─ <skill_id>/SKILL.md
   └─ <skill_id>/SKILL.md            # workspace 私有 skill
```

### 10.3 registry 约定

文件：
- `backend/skills/registry.json`

#### workspace registry

文件：
- `workspace/skills/registry.json`

workspace registry 初始为空：

```json
{
  "version": "0.1",
  "skills": []
}
```

### 10.4 统一后的运行时 SkillRecord

`SkillLoader` 内部不要直接混用三种 registry 原始结构，而应先归一化成统一的 `SkillRecord`。

建议结构：

```python
from dataclasses import dataclass

@dataclass
class SkillRecord:
    id: str
    name: str
    source: str               # "system" | "workspace"
    category: str
    entry: str                # registry 原始 entry
    runtime_path: str         # Agent 实际 read_file 的相对路径
    triggers: list[str]
    use_cases: str
    preferred_routes: list[str]
    origin_registry: str      # 便于调试
    overrides: str = ""       # 预留，Phase 5 默认不用
```

### 10.5 扫描顺序

`SkillLoader` 的扫描顺序固定为：

1. `system`
2. `workspace`

理由：
- `system` 表示产品级基础能力，必须最稳定
- `workspace` 表示用户当前项目私有能力

### 10.6 合并规则

#### 默认规则

- 所有 skill 都保留
- 不因同名自动覆盖
- snapshot 中必须展示 `source`
- Agent 通过 `runtime_path` 区分不同来源 skill

#### 运行时路径规则

| 来源 | runtime_path |
|------|--------------|
| `system` | `skills/_system/<id>/SKILL.md` |
| `workspace` | `skills/<id>/SKILL.md` |

#### 同名 skill 处理

若 `system` 和 `workspace` 都存在 `id = "xps_analysis"`：

- 默认并存
- snapshot 中显示两条：
  - `xps_analysis [system]`
  - `xps_analysis [workspace]`
- Agent 按 `runtime_path` 读取，不做隐式覆盖

#### 未来覆盖规则

若后续要支持覆盖，再引入：

```json
{
  "id": "xps_analysis",
  "overrides": "system:xps_analysis"
}
```

Phase 5 v2.1 不实现自动 shadow，只预留字段。

### 10.7 SkillLoader 详细流程

#### Step A: 读取多个 registry

新增内部方法：

```python
def _load_registry_file(self, path: Path) -> dict: ...
def _load_all_registries(self) -> list[tuple[str, Path, dict]]: ...
```

返回示意：

```python
[
    ("system", backend_system_registry_path, {...}),
    ("workspace", workspace_registry_path, {...}),
]
```

#### Step B: 归一化 SkillRecord

新增方法：

```python
def _normalize_registry(self, source: str, registry_path: Path, registry: dict) -> list[SkillRecord]: ...
```

关键逻辑：
- 校验必填字段：`id/name/entry`
- 补默认值：`category/triggers/use_cases/preferred_routes`
- 生成 `runtime_path`
- 写入 `origin_registry`

#### Step C: 同步 backend skill 到 workspace

新增方法：

```python
def _sync_backend_skills_to_workspace(self, skills: list[SkillRecord]) -> None: ...
```

规则：
- 只同步 `system`
- `workspace` 来源不做复制
- 若目标文件已存在，不覆盖
- 同步目标目录：
  - `system -> workspace/skills/_system/<id>/SKILL.md`

#### Step D: 生成 snapshot

新增方法：

```python
def _build_snapshot(self, skills: list[SkillRecord]) -> str: ...
```

snapshot 每条 skill 至少包含：
- `id`
- `name`
- `source`
- `category`
- `runtime_path`
- `triggers`
- `use_cases`
- `preferred_routes`

示例：

```markdown
## analysis

### `mechanism_evidence_chain` — 机理证据链审计
- source: system
- runtime_path: skills/_system/mechanism_evidence_chain/SKILL.md
- triggers: PMSO, DPD, 淬灭, Co(IV), ClO2
- use_cases: 审计机理证据链完整性
- preferred_routes: mechanism_closure
```

#### Step E: 写盘策略

保留当前“克制策略”，但要补一个刷新机制开关。

建议接口：

```python
def get_snapshot(self, force_refresh: bool = False) -> str: ...
```

规则：
- 每轮都重新生成 snapshot 文本并返回
- `SKILLS_SNAPSHOT.md` 默认只在不存在时写盘
- `force_refresh=True` 时覆盖写盘

### 10.8 `research_skill_creator` 详细方案

#### 位置

```text
backend/skills/research_skill_creator/SKILL.md
```

同时在：

```text
backend/skills/registry.json
```

注册为 system skill。

#### 目标

帮助用户在科研场景下构建自己的 workspace skill，而不是直接修改 backend 模板库。

#### 最小工作流

1. 询问用户 skill 要解决什么重复问题
2. 追问 5 个关键字段：
   - `when_to_use`
   - `inputs_required`
   - `reads`
   - `writes`
   - `outputs`
3. 基于 `_skill_template/SKILL.md` 生成 skill 文档
4. 写入：
   - `workspace/skills/<skill_id>/SKILL.md`
   - `workspace/skills/registry.json`
5. 提醒用户该 skill 是 workspace 私有 skill

#### 输出边界

`research_skill_creator` 不负责：
- 自动发布到 backend 之外的公共 skill 库
- 自动修改 backend system registry
- 自动覆盖现有 skill

### 10.9 安全与写入策略

要让用户能在 workspace 内创建 skill，必须先补齐路径安全边界。

#### 现状

- `read_file` 已限制在 workspace 内
- `write_file` 目前没有与 `read_file` 对齐的路径白名单策略
- `path_utils.py` 里的 `WRITABLE_PREFIXES` 还未包含 `skills/`

#### v2.1 方案

1. 将 `skills/` 加入可写前缀白名单
2. `write_file` 统一走 `resolve_safe_path(..., require_writable=True)`
3. skill 创建只允许写入：
   - `skills/registry.json`
   - `skills/<id>/SKILL.md`
   - `skills/_tmp/`（如果未来需要临时文件）

### 10.10 文件改动清单

#### 必改现有文件

- `backend/graph/skill_loader.py`
  - 从单 registry 升级为双 registry 合并
- `backend/graph/prompt_builder.py`
  - snapshot 中展示 `source` 和 `runtime_path`
- `backend/api/chat.py`
  - 保持现有 snapshot 注入逻辑，必要时支持 `force_refresh`
- `backend/graph/path_utils.py`
  - 将 `skills/` 纳入安全白名单
- `backend/tools/write_file_tool.py`
  - 接入统一路径安全校验
- `backend/tests/test_skill_loader.py`
  - 修复复制测试，新增多来源测试
- `backend/workspace-templates/BOOTSTRAP.md`
  - 同步 `SKILLS_SNAPSHOT` 的真实注入方式
- `backend/workspace-templates/README.md`
  - 补充 workspace skill 与 system skill 共存说明

#### 新建文件

- `backend/skills/research_skill_creator/SKILL.md`
- `backend/.openclaw/workspace-default/skills/registry.json` 或模板等价文件
- 如需拆测：
  - `backend/tests/test_research_skill_creator_contract.py`
  - `backend/tests/test_skill_loader_multi_source.py`

### 10.11 开发顺序

建议按以下顺序做，避免返工：

1. `SkillLoader` 双来源扫描与归一化
2. backend skill 到 workspace 命名空间目录的同步
3. snapshot 展示 `source/runtime_path`
4. workspace `skills/registry.json` 初始化
5. 路径安全与 `write_file` 收口
6. `research_skill_creator` system skill
7. 测试补强
8. 模板文档同步

### 10.12 验收标准（v2.1 追加）

1. `/api/chat` 每轮 prompt 中都能看到合并后的 snapshot
2. snapshot 同时包含 system/workspace 两类 skill
3. backend system skill 在 workspace 中落到 `_system/` 命名空间
4. workspace skill 可直接通过 `skills/<id>/SKILL.md` 读取
5. 同名 system/workspace skill 默认并存，不互相覆盖
6. `research_skill_creator` 能写出新的 workspace skill 并更新 `workspace/skills/registry.json`
7. `write_file` 对 `skills/` 的写入仍不能逃出 workspace 边界

---

## 十一、按文件实施清单

本节把 v2.1 方案压成可直接执行的文件级改造清单。默认按顺序实施，避免中途反复改接口。

### 11.1 `backend/graph/skill_loader.py`

**目标**：从单来源 loader 改成双来源 loader。

**要删/改的旧逻辑**
- 保留当前 `get_snapshot()` 主入口
- 废弃“只读 `backend/skills/registry.json`”的单来源假设
- 废弃“所有 backend skill 直接复制到 `workspace/skills/<id>/SKILL.md`”的单一路径

**新增方法**

```python
def _load_registry_file(self, path: Path) -> dict: ...
def _load_all_registries(self) -> list[tuple[str, Path, dict]]: ...
def _normalize_registry(self, source: str, registry_path: Path, registry: dict) -> list[SkillRecord]: ...
def _merge_skills(self, skill_lists: list[list[SkillRecord]]) -> list[SkillRecord]: ...
def _sync_system_skills_to_workspace(self, skills: list[SkillRecord]) -> None: ...
def _build_snapshot(self, skills: list[SkillRecord]) -> str: ...
```

**实现步骤**
1. 新增 `SkillRecord` 数据结构
2. 读取：
   - `backend/skills/registry.json`
   - `workspace/skills/registry.json`
3. 归一化出 `source/runtime_path`
4. system skill 同步到 `workspace/skills/_system/<id>/SKILL.md`
5. workspace skill 不复制，直接引用 `skills/<id>/SKILL.md`
6. snapshot 输出 `source` 和 `runtime_path`
7. `get_snapshot(force_refresh=False)` 支持强制刷新写盘

**实现后示意**

```python
loader = SkillLoader(workspace_dir)
snapshot = loader.get_snapshot()
```

### 11.2 `backend/graph/prompt_builder.py`

**目标**：不改主架构，只增强 snapshot 呈现。

**保留**
- `build(memory_map, skills_snapshot="", metadata=None)`
- block 顺序：
  `Identity -> Tooling -> Workspace/Metadata -> Control Plane -> Skills Snapshot -> Execution Contract -> Memory Map`

**调整点**
1. `_build_skills_snapshot_block()` 前增加简短说明：
   - system skill 在 `skills/_system/...`
   - workspace skill 在 `skills/...`
2. 避免在 prompt 中写死旧路径 `skills/<skill_id>/SKILL.md`
3. 统一让 Agent 以 snapshot 中的 `runtime_path` 为准

**最小改动**
- 只改文案，不改 `build()` 签名

### 11.3 `backend/api/chat.py`

**目标**：保持现有接入点稳定。

**保留**
- `ChatRequest.route`
- `SkillLoader.get_snapshot()`
- `PromptBuilder.build(...)`

**改动点**
1. `SkillLoader` 初始化后使用新的双来源 catalog
2. 若后续要支持前端“刷新 skills 菜单”，可预留：

```python
force_refresh: bool = False
```

3. 当前仍然只把 `route` 放进 metadata，不要在本轮顺手改 `ContextOrchestrator` 和 `TraceWriter`

**原因**
- 先把 skill 体系收口
- route 深化属于独立问题，避免 Phase 5.1 范围膨胀

### 11.4 `backend/graph/path_utils.py`

**目标**：允许安全写入 `skills/`。

**改动点**
- 将：

```python
WRITABLE_PREFIXES = ("memory/", "assets/", "context_trace/")
```

改为：

```python
WRITABLE_PREFIXES = ("memory/", "assets/", "context_trace/", "skills/")
```

**注意**
- 只开放 workspace 内 `skills/`
- 不允许绝对路径或越界路径

### 11.5 `backend/tools/write_file_tool.py`

**目标**：写 skill 时也走与 `read_file` 一致的安全边界。

**当前问题**
- 现在 `write_file` 没有统一调用 `resolve_safe_path(..., require_writable=True)`

**改动点**
1. 引入：

```python
from graph.path_utils import PathSecurityError, resolve_safe_path
```

2. 把当前直接拼路径的逻辑改为：

```python
target_path = resolve_safe_path(self.workspace_dir, path, require_writable=True)
```

3. 保留自动创建父目录
4. skill 创建失败时返回明确错误

**验收**
- 能写 `skills/my_skill/SKILL.md`
- 不能写 `../outside.md`

### 11.6 `backend/skills/registry.json`

**目标**：把 backend 现有 skill 全部视为 system skill。

**改动点**
1. 不新增第二份 backend system registry
2. `research_skill_creator` 也注册进这份 registry
3. 每个条目继续保留：
   - `id`
   - `name`
   - `entry`
   - `category`
   - `triggers`
   - `use_cases`
   - `preferred_routes`

**新增条目示意**

```json
{
  "id": "research_skill_creator",
  "name": "科研技能创建器",
  "category": "meta",
  "entry": "skills/research_skill_creator/SKILL.md",
  "triggers": ["创建 skill", "定制技能", "把这个流程沉淀成 skill"],
  "use_cases": "帮助用户为科研场景创建 workspace 私有 skill",
  "preferred_routes": ["experiment_closure", "mechanism_closure", "writing_closure", "stage_progress"]
}
```

### 11.7 `backend/skills/research_skill_creator/SKILL.md`

**目标**：提供一个跨 workspace 常驻的科研版 skill 创建器，先在网络上搜索最佳实践，给用户审核后再创建。

**内容结构建议**
1. `when_to_use`
2. `inputs_required`
3. `reads`
4. `writes`
5. `execution plan`
6. `output contract`
7. `prompt snippet`

**执行流程建议**
1. 先追问 skill 的使用场景
2. 再追问读写文件和产出结构
3. 基于 `_skill_template/SKILL.md` 生成 workspace skill
4. 写入：
   - `skills/<skill_id>/SKILL.md`
   - `skills/registry.json`
5. 输出“已创建哪些文件”和“下一步如何测试”

### 11.8 `backend/workspace-templates/README.md`

**目标**：文档与双来源结构一致。

**改动点**
- 明确写出：
  - backend skill 是 system skill 模板源
  - workspace/skills 是当前项目私有 skill
  - 运行时 system skill 会镜像到 `workspace/skills/_system/`

### 11.9 `backend/workspace-templates/BOOTSTRAP.md`

**目标**：修复与 Phase 5 真实注入方式的漂移。

**改动点**
1. 不再把 `SKILLS_SNAPSHOT` 描述为静态 control plane 文件之一
2. 改为：
   - `SKILLS_SNAPSHOT` 由 `SkillLoader` 在运行时生成并注入
3. 若 bootstrap 要提到 skill，应改成“后续可在 workspace/skills/ 下沉淀私有 skill”

### 11.10 `workspace/skills/registry.json` 模板

**目标**：给每个 workspace 一个可扩展的私有 skill 注册表。

**新增文件**

```json
{
  "version": "0.1",
  "skills": []
}
```

**放置位置**
- workspace 模板目录中预置
- 确保首次启动后存在于默认 workspace

### 11.11 `backend/tests/test_skill_loader.py`

**目标**：修复现有弱测试，并补双来源测试。

**必须修复**
- `test_skills_copied_to_workspace()` 里对 `src` 的错误拼接

**新增测试**
1. system registry + workspace registry 同时存在时，snapshot 同时含两类 skill
2. system skill 的 `runtime_path` 是 `skills/_system/...`
3. workspace skill 的 `runtime_path` 是 `skills/...`
4. 同名 system/workspace skill 默认并存
5. `research_skill_creator` 能出现在 snapshot 中
6. `force_refresh=True` 时会覆盖写盘 snapshot

### 11.12 `backend/tests/test_write_file_tool.py`

**目标**：补 skill 写入安全测试。

**新增测试**
1. 允许写入 `skills/demo_skill/SKILL.md`
2. 拒绝写入 `../demo.md`
3. 拒绝写入 workspace 外绝对路径

### 11.13 `backend/tests/test_chat_write_file_flow.py`

**目标**：不大改，只补一个最小集成回归。

**新增测试建议**
- 发起 `/api/chat` 后，即使未触发任何 skill 读取，也不影响原有写文件 trace
- 当 skill snapshot 存在时，chat 流不报错

### 11.14 推荐实施批次

#### 批次 A：底座
- `path_utils.py`
- `write_file_tool.py`
- workspace `skills/registry.json` 模板

#### 批次 B：SkillLoader 主体
- `skill_loader.py`
- `registry.json`
- `research_skill_creator/SKILL.md`

#### 批次 C：接线与文档
- `chat.py`
- `prompt_builder.py`
- `workspace-templates/README.md`
- `workspace-templates/BOOTSTRAP.md`

#### 批次 D：测试
- `test_skill_loader.py`
- `test_write_file_tool.py`
- `test_chat_write_file_flow.py`

### 11.15 每批完成后的验证命令

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache backend/.venv/bin/python -m unittest discover -s backend/tests -v
```

额外人工检查：
1. `workspace/skills/_system/` 是否生成
2. `workspace/skills/registry.json` 是否存在
3. 前端对话后 Trace 中是否能看到 `read_file` 读取 skill 的路径

---

**文档完成** | 2026-03-12（v2.1 审查修订 + 详细开发方案）

**注意**：本计划采用 Agent 自主决策架构，后端不做技能匹配逻辑。不包含 RAG 和多 agent 扩展。
