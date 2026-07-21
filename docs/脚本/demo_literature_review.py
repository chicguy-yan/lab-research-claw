#!/usr/bin/env python3
"""演示 literature-review skill 的实际使用和输出"""

import sys
from pathlib import Path
from datetime import datetime

# 添加 backend 到路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from graph.skill_loader import SkillLoader


def create_demo_task():
    """创建一个演示用的 TASK 文件"""
    workspace_dir = backend_dir / ".openclaw" / "workspace-default"
    tasks_dir = workspace_dir / "memory" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    task_content = f"""# TASK_literature_CRISPR_demo.md

> 演示 literature-review skill 的输出格式

## meta
- id: TASK_literature_CRISPR_demo
- concept: CONCEPT_gene_therapy_mechanisms
- status: done
- owner: agent
- created_at: {datetime.now().strftime('%Y-%m-%d')}
- last_updated: {datetime.now().strftime('%Y-%m-%d')}

---

## 1) Claim（要证明什么）

### claim_text
- 系统性综述 CRISPR-Cas9 治疗镰刀型细胞病的疗效和机制

### claim_type
- mechanism

### evidence_required（判据引用）
- 多数据库检索结果（PubMed, arXiv, bioRxiv）
- 质量评估（Cochrane Risk of Bias）
- 至少 30 篇高质量文献
- 引用验证通过率 > 95%

---

## 2) Evidence（目前有什么证据）

- Evidence 1:
  - type: paper
  - path_or_citation: DOI:10.1038/s41591-2023-02378-5
  - what_it_supports: AAV 载体递送效率 65-85%，在临床试验中显示良好疗效
  - limitations: 免疫原性问题，部分患者出现抗体反应；样本量较小（n=45）

- Evidence 2:
  - type: paper
  - path_or_citation: DOI:10.1016/j.cell.2023.05.012
  - what_it_supports: 脂质纳米颗粒（LNP）安全性更好，无明显免疫反应
  - limitations: 递送效率较低（40-60%），需要多次给药

- Evidence 3:
  - type: paper
  - path_or_citation: DOI:10.1056/NEJMoa2301665
  - what_it_supports: 长期随访（5年）显示持续疗效，HbF 水平维持在 20-30%
  - limitations: 仅针对成人患者，儿童数据不足

- Evidence 4:
  - type: paper
  - path_or_citation: DOI:10.1126/science.abq7960
  - what_it_supports: 脱靶效应发生率 < 0.1%，安全性可接受
  - limitations: 检测方法灵敏度限制，可能存在未检出的低频脱靶

---

## 3) Protocol（怎么做）

### steps[]
1. **定义研究问题**（PICO 框架）
   - Population: 镰刀型细胞病患者（儿童和成人）
   - Intervention: CRISPR-Cas9 基因编辑治疗
   - Comparison: 标准治疗（输血、羟基脲）
   - Outcome: 疗效、安全性、生活质量

2. **制定检索策略**
   - 关键词: "CRISPR", "Cas9", "sickle cell disease", "SCD", "gene editing", "gene therapy"
   - 布尔运算符: ("CRISPR" OR "Cas9") AND ("sickle cell" OR "SCD")
   - 时间范围: 2015-2024

3. **多数据库检索**
   - PubMed: 使用 gget skill
   - bioRxiv: 使用 gget skill
   - arXiv: 直接 API 访问
   - Semantic Scholar: API 访问

4. **PRISMA 流程筛选**
   - 标题筛选: 排除明显不相关
   - 摘要筛选: 应用纳入/排除标准
   - 全文筛选: 详细评估质量

5. **质量评估**
   - RCT: Cochrane Risk of Bias tool
   - 观察性研究: Newcastle-Ottawa Scale
   - 评分: High/Moderate/Low/Very Low

6. **数据提取和主题综合**
   - 提取: 研究设计、样本量、干预措施、结果、局限性
   - 主题: 递送系统、疗效、安全性、长期随访

7. **引用验证**
   - 使用 verify_citations.py 验证所有 DOI
   - 确保引用格式一致（Nature 格式）

8. **生成 PDF**
   - 使用 generate_pdf.py
   - 包含 PRISMA 流程图

### checkpoints[]
- CP1: 检索策略验证（预检索 50 篇，评估相关性 > 80%）
- CP2: 筛选后文献数量（目标 30-50 篇高质量文献）
- CP3: 质量评估完成（至少 70% 为 High/Moderate 质量）
- CP4: 引用验证通过（通过率 > 95%）

### controls[]
- 纳入标准:
  - 时间: 2015-2024 年
  - 语言: 英文
  - 类型: 同行评审期刊、临床试验、观察性研究
  - 主题: 直接相关 CRISPR-Cas9 治疗镰刀型细胞病

- 排除标准:
  - 综述文章（除非是系统性综述）
  - 病例报告（n < 5）
  - 会议摘要
  - 体外研究（除非与临床相关）
  - 动物模型（除非与临床转化相关）

### contamination_risks
- 发表偏倚: 阳性结果更容易发表
- 语言偏倚: 仅纳入英文文献
- 数据库偏倚: 可能遗漏灰色文献
- 时间偏倚: 最新研究可能未发表

---

## 4) Runs（一次或多次实际执行）

### run_01
- date: {datetime.now().strftime('%Y-%m-%d')}
- raw_data_paths[]:
  - assets/literature/search_results_pubmed.json
  - assets/literature/search_results_biorxiv.json
  - assets/literature/search_results_aggregated.json
  - assets/literature/CRISPR_SCD_review_draft.md
  - assets/literature/citation_report.json
  - assets/literature/figures/PRISMA_flow_diagram.png

- quick_results:
  - **PubMed 检索**: 247 篇初始结果
    - 标题筛选后: 156 篇
    - 摘要筛选后: 68 篇
    - 全文筛选后: 35 篇

  - **bioRxiv 检索**: 58 篇初始结果
    - 筛选后: 10 篇（其中 3 篇已发表在期刊）

  - **arXiv 检索**: 12 篇初始结果
    - 筛选后: 2 篇（计算生物学方法）

  - **去重后总计**: 45 篇高质量文献

  - **质量评估**:
    - High quality: 18 篇 (40%)
    - Moderate quality: 22 篇 (49%)
    - Low quality: 5 篇 (11%)

  - **引用验证**: 45/45 通过 (100%)

  - **主题分布**:
    - 递送系统: 15 篇 (AAV: 9, LNP: 6)
    - 临床疗效: 12 篇
    - 安全性评估: 10 篇
    - 长期随访: 5 篇
    - 机制研究: 3 篇

- verdict: supports
  - 证据充分支持 CRISPR-Cas9 治疗镰刀型细胞病的可行性
  - AAV 和 LNP 两种递送系统各有优劣
  - 短期疗效明确，长期安全性需要更多数据

- next_action:
  - 生成最终 PDF 报告
  - 更新 PACK_literature_CRISPR_mechanisms
  - 准备组会汇报材料
  - 关注 ClinicalTrials.gov 最新试验进展

---

## 5) Missing（缺什么信息）

- field: 长期随访数据（> 10 年）
  - why_needed: 评估基因编辑的长期安全性和持续疗效
  - how_to_provide: 持续关注已发表试验的长期随访报告

- field: 儿童患者数据
  - why_needed: 评估在不同年龄段的疗效和安全性
  - how_to_provide: 关注儿科临床试验（NCT04774536, NCT05329649）

- field: 成本效益分析
  - why_needed: 评估治疗的经济可行性
  - how_to_provide: 查找卫生经济学研究

- field: 不同种族人群数据
  - why_needed: 评估治疗在不同遗传背景下的效果
  - how_to_provide: 关注多中心国际临床试验

- field: 脱靶效应长期监测
  - why_needed: 评估基因编辑的长期安全性
  - how_to_provide: 全基因组测序长期随访数据
"""

    task_file = tasks_dir / "TASK_literature_CRISPR_demo.md"
    task_file.write_text(task_content, encoding="utf-8")

    return task_file


def create_demo_pack():
    """创建一个演示用的 PACK 文件"""
    workspace_dir = backend_dir / ".openclaw" / "workspace-default"
    packs_dir = workspace_dir / "memory" / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)

    pack_content = f"""# PACK_literature_CRISPR_mechanisms.md

> 演示 literature-review skill 产出的 PACK 格式

## meta
- id: PACK_literature_CRISPR_mechanisms
- pack_type: literature_pack
- created_at: {datetime.now().strftime('%Y-%m-%d')}
- time_range: 2015-01-01 ~ 2024-12-31

---

## task_refs[]
- TASK_literature_CRISPR_demo
- TASK_literature_delivery_methods (待创建)
- TASK_literature_safety_assessment (待创建)

---

## final_assets[]
- assets/literature/CRISPR_SCD_review.pdf
- assets/literature/CRISPR_SCD_review.md
- assets/literature/citation_report.json
- assets/literature/figures/PRISMA_flow_diagram.png
- assets/literature/figures/citation_network.png
- assets/literature/figures/timeline_publications.png
- assets/literature/search_results_aggregated.json

---

## takeaways[]（每个资产 1 句话）

### 关键发现
1. **AAV 载体递送效率高（65-85%）但存在免疫原性风险**
   - 9 篇研究报告了 AAV 载体的高效递送
   - 3 篇研究发现抗体反应问题
   - 需要免疫抑制或载体改造策略

2. **脂质纳米颗粒（LNP）安全性更好但效率较低（40-60%）**
   - 6 篇研究使用 LNP 递送系统
   - 无明显免疫反应报告
   - 可能需要多次给药

3. **临床试验显示初步疗效，HbF 水平提升 20-30%**
   - 12 篇临床研究报告疗效数据
   - 大部分患者症状改善
   - 输血需求显著降低

4. **长期随访（5 年）显示持续疗效，但数据有限**
   - 仅 5 篇研究报告长期随访
   - 疗效持续，无明显衰减
   - 需要更长期（> 10 年）数据

5. **脱靶效应发生率低（< 0.1%），但监测方法有限**
   - 10 篇研究评估脱靶效应
   - 检测灵敏度限制可能低估风险
   - 需要全基因组测序长期监测

6. **主要挑战：递送系统优化、长期安全性评估、成本控制**
   - 递送效率和安全性的平衡
   - 长期随访数据不足
   - 治疗成本高昂（> $100 万美元/人）

---

## narrative（给论文/组会的叙事骨架）

### 背景
镰刀型细胞病（SCD）是一种严重的遗传性血液病，影响全球数百万患者。
传统治疗方法（输血、羟基脲）只能缓解症状，无法根治。
CRISPR-Cas9 基因编辑技术为根治性治疗提供了新希望。

### 当前进展
过去 10 年（2015-2024），CRISPR-Cas9 治疗 SCD 的研究取得显著进展：
- 临床前研究证实了技术可行性
- 多项临床试验（Phase I/II）显示初步疗效
- 两种主要递送系统（AAV 和 LNP）各有优劣

### 递送系统比较
**AAV 载体**：
- 优势：高效递送（65-85%），单次给药
- 劣势：免疫原性问题，部分患者产生抗体
- 适用：免疫状态良好的患者

**脂质纳米颗粒（LNP）**：
- 优势：安全性好，无免疫反应
- 劣势：效率较低（40-60%），可能需要多次给药
- 适用：免疫敏感患者

### 疗效评估
临床试验数据显示：
- HbF 水平提升 20-30%
- 症状显著改善（疼痛发作减少 70-80%）
- 输血需求降低 80-90%
- 生活质量明显提高

### 安全性考量
短期安全性良好：
- 脱靶效应发生率低（< 0.1%）
- 无严重不良事件报告
- 大部分副作用为轻度和可逆

长期安全性需要更多数据：
- 目前最长随访 5 年
- 需要 10-20 年长期监测
- 关注潜在的迟发性效应

### 主要挑战
1. **递送系统优化**：平衡效率和安全性
2. **长期安全性评估**：需要更长期随访数据
3. **成本控制**：降低治疗成本，提高可及性
4. **监管审批**：建立基因编辑治疗的监管框架
5. **伦理考量**：生殖细胞编辑的伦理问题

### 未来方向
1. **新型递送系统**：外泌体、纳米材料、病毒样颗粒
2. **精准编辑**：提高编辑效率，降低脱靶
3. **个体化治疗**：根据患者基因型定制方案
4. **联合治疗**：基因编辑 + 药物治疗
5. **预防性治疗**：新生儿筛查 + 早期干预

---

## limitations & risks

### 研究局限性
1. **样本量小**：大部分研究 n < 50
2. **随访时间短**：最长 5 年，缺乏长期数据
3. **种族多样性不足**：主要为欧美人群，缺乏非洲、亚洲数据
4. **发表偏倚**：阳性结果更容易发表
5. **异质性高**：不同研究使用不同方法，难以直接比较

### 临床风险
1. **脱靶效应**：可能导致意外基因突变
2. **免疫反应**：AAV 载体可能引发免疫反应
3. **编辑效率不足**：部分患者疗效不佳
4. **长期安全性未知**：可能存在迟发性效应
5. **生殖细胞传递**：理论上可能影响后代（虽然概率极低）

### 社会经济风险
1. **成本高昂**：单次治疗 > $100 万美元
2. **可及性差**：发展中国家难以负担
3. **医疗资源不均**：加剧健康不平等
4. **保险覆盖**：保险公司可能拒绝覆盖
5. **伦理争议**：基因编辑的社会接受度

---

## next_plan

### 短期（3-6 个月）
1. **持续文献监测**
   - 每月更新 PubMed 检索
   - 关注 ClinicalTrials.gov 新试验
   - 订阅相关期刊 TOC alerts

2. **深入分析特定主题**
   - 免疫原性解决方案
   - 新型递送系统
   - 成本效益分析

3. **准备组会汇报**
   - 使用 mechanism_stage_report skill
   - 生成 PPT 结构
   - 准备答辩材料

### 中期（6-12 个月）
1. **建立文献数据库**
   - 使用 Zotero/Mendeley 管理
   - 建立主题标签系统
   - 定期更新和维护

2. **撰写综述论文**
   - 投稿目标：Nature Reviews Drug Discovery / Blood
   - 与实验室 PI 讨论合作
   - 联系领域专家审稿

3. **参与学术会议**
   - ASH (American Society of Hematology)
   - ASGCT (American Society of Gene & Cell Therapy)
   - 准备海报/口头报告

### 长期（1-2 年）
1. **跟踪临床试验进展**
   - 关注 Phase III 试验结果
   - 监测 FDA/EMA 审批进展
   - 分析真实世界数据

2. **探索新研究方向**
   - 基因编辑 + 免疫治疗
   - 人工智能辅助设计
   - 单细胞测序监测

3. **建立合作网络**
   - 联系临床试验中心
   - 与生物技术公司合作
   - 参与国际多中心研究
"""

    pack_file = packs_dir / "PACK_literature_CRISPR_mechanisms.md"
    pack_file.write_text(pack_content, encoding="utf-8")

    return pack_file


def create_demo_assets():
    """创建演示用的 assets 目录结构"""
    workspace_dir = backend_dir / ".openclaw" / "workspace-default"
    assets_dir = workspace_dir / "assets" / "literature"
    assets_dir.mkdir(parents=True, exist_ok=True)

    figures_dir = assets_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # 创建一个简单的 README
    readme_content = f"""# Literature Review Assets

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

```
assets/literature/
├── search_results_pubmed.json          # PubMed 原始检索结果
├── search_results_biorxiv.json         # bioRxiv 原始检索结果
├── search_results_aggregated.json      # 聚合去重后的结果
├── CRISPR_SCD_review.md                # Markdown 格式综述
├── CRISPR_SCD_review.pdf               # PDF 格式综述
├── citation_report.json                # 引用验证报告
└── figures/
    ├── PRISMA_flow_diagram.png         # PRISMA 流程图
    ├── citation_network.png            # 引用网络图
    └── timeline_publications.png       # 发表时间线
```

## 文件说明

### 检索结果文件
- **search_results_pubmed.json**: PubMed 数据库检索的原始 JSON 结果
- **search_results_biorxiv.json**: bioRxiv 预印本服务器检索结果
- **search_results_aggregated.json**: 合并、去重、排序后的最终结果

### 综述文档
- **CRISPR_SCD_review.md**: Markdown 格式的文献综述，包含：
  - 摘要
  - 引言
  - 方法（检索策略、筛选流程、质量评估）
  - 结果（按主题组织）
  - 讨论
  - 结论
  - 参考文献

- **CRISPR_SCD_review.pdf**: 专业格式的 PDF 文档，使用 pandoc 生成

### 验证报告
- **citation_report.json**: 引用验证详细报告，包含：
  - 每个 DOI 的验证状态
  - CrossRef 元数据
  - 格式化的引用文本
  - 错误和警告信息

### 图表
- **PRISMA_flow_diagram.png**: 系统性综述的 PRISMA 流程图
- **citation_network.png**: 文献引用网络可视化
- **timeline_publications.png**: 发表时间线和趋势分析

## 使用说明

这些文件由 literature-review skill 自动生成。

要重新生成这些文件，请使用：
```bash
python scripts/literature-review/generate_pdf.py CRISPR_SCD_review.md
python scripts/literature-review/verify_citations.py CRISPR_SCD_review.md
```
"""

    readme_file = assets_dir / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")

    return assets_dir


def main():
    """生成演示文件"""
    print("=" * 80)
    print("Literature Review Skill 演示文件生成")
    print("=" * 80)

    print("\n正在生成演示文件...")

    # 生成 TASK
    task_file = create_demo_task()
    print(f"✓ 已生成 TASK 文件: {task_file}")

    # 生成 PACK
    pack_file = create_demo_pack()
    print(f"✓ 已生成 PACK 文件: {pack_file}")

    # 生成 Assets 目录
    assets_dir = create_demo_assets()
    print(f"✓ 已生成 Assets 目录: {assets_dir}")

    print("\n" + "=" * 80)
    print("演示文件生成完成！")
    print("=" * 80)

    print("\n生成的文件位置：")
    print(f"1. TASK:   {task_file}")
    print(f"2. PACK:   {pack_file}")
    print(f"3. Assets: {assets_dir}")

    print("\n这些文件展示了 literature-review skill 的输出格式：")
    print("- TASK 文件包含完整的文献综述任务记录")
    print("- PACK 文件包含文献综述的交付物和叙事骨架")
    print("- Assets 目录包含原始数据、PDF 报告和图表")

    print("\n你可以查看这些文件来了解 skill 的实际输出。")


if __name__ == "__main__":
    main()
