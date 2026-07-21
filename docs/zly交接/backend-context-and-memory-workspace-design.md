# backend 上下文注入与记忆工作区设计梳理

> 目的：梳理这个项目里“上下文是如何组织与注入的”，以及“记忆功能对应的 workspace 文件夹为什么这样设计”。
>
> 这份文档面向另一个相似项目的迁移参考，尽量把当前代码里已经落地的机制讲清楚，并标出哪些是现状、哪些是可扩展方向。

---

## 1. 一句话结论

这个项目的“记忆功能”不是靠数据库里的隐藏状态完成的，而是靠一套 **File-first Memory（文件即记忆）** 设计完成的：

- **上下文选择**：由 `ContextOrchestrator` 扫描 workspace 的 memory/assets 结构，生成 `Memory Map`
- **上下文注入**：由 `PromptBuilder` 把控制层文件、Memory Map、执行契约、元数据拼成 system prompt
- **真实读取与写入**：由 Agent 通过 `read_file` / `write_file` 等工具显式完成
- **审计与回放**：由 `context_trace/{session_id}.json` 记录消息与工具轨迹

所以它本质上是一套：

> **“可见文件结构 + Prompt 注入规则 + 工具读写 + Trace 回放”组合起来的记忆系统。**

---

## 2. 相关实现文件

### 2.1 上下文选择与注入

- [backend/graph/context_orchestrator.py](../../backend/graph/context_orchestrator.py)
- [backend/graph/prompt_builder.py](../../backend/graph/prompt_builder.py)
- [backend/api/chat.py](../../backend/api/chat.py)
- [backend/graph/agent.py](../../backend/graph/agent.py)

### 2.2 workspace 与记忆模板

- [backend/config.py](../../backend/config.py)
- [backend/api/agents.py](../../backend/api/agents.py)
- [backend/workspace-templates/README.md](../../backend/workspace-templates/README.md)
- [backend/workspace-templates/AGENTS.md](../../backend/workspace-templates/AGENTS.md)
- [backend/workspace-templates/SOUL.md](../../backend/workspace-templates/SOUL.md)
- [backend/workspace-templates/TOOLS.md](../../backend/workspace-templates/TOOLS.md)
- [backend/workspace-templates/USER.md](../../backend/workspace-templates/USER.md)
- [backend/workspace-templates/BOOTSTRAP.md](../../backend/workspace-templates/BOOTSTRAP.md)
- [backend/workspace-templates/MEMORY.md](../../backend/workspace-templates/MEMORY.md)

> 说明：这里提到的 `memory/identity`、`memory/timeline`、`memory/concepts`、`memory/tasks`、`memory/packs` 等目录结构，是当前项目这套 Researchloop/OpenClaw agent workspace 的定制设计，不是 OpenClaw 通用 agent 的固定标配。

### 2.3 trace 与安全边界

- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)
- [backend/workspace-templates/context_trace/README.md](../../backend/workspace-templates/context_trace/README.md)
- [backend/graph/path_utils.py](../../backend/graph/path_utils.py)

---

## 3. 这个项目里的“上下文”到底分成哪几类

当前实现里，上下文并不是一个统一 blob，而是被拆成了几层。

## 3.1 控制层上下文（Control Plane Files）

这部分是最顶层、最稳定、最像“系统设定”的上下文。

`PromptBuilder` 会直接把这些文件内容读出来拼进 system prompt：

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `TOOLS.md`
- `BOOTSTRAP.md`
- `MEMORY.md`
- `memory/identity/project.md`

见：

- [backend/graph/prompt_builder.py:107-130](../../backend/graph/prompt_builder.py#L107-L130)

### 这层的作用

它们不承载“当天发生了什么”，而是承载：

- Agent 的行为原则
- 用户偏好
- 项目总目标
- 执行真实性契约
- 工具与环境说明

也就是说，这一层回答的是：

> **你是谁、你该怎么做、什么算真、什么算证据。**

---

## 3.2 导航层上下文（Memory Map）

这一层不是文件内容本身，而是“文件地图”。

`ContextOrchestrator.generate_memory_map()` 会扫描 workspace，产出一个结构：

```json
{
  "layer1": [...],
  "layer2": [...],
  "layer3": [...],
  "assets": [...],
  "recommended": [...]
}
```

见：

- [backend/graph/context_orchestrator.py:20-47](../../backend/graph/context_orchestrator.py#L20-L47)

### 它做了什么

#### Layer 1

扫描：

- `memory/identity/*.md`

见：

- [backend/graph/context_orchestrator.py:49-58](../../backend/graph/context_orchestrator.py#L49-L58)

#### Layer 2

扫描：

- `memory/timeline/180d_index.md`
- `memory/timeline/phases/*.md`
- 最近 5 个 `weeks/*.md`
- 最近 10 个 `days/*.md`
- 最近 5 个 `stage_reports/*.md`

见：

- [backend/graph/context_orchestrator.py:60-112](../../backend/graph/context_orchestrator.py#L60-L112)

#### Layer 3

扫描：

- `memory/concepts/*.md`
- `memory/tasks/*.md`
- `memory/packs/*.md`

见：

- [backend/graph/context_orchestrator.py:114-149](../../backend/graph/context_orchestrator.py#L114-L149)

#### Assets

扫描：

- `assets/uploads/`
- `assets/data/`
- `assets/figures/`
- `assets/ppt_pack/`

见：

- [backend/graph/context_orchestrator.py:151-160](../../backend/graph/context_orchestrator.py#L151-L160)

#### 推荐文件

根据用户消息的简单关键词做推荐，例如：

- “汇报 / R0” → 推荐 `180d_index.md` 和最新 `stage_report`
- “合成 / checklist” → 推荐 `lab_context.md`
- “机理 / 证据链” → 推荐 mechanism packs

见：

- [backend/graph/context_orchestrator.py:162-200](../../backend/graph/context_orchestrator.py#L162-L200)

### 这一层的本质

这层不是“已经读取的知识”，而是：

> **给模型一个当前工作区的可导航索引。**

这点非常重要，因为当前系统明确区分：

- **预加载的上下文**
- **真实调用工具读取过的文件**

---

## 3.3 真实工具读取上下文（Tool-read Context）

在当前实现里，Memory Map 只告诉模型“有哪些文件值得读”，但不会自动把所有 memory 文件内容都塞进 prompt。

真正把某个 memory 文件内容读进来，仍然要靠工具调用，例如：

- `read_file(path)`

这点在 `Execution Contract` 里写得很明确：

- Control Plane Files 是 system prompt 预加载的，不算 tool call
- Memory Map 和 Recommended Files 只是导航提示
- 只有真的调了 `read_file`，才能说“已读/已查看”

见：

- [backend/graph/prompt_builder.py:90-98](../../backend/graph/prompt_builder.py#L90-L98)

所以当前系统的上下文策略不是“全量塞入”，而是：

> **先注入规则和地图，再让 Agent 按需读取具体文件。**

这对另一个项目非常值得借鉴，因为它天然更省上下文窗口。

---

## 4. 上下文注入链路是怎么走的

这里按一次 `/api/chat` 请求来讲。

## 4.1 先确定 workspace

`SessionManager` 和整个 chat 流程都围绕一个 workspace 运行。

workspace 根目录来自：

- [backend/config.py:13-18](../../backend/config.py#L13-L18)

其中默认工作区是：

- `backend/.openclaw/workspace-default`

如果创建新的 agent workspace，则由：

- [backend/api/agents.py:103-136](../../backend/api/agents.py#L103-L136)

从 `workspace-templates/` 拷贝出一个独立 workspace。

---

## 4.2 生成 Memory Map

在聊天请求开始后：

- `ContextOrchestrator(workspace_dir).generate_memory_map(body.message)`

见：

- [backend/api/chat.py:48-50](../../backend/api/chat.py#L48-L50)

这一阶段不读具体 memory 文件正文，只是建立“文件清单 + 推荐线索”。

---

## 4.3 构建 System Prompt

然后：

- `PromptBuilder.build(memory_map, metadata)`

见：

- [backend/api/chat.py:52-60](../../backend/api/chat.py#L52-L60)

生成的 prompt 由几个块组成：

1. Identity
2. Tooling
3. Workspace
4. Execution Contract
5. Inbound Context(metadata)
6. Control Plane Files
7. Memory Map

见：

- [backend/graph/prompt_builder.py:35-59](../../backend/graph/prompt_builder.py#L35-L59)

### 这一步的设计意义

它不是把“记忆内容”一次性灌满，而是给模型以下能力：

- 知道自己要遵守什么规则
- 知道当前工程里有哪些记忆文件和资产目录
- 知道哪些文件可能与当前请求更相关
- 知道什么时候必须真实调用工具，不能靠嘴说

---

## 4.4 Agent 再按需读写

Agent 收到 system prompt 后，在执行过程中可以继续：

- 读取 memory 文件
- 写入 memory 文件
- 读取/写入 assets
- 写入 trace

工具能力说明会在 prompt 中被注入，见：

- [backend/graph/prompt_builder.py:61-76](../../backend/graph/prompt_builder.py#L61-L76)

因此当前的上下文模式可以概括为：

```text
预加载少量高价值规则文件
  + 注入 Memory Map 文件导航
  + 需要时再显式 read_file
```

这是典型的 **File-first + lazy read** 方案。

---

## 5. 当前上下文设计里最重要的思想

## 5.1 规则内容和业务内容分开

当前 workspace 里，根目录那几份 `.md` 文件和 `memory/` 目录承担的是不同职责。

### 根目录文件

负责：

- 行为规范
- 输出风格
- 项目身份与用户关系
- 环境小抄
- 启动说明
- 长期摘要

### memory/ 目录

负责：

- 项目长期知识
- 时间推进
- 单个概念/任务/交付物

这种拆分很合理，因为它避免把“行为规则”和“业务事实”混在同一个地方。

对另一个项目来说，也建议保留这种区分：

- **Control files**：指导模型怎么工作
- **Memory files**：承载模型要处理的业务记忆

---

## 5.2 稳定信息和变化信息分层

这个项目把 memory 分成了三层。

### Layer 1：Identity（长期稳定）

目录：

- `memory/identity/`

内容：

- `project.md`
- `user.md`
- `lab_context.md`
- `context_budget.md`

分别对应：

- 项目北极星、术语、判据
- 用户偏好与输出约束
- 现实环境与实验条件
- 上下文预算与裁剪策略

见：

- [backend/workspace-templates/memory/identity/project.md](../../backend/workspace-templates/memory/identity/project.md)
- [backend/workspace-templates/memory/identity/user.md](../../backend/workspace-templates/memory/identity/user.md)
- [backend/workspace-templates/memory/identity/lab_context.md](../../backend/workspace-templates/memory/identity/lab_context.md)
- [backend/workspace-templates/memory/identity/context_budget.md](../../backend/workspace-templates/memory/identity/context_budget.md)

### Layer 2：Timeline（时间推进）

目录：

- `memory/timeline/`

内容：

- `180d_index.md`
- `phases/`
- `weeks/`
- `days/`
- `stage_reports/`

它承载的是：

- 当前处在什么阶段
- 最近做了什么
- 阶段交付节奏是什么
- 风险与里程碑是什么

见：

- [backend/workspace-templates/memory/timeline/180d_index.md](../../backend/workspace-templates/memory/timeline/180d_index.md)
- [backend/workspace-templates/memory/timeline/days/_DAY_TEMPLATE.md](../../backend/workspace-templates/memory/timeline/days/_DAY_TEMPLATE.md)
- [backend/workspace-templates/memory/timeline/stage_reports/_STAGE_REPORT_TEMPLATE.md](../../backend/workspace-templates/memory/timeline/stage_reports/_STAGE_REPORT_TEMPLATE.md)

### Layer 3：Atom Notes（原子级任务与交付）

目录：

- `memory/concepts/`
- `memory/tasks/`
- `memory/packs/`

它们分别对应：

- `Concept`：主题容器
- `Task`：一次验证任务（Claim + Protocol + Run）
- `Pack`：面向交付的聚合容器（机理包、PPT 包、写作包、图集包）

见：

- [backend/workspace-templates/memory/concepts/CONCEPT_TEMPLATE.md](../../backend/workspace-templates/memory/concepts/CONCEPT_TEMPLATE.md)
- [backend/workspace-templates/memory/tasks/TASK_TEMPLATE.md](../../backend/workspace-templates/memory/tasks/TASK_TEMPLATE.md)
- [backend/workspace-templates/memory/packs/PACK_TEMPLATE.md](../../backend/workspace-templates/memory/packs/PACK_TEMPLATE.md)

### 这三层拆分背后的核心逻辑

它实际上是在把记忆按“稳定性”和“粒度”拆开：

- Layer 1：相对稳定，频繁复用
- Layer 2：按时间滚动，反映进展
- Layer 3：最具体，能落到单个验证与交付

这个设计对另一个项目也非常适合，因为很多项目都存在类似结构：

- 稳定规则 / 人设 / 判据
- 项目进度 / 周报 / 日报
- 具体 case / task / deliverable

---

## 5.3 assets 和 memory 分离

当前模板把 `assets/` 和 `memory/` 分开，这是一个非常正确的设计。

### memory/

放的是：

- 可读可总结的结构化知识
- 结论、判据、计划、任务、摘要
- 面向模型理解与推理

### assets/

放的是：

- 原始数据
- 图表
- 上传文件
- PPT 打包产物

当前路径约定包括：

- `assets/uploads/`
- `assets/data/`
- `assets/figures/`
- `assets/ppt_pack/`

见：

- [backend/workspace-templates/TOOLS.md:13-19](../../backend/workspace-templates/TOOLS.md#L13-L19)
- [backend/workspace-templates/memory/identity/lab_context.md:44-48](../../backend/workspace-templates/memory/identity/lab_context.md#L44-L48)

### 为什么要分开

因为这两类东西的使用方式完全不同：

- memory 是“模型要理解的抽象层”
- assets 是“模型可引用、但通常不该全量注入的原始材料层”

对另一个项目来说，也强烈建议分开：

- `memory/` 保存结构化知识
- `assets/` 保存原始素材

不要把原始大文件和长期记忆混在一起。

---

## 5.4 trace 目录是“回放层”，不是“知识层”

当前 workspace 里还有一个重要目录：

- `context_trace/`

模板说明见：

- [backend/workspace-templates/context_trace/README.md](../../backend/workspace-templates/context_trace/README.md)

会话与 trace 的实际持久化由：

- [backend/graph/session_manager.py](../../backend/graph/session_manager.py)
- [backend/graph/trace_writer.py](../../backend/graph/trace_writer.py)

负责。

### 这一层的定位

它不是项目知识本身，而是：

- 本轮发生了什么
- 调了哪些工具
- 怎么完成的
- 用于前端回放与调试

所以在架构上应把它看作：

> **execution memory / audit memory**

而不是：

> **domain memory / business memory**

这也是你在另一个项目里很容易做错的一点：

- `memory/` 是给后续任务复用的知识
- `context_trace/` 是给系统回放和核验执行链的日志

两者不要混用。

---

## 6. workspace 文件夹为什么这样设计

下面按目录解释它的架构动机。

## 6.1 每个 workspace 是一个完整、独立、可复制的 Agent 工作区

当前每个 agent workspace 都是从 `workspace-templates/` 复制出来的。

见：

- [backend/api/agents.py:114-127](../../backend/api/agents.py#L114-L127)

而默认工作区由配置指定：

- [backend/config.py:13-18](../../backend/config.py#L13-L18)

这意味着 workspace 不是“数据库里的一条记录”，而是一个真实目录树。

### 这个设计的好处

1. **天然可迁移**：拷目录即可迁移 Agent 记忆
2. **天然可备份**：zip 工作区即可
3. **天然可调试**：直接在 IDE 里看文件
4. **天然可多 Agent**：每个 agent 一个 workspace，彼此隔离

如果你另一个项目也是“单用户 + 多工作区 / 多助手”模式，这个设计非常值得照搬。

---

## 6.2 根目录控制文件是“系统人格层”

workspace 根目录放这些文件：

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `TOOLS.md`
- `BOOTSTRAP.md`
- `MEMORY.md`

它们的共同特点是：

- 相对短
- 高频复用
- 变化频率低于业务记忆
- 适合在每轮 prompt 中预加载

所以它们被放在根目录，而不是 memory 子目录深处。

这是一个很强的工程信号：

> **凡是每轮都高度相关、且能指导 Agent 行为的内容，尽量提到根目录。**

---

## 6.3 memory/ 是“长期业务记忆层”

把业务记忆统一放进 `memory/` 的价值在于：

1. 语义聚合明确
2. 便于工具安全限制
3. 便于后续做索引、压缩、RAG 或 UI 展示

从 [backend/graph/path_utils.py:15-16](../../backend/graph/path_utils.py#L15-L16) 可见，设计上写入白名单包括：

- `memory/`
- `assets/`
- `context_trace/`

这本质上就是把 workspace 拆成 3 大可写域：

- 业务知识
- 原始资产
- 审计回放

这是很适合迁移到另一个项目的安全边界。

---

## 6.4 timeline/ 的设计是为了防止“只会回答，不会推进项目”

很多 Agent 记忆系统只有：

- profile
- notes
- tasks

但这个项目额外强调了 `timeline/`，这很有意思。

它说明设计者希望 Agent 不只是“知道事实”，还要知道：

- 现在处在哪个阶段
- 最近刚做了什么
- 这周/今天的推进是什么
- 下一次阶段汇报该交付什么

所以这个 workspace 设计天然更适合“长期推进型项目”，而不是一次性问答机器人。

如果你的另一个项目也有长期推进特征，比如：

- 论文项目
- 产品迭代项目
- 客户交付项目
- 研发实验项目

那 `timeline/` 这层建议保留。

---

## 6.5 Task 模板的设计很适合做“可验证记忆”

`TASK_TEMPLATE.md` 不是普通 todo，它强制包含：

- Claim
- Evidence
- Protocol
- Runs
- Missing

见：

- [backend/workspace-templates/memory/tasks/TASK_TEMPLATE.md](../../backend/workspace-templates/memory/tasks/TASK_TEMPLATE.md)

这说明任务不是“我要做什么”，而是：

> **我要验证什么、用什么证据、做过哪些执行、还缺什么。**

这是非常适合另一个相似项目复用的，因为它让“记忆”从随手笔记升级成了“可判定状态的知识单元”。

你完全可以在另一个项目里把 Task 套用成：

- 假设验证单
- Bug 诊断单
- 需求实验单
- 客户问题排查单

---

## 6.6 Pack 模板的设计很适合做“从任务到交付”的桥梁

`PACK_TEMPLATE.md` 承担的是：

- 汇总多个 task
- 形成交付叙事
- 关联最终资产路径

见：

- [backend/workspace-templates/memory/packs/PACK_TEMPLATE.md](../../backend/workspace-templates/memory/packs/PACK_TEMPLATE.md)

它解决了一个很常见的问题：

- Task 很细，适合执行
- 但交付需要整合叙事

所以 Pack 相当于：

> **从原子任务到对外/对上交付物之间的中间层。**

如果你另一个项目也有“把一堆任务最后汇总成报告/PRD/汇报/PPT”的需求，Pack 这种目录层非常有价值。

---

## 7. 当前实现与目标态之间的差异

为了迁移时不误解，下面几点需要特别说明。

## 7.1 当前实现里的上下文是“预加载少量 + 导航更多”，不是“智能选片完整注入”

尽管 TAD 里提到了更完整的 context selection/budget/report，但当前代码真实落地的是：

- 预加载控制层文件
- 注入 Memory Map 文件路径列表
- 基于关键词推荐少量文件
- 是否真正读取文件正文，交给 Agent 自己用工具决定

所以它现在更接近：

> **规则预加载 + 文件导航 + 按需读文件**

而不是复杂的自动片段拼装系统。

---

## 7.2 `memory/identity/project.md` 是特殊高优先文件

当前 `PromptBuilder` 直接把 `memory/identity/project.md` 内容注入 control plane block，而不是只把它列在 Memory Map 里。

见：

- [backend/graph/prompt_builder.py:111-121](../../backend/graph/prompt_builder.py#L111-L121)

这说明在设计者看来，`project.md` 已经不只是普通记忆，而是近似“系统级项目判据”。

如果你另一个项目里也有一个最关键的项目主文件，比如：

- `product.md`
- `mission.md`
- `domain_rules.md`

你也可以把它升级为预加载文件，而不是普通 memory 文件。

---

## 7.3 `context_budget.md` 有模板，但当前代码没有真的执行完整 budget 裁剪

模板中已经写了：

- `totalMaxChars`
- `perFileMaxChars`
- `always_full`
- `truncated: true`
- `kept_sections`

见：

- [backend/workspace-templates/memory/identity/context_budget.md](../../backend/workspace-templates/memory/identity/context_budget.md)

但当前 `ContextOrchestrator` / `PromptBuilder` 还没有真正实现完整的 budget engine。

所以对另一个项目来说，这份文件更像：

- 很好的设计意图
- 可直接拿来当下一阶段扩展规范

但不是已经完全落地的能力。

---

## 8. 如果你要在另一个项目做类似记忆功能，我建议怎么复用

## 8.1 先保留这个总结构

我建议直接沿用这 4 层：

```text
workspace/
├─ 控制层文件（根目录）
├─ memory/
├─ assets/
└─ context_trace/
```

这是当前项目最稳的骨架。

---

## 8.2 memory/ 继续按“三层”拆分

建议保留：

```text
memory/
├─ identity/
├─ timeline/
├─ concepts/
├─ tasks/
└─ packs/
```

即便你的项目不是科研，也可以语义映射：

### 对软件/产品项目的映射

- `identity/`：产品目标、用户偏好、团队规则、上下文预算
- `timeline/`：版本计划、迭代周报、日报、阶段复盘
- `concepts/`：主题模块、功能域、问题域
- `tasks/`：单项验证、bug、需求实验、技术方案验证
- `packs/`：PRD、方案包、汇报包、发布包、复盘包

---

## 8.3 至少保留一个“高优先级项目主文件”

类似当前的 `memory/identity/project.md`。

因为这是把分散记忆统一到一个“主线判据”上的关键。

没有这个文件，Agent 很容易：

- 记住很多细节
- 但不知道整体目标是什么

---

## 8.4 上下文注入不要一开始就做太重

建议先照当前实现做：

1. 预加载少量控制文件
2. 生成 Memory Map
3. 基于关键词推荐少量文件
4. 剩下的由 Agent 按需调用 `read_file`

不要第一版就做：

- 大规模自动摘要拼装
- 复杂 RAG rerank
- 多级 budget optimizer

因为当前项目能跑起来，很大程度上就是因为这套方案足够轻。

---

## 8.5 把“真实性契约”写进 prompt 和测试里

这套记忆系统之所以靠谱，不只是目录设计得好，还因为它有一层明确契约：

- 预加载不等于已读
- 建议写入不等于已写入
- 没有工具证据不报完成

这层约束建议你在另一个项目里照搬。

否则记忆系统很容易退化成：

- LLM 声称已经记录
- 实际上没有文件落盘
- 下一轮也无法复现

---

## 9. 我对这套“上下文 + 记忆工作区”设计的评价

如果只看当前已实现的部分，我会这样总结。

### 优点

1. **结构非常清晰**：规则、记忆、资产、审计四层分离
2. **可迁移性强**：直接复制 workspace 即可迁移
3. **非常适合长期项目**：identity/timeline/task/pack 的层次感很强
4. **兼顾上下文成本**：不是把所有文件都塞进 prompt，而是先给地图再按需读取
5. **对真实性有明确约束**：避免“我好像记住了/我好像写了”的幻觉

### 不足

1. 目前自动上下文选择仍偏轻量，更多像导航而不是完整 orchestration
2. `context_budget` 还是设计意图多于实际执行逻辑
3. `skills` 在当前实现里还没有真正纳入这套 workspace 记忆闭环
4. `context_trace` 目前更偏工具轨迹，而不是完整的上下文注入审计

### 结论

如果你另一个项目也想做：

- 可解释的上下文注入
- 文件化长期记忆
- 长周期任务推进
- 真实读写可核验

那这套设计非常值得复用。

最值得直接迁移的是：

- **workspace 目录骨架**
- **三层 memory 结构**
- **控制层文件 + Memory Map 的双层上下文机制**
- **assets 与 memory 分离**
- **context_trace 作为回放层**

---

## 10. 可直接给另一个项目复用的最小版本

如果你只要一个最小落地版，我建议直接从下面这个结构开始：

```text
workspace/
├─ AGENTS.md
├─ USER.md
├─ MEMORY.md
├─ memory/
│  ├─ identity/
│  │  ├─ project.md
│  │  ├─ user.md
│  │  └─ context_budget.md
│  ├─ timeline/
│  │  ├─ index.md
│  │  └─ days/
│  ├─ concepts/
│  ├─ tasks/
│  └─ packs/
├─ assets/
│  ├─ uploads/
│  ├─ data/
│  └─ outputs/
└─ context_trace/
```

然后配一个最小上下文策略：

1. 每轮预加载 `AGENTS.md` + `USER.md` + `memory/identity/project.md`
2. 扫描 `memory/` 生成文件地图
3. 给模型推荐相关文件路径
4. 模型需要细节时再 `read_file`
5. 所有真实工具读写写入 `context_trace`

这样就已经能得到一个相当实用的“文件化记忆系统”。

---

## 11. 这份文档的核心结论

最后压缩成 3 句话：

1. **这个项目的上下文不是一次性灌入，而是“控制文件预加载 + Memory Map 导航 + 按需工具读取”。**
2. **这个项目的记忆不是隐式状态，而是 workspace 下按层组织的文件系统。**
3. **这个项目最有价值的地方，不只是目录设计，而是把“记忆、工具、审计、真实性契约”放成了一套闭环。**

---

## 12. 如果你下一步还要我继续做

我可以继续帮你两种方向：

1. **直接给你另一个项目出一版可复制的 workspace 模板设计**
   - 按你的业务类型重命名 `concept/task/pack`
   - 重新定义 `identity/timeline`

2. **直接给你出一版“上下文注入 + 记忆读写 + trace 审计”的技术实现方案**
   - 包括 schema、接口、模块拆分、伪代码
