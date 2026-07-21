# 图 1: Workspace 生命周期（Create → Run → Evolve → Archive → Clone）
为什么这么画

PRD/TAD 里的 workspace 本质是文件系统上的一个可回放工作台：从 workspace-templates/ 初始化，到对话运行产出 trace，再到记忆层与 pack 的演进，最终可归档并克隆复用。TAD 还明确了 .openclaw/workspace/ 与 workspace-{agent_id}/ 的初始化来源与结构，所以生命周期用“状态机”表达最直观：每个状态都有明确的触发 API/动作与落盘产物路径。

stateDiagram-v2
  direction LR

  [*] --> Create : 用户创建会话/工作区\nPOST /api/sessions\n或首次对话自动初始化

  Create --> Run : 工作区可用\n(已初始化 workspace 文件 + skills snapshot)

  Run --> Evolve : 回合 done\n写 trace + (可选) apply memory patch\n生成/更新 Concept Task Pack\n或 Skill Mining 触发

  Evolve --> Run : 继续对话\nPOST /api/chat

  Run --> Archive : 用户显式归档/压缩\nPOST /api/sessions/{id}/compress\n或阶段汇报 Pack 完成后归档

  Archive --> Clone : 用户需要新分支\n复制工作区到 workspace-{agent_id}\n或新 session 复用模板/记忆骨架

  Clone --> Run : 在新工作区继续对话\nPOST /api/chat

  Archive --> [*] : 项目结束/冻结\n保留 memory + packs + traces

  note right of Create
    Inputs:
      - workspace-templates/* (SOUL/IDENTITY/AGENTS/...)
      - skills/ 扫描 -> SKILLS_SNAPSHOT.md
    Outputs:
      - .openclaw/workspace/...
      - (可选) sessions/{session_id}.json
  end note

  note right of Run
    Trigger:
      - 用户消息 + uploads
    Outputs (per turn):
      - SSE 事件流 token/tool_start/tool_end/new_response/done
  end note

  note right of Evolve
    Deterministic logs:
      - .openclaw/context_trace/Txxxx.json
    Optional writes:
      - memory/identity|timeline|concepts|tasks|packs
      - assets/... (ppt_pack, figures, data)
  end note

  # 图 2: 单次对话的上下文拼接逻辑 + 最小对话闭环（Ingest → Plan → Close → Pack → Skill Mining）
为什么这么画

PRD 把“OpenClaw 风格两条消息(system + user)”的上下文注入顺序写得非常明确，并要求每回合把“读了哪些文件、裁剪原因、缺口字段、拟写入”落到 trace 里。这里最关键的可调试切分是：

Context Assembly（确定性）：Context Orchestrator 选文件 + budget 裁剪 + Prompt Builder 拼接。

Runtime Loop（闭环产物）：Ingest/Plan/Close/Pack/Skill Mining 是你的“研究闭环最小单元”，每一步都能映射到“读哪些层、写哪些资产”。

所以我用一个 flowchart，把“上下文拼接”和“闭环阶段”放在两个 subgraph 里，并把 trace 与 memory patch 放在边上，方便你做回放与定位。

flowchart TB
  %% =========================
  %% A) Context Assembly
  %% =========================
  subgraph A[Context Assembly: 上下文拼接 (确定性, 可测试)]
    U[User Message\n+ uploads paths] --> SM[SessionManager\nload_session_for_agent()]
    SM --> CO[ContextOrchestrator\nselect_files + budget_report\n+ trace_seed]

    CO --> PB[PromptBuilder\nOpenClaw 两条消息\nsystem + user]

    PB --> SYS[system:\nTooling + Workspace rules\n+ Project Context(注入文件全文)]
    PB --> USR[user:\n(untrusted block 可选)\n+ 用户正文]

    CO --> TR0[trace_seed:\ncontext_read plan\nmissing 初稿\nskills_selected 初稿]
  end

  %% 注入文件顺序（PRD 默认排序）
  SYS --- ORDER[默认注入顺序:\nworkspace/* -> SKILLS_SNAPSHOT -> L1 -> L2 -> L3 -> uploads]

  %% =========================
  %% B) Runtime Loop
  %% =========================
  subgraph B[Runtime Loop: 最小闭环 (产物驱动)]
    LLM[create_agent()\nAgent astream] --> ING[Ingest\n识别意图 + 缺口字段]
    ING --> PLN[Plan\n最小验证集/下一步]
    PLN --> CLS[Close\n把 run 的 raw_data_paths/quick_results/verdict\n写入 Task 或提出补齐]
    CLS --> PCK[Pack\n组织多个 Task -> Pack\n(PPT/机理证据链/写作段落/图集)]
    PCK --> SKM[Skill Mining\n高重复交付 -> 新 Skill 模板(半自动)]
  end

  %% =========================
  %% C) Trace + Memory Patch
  %% =========================
  LLM --> SSE[SSE stream:\ntoken/tool_start/tool_end/new_response/done]
  SSE --> TW[TraceWriter\nwrite trace\n+ 汇总 tool_calls\n+ (可选) apply memory patch]
  TW --> TRF[.openclaw/context_trace/Txxxx.json]

  %% Memory writes are file-first
  TW --> MEM[memory/\nidentity | timeline | concepts | tasks | packs]
  TW --> AST[assets/\nuploads | data | figures | ppt_pack]

  %% Context read sources
  CO --> WS[workspace/*\n(AGENTS/IDENTITY/USER/...)]
  CO --> SKS[skills/*\n+ SKILLS_SNAPSHOT.md]
  CO --> L1[memory/identity/*]
  CO --> L2[memory/timeline/*]
  CO --> L3[memory/concepts|tasks|packs/*]
  CO --> UP[assets/uploads/*\n(必要时仅路径+摘要/采样)]

  %% Tight coupling: trace records reads/writes/missing
  TRF -.记录.-> WS
  TRF -.记录.-> MEM
  TRF -.记录.-> AST
  TRF -.记录.-> CO


  # 图 3: 前后端 + 记忆系统 + workspace 架构（TAD 结构落点图）
为什么这么画

你要用 Mermaid 图去“盯进度(issues) + 定位问题(日志)”，那最有效的是把 TAD 的目录级模块直接变成架构块：

前端三栏对应 PRD 的 L1/L2 面板、Chat 流式 ThoughtChain、L3 Atom Notes。

后端 FastAPI API 层对应 api/chat.py、files.py、sessions.py、assets.py、traces.py。

graph/ 核心把“选文件/拼 prompt/写 trace”这些可测试确定逻辑立起来。

File-first 记忆与 workspace用真实目录表示，这样你在调试时能直接跳到路径。

flowchart LR
  %% ========= Frontend =========
  subgraph FE[Frontend (Next.js 三栏 IDE)]
    MP[MemoryPanel\n(Layer1+Layer2 tree)\nMonaco 打开/编辑] 
    CP[ChatPanel\n消息 + 输入]
    TC[ThoughtChain\n解析 SSE\n(tool_start/tool_end/new_response)]
    AP[AtomPanel\n(Layer3)\nConcepts/Tasks/Packs 列表]
    CP --> TC
  end

  %% ========= Backend API =========
  subgraph BE[Backend (FastAPI)]
    CHAT[POST /api/chat\nSSE 不变]
    FILES[GET/POST /api/files\n+ tree/preview\n+ /api/skills]
    SESS[Sessions CRUD\n+ history + compress]
    ASSET[POST /api/assets/upload]
    TRACES[GET /api/traces\nGET /api/traces/{turn_id}]
  end

  %% ========= Core Graph =========
  subgraph CORE[graph/ (LangChain create_agent 编排)]
    AM[AgentManager\n_build_agent per request\nastream()]
    SM[SessionManager\nload_session_for_agent\nsave_message\ncompress_history]
    CO[ContextOrchestrator\nselect_files\nbudget_report\ntrace_seed]
    PB[PromptBuilder\nsystem+user 拼接\n注入 Project Context]
    TW[TraceWriter\nwrite trace\n(可选) apply memory patch]
    KI[KnowledgeIndexer (可选)\nknowledge/ Hybrid Search\nretrieval SSE]
  end

  %% ========= Tools =========
  subgraph TOOLS[tools/ (6 Core Tools)]
    T1[terminal]
    T2[python_repl]
    T3[fetch_url]
    T4[read_file]
    T5[search_knowledge_base]
    T6[web_search (条件启用)]
  end

  %% ========= File System =========
  subgraph FS[File-first Storage (本地文件系统)]
    WS[.openclaw/workspace/\nworkspace-{agent_id}/]
    WST[workspace-templates/\n(初始化来源)]
    MEM[memory/\nidentity\n timeline\n concepts\n tasks\n packs]
    SK[skills/\n*/SKILL.md\n+ SKILLS_SNAPSHOT.md]
    CT[.openclaw/context_trace/\nTxxxx.json]
    SESF[sessions/\n{session_id}.json\narchive/]
    AS[assets/\nuploads data figures ppt_pack]
    KB[knowledge/\n+ storage/knowledge_index/]
  end

  %% ========= Frontend <-> Backend =========
  MP <--> FILES
  AP <--> FILES
  CP --> CHAT
  TC <--- CHAT

  CP --> ASSET
  MP --> TRACES
  TC --> TRACES

  %% ========= Backend -> Core =========
  CHAT --> AM
  CHAT --> SM
  CHAT --> CO
  CHAT --> PB
  CHAT --> KI
  CHAT --> TW

  %% ========= Core relations =========
  AM --> TOOLS
  CO --> FS
  PB --> FS
  TW --> FS
  SM --> SESF
  KI --> KB

  %% ========= File relations =========
  WST --> WS
  SK --> PB
  MEM --> CO
  WS --> CO
  CO --> PB
  PB --> AM
  AM --> TW
  TW --> CT
  TW --> MEM
  TW --> AS