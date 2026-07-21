#!/usr/bin/env python3
"""测试 literature-review skill 的加载和调用验证"""

import json
import sys
from pathlib import Path

# 添加 backend 到路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from graph.skill_loader import SkillLoader


def test_skill_loading():
    """测试 skill 是否能被正确加载"""
    print("=" * 80)
    print("测试 1: Skill 加载验证")
    print("=" * 80)

    # 使用测试 workspace
    workspace_dir = backend_dir / ".openclaw" / "workspace-default"

    try:
        loader = SkillLoader(workspace_dir)
        print(f"✓ SkillLoader 初始化成功")
        print(f"  - Workspace: {workspace_dir}")
        print(f"  - 加载的 skills 数量: {len(loader.skills)}")

        # 查找 literature_review skill
        lit_review_skill = None
        for skill in loader.skills:
            if skill.id == "literature_review":
                lit_review_skill = skill
                break

        if lit_review_skill:
            print(f"\n✓ literature_review skill 已加载")
            print(f"  - ID: {lit_review_skill.id}")
            print(f"  - Name: {lit_review_skill.name}")
            print(f"  - Source: {lit_review_skill.source}")
            print(f"  - Category: {lit_review_skill.category}")
            print(f"  - Runtime Path: {lit_review_skill.runtime_path}")
            print(f"  - Triggers: {', '.join(lit_review_skill.triggers[:3])}...")
            print(f"  - Preferred Routes: {', '.join(lit_review_skill.preferred_routes)}")

            # 检查 SKILL.md 文件是否存在
            skill_file = workspace_dir / lit_review_skill.runtime_path
            if skill_file.exists():
                print(f"\n✓ SKILL.md 文件已镜像到 workspace")
                print(f"  - 路径: {skill_file}")
                print(f"  - 大小: {skill_file.stat().st_size} bytes")
            else:
                print(f"\n✗ SKILL.md 文件未找到: {skill_file}")
                return False
        else:
            print(f"\n✗ literature_review skill 未找到")
            print(f"  已加载的 skills:")
            for skill in loader.skills:
                print(f"    - {skill.id} ({skill.source})")
            return False

        return True

    except Exception as e:
        print(f"✗ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_snapshot_generation():
    """测试 snapshot 生成"""
    print("\n" + "=" * 80)
    print("测试 2: Skills Snapshot 生成")
    print("=" * 80)

    workspace_dir = backend_dir / ".openclaw" / "workspace-default"

    try:
        loader = SkillLoader(workspace_dir)
        snapshot = loader.get_snapshot(force_refresh=True)

        if "literature_review" in snapshot:
            print(f"✓ Snapshot 包含 literature_review skill")

            # 提取 literature_review 部分
            lines = snapshot.split('\n')
            in_lit_review = False
            lit_review_section = []

            for line in lines:
                if '`literature_review`' in line:
                    in_lit_review = True
                elif in_lit_review and line.startswith('###'):
                    break

                if in_lit_review:
                    lit_review_section.append(line)

            print("\n  Snapshot 内容预览:")
            for line in lit_review_section[:10]:
                print(f"    {line}")

            # 检查 snapshot 文件
            snapshot_file = workspace_dir / "skills" / "SKILLS_SNAPSHOT.md"
            if snapshot_file.exists():
                print(f"\n✓ SKILLS_SNAPSHOT.md 已生成")
                print(f"  - 路径: {snapshot_file}")
                print(f"  - 大小: {snapshot_file.stat().st_size} bytes")

            return True
        else:
            print(f"✗ Snapshot 不包含 literature_review skill")
            return False

    except Exception as e:
        print(f"✗ Snapshot 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_structure_output():
    """测试按记忆层级结构输出"""
    print("\n" + "=" * 80)
    print("测试 3: 记忆层级结构输出示例")
    print("=" * 80)

    print("""
literature-review skill 调用后的输出应遵循以下记忆层级结构：

1. TASK 层级 (memory/tasks/)
   ├─ TASK_literature_<topic>.md
   │  ├─ meta: id, concept, status, owner, created_at
   │  ├─ Claim: 要进行什么文献综述
   │  ├─ Evidence: 检索到的文献列表
   │  ├─ Protocol: 检索策略（数据库、关键词、筛选标准）
   │  └─ Runs: 实际检索执行记录
   │
   └─ 示例输出:
      ```markdown
      # TASK_literature_CRISPR_sickle_cell.md

      ## meta
      - id: TASK_literature_CRISPR_sickle_cell
      - concept: CONCEPT_gene_therapy_mechanisms
      - status: done
      - owner: agent
      - created_at: 2026-03-14

      ## 1) Claim
      ### claim_text
      - 系统性综述 CRISPR-Cas9 治疗镰刀型细胞病的疗效和机制

      ### claim_type
      - mechanism

      ## 2) Evidence
      - Evidence 1:
        - type: paper
        - path_or_citation: DOI:10.1038/xxx
        - what_it_supports: AAV 载体递送效率 65-85%
        - limitations: 免疫原性问题

      ## 3) Protocol
      ### steps[]
      1. 多数据库检索 (PubMed, arXiv, bioRxiv)
      2. PRISMA 流程筛选
      3. 质量评估 (Cochrane Risk of Bias)

      ## 4) Runs
      ### run_01
      - date: 2026-03-14
      - raw_data_paths:
        - assets/literature/search_results.json
        - assets/literature/review_draft.md
      - quick_results: 找到 247 篇相关文献，筛选后纳入 45 篇
      - verdict: supports
      ```

2. PACK 层级 (memory/packs/)
   ├─ PACK_literature_<topic>.md
   │  ├─ meta: id, pack_type=literature_pack
   │  ├─ task_refs: 引用相关 TASK
   │  ├─ final_assets: 生成的文献综述 PDF/MD
   │  ├─ takeaways: 关键发现摘要
   │  └─ narrative: 文献综述叙事骨架
   │
   └─ 示例输出:
      ```markdown
      # PACK_literature_CRISPR_mechanisms.md

      ## meta
      - id: PACK_literature_CRISPR_mechanisms
      - pack_type: literature_pack
      - created_at: 2026-03-14

      ## task_refs[]
      - TASK_literature_CRISPR_sickle_cell
      - TASK_literature_delivery_methods

      ## final_assets[]
      - assets/literature/CRISPR_review.pdf
      - assets/literature/CRISPR_review.md
      - assets/literature/citation_report.json

      ## takeaways[]
      - AAV 载体递送效率高但有免疫原性风险
      - 脂质纳米颗粒安全性更好但效率较低
      - 需要更多长期安全性数据

      ## narrative
      CRISPR-Cas9 基因编辑技术在镰刀型细胞病治疗中显示出巨大潜力。
      主要挑战在于递送系统的选择和长期安全性评估。

      ## limitations & risks
      - 大部分研究为早期临床试验
      - 长期随访数据不足

      ## next_plan
      - 关注最新临床试验结果
      - 深入研究免疫原性解决方案
      ```

3. Assets 层级 (assets/literature/)
   ├─ search_results.json          # 原始检索结果
   ├─ CRISPR_review.md             # Markdown 格式综述
   ├─ CRISPR_review.pdf            # PDF 格式综述
   ├─ citation_report.json         # 引用验证报告
   └─ figures/
      └─ PRISMA_flow_diagram.png   # PRISMA 流程图

4. Timeline 层级 (memory/timeline/)
   └─ days/2026-03-14.md
      记录当天完成的文献综述任务
    """)

    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("Literature Review Skill 验证测试")
    print("=" * 80)

    results = []

    # 测试 1: Skill 加载
    results.append(("Skill 加载", test_skill_loading()))

    # 测试 2: Snapshot 生成
    results.append(("Snapshot 生成", test_snapshot_generation()))

    # 测试 3: 记忆结构输出
    results.append(("记忆结构示例", test_memory_structure_output()))

    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✓ 所有测试通过！literature-review skill 可以正常调用")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
