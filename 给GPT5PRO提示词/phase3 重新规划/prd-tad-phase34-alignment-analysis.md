# PRD-TAD-Phase3-4-JSON 对齐分析与架构设计

**版本**: v1.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## 一、文档对齐分析

### 1.1 PRD vs TAD 对齐情况

| 维度 | PRD 定义 | TAD 实现 | 对齐状态 |
|------|---------|---------|---------|
| **三层记忆系统** | Layer1(Identity) + Layer2(Timeline) + Layer3(Atom Notes) | ✅ 完全对齐 | ✅ PASS |
| **六大核心工具** | terminal, python_repl, fetch_url, read_file, search_knowledge, web_search | ✅ 完全对齐 | ✅ PASS |
| **System Prompt 结构** | 两条消息(system+user), Project Context 注入 | ✅ 完全对齐 | ✅ PASS |
| **Workspace 生命周期** | Create → Run → Evolve → Archive → Clone | ⚠️ TAD 未明确 Evolve/Archive/Clone | ⚠️ 部分缺失 |
| **Context Orchestrator** | 选文件+预算控制+缺口检测 | ✅ 完全对齐 | ✅ PASS |
| **Trace 审计** | context_read/write/missing/artifacts | ✅ 完全对齐 | ✅ PASS |

### 1.2 PRD vs Phase3-4 Merged Plan 对齐情况

| 维度 | PRD 定义 | Phase3-4 Plan | 对齐状态 |
|------|---------|--------------|---------|
| **Memory 访问方式** | PRD 未明确指定 | Tool-Driven (read_file/write_file) | ✅ 合理扩展 |
| **工具设计** | 6个核心工具(含terminal/python_repl) | ❌ Phase3-4 Plan 只有 read_file/write_file/list_directory | ❌ **不对齐** |
| **Context 注入** | 控制层+选中的memory文件内容 | 控制层+memory目录列表(不注入内容) | ⚠️ 架构差异 |
| **ContextOrchestrator** | 必须实现 | ❌ Phase3-4 Plan 移除了 | ❌ **不对齐** |

### 1.3 JSON 用户示例 vs 系统能力对齐

基于 `yyq_chlorite_full_lifecycle_180d_300turns.json` 分析:

| 用户场景 | JSON 示例 | 系统需要的能力 | 当前状态 |
|---------|----------|--------------|---------|
| **合成 checklist** | T0001: "把今天的合成流程整理成按时间顺序的checklist" | 读取 protocol + 生成结构化输出 | ✅ 可实现 |
| **开题背景润色** | T0002: "把背景写成漏斗结构" + 上传图片 | 读取图片 + 文本生成 | ⚠️ 需要图片解析 |
| **文献调研** | T0007: "写一个 deepresearch 提示词" + 上传PDF | 读取PDF + 生成提示词 | ⚠️ 需要PDF解析 |
| **实验数据分析** | T0005: 上传 CSV + PNG | 读取CSV + 图片 + 数据分析 | ⚠️ 需要 python_repl |
| **阶段汇报** | 多处提到 "assets/ppt_pack/Rxx_YYYYMMDD/" | 读取多个文件 + 生成PPT结构 | ✅ 可实现 |

**关键发现**:
1. ❌ Phase3-4 Plan 缺少 `terminal` 和 `python_repl` 工具,无法支持数据分析场景
2. ⚠️ 需要增强文件解析能力(PDF/图片/CSV)
3. ✅ 基本的文本生成和记忆管理能力对齐

---

## 二、核心架构不对齐问题

### 2.1 问题1: Phase3-4 Plan 移除了 ContextOrchestrator

**PRD 要求**:
- 必须实现 ContextOrchestrator
- 职责: 选文件 + 预算控制 + 缺口检测
- 输出: selected_files[] + budget_report

**Phase3-4 Plan 方案**:
- 移除 ContextOrchestrator
- 只提供 memory 目录列表
- LLM 通过 read_file 工具按需读取

**冲突分析**:
- PRD 强调"上下文选择必须显式"
- Phase3-4 Plan 依赖 LLM 自主决策
- 可能导致: token 消耗不可控、关键文件遗漏

**建议**: 保留 ContextOrchestrator,但简化为"推荐文件列表",LLM 可选择性读取

### 2.2 问题2: 工具集不完整

**PRD 要求的 6 个核心工具**:
1. ✅ terminal (命令行)
2. ✅ python_repl (Python解释器)
3. ✅ fetch_url (网络抓取)
4. ✅ read_file (文件读取)
5. ✅ search_knowledge_base (RAG检索)
6. ✅ web_search (网络搜索)

**Phase3-4 Plan 只实现了 3 个**:
1. ✅ read_file
2. ✅ write_file
3. ✅ list_directory

**缺失工具的影响**:
- ❌ 无法执行数据分析 (需要 python_repl)
- ❌ 无法执行系统命令 (需要 terminal)
- ❌ 无法联网查询 (需要 fetch_url/web_search)
- ❌ 无法检索知识库 (需要 search_knowledge_base)

**建议**: Phase3-4 必须补充完整的 6 个核心工具

---

## 三、推荐的对齐方案

### 3.1 混合方案: ContextOrchestrator + Tool-Driven

**核心思路**: 结合两种方案的优点

1. **ContextOrchestrator 负责**:
   - 分析用户意图
   - 推荐相关文件列表 (不强制注入)
   - 预算控制和缺口检测

2. **LLM 通过工具**:
   - 根据推荐列表选择性读取
   - 按需读取其他文件
   - 主动写入 memory

**优势**:
- ✅ 保持 PRD 要求的显式上下文选择
- ✅ 保持 Phase3-4 的灵活性
- ✅ 降低 token 消耗
- ✅ 提供审计能力

### 3.2 完整工具集设计

**Phase3-4 必须实现的工具**:

```python
# 1. Memory 操作工具 (Phase3-4 已有)
- read_file(path: str) -> str
- write_file(path: str, content: str) -> str
- list_directory(path: str) -> list[str]

# 2. 核心执行工具 (Phase3-4 缺失,必须补充)
- terminal(command: str) -> str          # 执行Shell命令
- python_repl(code: str) -> str          # 执行Python代码

# 3. 网络工具 (Phase4/5)
- fetch_url(url: str) -> str             # 抓取网页
- web_search(query: str) -> list[dict]   # 网络搜索

# 4. 知识库工具 (Phase5)
- search_knowledge_base(query: str) -> list[dict]  # RAG检索
```

---

## 四、对齐后的 Phase3-4 实施方案

### 4.1 Phase3: Context Orchestrator + Prompt Builder

**ContextOrchestrator 职责**:
1. 分析用户意图 (合成/汇报/机理/写作/作图)
2. 生成推荐文件列表 (不强制注入)
3. 预算控制和缺口检测
4. 输出 trace seed

**PromptBuilder 职责**:
1. 构建 System Prompt:
   - Block 1-5: 控制层完整注入
   - Block 6: Memory Map (目录结构 + 推荐文件列表)
   - Block 7: Tools 说明
2. 构建 User Message

**关键变化**:
- ContextOrchestrator 不再强制注入文件内容
- 只提供推荐列表,LLM 自主决策是否读取

### 4.2 Phase4: 完整工具集

**必须实现的工具**:

1. **read_file** (已有)
2. **write_file** (已有)
3. **list_directory** (已有)
4. **terminal** (新增)
5. **python_repl** (新增)

**Phase5 补充**:
6. **fetch_url**
7. **web_search**
8. **search_knowledge_base**

---

## 五、关键设计决策

### 决策1: 保留 ContextOrchestrator 但简化

**原因**:
- PRD 明确要求"上下文选择必须显式"
- 需要预算控制和缺口检测
- 需要生成 trace seed

**新职责**:
- 不再强制注入文件内容
- 只生成推荐文件列表
- LLM 自主决策是否读取

### 决策2: Phase3-4 必须包含 terminal 和 python_repl

**原因**:
- JSON 用户示例中大量数据分析场景
- PRD 明确列出 6 个核心工具
- 这是最小 MVP 的必要能力

**实施**:
- Phase4 补充 terminal 和 python_repl
- 使用 LangChain 原生工具
- 添加安全检查

### 决策3: assets 与 memory 的溯源关系

**设计**:
1. 用户上传文件 → 保存到 `assets/uploads/`
2. LLM 处理后 → 写入 memory (带 assets 路径)
3. Memory 文件格式:
```markdown
## 实验数据

**数据来源**: [原始CSV](assets/data/exp_003.csv)
**图片**: [XRD谱图](assets/figures/xrd_exp_003.png)

### 分析结果
...
```

**优势**:
- ✅ 用户可溯源
- ✅ 便于审计
- ✅ 支持多模态

---

## 六、未实现功能清单

基于 PRD 分析,以下功能尚未实现:

### 6.1 核心功能

| 功能 | PRD 章节 | 状态 | 优先级 |
|------|---------|------|--------|
| **Workspace 生命周期管理** | §4.8 | ❌ 未实现 Evolve/Archive/Clone | P0 |
| **Skills 系统** | §3 | ❌ 未实现 load/execute | P0 |
| **terminal 工具** | §2.1 | ❌ Phase3-4 缺失 | P0 |
| **python_repl 工具** | §2.2 | ❌ Phase3-4 缺失 | P0 |
| **fetch_url 工具** | §2.3 | ❌ 未实现 | P1 |
| **web_search 工具** | §2.6 | ❌ 未实现 | P1 |
| **search_knowledge_base 工具** | §2.5 | ❌ 未实现 | P1 |
| **资产上传** | §5.4 | ❌ 未实现 | P0 |
| **Trace 回放** | §5.5 | ❌ 未实现 | P1 |

### 6.2 前端功能

| 功能 | PRD 章节 | 状态 | 优先级 |
|------|---------|------|--------|
| **三栏布局** | §6.1 | ❌ 未实现 | P0 |
| **左侧面板 (Layer1+2)** | §6.2 | ❌ 未实现 | P0 |
| **右侧面板 (Layer3)** | §6.4 | ❌ 未实现 | P0 |
| **Monaco 编辑器** | §6 | ❌ 未实现 | P1 |
| **Trace 回放视图** | §6.5 | ❌ 未实现 | P1 |

### 6.3 高级功能

| 功能 | PRD 章节 | 状态 | 优先级 |
|------|---------|------|--------|
| **RAG 知识库** | §2.5 | ❌ 未实现 | P2 |
| **Skill Mining** | §4.5 | ❌ 未实现 | P2 |
| **多 Agent 并行** | §4.8 | ❌ 未实现 | P2 |

---

## 七、实施路线图

### Phase3 (当前)
- ✅ ContextOrchestrator (简化版)
- ✅ PromptBuilder (OpenClaw 风格)
- ✅ TraceWriter
- ✅ read_file/write_file/list_directory

### Phase4 (紧急补充)
- ❌ terminal 工具
- ❌ python_repl 工具
- ❌ 资产上传 API

### Phase5 (Skills + RAG)
- ❌ Skills 加载系统
- ❌ fetch_url 工具
- ❌ web_search 工具
- ❌ search_knowledge_base 工具

### Phase6 (前端)
- ❌ 三栏布局
- ❌ Memory/Atom 面板
- ❌ Trace 回放

---

## 八、总结

### 8.1 关键对齐问题

1. ❌ **Phase3-4 Plan 移除了 ContextOrchestrator** - 与 PRD 不符
2. ❌ **Phase3-4 Plan 缺少 terminal 和 python_repl** - 无法支持数据分析
3. ⚠️ **Workspace 生命周期未完整实现** - 缺少 Evolve/Archive/Clone

### 8.2 推荐方案

**混合方案**: ContextOrchestrator (推荐文件) + Tool-Driven (按需读取)

**优势**:
- ✅ 保持 PRD 要求的显式上下文选择
- ✅ 保持灵活性和可扩展性
- ✅ 降低 token 消耗
- ✅ 提供完整审计能力

### 8.3 下一步行动

1. **立即**: 补充 terminal 和 python_repl 工具到 Phase4
2. **立即**: 修正 Phase3-4 Plan,保留简化版 ContextOrchestrator
3. **短期**: 实现资产上传和溯源机制
4. **中期**: 实现 Skills 加载系统
5. **长期**: 实现前端三栏布局

---

**文档完成** | 2026-03-09
