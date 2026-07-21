# Step 2：架构地图

## 总体分层

```
┌─────────────────────────────────────────────────────────────┐
│                      Control Plane                          │
│  SOUL.md / IDENTITY.md / AGENTS.md / USER.md / TOOLS.md    │
│  → 定义 Agent "如何工作"的硬协议，优先级最高                   │
├─────────────────────────────────────────────────────────────┤
│                       Data Plane                            │
│  Layer1: identity/   Layer2: timeline/   Layer3: atoms/     │
│  → 存放长期事实、时间推进、原子资产，服从 Control Plane         │
├─────────────────────────────────────────────────────────────┤
│                      Trace Plane                            │
│  context_trace/{session_id}.json                            │
│  → 全链路审计：读了什么、写了什么、缺什么、为什么               │
└─────────────────────────────────────────────────────────────┘
```

---

## Control Plane：定义"Agent 如何工作"

### 组成文件

| 文件 | 职责 | 关键内容 |
|------|------|---------|
| SOUL.md | 行为准则 | 科研三问（What/So what/Now what）、证据标准（硬约束：所有结论必须带证据类型+数据路径+对照+判据）、执行真实性（不脑补执行结果） |
| IDENTITY.md | 身份定义 | Name/Role/Domain/Vibe，定义"像靠谱师兄+严谨审稿人"的气质 |
| AGENTS.md | Agent 管理协议 | 技能协议、记忆协议、工具边界 |
| USER.md | 用户信息 | 用户偏好与输出约束 |
| TOOLS.md | 工具调用约定 | 5 个核心工具的使用规范 |
| BOOTSTRAP.md | 首次初始化协议 | 识别语义边界、引导初始 assets、生成最小 memory 骨架 |
| MEMORY.md | 记忆系统说明 | 三层记忆的读写规则 |

### 为什么这样设计

Control Plane 的本质是**把 LLM 的不确定性关进确定性的笼子里**。

产品判断：科研场景对"幻觉"零容忍。导师追问时，如果 AI 给的建议没有证据支撑，用户的信任会瞬间崩塌。所以必须在 Prompt 最高优先级位置注入硬约束（SOUL.md 的证据标准），而不是靠 LLM 自觉。

技术实现：PromptBuilder 在构建 System Prompt 时，Control Plane 文件排在 Block 5（Project Context）的最前面，确保 LLM 在处理任何用户输入之前，先"读到"行为准则。

### 对应的产品判断

- **"不装读心"**：SOUL.md 强制要求 A/B 轻量试探，而非直接猜测用户意图。这是从用户访谈中提炼的——科研用户被"AI 自作聪明"伤害过太多次。
- **"事实与推断分离"**：SOUL.md 要求所有输出区分事实区和推断区。这不是技术炫技，而是科研写作的基本规范——Results 和 Discussion 本来就是分开的。
- **"证据回指"**：每条建议必须挂 trace 回指。这解决的是"面试时被追问'你怎么知道的'"的问题——不是 AI 说的，是数据说的。

---

## Data Plane：存放"Agent 知道什么"

### Layer1：Identity（身份与规则，长期稳定）

```
memory/identity/
├── user.md           # 用户偏好与输出约束
├── project.md        # 项目北极星、主线假设、指标、术语表、判据（最关键）
├── lab_context.md    # 实验室现实约束：仪器/表征/命名/污染风险
└── context_budget.md # 单回合上下文预算与截断策略
```

**职责**：让系统长期知道"你是谁、项目是什么、输出应该长什么样"。

**为什么这样设计**：科研项目有一个"北极星"——主线假设和判据。这些信息在 180 天内几乎不变，但每次对话都需要。如果每次都让用户重复说明，体验极差。Layer1 解决的是"系统应该永远记住的东西"。

**对应的产品判断**：`project.md` 是整个记忆系统的锚点。ContextOrchestrator 在每次对话中都会优先注入它，因为"判据"决定了 AI 给出的建议是否靠谱。没有判据的建议就是幻觉。

### Layer2：Timeline（时间轴推进，阶段→周→日）

```
memory/timeline/
├── 180d_index.md              # 180天总览：阶段划分、里程碑、风险雷达
├── phases/                    # 阶段文档（P01-P05）
├── weeks/                     # 周报
├── days/                      # 日志
└── stage_reports/             # 阶段汇报（R01-R10）
```

**职责**：把 180 天从"阶段计划"落到"每天执行"，并能自动汇总成阶段汇报。

**为什么这样设计**：科研的时间粒度是"阶段→周→日"。导师问"这两周做了什么"时，系统需要能快速定位到对应的周报和日志，而不是搜索全部对话历史。

**对应的产品判断**：ContextOrchestrator 的意图识别会根据用户输入自动选择注入哪些时间文件。比如用户说"帮我做第 6 次阶段汇报"，系统会自动拉取 time_range 内的 weeks/days + 上一期 stage_report，而不需要用户手动指定。

### Layer3：AtomNotes（原子资产，跨周期证据链）

```
memory/concepts/    # Concept：研究主题容器（你在验证什么）
memory/tasks/       # Task：验证任务（= Claim + Protocol + Run）
memory/packs/       # Pack：交付包（PPT/机理证据链/论文写作/图集）
```

**职责**：跨时间周期的证据链与可复用对象。

**为什么这样设计**：科研不是线性的。一个 Concept（比如"Co(IV) 的存在性"）可能跨越 3 个月、涉及 10 个 Task、最终汇聚成 1 个 Pack（机理证据链）。Layer2 的时间轴无法表达这种"跨周期关联"，所以需要 Layer3 作为"原子资产层"。

**三对象模型的产品判断**：
- **Concept** = 你在验证什么（研究问题的容器）
- **Task** = 你怎么验证的（Claim + Protocol + Run，可追加多次 run）
- **Pack** = 你验证出了什么（交付物，面向导师/论文/PPT）

这三个对象的关系是：Concept 驱动 Task，Task 的结果汇聚成 Pack。这不是我们发明的抽象，而是科研工作流的自然结构——只是以前散落在 Excel、Word、PPT、实验本里，现在被统一建模了。

---

## Trace Plane：记录"Agent 做了什么"

### 存储位置

```
context_trace/{session_id}.json
```

### Schema（Envelope 格式）

```json
{
  "messages": [...],     // SessionManager 读写：OpenAI messages 数组
  "traces": [...],       // TraceWriter 读写：审计信息数组
  "prompt": {...}        // PromptBuilder 写入：本轮 System Prompt 元数据
}
```

### trace 的 context_read[] 最小字段

```json
{
  "path": "memory/identity/project.md",
  "layer": "memory_identity",
  "why": "项目北极星与判据，每轮必读",
  "status": "full"
}
```

**职责**：全链路审计——本轮读了什么文件、为什么读、是否被裁剪、调用了什么工具、输入输出是什么。

**为什么这样设计**：Trace 不是"为了合规做的日志"，而是产品核心功能。科研用户需要理解"AI 为什么给出这个建议"才敢用它的输出去面对导师。Trace 让用户可以"点一下回放"，看到完整的推理链路。

**对应的产品判断**：这是 OpenClaw 与普通 AI 助手最本质的区别。ChatGPT 给你一个答案，你不知道它基于什么。OpenClaw 给你一个答案，同时告诉你"我读了你的 project.md 判据 + 上周的实验日志 + 那个 XRD csv，基于这些得出的结论"。

---

## 核心模块职责

### ContextOrchestrator（上下文编排器）

```python
# graph/context_orchestrator.py
class ContextOrchestrator:
    def generate_memory_map(message, workspace_dir) -> MemoryMap
```

**职责**：扫描 workspace memory 目录，基于用户消息推荐文件，生成 Memory Map。

**核心逻辑**：
1. 扫描 Layer1/2/3 + Assets 目录结构
2. 基于关键词匹配做意图识别（汇报/合成/机理/通用）
3. 按"稳定→变化→本轮相关"排序推荐文件
4. 输出 Memory Map（含文件清单 + 推荐理由）

**为什么需要它**：LLM 的上下文窗口有限。180 天的记忆文件可能有几百个，不可能全部注入。ContextOrchestrator 的作用是"替用户选择本轮最相关的上下文"，并在 trace 中记录选择原因，确保可审计。

**产品判断**：这是"AI-native"产品与"套壳 ChatGPT"的分水岭。套壳产品把所有历史塞进 context window；OpenClaw 做的是"智能上下文选择"——读什么、不读什么、为什么，都有据可查。

### PromptBuilder（Prompt 构建器）

```python
# graph/prompt_builder.py
class PromptBuilder:
    def build(workspace_dir, memory_map, skill_snapshot, tools_desc) -> str
```

**职责**：将 Control Plane + Memory Map + Skills Snapshot + 工具说明 + 可信元数据拼接为完整的 System Prompt。

**7 个 Block 的固定顺序**：
1. Identity — 身份行（固定常量）
2. Tooling — 5 工具说明 + 参数契约 + 示例
3. Workspace — 工作目录 + 规则（禁止脑补、Missing checklist）
4. Metadata — 可信元数据（平台/时区/语言/日期）
5. Control Plane — AGENTS/SOUL/IDENTITY/USER/TOOLS/project.md 全文注入
6. Skills Snapshot — 技能菜单（Agent 据此自主决策读取哪些技能）
7. Memory Map — Layer1/2/3 + Assets + 推荐文件

**为什么需要它**：Prompt 的结构决定了 LLM 的行为质量。Block 顺序不是随意的——稳定信息在前（Identity/Tooling/Workspace），变化信息在后（Memory Map），确保 LLM 先建立"我是谁、我能做什么"的认知，再处理"本轮用户要什么"。

**产品判断**：PromptBuilder 的设计体现了一个关键洞察——**Prompt Engineering 不是写一段好的提示词，而是设计一套可维护、可迭代、可审计的 Prompt 拼接系统**。每个 Block 都可以独立修改和测试，而不会影响其他 Block。

### TraceWriter（追踪记录器）

```python
# graph/trace_writer.py
class TraceWriter:
    def write_trace(session_id, tool_calls, prompt_metadata) -> None
```

**职责**：每轮对话完成后，将工具调用列表 + Prompt 元数据写入 trace 文件。

**核心逻辑**：
1. 读取现有 envelope（保留 messages 字段）
2. 追加 trace 条目（tool_calls + context_read + prompt 元数据）
3. 写回文件

**为什么需要它**：TraceWriter 是 Trace Plane 的写入端。它确保每次对话的"决策过程"都被记录下来，而不仅仅是"对话结果"。

**产品判断**：Trace 的价值不在于"记录了什么"，而在于"能回放什么"。当用户（或面试官）问"系统为什么给出这个建议"时，trace 能精确回答：读了哪些文件、用了什么工具、输入输出是什么。

### SkillLoader（技能加载器）

```python
# graph/skill_loader.py
class SkillLoader:
    def get_snapshot() -> str  # 返回 SKILLS_SNAPSHOT.md
```

**职责**：读取 system/workspace skills registry，生成菜单型摘要（SKILLS_SNAPSHOT.md），注入 System Prompt。

**核心逻辑**：
1. 加载 system registry（`backend/skills/registry.json`）
2. 加载 workspace registry（如有）
3. 合并去重，生成统一 SkillRecord 列表
4. 将 system skills 镜像到 workspace（`skills/_system/`）
5. 生成 Markdown 菜单摘要

**为什么需要它**：Skills 系统采用"渐进式披露"——System Prompt 只注入菜单摘要（技能名 + 一句话描述 + 触发条件），Agent 根据用户输入自主决策是否需要读取某个技能的完整说明书（通过 read_file 工具）。

**产品判断**：这是 Anthropic Agent Skills 范式的实现。Skill 不是预置函数，而是 Markdown 说明书。这意味着：
- 用户可以自己写 Skill（拖入文件夹即用）
- Skill 的行为可以被审计（因为它就是一段文本）
- Agent 的能力可以无限扩展，而不需要改代码

### WorkspaceRuntimeRegistry（工作空间运行时注册表）

```python
# runtime/workspace_registry.py
class WorkspaceRuntimeRegistry:
    def get_runtime(workspace_id) -> WorkspaceRuntime
    def create_workspace(workspace_id, name) -> dict
```

**职责**：Phase 5.3 核心改造。替代全局单例模式，管理多 workspace 的生命周期、manifest、运行时资源隔离。

**核心架构**：
```
SharedAgentResources（进程级单例）
├── llm: ChatOpenAI          # 所有 workspace 共享同一个 LLM 实例
└── fetch_url_tool            # 所有 workspace 共享（无状态工具）

WorkspaceRuntime（per-workspace 隔离）
├── workspace_id
├── workspace_dir
├── session_manager           # 每个 workspace 独立的会话管理
└── workspace_tools[]         # terminal/python_repl/read_file/write_file（CWD 绑定到 workspace）
```

**为什么需要它**：Phase 5.3 之前，系统只有一个全局 SessionManager，所有对话共享同一个 workspace。这在"单用户单项目"场景下没问题，但科研用户可能同时推进多个课题（比如"Co(IV) 机理"和"材料筛选"），需要隔离的工作空间。

**产品判断**：Workspace 隔离解决的不是技术问题，而是产品问题——用户的心智模型是"我有多个课题，每个课题有自己的记忆和文件"。如果所有课题混在一起，记忆系统的精准度会急剧下降。

---

## 单次对话完整流线

```
用户发送消息
    │
    ▼
[1] WorkspaceRuntimeRegistry.get_runtime(workspace_id)
    → 获取对应 workspace 的 SessionManager + Tools
    │
    ▼
[2] SessionManager.load_session(session_id)
    → 获取历史消息（合并连续 assistant 消息）
    │
    ▼
[3] ContextOrchestrator.generate_memory_map(message, workspace_dir)
    → 扫描 memory 目录 → 意图识别 → 推荐文件 → 输出 Memory Map
    │
    ▼
[4] SkillLoader.get_snapshot()
    → 生成 SKILLS_SNAPSHOT.md 菜单
    │
    ▼
[5] PromptBuilder.build(workspace_dir, memory_map, skill_snapshot, tools)
    → 拼接 7 Block System Prompt
    │
    ▼
[6] AgentManager.astream(messages, system_prompt, tools)
    → LangChain create_agent 构建 Agent → 流式执行
    → SSE 事件流：token / tool_start / tool_end / new_response
    │
    ▼
[7] SessionManager.save_message(session_id, messages)
    → 持久化到 context_trace/{session_id}.json 的 messages 字段
    │
    ▼
[8] TraceWriter.write_trace(session_id, tool_calls, prompt_metadata)
    → 持久化到 context_trace/{session_id}.json 的 traces 字段
    │
    ▼
[9] SSE: done {session_id, trace_path}
    → 前端收到 done → 请求 trace → 渲染回放卡片
```

**关键设计决策**：done 事件在 trace 写入完成后才发送（同步写入），避免前端读到不完整的 trace 文件。这是 Phase 3 中识别并解决的竞态条件问题。

---

## 设计决策与产品判断对照表

| 设计决策 | 技术实现 | 对应的产品判断 |
|---------|---------|--------------|
| 文件即记忆，不用向量数据库 | 三层 Markdown 文件系统 | 科研用户需要"看得见、改得了、追得回"的记忆，向量数据库是黑盒 |
| Control Plane 优先级最高 | PromptBuilder Block 5 最先注入 workspace 文件 | LLM 行为必须被硬约束控制，不能靠"自觉" |
| 意图识别用关键词匹配+降级 | ContextOrchestrator 简单规则 | MVP 阶段不需要复杂的意图分类器，降级为全量注入是安全的 |
| Envelope Schema 统一存储 | messages + traces 同一文件 | 避免两个文件的同步问题，SessionManager 和 TraceWriter 各管各的字段 |
| 共享 LLM + 隔离 Tools | SharedAgentResources + WorkspaceRuntime | LLM 是无状态的可以共享，但文件操作必须绑定到 workspace 目录 |
| Skills 渐进式披露 | 菜单摘要注入 Prompt，Agent 自主 read_file | 避免 Prompt 膨胀，同时保留 Agent 的自主决策能力 |
| 双文件依赖策略 | requirements.txt（范围）+ requirements.lock（精确锁） | 开发时灵活，部署时确定，避免"在我机器上能跑"问题 |
| 路径安全用 Path.relative_to() | resolve_safe_path() 工具函数 | 禁止 str.startswith()（可被 Unicode 绕过），这是安全意识的体现 |
