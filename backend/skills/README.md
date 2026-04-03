# Skills（技能插件）

每个技能一个文件夹：`skills/<skill_id>/SKILL.md`

## 设计原则

- **可插拔**：拖入文件夹即可新增能力
- **可审计**：SKILL.md 必须写清楚输入/输出/边界/质量检查
- **可抽象**：高频交付从对话中提炼为 skill，并更新 `skills/registry.json`
- **渐进式披露**：Agent 先看 SKILLS_SNAPSHOT 菜单，按需 read_file 读取完整 SKILL.md

## 新建技能

复制 `skills/_skill_template/` 作为起点。

## SKILL.md 统一结构

```
---
name: <skill_id>
description: <一句话描述>
allowed-tools: Read Write Edit Bash
license: Same as repository license
---

# <Skill Name>
## Overview
## When to Use This Skill
## When NOT to Use This Skill
## Required Inputs
## Expected Outputs
## Workflow (Step 1-N)
## Boundary with Sibling Skills
## Quality Checks
## Common Failure Modes
## Red Flags / Escalation Notes
## Example Patterns
## Example Requests
## Related Skills
```

## Skill 分类

| category | 说明 | 示例 |
|----------|------|------|
| analysis | 机理分析、证据整理、图句锚定 | mechanism_mapping, reactive_species_evidence_matrix |
| literature | 文献检索、拆解、综述 | paper_quad_summary, deepresearch_prompt |
| experiment | 实验设计、合成流程 | synthesis_checklist, experiment_matrix |
| word | 写作结构、R&D 提纲 | writing_outline_rd, results_to_report_structuring |
| ppt | 阶段汇报 PPT | stage_report_ppt |
| meta | 技能创建器 | research_skill_creator |
| foundation | 通用基础能力（PDF/图片/表格） | （待补充） |

## 目录结构

核心科研 skill（可选带 examples）：
```
skills/<skill_id>/
├── SKILL.md          ← 必须，Agent 运行时读取
└── examples/         ← 可选，Agent 按需 read_file
    ├── example_1.md
    └── example_2.md
```

Foundation skill（单文件即可）：
```
skills/<skill_id>/
└── SKILL.md
```

## 注册

每个 skill 必须在 `registry.json` 中注册，必填字段：`id`、`name`、`entry`。
