#!/usr/bin/env python3
"""
交互式 Skill 创建工具
用于快速创建和注册新的 workspace 私有 skill
"""

import json
import sys
from pathlib import Path
from typing import Optional

# 添加 backend 到 path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import config as cfg


def prompt_input(question: str, default: Optional[str] = None) -> str:
    """带默认值的输入提示"""
    if default:
        answer = input(f"{question} [{default}]: ").strip()
        return answer if answer else default
    return input(f"{question}: ").strip()


def prompt_list(question: str, example: str = "") -> list[str]:
    """输入列表（逗号分隔）"""
    hint = f" (逗号分隔，例如: {example})" if example else " (逗号分隔)"
    answer = input(f"{question}{hint}: ").strip()
    return [item.strip() for item in answer.split(",") if item.strip()]


def create_skill_interactive():
    """交互式创建 skill"""
    print("=" * 60)
    print("科研技能创建器 - 交互式模式")
    print("=" * 60)
    print()

    # 1. 基本信息
    print("📋 第 1 步：基本信息")
    print("-" * 60)
    skill_id = prompt_input("Skill ID (英文小写+下划线)", "my_custom_skill")
    skill_name = prompt_input("Skill 名称 (中文描述)", "我的自定义技能")
    category = prompt_input(
        "分类 (experiment/literature/analysis/ppt/word/meta)",
        "experiment"
    )
    print()

    # 2. 触发条件
    print("🎯 第 2 步：触发条件")
    print("-" * 60)
    print("什么时候应该使用这个 skill？")
    when_to_use = prompt_input("使用场景描述")
    triggers = prompt_list(
        "触发关键词",
        "实验 checklist, SOP 整理"
    )
    print()

    # 3. 输入输出
    print("📥 第 3 步：输入输出")
    print("-" * 60)
    inputs_required = prompt_list(
        "需要哪些输入",
        "实验类型, 原理描述, SOP文档"
    )
    outputs = prompt_list(
        "会产出什么",
        "Markdown checklist, 缺失对照清单"
    )
    print()

    # 4. 文件读写
    print("📂 第 4 步：文件读写")
    print("-" * 60)
    reads = prompt_list(
        "需要读取哪些文件",
        "memory/identity/project.md, memory/tasks/TASK_*"
    )
    writes = prompt_list(
        "会写入哪些文件",
        "memory/tasks/TASK_experiment_*.md"
    )
    print()

    # 5. 执行步骤
    print("⚙️  第 5 步：执行步骤")
    print("-" * 60)
    print("请描述执行步骤（每行一个步骤，输入空行结束）：")
    execution_steps = []
    step_num = 1
    while True:
        step = input(f"  {step_num}. ").strip()
        if not step:
            break
        execution_steps.append(step)
        step_num += 1
    print()

    # 6. 路由偏好
    print("🛤️  第 6 步：路由偏好")
    print("-" * 60)
    preferred_routes = prompt_list(
        "推荐在哪些工作语境使用",
        "experiment, mechanism_closure"
    )
    print()

    # 7. 生成 SKILL.md
    print("=" * 60)
    print("生成 SKILL.md...")
    print("=" * 60)

    skill_content = generate_skill_md(
        skill_id=skill_id,
        skill_name=skill_name,
        when_to_use=when_to_use,
        inputs_required=inputs_required,
        outputs=outputs,
        reads=reads,
        writes=writes,
        triggers=triggers,
        execution_steps=execution_steps,
        category=category
    )

    # 8. 确认并写入
    print("\n预览 SKILL.md 内容：")
    print("-" * 60)
    print(skill_content[:500] + "...\n")

    confirm = prompt_input("确认创建？(y/n)", "y")
    if confirm.lower() != "y":
        print("❌ 已取消")
        return

    # 9. 写入文件
    workspace_dir = cfg.DEFAULT_WORKSPACE_DIR
    skill_dir = workspace_dir / "skills" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_content, encoding="utf-8")
    print(f"✅ 已创建: {skill_file}")

    # 10. 更新 registry.json
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
    print("=" * 60)
    print("🎉 Skill 创建完成！")
    print("=" * 60)
    print(f"Skill ID: {skill_id}")
    print(f"位置: {skill_file}")
    print(f"触发词: {', '.join(triggers)}")
    print()
    print("💡 测试提示词:")
    print(f"   \"{triggers[0] if triggers else skill_name}\"")
    print()


def generate_skill_md(
    skill_id: str,
    skill_name: str,
    when_to_use: str,
    inputs_required: list[str],
    outputs: list[str],
    reads: list[str],
    writes: list[str],
    triggers: list[str],
    execution_steps: list[str],
    category: str
) -> str:
    """生成 SKILL.md 内容"""

    inputs_str = "\n".join(f"  - {inp}" for inp in inputs_required)
    outputs_str = "\n".join(f"  - {out}" for out in outputs)
    reads_str = "\n".join(f"  - `{r}`" for r in reads)
    writes_str = "\n".join(f"  - `{w}`" for w in writes)
    triggers_str = "\n".join(f'  - "{t}"' for t in triggers)
    steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(execution_steps))

    return f"""# Skill: {skill_id}

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
"""


if __name__ == "__main__":
    try:
        create_skill_interactive()
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
