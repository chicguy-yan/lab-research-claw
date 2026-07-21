# Experiment Researchloop-OpenClaw Workspace Templates

这是一个面向**环境材料/催化/高级氧化**等实验型科研的 OpenClaw 风格工作区初始化模板。

## 你会得到什么

- **File-first Memory（文件即记忆）**：所有“记忆 / 证据链 / 实验记录 / 交付物”都落到 Markdown/JSON 文件里。
- **Skills as Plugins（技能即插件）**：运行时同时支持 `backend/skills/` 的 system skill 和 `workspace/skills/` 的私有 skill。
- **透明可控**：每回合写入 `.openclaw/context_trace/`，可回放“读了哪些文件、写了哪些文件、缺哪些字段、用了哪些技能/工具”。

> 推荐配合：你自己的原子笔记系统（Obsidian/VS Code）一起使用。

## 目录总览（最重要）

```text
.
├─ AGENTS.md / SOUL.md / TOOLS.md / IDENTITY.md / USER.md / BOOTSTRAP.md / MEMORY.md
├─ memory/
│  ├─ identity/          # Layer1：身份与规则（长期稳定）
│  ├─ timeline/          # Layer2：时间轴推进（阶段→周→天→阶段汇报）
│  ├─ concepts/          # Layer3：Concept（主题容器）
│  ├─ tasks/             # Layer3：Task（Claim + Protocol + Run）
│  ├─ packs/             # Layer3：Pack（交付物：组会/机理/写作/图集）
├─ skills/
│  ├─ _system/           # 后端镜像下来的跨 workspace system skills
│  ├─ registry.json      # 当前 workspace 私有 skills 索引
│  └─ <skill_id>/        # 当前 workspace 私有技能
├─ .openclaw/context_trace/  # 每回合回放 trace（JSON）
└─ assets/               # 数据/图/组会打包目录（前端可直连）
temporary_dir/        # session 级短暂脚本/管道输出/中间文件
```

补充约定：
- `assets/` 是素材层 / 原始层。
- `memory/` 是结构化沉淀层 / 可复用知识层。
- `temporary_dir/` 是短暂文件层，推荐写入 `temporary_dir/<session_id>/...`，session 清空时自动清理。

## 使用建议（极简）

1. 第一次启动：按 `BOOTSTRAP.md` 填好 `IDENTITY.md / USER.md / memory/identity/*.md`
2. 每天实验：用 `memory/timeline/days/` 创建当天文件（或用 `_DAY_TEMPLATE.md` 复制）
3. 重要验证：在 `memory/tasks/` 新建一个 Task（Claim + Protocol + Run）
4. 阶段汇报：在 `memory/timeline/stage_reports/` 新建 Rxx 文件，并把素材打包到 `assets/ppt_pack/Rxx_YYYYMMDD/`

---

如果你正在开发 Agent：请阅读 `prompt_prd.md`（单独交付的 PRD）作为“模型如何拼接上下文 / 读写记忆 / 调用技能”的准则。

## Skills 说明

- `backend/skills/registry.json` 定义跨 workspace 常驻的 system skills。
- 运行时 `SkillLoader` 会将 system skills 镜像到 `workspace/skills/_system/`，供 Agent 用 `read_file` 读取。
- 用户或 Agent 自主创建的私有 skill 应写入 `workspace/skills/<skill_id>/SKILL.md`，并登记到 `workspace/skills/registry.json`。
- `workspace/skills/SKILLS_SNAPSHOT.md` 是运行时生成的菜单快照，不是手工维护文件。
