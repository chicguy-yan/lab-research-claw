# Skill Creator 使用指南

## 概述

Skill Creator 提供两种方式创建自定义科研技能：
1. **交互式模式**：通过命令行问答创建
2. **配置文件模式**：通过 JSON 配置文件批量创建

## 方式 1：交互式创建

### 使用方法

```bash
cd backend
source .venv/bin/activate
python scripts/create_skill.py
```

### 交互流程

脚本会引导你完成 6 个步骤：

1. **基本信息**
   - Skill ID（英文小写+下划线，如 `my_experiment_skill`）
   - Skill 名称（中文描述）
   - 分类（experiment/literature/analysis/ppt/word/meta）

2. **触发条件**
   - 使用场景描述
   - 触发关键词（逗号分隔）

3. **输入输出**
   - 需要哪些输入
   - 会产出什么

4. **文件读写**
   - 需要读取哪些文件
   - 会写入哪些文件

5. **执行步骤**
   - 逐步描述执行流程（每行一个步骤）

6. **路由偏好**
   - 推荐在哪些工作语境使用

### 示例

```
Skill ID: pmso_analysis
Skill 名称: PMSO 实验分析
分类: analysis
使用场景: 用户上传 PMSO 实验数据，需要判断活性物种
触发关键词: PMSO, 活性物种, 自由基分析
需要哪些输入: PMSO 实验数据, 对照组数据
会产出什么: 活性物种判断报告, 证据链表格
需要读取哪些文件: memory/identity/project.md, memory/tasks/TASK_mechanism_*
会写入哪些文件: memory/tasks/TASK_pmso_*.md
执行步骤:
  1. 读取 PMSO 实验数据
  2. 对比对照组
  3. 判断活性物种类型
  4. 生成证据链表格
  5. 输出分析报告
推荐路由: mechanism_closure, experiment
```

---

## 方式 2：配置文件创建

### 使用方法

1. 复制模板：
```bash
cp backend/scripts/skill_config_template.json my_skill_config.json
```

2. 编辑配置文件：
```json
{
  "skill_id": "pmso_analysis",
  "skill_name": "PMSO 实验分析",
  "category": "analysis",
  "when_to_use": "用户上传 PMSO 实验数据，需要判断活性物种",
  "inputs_required": [
    "PMSO 实验数据",
    "对照组数据"
  ],
  "outputs": [
    "活性物种判断报告",
    "证据链表格"
  ],
  "reads": [
    "memory/identity/project.md",
    "memory/tasks/TASK_mechanism_*.md"
  ],
  "writes": [
    "memory/tasks/TASK_pmso_*.md"
  ],
  "triggers": [
    "PMSO",
    "活性物种",
    "自由基分析"
  ],
  "execution_steps": [
    "读取 PMSO 实验数据",
    "对比对照组",
    "判断活性物种类型",
    "生成证据链表格",
    "输出分析报告"
  ],
  "preferred_routes": [
    "mechanism_closure",
    "experiment"
  ]
}
```

3. 运行创建脚本：
```bash
cd backend
source .venv/bin/activate
python scripts/create_skill_from_config.py ../my_skill_config.json
```

---

## 创建后的文件结构

创建成功后，会生成以下文件：

```
workspace-default/
└── skills/
    ├── registry.json          # 已更新，包含新 skill
    └── <skill_id>/
        └── SKILL.md           # 新 skill 定义
```

---

## 验证新 Skill

### 1. 检查 registry

```bash
cat .openclaw/workspace-default/skills/registry.json
```

确认新 skill 已注册。

### 2. 重启后端

```bash
cd backend
python app.py
```

### 3. 测试触发

在聊天界面输入触发词，观察 Agent 是否读取了新 skill。

---

## Skill 设计最佳实践

### 1. Skill ID 命名
- 使用英文小写 + 下划线
- 体现功能：`csv_plot_kobs`, `pmso_analysis`
- 避免过于宽泛：❌ `data_analysis`，✅ `kobs_fitting`

### 2. 触发词设计
- 包含领域术语：`PMSO`, `EPR`, `kobs`
- 包含动作词：`拆解`, `整理`, `分析`
- 3-5 个触发词为宜

### 3. 输入输出明确
- 输入：具体数据类型（CSV / PDF / 图片）
- 输出：具体交付物（报告 / 表格 / 图表）

### 4. 文件路径规范
- 读取：使用通配符 `TASK_*.md`
- 写入：使用模板 `TASK_<type>_<topic>.md`
- 相对于 workspace 根目录

### 5. 执行步骤清晰
- 每步一句话
- 可操作、可验证
- 3-7 步为宜

---

## 常见问题

### Q: 创建的 skill 不生效？
A: 检查：
1. registry.json 是否更新
2. 后端是否重启
3. 触发词是否匹配

### Q: 如何修改已有 skill？
A: 直接编辑 `workspace-default/skills/<skill_id>/SKILL.md`，无需重新注册。

### Q: 如何删除 skill？
A:
1. 删除 `workspace-default/skills/<skill_id>/` 目录
2. 从 `registry.json` 中移除对应条目
3. 重启后端

### Q: System skill 和 workspace skill 的区别？
A:
- **System skill**：`backend/skills/`，所有 workspace 共享
- **Workspace skill**：`workspace-default/skills/`，当前 workspace 私有
- 本工具创建的是 **workspace skill**

---

## 高级用法

### 批量创建

准备多个配置文件，使用脚本批量创建：

```bash
for config in configs/*.json; do
    python scripts/create_skill_from_config.py "$config"
done
```

### 从现有 skill 复制

```bash
cp -r workspace-default/skills/csv_plot_kobs workspace-default/skills/my_new_skill
# 编辑 SKILL.md
# 更新 registry.json
```

---

## 参考资料

- [Phase 5.1 开发计划](../docs/phase5.1-dev-plan.md)
- [Skill 模板](../backend/skills/_skill_template/SKILL.md)
- [现有 System Skills](../backend/skills/)
