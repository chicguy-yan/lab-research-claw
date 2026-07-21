# 项目对齐与架构设计总结

**版本**: v1.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## 📋 已完成的文档

我已经为你创建了以下 4 个核心文档:

### 1. [prd-tad-phase34-alignment-analysis.md](docs/prd-tad-phase34-alignment-analysis.md)
**PRD-TAD-Phase3-4-JSON 对齐分析**

**核心内容**:
- ✅ PRD vs TAD 对齐情况分析
- ✅ PRD vs Phase3-4 Merged Plan 对齐情况
- ✅ JSON 用户示例 vs 系统能力对齐
- ✅ 核心架构不对齐问题识别
- ✅ 推荐的混合方案设计
- ✅ PRD 中未实现功能清单

**关键发现**:
1. ❌ Phase3-4 Plan 移除了 ContextOrchestrator - 与 PRD 不符
2. ❌ Phase3-4 Plan 缺少 terminal 和 python_repl - 无法支持数据分析
3. ⚠️ Workspace 生命周期未完整实现 - 缺少 Evolve/Archive/Clone

---

### 2. [architecture-diagrams.md](docs/architecture-diagrams.md)
**系统架构图集 (Mermaid)**

**包含的架构图**:
1. ✅ 系统总体架构 (前后端 + 记忆系统 + Workspace)
2. ✅ Agent-Skills-Tools-Memory&Assets 关系架构
3. ✅ 单次对话的完整流程 (Sequence Diagram)
4. ✅ Workspace 生命周期 (State Diagram)
5. ✅ Memory 三层架构详解
6. ✅ Assets 与 Memory 的溯源关系
7. ✅ Phase 5: Skills 加载系统架构
8. ✅ 工具安全架构

**关键设计**:
- File-first: 所有数据以文件形式存储
- Tool-Driven: LLM 通过工具主动访问 memory
- 三层记忆: Layer1(稳定) + Layer2(时间轴) + Layer3(原子资产)
- 溯源机制: Memory 嵌入 assets 路径

---

### 3. [phase5-skills-system-design.md](docs/phase5-skills-system-design.md)
**Phase 5: Skills 加载系统设计**

**核心内容**:
- ✅ Skills 系统概述 (Instruction-following 范式)
- ✅ Skills 目录结构和 SKILL.md 标准格式
- ✅ Bootstrap 阶段: SKILLS_SNAPSHOT 生成
- ✅ Runtime 阶段: Skills 执行流程
- ✅ 默认 Skills 清单 (7个推荐 Skills)
- ✅ Skills 与 Tools 的关系
- ✅ Skills 测试场景
- ✅ Skills 扩展机制

**推荐的默认 Skills**:
1. stage_report_ppt (阶段汇报 PPT)
2. synthesis_checklist (合成 checklist)
3. mechanism_audit (机理证据链审计)
4. characterization_audit (表征审计)
5. writing_outline (写作大纲)
6. experiment_matrix (实验矩阵)
7. csv_kobs_fit (CSV 数据拟合)

---

### 4. [phase3-4-tools-design.md](docs/phase3-4-tools-design.md)
**Phase 3-4: 完整工具集设计 (含 terminal 和 python_repl)**

**核心内容**:
- ✅ 完整工具列表 (8个工具)
- ✅ Phase 3 工具详细设计 (read_file/write_file/list_directory)
- ✅ Phase 4 工具详细设计 (terminal/python_repl)
- ✅ 工具注册与集成
- ✅ 工具使用场景 (数据分析/合成 checklist/阶段汇报)
- ✅ 工具安全措施
- ✅ 审计日志设计

**关键工具**:
- read_file: 读取文件 (路径安全检查 + 自动截断)
- write_file: 写入文件 (限制 memory/ 目录)
- terminal: 执行 Shell 命令 (黑名单拦截 + 超时)
- python_repl: 执行 Python 代码 (隔离环境 + 异常捕获)

---

## 🎯 核心问题与解决方案

### 问题 1: Phase3-4 Plan 与 PRD 不对齐

**问题**:
- Phase3-4 Plan 移除了 ContextOrchestrator
- Phase3-4 Plan 缺少 terminal 和 python_repl 工具

**解决方案**:
- 采用混合方案: ContextOrchestrator (推荐文件) + Tool-Driven (按需读取)
- Phase4 必须补充 terminal 和 python_repl 工具

---

### 问题 2: Assets 与 Memory 的溯源关系不清晰

**问题**:
- 用户上传的文件如何与 memory 关联?
- 如何实现溯源?

**解决方案**:
1. 用户上传文件 → 保存到 `assets/uploads/`
2. LLM 处理后 → 写入 memory (带 assets 路径)
3. Memory 文件格式:
```markdown
## 实验数据
**数据来源**: [原始CSV](assets/data/exp_003.csv)
**图片**: [XRD谱图](assets/figures/xrd_exp_003.png)
```

---

### 问题 3: Skills 加载系统未设计

**问题**:
- Skills 如何加载?
- Skills 如何执行?

**解决方案**:
1. Bootstrap 阶段: 扫描 skills/ → 生成 SKILLS_SNAPSHOT.md
2. System Prompt 注入: SKILLS_SNAPSHOT 作为可用技能清单
3. Runtime 执行: Agent 通过 read_file 读取完整 SKILL.md → 按说明执行

---

## 📊 PRD 未实现功能清单

### P0 (必须实现)

| 功能 | PRD 章节 | 状态 |
|------|---------|------|
| **Workspace 生命周期管理** | §4.8 | ❌ 未实现 Evolve/Archive/Clone |
| **Skills 系统** | §3 | ❌ 未实现 load/execute |
| **terminal 工具** | §2.1 | ❌ Phase3-4 缺失 |
| **python_repl 工具** | §2.2 | ❌ Phase3-4 缺失 |
| **资产上传** | §5.4 | ❌ 未实现 |
| **三栏布局** | §6.1 | ❌ 未实现 |

### P1 (推荐实现)

| 功能 | PRD 章节 | 状态 |
|------|---------|------|
| **fetch_url 工具** | §2.3 | ❌ 未实现 |
| **web_search 工具** | §2.6 | ❌ 未实现 |
| **search_knowledge_base 工具** | §2.5 | ❌ 未实现 |
| **Trace 回放** | §5.5 | ❌ 未实现 |
| **Monaco 编辑器** | §6 | ❌ 未实现 |

### P2 (可选)

| 功能 | PRD 章节 | 状态 |
|------|---------|------|
| **RAG 知识库** | §2.5 | ❌ 未实现 |
| **Skill Mining** | §4.5 | ❌ 未实现 |
| **多 Agent 并行** | §4.8 | ❌ 未实现 |

---

## 🚀 实施路线图

### Phase 3 (当前)
- ✅ ContextOrchestrator (简化版)
- ✅ PromptBuilder (OpenClaw 风格)
- ✅ TraceWriter
- ✅ read_file/write_file/list_directory

### Phase 4 (紧急补充)
- ❌ terminal 工具
- ❌ python_repl 工具
- ❌ 资产上传 API

### Phase 5 (Skills + RAG)
- ❌ Skills 加载系统
- ❌ fetch_url 工具
- ❌ web_search 工具
- ❌ search_knowledge_base 工具

### Phase 6 (前端)
- ❌ 三栏布局
- ❌ Memory/Atom 面板
- ❌ Trace 回放

---

## 💡 关键设计决策

### 决策 1: 混合方案 (ContextOrchestrator + Tool-Driven)

**理由**:
- 保持 PRD 要求的显式上下文选择
- 保持灵活性和可扩展性
- 降低 token 消耗
- 提供完整审计能力

### 决策 2: Phase3-4 必须包含 terminal 和 python_repl

**理由**:
- JSON 用户示例中大量数据分析场景
- PRD 明确列出 6 个核心工具
- 这是最小 MVP 的必要能力

### 决策 3: Assets 与 Memory 的溯源机制

**理由**:
- 用户需要溯源到原始文件
- 支持多模态 (CSV/图片/PDF)
- 便于审计和回溯

---

## ✅ 验收标准

### 文档完整性
- ✅ PRD-TAD-Phase3-4 对齐分析完成
- ✅ 架构图集完成 (9个 Mermaid 图)
- ✅ Phase 5 Skills 系统设计完成
- ✅ Phase 3-4 工具设计完成 (含 terminal/python_repl)
- ✅ Assets 与 Memory 溯源关系明确
- ✅ PRD 未实现功能清单完成

### 架构对齐
- ✅ 识别了 Phase3-4 Plan 与 PRD 的不对齐问题
- ✅ 提供了混合方案解决不对齐问题
- ✅ 明确了工具集必须包含 terminal 和 python_repl

### 可实施性
- ✅ 提供了详细的实施步骤
- ✅ 提供了代码示例
- ✅ 提供了测试场景
- ✅ 提供了验收标准

---

## 📝 下一步行动

### 立即行动
1. **补充 terminal 和 python_repl 工具到 Phase4**
2. **修正 Phase3-4 Plan,保留简化版 ContextOrchestrator**
3. **实现资产上传和溯源机制**

### 短期行动
1. **实现 Skills 加载系统 (Phase5)**
2. **实现 fetch_url/web_search/search_knowledge_base 工具**
3. **实现 Trace 回放功能**

### 长期行动
1. **实现前端三栏布局 (Phase6)**
2. **实现 Workspace 生命周期管理 (Evolve/Archive/Clone)**
3. **实现 RAG 知识库和 Skill Mining**

---

## 📚 文档索引

1. [PRD-TAD-Phase3-4 对齐分析](docs/prd-tad-phase34-alignment-analysis.md)
2. [系统架构图集](docs/architecture-diagrams.md)
3. [Phase 5: Skills 系统设计](docs/phase5-skills-system-design.md)
4. [Phase 3-4: 工具设计](docs/phase3-4-tools-design.md)

---

**文档完成** | 2026-03-09

**作者**: Claude Code (Opus 4.6)
