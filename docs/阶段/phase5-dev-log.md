# Phase 5 开发日志

> 目标：实现 Skills 渐进式披露机制——SkillLoader 生成技能菜单摘要，Agent 自主通过 read_file 按需读取完整技能内容

## 2026-03-12 审查补记（计划 / 日志 / 代码对齐）

本日志在原始开发记录基础上，补充一次面向代码的审查结论。以下内容用于区分：

- **当前已实现**：代码里已经存在并可运行的部分
- **审查发现**：日志原先表述过满、测试覆盖不足或文档漂移的部分
- **后续修正项**：已纳入 `phase5-dev-plan.md` v2.1 的新增范围

### 当前代码现状

当前 Phase 5 实现的是 **单来源 system skill + Agent 自主读取** 架构：

- `SkillLoader` 读取 `backend/skills/registry.json`
- backend skill 会被复制到 `workspace/skills/`
- `PromptBuilder` 每轮注入 `Skills Snapshot`
- Agent 通过 `read_file` 自主读取 skill
- `/api/chat` 已支持 `route`
- 前端已通过 URL hash 传入 `route`

### 审查发现

1. **route 的实际作用被写大了**
   - 当前代码只实现了 `route -> metadata`
   - 尚未实现 `route -> ContextOrchestrator`
   - 尚未实现 `route -> TraceWriter`
   - 因此日志中凡是写 “route 已用于 context selection / trace” 的地方，都应理解为目标状态，不是已完成状态

2. **SKILL.md 复制测试覆盖不足**
   - `test_skill_loader.py` 中 “SKILL.md 复制到 workspace” 的测试仍沿用了错误的 `src` 拼接方式
   - 由于测试写法带 `if src.exists():` 条件，导致复制校验可能被跳过
   - 结论：测试全绿不等于这条能力被有效证明

3. **block 顺序文案存在两套说法**
   - 当前真实实现顺序是：
     `Identity -> Tooling -> Workspace/Metadata -> Control Plane -> Skills Snapshot -> Execution Contract -> Memory Map`
   - 早期表格里曾简写成 “Skills Snapshot 在 Control Plane 之后、Memory Map 之前”，容易漏掉 `Execution Contract`
   - 后续以代码实现顺序为准

4. **模板文档存在漂移**
   - `BOOTSTRAP.md` 仍把 `SKILLS_SNAPSHOT` 写成常驻控制面文件之一
   - 但当前代码中，`SKILLS_SNAPSHOT` 不是 control plane 预载文件，而是由 `SkillLoader` 每轮单独注入

### 后续修正项（已升级为计划范围）

1. 支持 `system + workspace` 两层 skill 来源同时可用
2. 新增跨 workspace 常驻的科研版 `research_skill_creator`
3. 支持 workspace 私有 skill 的注册、加载和展示
4. 为 skill 创建补齐 `workspace/skills/` 写入权限与路径安全策略
5. 修复并补强 SkillLoader 相关测试

## 文件创建/更新记录

### Step 1: 实现 SkillLoader
- 创建：`backend/graph/skill_loader.py`
  - 实现 `_load_registry()` 方法，加载 `backend/skills/registry.json`
  - 实现 `_ensure_skills_in_workspace()` 方法，从 backend/skills/ 复制 SKILL.md 到 workspace/skills/<skill_id>/SKILL.md
  - 实现 `get_snapshot()` 方法，生成 SKILLS_SNAPSHOT.md 菜单摘要
  - 复制策略克制：只在 workspace 不存在时复制，不覆盖用户定制版本
  - 写盘策略克制：snapshot 只在首次不存在时写盘

### Step 1.5: 更新 registry.json
- 修改：`backend/skills/registry.json`
  - 版本从 `0.1` 升级到 `0.2`
  - 移除旧字段 `selection_rule`、`primary_intents`
  - 为所有 8 个技能新增 `category`、`use_cases`、`preferred_routes` 字段
  - 保留原有的 `id`、`name`、`triggers`、`entry` 字段

### Step 2: 修改 PromptBuilder
- 修改：`backend/graph/prompt_builder.py`
  - `build()` 新增 `skills_snapshot` 参数（默认 `""`，向后兼容）
  - 新增 `_build_skills_snapshot_block()` 方法
  - 调整 Block 顺序为：Identity → Tooling → Workspace/Metadata → Control Plane → **Skills Snapshot** → Execution Contract → Memory Map
  - 更新模块文档说明

### Step 3: 修改 Chat API
- 修改：`backend/api/chat.py`
  - `ChatRequest` 新增 `route: str = ""` 字段
  - 导入 `SkillLoader`
  - `event_generator` 中调用 `SkillLoader.get_snapshot()` 并传入 `PromptBuilder.build()`
  - `metadata` 字典新增 `route` 键

### Step 3.5: 前端 route 传入
- 修改：`frontend/index.html`
  - `sendMessage()` 中 POST body 新增 `route` 字段
  - 通过 URL hash 解析 route：`#route=mechanism_closure` → `new URLSearchParams(location.hash.slice(1)).get('route')`

### Step 4: 新增测试
- 创建：`backend/tests/test_skill_loader.py`
  - `SkillLoaderTests`（6 项）：snapshot 元信息完整性、不覆盖已存在 SKILL.md、snapshot 只写盘一次、registry 不存在时降级、snapshot 不按 route 过滤、SKILL.md 复制验证
  - `PromptBuilderBackwardCompatTests`（3 项）：无 snapshot 时向后兼容、有 snapshot 时正确注入、block 顺序验证

## 已处理问题

1. **entry 路径双重前缀问题**
   - 问题：`registry.json` 中 entry 格式为 `skills/xxx/SKILL.md`（相对于 backend/），但 `config.SKILLS_DIR` 已经是 `backend/skills/`，导致 `SKILLS_DIR / entry` 拼出 `backend/skills/skills/xxx/SKILL.md`
   - 处理：`_ensure_skills_in_workspace()` 中改用 `SKILLS_DIR.parent / entry`（即 `backend/ + skills/xxx/SKILL.md`），正确解析路径
   - 理由：保持 registry.json 中 entry 路径约定不变（与旧版本兼容），修改代码侧拼接逻辑

2. **registry.json 字段升级**
   - 问题：旧版 registry.json 含 `selection_rule`、`primary_intents` 等 Phase 5 不再需要的字段，缺少 `category`、`use_cases`、`preferred_routes`
   - 处理：升级到 v0.2 格式，移除旧字段，新增 Phase 5 所需字段
   - 理由：Phase 5 架构从「后端匹配」转为「Agent 自主决策」，旧的匹配规则字段不再需要

3. **PromptBuilder Block 顺序调整**
   - 问题：Phase 3 的 Block 顺序中 Execution Contract 在 Metadata 之前，Phase 5 计划冻结的顺序要求 Skills Snapshot 在 Control Plane 之后、Memory Map 之前
   - 处理：重新排列为 Identity → Tooling → Workspace/Metadata → Control Plane → Skills Snapshot → Execution Contract → Memory Map
   - 理由：遵循 Phase 5 计划的冻结顺序，同时保持 Execution Contract 紧靠 Memory Map 前面（防止 Agent 在看到 Memory Map 后就开始幻觉）

## 审查后新增发现（需继续修正）

1. **`route` 目前仅进入 metadata**
   - 代码位置：`backend/api/chat.py`
   - 当前状态：已进入 `ChatRequest` 和 prompt metadata
   - 未完成项：尚未进入 `ContextOrchestrator` / `TraceWriter`

2. **`test_skills_copied_to_workspace` 需要修复**
   - 当前问题：测试中的源路径拼接与实现不一致
   - 影响：日志中 “SKILL.md 复制验证 PASS” 的证据强度不足

3. **多来源 skill 还未实现**
   - 当前只有 `backend/skills/` 单来源
   - 尚未支持：
     - backend system skill 与 workspace 私有 skill 的统一 catalog
     - workspace 私有 skill
     - 多 registry 合并后的统一 snapshot

4. **用户自主创建 skill 的写入链路还没打通**
   - 当前没有科研版 `research_skill_creator`
   - 当前也没有专门收口到 `workspace/skills/` 的安全写入策略

## 测试结果

### Phase 5 新增测试

| # | 测试项 | 命令 | 预期 | 状态 |
|---|--------|------|------|------|
| 1 | snapshot 包含所有技能元信息 | `unittest test_skill_loader` | 8 个技能的 id/name/triggers 都在 snapshot 中 | ✅ PASS |
| 2 | 不覆盖已存在的 SKILL.md | `unittest test_skill_loader` | 自定义内容不被 backend 模板覆盖 | ✅ PASS |
| 3 | snapshot 只写盘一次 | `unittest test_skill_loader` | 二次调用不覆盖已有文件 | ✅ PASS |
| 4 | registry 不存在时降级 | `unittest test_skill_loader` | 返回空字符串，不报错 | ✅ PASS |
| 5 | snapshot 不按 route 过滤 | `unittest test_skill_loader` | 所有技能始终包含在 snapshot 中 | ✅ PASS |
| 6 | SKILL.md 复制到 workspace | `unittest test_skill_loader` | 8 个 SKILL.md 都在 workspace/skills/ 下 | ✅ PASS |
| 7 | build 无 snapshot 向后兼容 | `unittest test_skill_loader` | prompt 中无 Skills Menu | ✅ PASS |
| 8 | build 有 snapshot 正确注入 | `unittest test_skill_loader` | prompt 中有 Skills Menu + 技能内容 | ✅ PASS |
| 9 | block 顺序验证 | `unittest test_skill_loader` | Control Plane < Skills < Execution Contract < Memory Map | ✅ PASS |

### 已有测试回归检查

| # | 测试项 | 状态 |
|---|--------|------|
| 1 | test_prompt_includes_execution_authenticity_contract | ✅ PASS |
| 2 | test_runtime_six_files_contain_non_fabrication_rules | ✅ PASS |
| 3 | test_writes_nested_file_under_memory | ✅ PASS |
| 4 | test_real_write_file_tool_creates_file_and_trace | ✅ PASS |
| 5 | test_plain_text_claim_does_not_create_file_or_trace | ✅ PASS |

### 执行命令

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache backend/.venv/bin/python -m unittest discover -s backend/tests -v
```

全部 14 项测试通过，说明 Phase 5 当前实现没有引入已有测试回归；但这 **不等于** 双来源 skill、workspace 自定义 skill 和 `research_skill_creator` 已实现，也 **不等于** Skill 复制链路已被强测试充分覆盖。

### 端到端验证

```bash
# 验证 block 顺序 + snapshot 内容 + 文件复制
backend/.venv/bin/python -c "
import sys; sys.path.insert(0, 'backend')
from graph.prompt_builder import PromptBuilder
from graph.context_orchestrator import ContextOrchestrator
from graph.skill_loader import SkillLoader
import config as cfg

workspace = cfg.DEFAULT_WORKSPACE_DIR
skill_loader = SkillLoader(workspace)
snapshot = skill_loader.get_snapshot()
print(f'Skills in snapshot: {snapshot.count(\"###\")}')  # 8

pb = PromptBuilder(workspace)
memory_map = ContextOrchestrator(workspace).generate_memory_map('帮我整理证据链')
prompt = pb.build(memory_map=memory_map, skills_snapshot=snapshot,
                  metadata={'current_date': '2026-03-12', 'route': 'mechanism_closure'})

blocks = ['OpenClaw', '## Tooling', '## Workspace', '# Project Context',
          '# Skills Menu', '## Execution Contract', '# Memory Map']
positions = [prompt.find(b) for b in blocks]
assert all(p >= 0 for p in positions), 'Missing blocks!'
assert positions == sorted(positions), 'Wrong order!'
print('All blocks in correct order')
print(f'Prompt length: {len(prompt)} chars')
"
```

结果：
- ✅ Skills in snapshot: 8
- ✅ All blocks in correct order
- ✅ Prompt length: 12392 chars

## Phase 5 产出汇总

| 指标 | 值 |
|------|-----|
| 新建文件 | 2 个（skill_loader.py, test_skill_loader.py） |
| 修改文件 | 4 个（prompt_builder.py, chat.py, registry.json, index.html） |
| 新增 API 端点 | 0 个 |
| Phase 1-4 核心模块修改 | 0 个（仅扩展 PromptBuilder 参数，向后兼容） |
| 新增测试 | 9 项 |
| 回归测试 | 5 项全部通过 |

## 审查后状态修正

| 项目 | 原日志结论 | 审查后结论 |
|------|-----------|-----------|
| system skill snapshot 注入 | 已完成 | 已完成 |
| Agent 自主读取 skill | 已完成 | 已完成 |
| route 进入 `/api/chat` + 前端可传入 | 已完成 | 已完成 |
| route 用于 context selection / trace | 隐含已完成 | **未完成，仅 metadata 已落地** |
| SKILL.md 复制验证 | 已完成 | **测试需补强后才能算强验证** |
| 双来源 skill（backend + workspace） | 未提及 | **新需求，未实现** |
| 科研版 `research_skill_creator` | 未提及 | **新需求，未实现** |
| workspace skill 安全写入 | 未提及 | **新需求，未实现** |

## 后续开发项（纳入 Phase 5 v2.1）

1. **多来源 SkillLoader**
   - 合并 `system/workspace` 两层 registry
   - 为 snapshot 增加 `source` 和 `runtime_path`

2. **workspace 自定义 skill**
   - 支持 `workspace/skills/registry.json`
   - backend system skill 与 workspace skill 同时可见、同时可用

3. **科研版 `research_skill_creator`**
   - 作为跨 workspace 常驻 system skill

## 2026-03-12 实施补记（Phase 5.1 第二轮）

本轮开始按 v2.1 方案落地双来源 skills，并同步补测试与模板文档。

### 本轮已实现

1. **SkillLoader 升级为两层来源**
   - 代码：`backend/graph/skill_loader.py`
   - system skills 来源：`backend/skills/registry.json`
   - workspace skills 来源：`workspace/skills/registry.json`
   - 运行时统一数据结构：`SkillRecord`
   - snapshot 新增字段：
     - `source`
     - `runtime_path`
   - system skill 运行时命名空间固定为：
     - `workspace/skills/_system/<skill_id>/SKILL.md`
   - workspace 私有 skill 运行时路径保持：
     - `workspace/skills/<skill_id>/SKILL.md`

## 2026-03-15 实施补记（工具层 cwd/path 强约束）

本轮针对最新会话里暴露出的工具参数混淆问题，做了一次**工具层兜底**，目标是不再只靠 prompt 提示词约束 `path/cwd/url` 的用法。

### 背景

- 最新会话 trace 中出现了把 `{"path": "memory/identity/project.md"}` 传给 `terminal` 的错误调用
- `fetch_url` 也出现了 provider / 模型把 URL 字段误标成 `path` 的风险
- 仅靠 system prompt 约束不够稳，尤其在 prompt 中大量出现 `read_file(path)`、memory 路径、技能 runtime_path 的情况下，模型容易把“路径参数”泛化到错误工具上

### 本轮改动

1. **统一路径解析基座**
   - 修改：`backend/graph/path_utils.py`
   - 新增：
     - `resolve_safe_dir(base_dir, user_cwd)`
     - `resolve_safe_path_from_cwd(base_dir, user_path, cwd=".", require_writable=False)`
   - 作用：
     - 所有工具共享同一套 cwd 校验逻辑
     - 相对路径统一先相对 `cwd`，再做 workspace 边界检查

2. **read_file 支持 cwd**
   - 修改：`backend/tools/read_file_tool.py`
   - 新增显式 `args_schema`
   - 接口从 `read_file(path)` 扩展为 `read_file(path, cwd=".")`
   - 行为：
     - `path` 可相对 `cwd`
     - schema 层禁止额外未知字段

3. **write_file 支持 cwd**
   - 修改：`backend/tools/write_file_tool.py`
   - 新增显式 `args_schema`
   - 接口从 `write_file(path, content)` 扩展为 `write_file(path, content, cwd=".")`
   - 行为：
     - 写入路径先相对 `cwd` 解析
     - 仍受 writable whitelist 约束
     - 返回值统一回显规范化后的 workspace 相对路径

4. **python_repl 支持 cwd**
   - 修改：`backend/tools/python_repl_tool.py`
   - 新增显式 `args_schema`
   - 接口从 `python_repl(code)` 扩展为 `python_repl(code, cwd=".")`
   - 行为：
     - 执行前切换到安全解析后的 cwd
     - Python 内部的相对文件读写与 shell 工具的 cwd 语义对齐

5. **fetch_url 增加 schema 与 `path -> url` 兜底**
   - 修改：`backend/tools/fetch_url_tool.py`
   - 新增显式 `args_schema`
   - 支持：
     - 标准调用：`fetch_url({"url": "https://..."})`
     - 兼容兜底：`fetch_url({"path": "https://..."})`
   - 同时增加 `http://` / `https://` 校验，避免把本地文件路径误当 URL 抓取

6. **同步更新 prompt/tooling 文案**
   - 修改：
     - `backend/graph/prompt_builder.py`
     - `backend/workspace-templates/TOOLS.md`
   - 更新内容：
     - 明确 `read_file` / `write_file` / `python_repl` 的 `cwd` 合同
     - 明确 `fetch_url` 的 `url` 合同及 provider `path` 兜底
     - 补充结构化示例，减少模型把 `path` 乱传到其他工具

### 新增测试

- 创建：`backend/tests/test_read_file_tool.py`
  - 验证 `read_file(..., cwd=...)` 的相对路径解析
- 创建：`backend/tests/test_python_repl_tool.py`
  - 验证 Python 相对文件访问以 `cwd` 为基准
- 创建：`backend/tests/test_fetch_url_tool.py`
  - 验证 `fetch_url(path="https://...")` 会自动归一化为 URL
- 修改：`backend/tests/test_write_file_tool.py`
  - 补充 `write_file(..., cwd=...)` 的行为验证

### 验证情况

- 已完成：语法级校验（`compile(...)` 通过）
- 未完成：完整 unittest 回归
  - 原因：当前执行环境缺少 `langchain_core` 与 `html2text` 依赖，无法在本机解释器下跑完整测试
  - 影响：本轮可以确认代码可解析、接口和 prompt 已对齐，但还需要在项目虚拟环境内补一次真实回归

### 当前结论

- 这次改动已经把“文件路径/cwd 相关问题”从**提示词约束**下沉到**工具实现约束**
- 这能显著降低：
  - `read/write/python` 相对路径漂移
  - `fetch_url(path=...)` 直接报错
  - prompt 中大量 `path` 语义导致的参数泛化
- 但**还没有覆盖 trace 丢参问题**
  - `tool_start/tool_end` 对不齐、`args: null` 的问题仍在 `backend/graph/agent.py` 的流式 tool-call 聚合逻辑里
  - 该问题应作为下一轮独立修复项

2. **workspace 私有 skill registry 自动初始化**
   - 若 `workspace/skills/registry.json` 不存在，`SkillLoader` 会自动创建空 registry：
     - `{"version": "0.1", "skills": []}`
   - 目的：让 workspace skill 能被用户或 Agent 直接登记，而不依赖手工预置。

3. **新增跨 workspace system skill：`research_skill_creator`**
   - 新增：`backend/skills/research_skill_creator/SKILL.md`
   - 注册到：`backend/skills/registry.json`
   - 职责边界：
     - 帮用户把高频科研工作流沉淀成 workspace 私有 skill
     - 允许写入 `workspace/skills/<skill_id>/SKILL.md`
     - 允许更新 `workspace/skills/registry.json`
     - 不负责修改 backend system skills

4. **打通 `skills/` 写入权限与路径安全**
   - 修改：`backend/graph/path_utils.py`
     - `WRITABLE_PREFIXES` 新增 `skills/`
   - 修改：`backend/tools/write_file_tool.py`
     - 写入前统一走 `resolve_safe_path(..., require_writable=True)`
     - 拒绝路径穿越和 workspace 边界逃逸
   - 结果：
     - 允许写入 `workspace/skills/...`
     - 不允许写入 `../outside.md` 这类越界路径

5. **模板文档同步**
   - 修改：`backend/workspace-templates/README.md`
     - 明确两层 skills：
       - `backend/skills/` 为 system
       - `workspace/skills/` 为私有 skill
     - 明确 `workspace/skills/_system/` 是运行时镜像目录
   - 修改：`backend/workspace-templates/BOOTSTRAP.md`
     - 将 `SKILLS_SNAPSHOT.md` 从“常驻控制面文件”修正为“运行时由 SkillLoader 自动生成并注入”
   - 新增：`backend/workspace-templates/skills/registry.json`

### 本轮补强测试

1. **重写 `test_skill_loader.py`**
   - 修复了旧版 “复制验证可能空跑” 的问题
   - 新覆盖项：
     - snapshot 包含合并后的全部 skill 元信息
     - snapshot 包含 `source` 和 `runtime_path`
     - system skill 会镜像到 `workspace/skills/_system/`
     - 已存在的 system 镜像文件不会被覆盖
     - workspace 私有 skill 会进入统一 catalog，且不会遮蔽 system skills
     - `force_refresh=True` 时允许刷新 `SKILLS_SNAPSHOT.md`
     - system registry 缺失时安全降级

2. **补充 `test_write_file_tool.py`**
   - 新增允许写入：
     - `skills/demo_skill/SKILL.md`
   - 新增拒绝路径穿越：
     - `../outside.md`

### 本轮测试结果

执行命令：

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache backend/.venv/bin/python -m unittest discover -s backend/tests -v
```

结果：

- 共 `16` 项测试
- `16 / 16` 全部通过

新增后有效覆盖的能力包括：

- 双来源 `system + workspace` skill catalog
- system skill 镜像到 workspace `_system` 命名空间
- workspace 私有 skill 进入 snapshot
- `skills/` 安全写入

## 2026-03-13 调试补记：将最终入模 Prompt 落到 `context_trace`

本轮额外补了一条非常实用的调试链路：把**最终实际传给模型的 prompt 载荷**直接写进 `context_trace/{session_id}.json`。

### 改动内容

- `context_trace/{session_id}.json` 顶层新增 `prompt`
- `prompt.system_prompt`
  - 保存本轮最终传给 Agent / LLM runtime 的完整 system prompt
- `prompt.messages`
  - 保存本轮最终入模的消息数组
  - 结构为：`history + 当前 user message`
  - 不包含本轮新生成的 assistant 回复

示意结构：

```json
{
  "messages": [...],
  "traces": [...],
  "prompt": {
    "system_prompt": "You are a personal assistant running inside OpenClaw.\n\n...",
    "messages": [
      {"role": "user", "content": "帮我整理证据链"}
    ]
  }
}
```

### 为什么这对 debug 很有用

1. **能直接确认“模型到底看到了什么”**
   - 不再需要靠猜 prompt builder 是否注入成功
   - 也不需要只看代码推断 `metadata / route / skills snapshot` 是否真的进入入模上下文

2. **能快速区分“prompt 问题”还是“模型决策问题”**
   - 如果 `Skills Snapshot`、`route`、`prompt_context` 根本没进 `prompt.system_prompt`，那是组 prompt 的问题
   - 如果明明已经进了，但模型仍然没按预期行动，那才是模型理解/推理/工具选择的问题

3. **对回放问题非常方便**
   - 出现“这轮为什么没读 skill / 为什么没用 route / 为什么没按 metadata 行动”时
   - 直接打开对应 session 的 `context_trace` 文件即可复盘，不用额外加日志

4. **对前后端联调很友好**
   - 前端传入的 `route`、`ctx_*` 扩展上下文，最终是否真的进入 prompt，可以直接从 trace 核对
   - 这比只看网络请求 body 更可靠，因为它记录的是**最终入模版本**

### 边界说明

- 当前 `route` 仍未作为独立结构化字段进入 trace
- 但它已经会体现在 `prompt.system_prompt` 里，因此调试时已经可见
- 所以当前状态应理解为：
  - `route` **尚未进入结构化 trace schema**
  - 但 **已能通过 `context_trace.prompt` 间接审计**

### 当前仍未完成

1. `route` 仍未进入 `ContextOrchestrator`，也尚未作为独立结构化字段进入 trace
   - 但已可通过 `context_trace.prompt.system_prompt` 间接查看
2. `research_skill_creator` 只是 system skill 模板，尚未做专门的端到端对话验证
3. system/workspace 同名 skill 的 `overrides` 语义还未真正落地，只是保留了字段
   - 帮助用户在科研场景下生成自己的 workspace skill

4. **安全收口**
   - 明确允许写入 `workspace/skills/`
   - 统一 `read_file` / `write_file` 的路径安全策略

5. **测试补强**
   - 修复 Skill 复制测试
   - 新增双来源 skill、命名空间路径、workspace skill 并存等测试

## Phase 5 → Phase 6 衔接

| Phase 5 提供 | Phase 6 如何使用 | 可靠性 |
|-------------|-------------|--------|
| **SkillLoader** | 前端可展示当前 Agent 读取的技能名称（通过 trace 中的 read_file 调用） | 可直接使用 |
| **SKILLS_SNAPSHOT.md**（workspace/skills/） | 前端可展示技能菜单面板 | 可直接使用 |
| **registry.json**（含 category/preferred_routes） | 前端按 category 分组展示技能选择器；preferred_routes 可用于 UI 提示"推荐场景" | 可扩展 |
| **workspace/skills/\<skill_id\>/SKILL.md** | 前端可提供技能预览功能 | 可直接使用 |
| **ChatRequest.route** | 前端可添加 route 选择器，传入工作语境 | 可直接使用（当前通过 URL hash 传入） |

### Phase 5 已知限制

1. **Agent 决策质量**：依赖 LLM 理解力，可能漏读或误读技能
2. **route 传入方式**：当前仅支持 URL hash（`#route=xxx`），Phase 6 应添加 UI 选择器
3. **registry 热重载**：修改 registry.json 后需重启服务（未实现 watch 机制）
4. **snapshot 更新**：registry.json 变更后，需手动删除 workspace/skills/SKILLS_SNAPSHOT.md 才会重新写盘
5. **route 落地不完整**：目前未进入 context selection，也未作为结构化字段进入 trace
   - 但已可通过 `context_trace.prompt.system_prompt` 调试查看
6. **双来源 skill 未接入**：当前只有 backend system skill，workspace 自定义 skill 尚未纳入 catalog
7. **科研版 skill creator 未提供**：用户还不能在前端闭环地自建 workspace skill
8. **测试仍需补强**：Skill 复制链路和双来源合并链路还缺强测试

---

**开发完成日期**：2026-03-12
**审查修订日期**：2026-03-12
