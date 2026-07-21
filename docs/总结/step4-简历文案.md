# Step 4：简历文案

---

## 项目名称

Experimental-Research-OpenClaw —— 面向实验学科的本地化科研 AI Agent 系统

## 项目角色

AI 产品设计 + 后端架构 + Prompt 工程 + 迭代推进

## 项目周期

6 个 Phase 迭代开发（Phase 1-5.3 已完成，Phase 6 前端增强进行中）

---

### 需求洞察

- 针对材料/化学/环境等实验学科硕博生，识别出长周期科研（180 天）中的三重核心痛点：跨阶段记忆断裂（10+ 次阶段汇报无法快速关联历史数据）、结论与证据脱钩（口头描述无法追溯到原始实验文件）、被导师 challenge 后缺乏结构化排查框架。
- 通过用户访谈提炼出 2 类典型托管模式（DDL 交付型 / 认知探索型）和 7 个高频科研场景（合成 checklist、实验矩阵、机理证据链审计、表征审计、阶段汇报、写作结构、CSV 作图拟合），每个场景定义明确的上下文读写策略。
- 明确产品定位差异：不做"更聪明的 ChatGPT"，而是做"带证据链的科研工作台"——输入是实验材料（照片/csv/文献/口头描述），输出是结构化交付物（PPT 大纲/实验 SOP/机理证据链），每条结论区分事实与推断并挂证据回指。

### 功能设计

- 设计三层文件记忆架构（Layer1 身份与规则 / Layer2 时间轴推进 / Layer3 原子资产），以 Markdown 文件系统替代向量数据库，实现 180 天实验周期的持久化记忆，用户可直接查看、编辑、追溯所有记忆内容。
- 抽象 Concept/Task/Pack 三对象模型：Concept 承载研究假设，Task 承载验证过程（Claim + Protocol + Run），Pack 承载阶段交付物（PPT/机理证据链/论文段落），三者形成"假设→验证→交付"的完整闭环。
- 构建 Control Plane / Data Plane / Trace Plane 三面分离架构：Control Plane（SOUL.md/IDENTITY.md 等）定义 Agent 行为硬约束，Data Plane（三层 memory）存放事实数据，Trace Plane 记录全链路决策过程（读了什么文件/为什么读/是否被裁剪/工具调用输入输出）。
- 实现 ContextOrchestrator 智能上下文选择（基于意图识别自动匹配文件，按"稳定→变化→本轮相关"排序注入）、PromptBuilder 7-Block 结构化 Prompt 拼接、SkillLoader 渐进式技能披露（菜单摘要注入 Prompt，Agent 自主决策读取完整说明书）。
- Phase 5.3 完成从全局单例到 WorkspaceRuntimeRegistry 的架构重构，实现多 workspace 运行时隔离（共享 LLM 实例 + 隔离 workspace-scoped 工具），保持 API 向后兼容。

### 评测体系

- 设计 2 条 Golden Test 剧本（DDL 交付型 10 轮对话 / 认知探索型 12 轮对话）作为端到端回归测试基线，验证三卡落盘（Evidence/Task/Result）的结构完整性与证据回指准确性。
- 定义三类科研闭环测试标准（文献闭环 / 实验闭环 / 写作闭环），从 1.45GB 真实科研资料中构建结构化测试数据集，标注 4 类能力标签（上下文命中 / 对象落点 / trace 回放 / 写作组织）。
- 每个 Phase 配备结构化验收矩阵（PASS/FAIL 状态），8 个单元测试覆盖核心模块契约（SkillLoader 菜单生成、Chat+WriteFile 完整流程、System Prompt 契约、5 个核心工具）。
- 建立 Phase 开发三件套纪律（dev-plan → dev-log → architecture.html），已知限制显式标注，Bug 修复追加记入对应 Phase 日志。
