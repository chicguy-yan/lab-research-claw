# Literature Review Skill 测试结果文件位置

## 生成时间
2026-03-14 18:06

## 文件清单

### 1. 验证报告（你正在看的文件）
📄 **位置**: `docs/literature-review-skill-integration-report.md`
- 完整的集成验证报告
- 包含 skill 功能说明、记忆层级结构规范、使用场景

### 2. TASK 演示文件（6.0 KB）
📄 **位置**: `backend/.openclaw/workspace-default/memory/tasks/TASK_literature_CRISPR_demo.md`

**内容概览**:
```markdown
# TASK_literature_CRISPR_demo.md

## meta
- id: TASK_literature_CRISPR_demo
- concept: CONCEPT_gene_therapy_mechanisms
- status: done
- owner: agent
- created_at: 2026-03-14

## 1) Claim（要证明什么）
- 系统性综述 CRISPR-Cas9 治疗镰刀型细胞病的疗效和机制

## 2) Evidence（目前有什么证据）
- 45 篇高质量文献
- PubMed: 247 → 35 篇
- bioRxiv: 58 → 10 篇
- 引用验证: 45/45 通过 (100%)

## 3) Protocol（怎么做）
- PICO 框架定义研究问题
- 多数据库检索（PubMed, bioRxiv, arXiv）
- PRISMA 流程筛选
- Cochrane Risk of Bias 质量评估
- 引用验证和 PDF 生成

## 4) Runs（实际执行）
- 检索结果: 247 + 58 + 12 = 317 篇
- 筛选后: 45 篇高质量文献
- 质量分布: High 40%, Moderate 49%, Low 11%
- 主题: 递送系统、疗效、安全性、长期随访

## 5) Missing（缺什么信息）
- 长期随访数据（> 10 年）
- 儿童患者数据
- 成本效益分析
- 不同种族人群数据
```

### 3. PACK 演示文件（6.0 KB）
📄 **位置**: `backend/.openclaw/workspace-default/memory/packs/PACK_literature_CRISPR_mechanisms.md`

**内容概览**:
```markdown
# PACK_literature_CRISPR_mechanisms.md

## meta
- id: PACK_literature_CRISPR_mechanisms
- pack_type: literature_pack
- created_at: 2026-03-14
- time_range: 2015-01-01 ~ 2024-12-31

## task_refs[]
- TASK_literature_CRISPR_demo

## final_assets[]
- assets/literature/CRISPR_SCD_review.pdf
- assets/literature/citation_report.json
- assets/literature/figures/PRISMA_flow_diagram.png

## takeaways[]
1. AAV 载体递送效率高（65-85%）但存在免疫原性风险
2. 脂质纳米颗粒安全性更好但效率较低（40-60%）
3. 临床试验显示初步疗效，HbF 水平提升 20-30%
4. 长期随访（5 年）显示持续疗效，但数据有限
5. 脱靶效应发生率低（< 0.1%），但监测方法有限
6. 主要挑战：递送系统优化、长期安全性评估、成本控制

## narrative（给论文/组会的叙事骨架）
CRISPR-Cas9 基因编辑技术在镰刀型细胞病治疗中显示出巨大潜力...
[完整叙事骨架，包含背景、进展、挑战、未来方向]

## limitations & risks
- 研究局限性：样本量小、随访时间短、种族多样性不足
- 临床风险：脱靶效应、免疫反应、长期安全性未知
- 社会经济风险：成本高昂、可及性差、伦理争议

## next_plan
- 短期：持续文献监测、深入分析、准备组会汇报
- 中期：建立文献数据库、撰写综述论文、参与学术会议
- 长期：跟踪临床试验、探索新方向、建立合作网络
```

### 4. Assets 目录
📁 **位置**: `backend/.openclaw/workspace-default/assets/literature/`

**目录结构**:
```
assets/literature/
├── README.md                           # 资产说明文档
└── figures/                            # 图表目录
    ├── PRISMA_flow_diagram.png         # (待生成)
    ├── citation_network.png            # (待生成)
    └── timeline_publications.png       # (待生成)
```

**预期生成的文件**（实际使用时会生成）:
```
assets/literature/
├── search_results_pubmed.json          # PubMed 检索结果
├── search_results_biorxiv.json         # bioRxiv 检索结果
├── search_results_aggregated.json      # 聚合结果
├── CRISPR_SCD_review.md                # Markdown 综述
├── CRISPR_SCD_review.pdf               # PDF 综述
├── citation_report.json                # 引用验证报告
└── figures/
    ├── PRISMA_flow_diagram.png
    ├── citation_network.png
    └── timeline_publications.png
```

### 5. Skills Snapshot
📄 **位置**: `backend/.openclaw/workspace-default/skills/SKILLS_SNAPSHOT.md`

**literature_review 条目**:
```markdown
### `literature_review` — 系统性文献综述（多数据库检索+引用验证+PDF生成）
- **source**: system
- **runtime_path**: skills/_system/literature_review/SKILL.md
- **triggers**: 文献综述, literature review, 系统性综述, 文献检索, 多数据库检索, PRISMA, meta分析
- **use_cases**: 进行系统性文献综述，支持多数据库检索（PubMed/arXiv/bioRxiv/Semantic Scholar），引用验证，生成专业格式的文献综述文档
- **preferred_routes** (仅供参考): mechanism_closure
```

### 6. Skill 源文件
📄 **位置**: `backend/skills/literature-review/SKILL.md` (23.8 KB)

完整的 skill 定义文档，包含：
- 使用场景和触发条件
- 7 个阶段的完整工作流程
- 多数据库检索策略
- PRISMA 系统性综述方法
- 引用验证和 PDF 生成
- 最佳实践和常见陷阱

## 快速访问

### 在 IDE 中打开
```bash
# TASK 文件
open "backend/.openclaw/workspace-default/memory/tasks/TASK_literature_CRISPR_demo.md"

# PACK 文件
open "backend/.openclaw/workspace-default/memory/packs/PACK_literature_CRISPR_mechanisms.md"

# Assets 目录
open "backend/.openclaw/workspace-default/assets/literature/"

# Skill 源文件
open "backend/skills/literature-review/SKILL.md"
```

### 在终端中查看
```bash
# 查看 TASK
cat backend/.openclaw/workspace-default/memory/tasks/TASK_literature_CRISPR_demo.md

# 查看 PACK
cat backend/.openclaw/workspace-default/memory/packs/PACK_literature_CRISPR_mechanisms.md

# 查看 Assets README
cat backend/.openclaw/workspace-default/assets/literature/README.md
```

## 文件说明

### TASK 文件特点
- ✓ 完整的 5 段式结构（meta, Claim, Evidence, Protocol, Runs, Missing）
- ✓ 详细的检索策略和筛选流程
- ✓ 质量评估和引用验证记录
- ✓ 清晰的缺失信息和下一步行动

### PACK 文件特点
- ✓ 交付物容器，聚合多个 TASK
- ✓ 关键发现摘要（takeaways）
- ✓ 完整的叙事骨架（narrative）
- ✓ 局限性和风险分析
- ✓ 短中长期行动计划

### Assets 目录特点
- ✓ 原始数据文件（JSON）
- ✓ 最终交付物（PDF, MD）
- ✓ 验证报告（citation_report.json）
- ✓ 可视化图表（PRISMA, 引用网络, 时间线）

## 与 Phase 5.1 的关系

这些演示文件展示了 literature-review skill 在 **Phase 5.1 科研闭环场景 1（文献机理闭环）** 中的实际应用：

1. **输入**: 用户请求"帮我做一个关于 CRISPR 治疗镰刀型细胞病的系统性文献综述"
2. **Skill 调用**: Agent 读取 `skills/_system/literature_review/SKILL.md`
3. **执行流程**: 多数据库检索 → PRISMA 筛选 → 质量评估 → 引用验证 → PDF 生成
4. **输出**:
   - TASK 文件记录完整过程
   - PACK 文件聚合交付物
   - Assets 目录存储原始数据和最终报告

## 下一步

如果你想看**真实的 API 调用和 Agent 执行**，需要：
1. 启动后端服务：`cd backend && python app.py`
2. 发送 chat 请求，触发 literature_review skill
3. Agent 会自动读取 skill 并执行文献综述流程

---

**生成时间**: 2026-03-14 18:06
**生成脚本**: `demo_literature_review.py`
