# Experimental-Research-OpenClaw 架构图集

**版本**: v1.0 | **日期**: 2026-03-09

---

## 一、系统总体架构

### 1.1 前后端 + 记忆系统 + Workspace 架构

```mermaid
graph TB
    subgraph "前端 Frontend (Next.js)"
        UI[三栏UI]
        L1Panel[左侧面板<br/>Layer1+Layer2]
        ChatPanel[中间面板<br/>Chat+ThoughtChain]
        L3Panel[右侧面板<br/>Layer3 Atom Notes]
    end

    subgraph "后端 Backend (FastAPI)"
        API[API 路由层]
        AgentMgr[AgentManager<br/>LangChain create_agent]
        ContextOrch[ContextOrchestrator<br/>选文件+预算+缺口]
        PromptBuilder[PromptBuilder<br/>System+User拼接]
        SessionMgr[SessionManager<br/>会话持久化]
        TraceWriter[TraceWriter<br/>审计落盘]
    end

    subgraph "工具层 Tools"
        ReadFile[read_file]
        WriteFile[write_file]
        Terminal[terminal]
        PythonREPL[python_repl]
        FetchURL[fetch_url]
        WebSearch[web_search]
        SearchKB[search_knowledge_base]
    end

    subgraph "Workspace (File-first)"
        Control[控制层<br/>SOUL/IDENTITY/USER/AGENTS]
        Skills[Skills<br/>SKILLS_SNAPSHOT]
        Memory[三层记忆<br/>Layer1/2/3]
        Assets[资产<br/>uploads/data/figures/ppt_pack]
        Trace[审计<br/>context_trace]
    end

    UI --> API
    API --> AgentMgr
    AgentMgr --> ContextOrch
    AgentMgr --> PromptBuilder
    AgentMgr --> SessionMgr
    AgentMgr --> TraceWriter

    AgentMgr --> ReadFile
    AgentMgr --> WriteFile
    AgentMgr --> Terminal
    AgentMgr --> PythonREPL
    AgentMgr --> FetchURL
    AgentMgr --> WebSearch
    AgentMgr --> SearchKB

    ContextOrch --> Memory
    PromptBuilder --> Control
    PromptBuilder --> Skills
    PromptBuilder --> Memory

    ReadFile --> Memory
    ReadFile --> Assets
    WriteFile --> Memory
    Terminal --> Assets
    PythonREPL --> Assets

    TraceWriter --> Trace
    SessionMgr --> Trace
```

**说明**:
- **前端**: 三栏 IDE 风格,支持拖拽分隔条
- **后端**: FastAPI + LangChain create_agent,SSE 流式推送
- **工具层**: 7个核心工具,支持文件操作、代码执行、网络访问
- **Workspace**: File-first 设计,所有数据以文件形式存储

---

## 二、Agent-Skills-Tools-Memory&Assets 关系架构

### 2.1 核心关系图

```mermaid
graph LR
    subgraph "Agent 层"
        Agent[LangChain Agent<br/>create_agent]
    end

    subgraph "Skills 层"
        SkillSnapshot[SKILLS_SNAPSHOT.md<br/>技能清单]
        Skill1[stage_report_ppt]
        Skill2[synthesis_checklist]
        Skill3[mechanism_audit]
    end

    subgraph "Tools 层"
        T1[read_file]
        T2[write_file]
        T3[terminal]
        T4[python_repl]
        T5[fetch_url]
        T6[web_search]
        T7[search_knowledge_base]
    end

    subgraph "Memory 层"
        L1[Layer1: Identity<br/>user/project/lab_context]
        L2[Layer2: Timeline<br/>180d_index/phases/weeks/days]
        L3[Layer3: Atom Notes<br/>concepts/tasks/packs]
    end

    subgraph "Assets 层"
        A1[uploads/<br/>用户上传]
        A2[data/<br/>实验数据]
        A3[figures/<br/>图表]
        A4[ppt_pack/<br/>汇报素材]
    end

    Agent -->|1.读取技能清单| SkillSnapshot
    Agent -->|2.决定使用技能| Skill1
    Skill1 -->|3.调用工具| T1
    Skill1 -->|3.调用工具| T4

    Agent -->|直接调用| T1
    Agent -->|直接调用| T2
    Agent -->|直接调用| T3
    Agent -->|直接调用| T4

    T1 -->|读取| L1
    T1 -->|读取| L2
    T1 -->|读取| L3
    T1 -->|读取| A1
    T1 -->|读取| A2

    T2 -->|写入| L1
    T2 -->|写入| L2
    T2 -->|写入| L3

    T3 -->|生成| A3
    T4 -->|生成| A2
    T4 -->|生成| A3

    A1 -.溯源路径.-> L3
    A2 -.溯源路径.-> L3
    A3 -.溯源路径.-> L3
```

**关键流程**:
1. Agent 读取 SKILLS_SNAPSHOT,了解可用技能
2. Agent 根据任务决定使用哪个 Skill
3. Skill 通过调用 Tools 完成任务
4. Tools 操作 Memory 和 Assets
5. Memory 中记录 Assets 的溯源路径

---

## 三、单次对话的完整流程

### 3.1 用户消息处理流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as 前端
    participant API as API层
    participant ContextOrch as ContextOrchestrator
    participant PromptBuilder as PromptBuilder
    participant Agent as AgentManager
    participant Tools as Tools
    participant Memory as Memory
    participant Assets as Assets
    participant Trace as TraceWriter

    User->>Frontend: 发送消息 + 上传文件
    Frontend->>API: POST /api/chat

    API->>ContextOrch: 分析意图 + 选择文件
    ContextOrch->>Memory: 扫描 Layer1/2/3
    ContextOrch-->>API: 返回 selected_files + trace_seed

    API->>PromptBuilder: 构建 System+User Prompt
    PromptBuilder->>Memory: 读取控制层文件
    PromptBuilder-->>API: 返回完整 Prompt

    API->>Agent: astream(prompt, history)

    loop SSE 流式推送
        Agent->>Tools: 调用工具 (read_file/python_repl/...)
        Tools->>Memory: 读取/写入
        Tools->>Assets: 读取/生成
        Tools-->>Agent: 返回结果
        Agent-->>Frontend: SSE: token/tool_start/tool_end
    end

    Agent-->>API: done
    API->>Trace: 写入审计日志
    Trace->>Memory: 保存到 context_trace/
    API-->>Frontend: SSE: done + trace_path

    Frontend->>API: GET /api/traces/{trace_path}
    API-->>Frontend: 返回 trace 详情
    Frontend->>User: 展示回放
```

**关键步骤**:
1. **意图识别**: ContextOrchestrator 分析用户意图,选择相关文件
2. **Prompt 构建**: PromptBuilder 拼接 System+User 消息
3. **Agent 执行**: 流式调用工具,生成响应
4. **审计落盘**: TraceWriter 记录所有操作
5. **回放展示**: 前端展示完整的执行过程

---

## 四、Workspace 生命周期

### 4.1 完整生命周期

```mermaid
stateDiagram-v2
    [*] --> Create: 用户创建 Agent

    Create --> Run: 初始化完成

    state Create {
        [*] --> CopyTemplates: 复制 workspace-templates
        CopyTemplates --> InitMemory: 初始化 memory/
        InitMemory --> InitAssets: 初始化 assets/
        InitAssets --> InitTrace: 初始化 context_trace/
        InitTrace --> [*]
    }

    Run --> Run: 每次对话
    Run --> Evolve: 检测到重复模式

    state Run {
        [*] --> Ingest: 意图识别
        Ingest --> Plan: 选择文件
        Plan --> Execute: Agent执行
        Execute --> Close: 写回记忆
        Close --> Trace: 审计落盘
        Trace --> [*]
    }

    state Evolve {
        [*] --> DetectPattern: 检测重复任务
        DetectPattern --> ExtractSkill: 提炼为 Skill
        ExtractSkill --> UpdateMemory: 更新 Layer2
        UpdateMemory --> [*]
    }

    Evolve --> Run: 继续运行
    Run --> Archive: 周期结束

    state Archive {
        [*] --> Freeze: 冻结最终状态
        Freeze --> GenerateManifest: 生成 manifest.json
        GenerateManifest --> [*]
    }

    Archive --> Clone: 创建新周期
    Archive --> [*]: 归档完成

    state Clone {
        [*] --> SelectLayers: 选择继承层
        SelectLayers --> CopySelected: 复制选中内容
        CopySelected --> InitNew: 初始化新 workspace
        InitNew --> [*]
    }

    Clone --> Run: 新周期开始
```

**生命周期说明**:
1. **Create**: 从模板创建新 workspace
2. **Run**: 日常对话循环
3. **Evolve**: 自动提炼 Skills 和更新记忆
4. **Archive**: 周期结束,冻结状态
5. **Clone**: 创建新周期,选择性继承

---

## 五、Memory 三层架构详解

### 5.1 三层记忆结构

```mermaid
graph TB
    subgraph "Layer1: Identity (长期稳定)"
        L1_1[user.md<br/>用户偏好]
        L1_2[project.md<br/>项目北极星+判据]
        L1_3[lab_context.md<br/>实验室约束]
        L1_4[context_budget.md<br/>上下文预算]
    end

    subgraph "Layer2: Timeline (时间轴)"
        L2_1[180d_index.md<br/>180天总览]
        L2_2[phases/<br/>P01-P05阶段]
        L2_3[weeks/<br/>周报]
        L2_4[days/<br/>日志]
        L2_5[stage_reports/<br/>阶段汇报]
    end

    subgraph "Layer3: Atom Notes (原子资产)"
        L3_1[concepts/<br/>研究主题]
        L3_2[tasks/<br/>实验任务]
        L3_3[packs/<br/>交付物]
    end

    subgraph "Assets (原始资产)"
        A1[uploads/]
        A2[data/]
        A3[figures/]
        A4[ppt_pack/]
    end

    L1_1 -.定义.-> L2_1
    L1_2 -.指导.-> L3_1
    L2_2 -.包含.-> L2_3
    L2_3 -.包含.-> L2_4
    L3_1 -.包含.-> L3_2
    L3_2 -.组成.-> L3_3

    A1 -.溯源.-> L3_2
    A2 -.溯源.-> L3_2
    A3 -.溯源.-> L3_3
    A4 -.溯源.-> L3_3
```

**层级关系**:
- **Layer1**: 定义"你是谁、项目是什么"
- **Layer2**: 记录"时间推进、阶段进展"
- **Layer3**: 存储"原子证据、可复用对象"
- **Assets**: 保存"原始文件、生成产物"

---

## 六、Assets 与 Memory 的溯源关系

### 6.1 溯源流程

```mermaid
graph LR
    subgraph "用户操作"
        Upload[用户上传文件]
    end

    subgraph "Assets 存储"
        SaveAssets[保存到 assets/uploads/]
        GetPath[获取文件路径]
    end

    subgraph "LLM 处理"
        ReadAssets[LLM 读取 assets]
        ProcessData[处理数据/分析]
        GenerateMemory[生成 memory 内容]
    end

    subgraph "Memory 写入"
        WriteMemory[写入 memory/tasks/ 或 memory/packs/]
        EmbedPath[嵌入 assets 路径]
    end

    subgraph "用户溯源"
        ViewMemory[查看 memory 文件]
        ClickPath[点击 assets 路径]
        ViewOriginal[查看原始文件]
    end

    Upload --> SaveAssets
    SaveAssets --> GetPath
    GetPath --> ReadAssets
    ReadAssets --> ProcessData
    ProcessData --> GenerateMemory
    GenerateMemory --> WriteMemory
    WriteMemory --> EmbedPath

    EmbedPath --> ViewMemory
    ViewMemory --> ClickPath
    ClickPath --> ViewOriginal
```

**溯源示例**:

```markdown
## TASK_exp_005.md

### 实验数据

**原始数据**: [XRD数据](assets/data/exp_005_xrd.csv)
**谱图**: [XRD谱图](assets/figures/exp_005_xrd.png)
**实验照片**: [样品照片](assets/uploads/20250901_sample.jpg)

### 分析结果

根据 XRD 数据分析,Co(IV) 特征峰在 2θ=31.2°...
```

**关键设计**:
1. ✅ Memory 文件中嵌入 assets 相对路径
2. ✅ 前端支持点击路径跳转
3. ✅ 支持多模态溯源 (CSV/图片/PDF)

---

## 七、Phase 5: Skills 加载系统

### 7.1 Skills 系统架构

```mermaid
graph TB
    subgraph "Skills 目录"
        SkillDir[backend/skills/]
        Skill1[stage_report_ppt/<br/>SKILL.md]
        Skill2[synthesis_checklist/<br/>SKILL.md]
        Skill3[mechanism_audit/<br/>SKILL.md]
    end

    subgraph "Bootstrap 阶段"
        Scanner[Skills Scanner]
        Parser[Frontmatter Parser]
        Generator[SKILLS_SNAPSHOT Generator]
    end

    subgraph "System Prompt"
        Snapshot[SKILLS_SNAPSHOT.md]
        PromptBuilder[PromptBuilder]
    end

    subgraph "Runtime 阶段"
        Agent[Agent]
        ReadFile[read_file tool]
        SkillContent[读取 SKILL.md 完整内容]
        Execute[按 Skill 说明执行]
    end

    SkillDir --> Scanner
    Skill1 --> Scanner
    Skill2 --> Scanner
    Skill3 --> Scanner

    Scanner --> Parser
    Parser --> Generator
    Generator --> Snapshot

    Snapshot --> PromptBuilder
    PromptBuilder --> Agent

    Agent -->|1.看到技能清单| Snapshot
    Agent -->|2.决定使用| ReadFile
    ReadFile -->|3.读取完整说明| SkillContent
    SkillContent --> Execute
```

**Skills 加载流程**:
1. **Bootstrap**: 扫描 skills/ 目录,生成 SKILLS_SNAPSHOT.md
2. **注入**: PromptBuilder 将 SKILLS_SNAPSHOT 注入 System Prompt
3. **执行**: Agent 通过 read_file 读取完整 SKILL.md,按说明执行

**SKILL.md 格式**:

```markdown
---
name: stage_report_ppt
description: 生成阶段汇报 PPT 的页级结构
version: 1.0
---

# Stage Report PPT Skill

## 使用场景
当用户请求"准备第N次阶段汇报"时使用

## 输入要求
- assets/ppt_pack/Rxx_YYYYMMDD/ 素材路径
- 时间范围 (如"最近两周")

## 执行步骤
1. 使用 read_file 读取 memory/timeline/stage_reports/上一期.md
2. 使用 read_file 读取 memory/timeline/weeks/ 相关周报
3. 使用 python_repl 分析素材文件
4. 生成 PPT 结构 (页级 + 中心句)
5. 使用 write_file 写入 memory/packs/PACK_stage_report_Rxx.md

## 输出格式
...
```

---

## 八、工具安全架构

### 8.1 工具安全检查

```mermaid
graph TB
    subgraph "工具调用"
        Agent[Agent 调用工具]
    end

    subgraph "安全检查层"
        PathCheck[路径安全检查<br/>resolve_safe_path]
        BlacklistCheck[黑名单检查<br/>危险命令拦截]
        WhitelistCheck[白名单检查<br/>允许目录]
        SizeCheck[大小检查<br/>文件截断]
    end

    subgraph "执行层"
        ReadOp[读取操作]
        WriteOp[写入操作]
        ExecOp[执行操作]
    end

    subgraph "审计层"
        TraceLog[Trace 日志]
    end

    Agent --> PathCheck
    PathCheck -->|通过| BlacklistCheck
    PathCheck -->|拒绝| TraceLog

    BlacklistCheck -->|通过| WhitelistCheck
    BlacklistCheck -->|拒绝| TraceLog

    WhitelistCheck -->|通过| SizeCheck
    WhitelistCheck -->|拒绝| TraceLog

    SizeCheck --> ReadOp
    SizeCheck --> WriteOp
    SizeCheck --> ExecOp

    ReadOp --> TraceLog
    WriteOp --> TraceLog
    ExecOp --> TraceLog
```

**安全措施**:
1. **路径检查**: 防止路径遍历攻击
2. **黑名单**: 拦截危险命令 (rm -rf /, dd, mkfs 等)
3. **白名单**: 限制操作目录 (workspace/, memory/, assets/)
4. **大小限制**: 自动截断超大文件 (20000 字符)
5. **审计日志**: 记录所有工具调用

---

## 九、总结

### 9.1 架构关键点

1. **File-first**: 所有数据以文件形式存储,透明可审计
2. **Tool-Driven**: LLM 通过工具主动访问 memory 和 assets
3. **三层记忆**: Layer1(稳定) + Layer2(时间轴) + Layer3(原子资产)
4. **溯源机制**: Memory 嵌入 assets 路径,支持回溯
5. **Skills 系统**: Instruction-following 范式,拖入即用
6. **安全设计**: 多层安全检查,完整审计日志

### 9.2 架构优势

- ✅ **透明**: 所有数据可读可审计
- ✅ **灵活**: 按需读取,降低 token 消耗
- ✅ **可扩展**: 易于添加新工具和 Skills
- ✅ **可溯源**: 完整的 assets → memory 溯源链
- ✅ **安全**: 多层安全检查,防止误操作

---

**文档完成** | 2026-03-09
