# Phase 5: Skills 加载系统设计

**版本**: v1.0 | **日期**: 2026-03-09
**项目**: Experimental-Research-OpenClaw

---

## 一、Skills 系统概述

### 1.1 设计理念

Skills 遵循 **Instruction-following** (指令遵循) 范式:
- Skill 是教会 Agent 如何使用 Core Tools 的"说明书"
- 不是预先写好的 Python 函数
- 支持"拖入即用"的扩展方式

### 1.2 核心流程

```
1. Bootstrap 阶段: 扫描 skills/ → 生成 SKILLS_SNAPSHOT.md
2. System Prompt 注入: SKILLS_SNAPSHOT 作为可用技能清单
3. Runtime 执行: Agent 通过 read_file 读取完整 SKILL.md → 按说明执行
```

---

## 二、Skills 目录结构

### 2.1 标准目录结构

```
backend/
├── skills/                          # 所有 Skills 根目录
│   ├── stage_report_ppt/            # 阶段汇报 PPT 生成
│   │   ├── SKILL.md                 # 技能说明书 (必需)
│   │   ├── examples/                # 示例 (可选)
│   │   └── templates/               # 模板 (可选)
│   ├── synthesis_checklist/         # 合成 checklist 生成
│   │   └── SKILL.md
│   ├── mechanism_audit/             # 机理证据链审计
│   │   └── SKILL.md
│   ├── characterization_audit/      # 表征审计
│   │   └── SKILL.md
│   ├── writing_outline/             # 写作大纲生成
│   │   └── SKILL.md
│   ├── experiment_matrix/           # 实验矩阵设计
│   │   └── SKILL.md
│   └── csv_kobs_fit/                # CSV 数据拟合作图
│       └── SKILL.md
└── SKILLS_SNAPSHOT.md               # 自动生成的技能清单
```

### 2.2 SKILL.md 标准格式

```markdown
---
name: stage_report_ppt
description: 生成阶段汇报 PPT 的页级结构和中心句
version: 1.0
author: system
tags: [reporting, ppt, synthesis]
---

# Stage Report PPT Skill

## 使用场景
当用户请求"准备第N次阶段汇报"或提供 `assets/ppt_pack/Rxx_YYYYMMDD/` 路径时使用

## 输入要求
- 阶段编号 (如 R06)
- 素材路径: `assets/ppt_pack/Rxx_YYYYMMDD/`
- 时间范围 (如"最近两周")

## 执行步骤

### Step 1: 读取上一期汇报
```
使用 read_file 读取 memory/timeline/stage_reports/上一期.md
提取: 上次汇报的关键结论、遗留问题
```

### Step 2: 读取时间范围内的周报和日志
```
使用 read_file 读取 memory/timeline/weeks/YYYY-Wxx.md (最近2周)
使用 read_file 读取 memory/timeline/days/YYYY-MM-DD.md (关键实验日)
提取: 本期完成的实验、关键数据、遇到的问题
```

### Step 3: 读取相关 Tasks 和 Packs
```
使用 read_file 读取 memory/tasks/TASK_*.md (本期相关任务)
使用 read_file 读取 memory/packs/PACK_mechanism_*.md (机理证据包)
提取: 实验结论、证据链、图表路径
```

### Step 4: 分析素材文件
```
使用 list_directory 列出 assets/ppt_pack/Rxx_YYYYMMDD/
使用 python_repl 分析图片尺寸、CSV 数据
生成素材清单
```

### Step 5: 生成 PPT 结构
```
按照模板生成:
- 封面页
- 目录页
- 背景与目标 (1-2页)
- 本期工作 (3-5页)
- 关键数据与结论 (2-3页)
- 下一步计划 (1页)
- 致谢页
```

### Step 6: 写入 Pack
```
使用 write_file 写入 memory/packs/PACK_stage_report_Rxx.md
包含:
- PPT 页级结构
- 每页中心句
- 素材路径映射
- WPS AI 提示词
```

## 输出格式

### PPT 结构示例
```markdown
## 第6次阶段汇报 (R06)

### 页面结构

#### P1: 封面
- 标题: Co3O4/Ce-Co3O4 激活 NaClO2 降解 SMX 研究进展
- 副标题: 第6次阶段汇报 (2025.11.09-2025.11.23)
- 汇报人: 杨雨晴

#### P2: 目录
1. 背景与目标
2. 本期工作
3. 关键数据与结论
4. 下一步计划

#### P3: 背景与目标
- 中心句: 验证 Ce 掺杂对 Co3O4 激活 NaClO2 的选择性氧化能力的影响
- 素材: [项目北极星](memory/identity/project.md)

#### P4: 本期工作 - 材料合成
- 中心句: 完成 0.5Ce-Co3O4 的水热合成与煅烧
- 素材: [合成照片](assets/ppt_pack/R06_20251123/synthesis_photos.png)
- 数据: [XRD谱图](assets/ppt_pack/R06_20251123/xrd_comparison.png)

#### P5: 本期工作 - DPD 显色实验
- 中心句: DPD 显色证实 ClO2 生成,0.5Ce-Co3O4 显色强度高于 Co3O4
- 素材: [DPD显色照片](assets/ppt_pack/R06_20251123/dpd_color.jpg)
- 数据: [吸光度对比](assets/ppt_pack/R06_20251123/dpd_absorbance.csv)

...
```

### WPS AI 提示词
```
请根据以下结构生成 PPT:
[粘贴上述页面结构]

要求:
1. 使用学术风格模板
2. 每页不超过3个要点
3. 图表占比60%以上
4. 使用蓝色主题
```

## 注意事项
1. 必须引用 memory 中的实际文件,不要脑补
2. 素材路径必须是 assets/ 下的真实路径
3. 如果缺少关键信息,列出 Missing checklist
4. 生成的 Pack 必须包含溯源路径

## 相关 Skills
- synthesis_checklist: 合成流程整理
- mechanism_audit: 机理证据链审计
```

---

## 三、Bootstrap 阶段: SKILLS_SNAPSHOT 生成

### 3.1 Skills Scanner 实现

**文件**: `backend/graph/skills_scanner.py`

```python
from pathlib import Path
import yaml
from typing import List, Dict

class SkillsScanner:
    """扫描 skills/ 目录,生成 SKILLS_SNAPSHOT.md"""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir

    def scan(self) -> List[Dict]:
        """扫描所有 SKILL.md,提取 Frontmatter"""
        skills = []

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            # 解析 Frontmatter
            metadata = self._parse_frontmatter(skill_md)
            metadata["location"] = str(skill_md.relative_to(self.skills_dir.parent))

            skills.append(metadata)

        return skills

    def _parse_frontmatter(self, skill_md: Path) -> Dict:
        """解析 SKILL.md 的 Frontmatter"""
        content = skill_md.read_text(encoding="utf-8")

        # 提取 YAML Frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                return frontmatter

        return {}

    def generate_snapshot(self, skills: List[Dict]) -> str:
        """生成 SKILLS_SNAPSHOT.md"""
        lines = [
            "# Available Skills",
            "",
            "This file is auto-generated. Do not edit manually.",
            "",
            "## Skills List",
            ""
        ]

        for skill in skills:
            lines.append(f"### {skill['name']}")
            lines.append(f"- **Description**: {skill.get('description', 'N/A')}")
            lines.append(f"- **Version**: {skill.get('version', '1.0')}")
            lines.append(f"- **Location**: `{skill['location']}`")
            lines.append(f"- **Tags**: {', '.join(skill.get('tags', []))}")
            lines.append("")

        lines.append("## Usage")
        lines.append("")
        lines.append("To use a skill:")
        lines.append("1. Identify the skill from the list above")
        lines.append("2. Use `read_file(location)` to read the full SKILL.md")
        lines.append("3. Follow the instructions in the SKILL.md")
        lines.append("")

        return "\n".join(lines)
```

### 3.2 启动时自动生成

**在 `app.py` 中**:

```python
from graph.skills_scanner import SkillsScanner

# 启动时生成 SKILLS_SNAPSHOT
skills_dir = Path("backend/skills")
scanner = SkillsScanner(skills_dir)
skills = scanner.scan()
snapshot_content = scanner.generate_snapshot(skills)

# 写入 SKILLS_SNAPSHOT.md
snapshot_path = Path("backend/SKILLS_SNAPSHOT.md")
snapshot_path.write_text(snapshot_content, encoding="utf-8")

print(f"✅ Generated SKILLS_SNAPSHOT.md with {len(skills)} skills")
```

---

## 四、Runtime 阶段: Skills 执行

### 4.1 执行流程

```
1. Agent 在 System Prompt 中看到 SKILLS_SNAPSHOT
2. Agent 识别用户意图,决定使用哪个 Skill
3. Agent 调用 read_file(skill_location) 读取完整 SKILL.md
4. Agent 按照 SKILL.md 中的步骤执行:
   - 调用 read_file 读取 memory
   - 调用 python_repl 分析数据
   - 调用 write_file 写入结果
5. Agent 返回结果给用户
```

### 4.2 System Prompt 注入

**在 PromptBuilder 中**:

```python
def build_system_prompt(self, ...):
    blocks = []

    # Block 1-4: 身份、工具、工作区、元数据
    ...

    # Block 5: 控制层文件
    blocks.append("# Project Context")
    blocks.append("## AGENTS.md")
    blocks.append(self._read_file("workspace/AGENTS.md"))
    ...

    # Block 6: SKILLS_SNAPSHOT
    blocks.append("## SKILLS_SNAPSHOT.md")
    blocks.append(self._read_file("SKILLS_SNAPSHOT.md"))

    # Block 7: Memory Map
    blocks.append("# Memory Map")
    ...

    return "\n\n".join(blocks)
```

---

## 五、默认 Skills 清单

### 5.1 实验版推荐的 7 个默认 Skills

| Skill 名称 | 描述 | 使用场景 |
|-----------|------|---------|
| **stage_report_ppt** | 生成阶段汇报 PPT 结构 | 用户请求"准备第N次阶段汇报" |
| **synthesis_checklist** | 生成合成流程 checklist | 用户请求"整理今天的合成流程" |
| **mechanism_audit** | 机理证据链审计 | 用户请求"审计 Co(IV) 证据链" |
| **characterization_audit** | 表征审计 (能证明/不能证明) | 用户请求"XRD 能证明什么" |
| **writing_outline** | 写作大纲生成 | 用户请求"写 Results & Discussion 大纲" |
| **experiment_matrix** | 实验矩阵设计 | 用户请求"设计对照实验" |
| **csv_kobs_fit** | CSV 数据拟合作图 | 用户上传 CSV 并请求"拟合 kobs" |

### 5.2 Skills 优先级

**P0 (必须实现)**:
- stage_report_ppt
- synthesis_checklist

**P1 (推荐实现)**:
- mechanism_audit
- characterization_audit
- experiment_matrix

**P2 (可选)**:
- writing_outline
- csv_kobs_fit

---

## 六、Skills 与 Tools 的关系

### 6.1 Skills 调用 Tools 的模式

```markdown
# Skill 说明书中的典型步骤

### Step 1: 读取项目北极星
```
使用 read_file("memory/identity/project.md")
提取: 主线假设、判据
```

### Step 2: 读取最近的实验日志
```
使用 read_file("memory/timeline/days/2025-11-23.md")
提取: 今天做了什么实验
```

### Step 3: 分析 CSV 数据
```
使用 python_repl 执行:
import pandas as pd
df = pd.read_csv("assets/data/exp_005.csv")
print(df.describe())
```

### Step 4: 生成图表
```
使用 python_repl 执行:
import matplotlib.pyplot as plt
plt.plot(df['time'], df['concentration'])
plt.savefig("assets/figures/exp_005_kinetics.png")
```

### Step 5: 写入 Task
```
使用 write_file("memory/tasks/TASK_exp_005.md", content)
```
```

### 6.2 Tools 使用频率

| Tool | 在 Skills 中的使用频率 | 典型用途 |
|------|---------------------|---------|
| **read_file** | ⭐⭐⭐⭐⭐ | 读取 memory/assets |
| **write_file** | ⭐⭐⭐⭐⭐ | 写入 memory |
| **python_repl** | ⭐⭐⭐⭐ | 数据分析、作图 |
| **list_directory** | ⭐⭐⭐ | 列出素材文件 |
| **terminal** | ⭐⭐ | 执行系统命令 |
| **fetch_url** | ⭐ | 联网查询 |
| **web_search** | ⭐ | 文献检索 |

---

## 七、Skills 测试

### 7.1 测试场景

**场景 1: 阶段汇报**
```
用户输入: "帮我准备第6次阶段汇报,素材在 assets/ppt_pack/R06_20251123/"

预期流程:
1. Agent 识别意图 → 决定使用 stage_report_ppt
2. Agent 调用 read_file("skills/stage_report_ppt/SKILL.md")
3. Agent 按步骤执行:
   - read_file("memory/timeline/stage_reports/R05.md")
   - read_file("memory/timeline/weeks/2025-W46.md")
   - list_directory("assets/ppt_pack/R06_20251123/")
   - python_repl 分析素材
   - write_file("memory/packs/PACK_stage_report_R06.md", ...)
4. Agent 返回 PPT 结构

验收标准:
✅ 生成的 Pack 包含完整的页级结构
✅ 每页有中心句
✅ 素材路径正确
✅ 包含 WPS AI 提示词
```

**场景 2: 合成 checklist**
```
用户输入: "帮我整理今天的合成流程,按时间顺序"

预期流程:
1. Agent 识别意图 → 决定使用 synthesis_checklist
2. Agent 调用 read_file("skills/synthesis_checklist/SKILL.md")
3. Agent 按步骤执行:
   - read_file("memory/identity/lab_context.md")
   - read_file("memory/timeline/days/2025-11-23.md")
   - 生成 checklist
   - write_file("memory/timeline/days/2025-11-23.md", 追加 checklist)
4. Agent 返回 checklist

验收标准:
✅ Checklist 按时间顺序
✅ 包含称量量、容器、标号
✅ 标注易混淆步骤
✅ 写入当天日志
```

---

## 八、Skills 扩展机制

### 8.1 用户自定义 Skills

用户可以在 `backend/skills/` 下创建新的 Skill:

```bash
mkdir backend/skills/my_custom_skill
cat > backend/skills/my_custom_skill/SKILL.md <<EOF
---
name: my_custom_skill
description: 我的自定义技能
version: 1.0
tags: [custom]
---

# My Custom Skill

## 使用场景
...

## 执行步骤
...
EOF
```

重启后端,自动生成新的 SKILLS_SNAPSHOT.md

### 8.2 Skill Mining (自动提炼)

**未来功能 (Phase 6+)**:

当检测到重复任务 (如"阶段汇报"出现 ≥3 次),系统自动:
1. 分析历史 trace
2. 提取共同模式
3. 生成 SKILL.md 草稿
4. 提示用户审核

---

## 九、实施步骤

### Step 1: 创建 Skills 目录结构
```bash
mkdir -p backend/skills/{stage_report_ppt,synthesis_checklist}
```

### Step 2: 编写默认 Skills
- stage_report_ppt/SKILL.md
- synthesis_checklist/SKILL.md

### Step 3: 实现 SkillsScanner
- backend/graph/skills_scanner.py

### Step 4: 集成到 app.py
- 启动时自动生成 SKILLS_SNAPSHOT.md

### Step 5: 修改 PromptBuilder
- 注入 SKILLS_SNAPSHOT 到 System Prompt

### Step 6: 端到端测试
- 测试阶段汇报场景
- 测试合成 checklist 场景

---

## 十、验收标准

| 验收项 | 标准 | 状态 |
|-------|------|------|
| **SKILLS_SNAPSHOT 生成** | 启动时自动生成,包含所有 skills/ 下的技能 | ⏳ |
| **System Prompt 注入** | SKILLS_SNAPSHOT 正确注入到 System Prompt | ⏳ |
| **Skills 执行** | Agent 能正确读取 SKILL.md 并按步骤执行 | ⏳ |
| **溯源路径** | 生成的 Pack 包含正确的 assets 路径 | ⏳ |
| **端到端测试** | 阶段汇报和合成 checklist 场景测试通过 | ⏳ |

---

**文档完成** | 2026-03-09
