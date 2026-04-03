#!/usr/bin/env python3
"""
从 JSON 配置文件创建 Skill
用法: python create_skill_from_config.py <config.json>
"""

import json
import sys
from pathlib import Path

# 添加 backend 到 path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import config as cfg


def create_skill_from_config(config_path: Path):
    """从配置文件创建 skill"""

    # 读取配置
    config = json.loads(config_path.read_text(encoding="utf-8"))

    skill_id = config["skill_id"]
    skill_name = config["skill_name"]
    category = config.get("category", "experiment")
    when_to_use = config["when_to_use"]
    inputs_required = config["inputs_required"]
    outputs = config["outputs"]
    reads = config["reads"]
    writes = config["writes"]
    triggers = config["triggers"]
    execution_steps = config["execution_steps"]
    preferred_routes = config.get("preferred_routes", ["experiment"])
    prompt_extra = config.get("prompt_snippet_extra", "")

    # 生成 SKILL.md
    inputs_str = "\n".join(f"  - {inp}" for inp in inputs_required)
    outputs_str = "\n".join(f"  - {out}" for out in outputs)
    reads_str = "\n".join(f"  - `{r}`" for r in reads)
    writes_str = "\n".join(f"  - `{w}`" for w in writes)
    triggers_str = "\n".join(f'  - "{t}"' for t in triggers)
    steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(execution_steps))

    skill_content = f"""# Skill: {skill_id}

## 0) Skill meta
- `id`: {skill_id}
- `name`: {skill_name}
- `category`: {category}
- `when_to_use`: {when_to_use}
- `inputs_required`:
{inputs_str}
- `outputs`:
{outputs_str}
- `reads`:
{reads_str}
- `writes`:
{writes_str}
- `artifacts`: 无

## 1) Intent routing（触发关键词）
- triggers:
{triggers_str}

## 2) Context loading plan（读哪些文件）
- Layer1: `memory/identity/project.md`（项目背景）
- Layer2: `memory/timeline/days/<today>.md`（当天记录）
- Layer3: 相关 TASK/PACK 文件
- Skill-local: 用户提供的输入文件

## 3) Execution plan（执行步骤）
{steps_str}

## 4) Output contract（输出结构）
- **Deliverable**: {outputs[0] if outputs else "待定义"}
- **Missing info checklist**: 如果输入不足，列出缺失项
- **Memory patch**: 建议写入的文件路径

## 5) Memory patch rules（写回规则）
- **update day**: 在 `memory/timeline/days/<today>.md` 记录本次执行
- **update task**: 更新或创建相关 TASK 文件
- **create pack**: 如果产出可复用资产，考虑创建 PACK

## 6) Prompt snippet（给模型的固定提示词）

你正在执行 `{skill_id}` 技能。请严格遵守：
- 以证据为准：无 evidence 不下结论
- 以文件为准：把关键信息写回指定文件
- 输出按约定结构
- 如果输入不足，先列出缺失项，不要硬写
- 所有文件路径必须相对于 workspace 根目录
{f"- {prompt_extra}" if prompt_extra else ""}
"""

    # 写入文件
    workspace_dir = cfg.DEFAULT_WORKSPACE_DIR
    skill_dir = workspace_dir / "skills" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_content, encoding="utf-8")
    print(f"✅ 已创建: {skill_file}")

    # 更新 registry.json
    registry_file = workspace_dir / "skills" / "registry.json"
    if registry_file.exists():
        registry = json.loads(registry_file.read_text(encoding="utf-8"))
    else:
        registry = {"version": "0.1", "skills": []}

    # 检查是否已存在
    existing_ids = {s["id"] for s in registry["skills"]}
    if skill_id in existing_ids:
        print(f"⚠️  Skill '{skill_id}' 已存在于 registry，跳过注册")
    else:
        registry["skills"].append({
            "id": skill_id,
            "name": skill_name,
            "category": category,
            "entry": f"skills/{skill_id}/SKILL.md",
            "triggers": triggers,
            "use_cases": when_to_use,
            "preferred_routes": preferred_routes
        })
        registry_file.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✅ 已注册到: {registry_file}")

    print()
    print("🎉 Skill 创建完成！")
    print(f"Skill ID: {skill_id}")
    print(f"触发词: {', '.join(triggers)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python create_skill_from_config.py <config.json>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    try:
        create_skill_from_config(config_path)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
