---
source_assets:
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/45307a7c_test_cases_writing.md
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
created: 2026-03-21
---

# E_benchmark_prioritization
## 入选 benchmark
建议第一版精简 benchmark 采用 **8 个核心 session 类型**，并保留 **2 个暂缓候选** 作为第二版扩展位。
| ID | Session 类型 | 来源 | 主要覆盖能力 |
|---|---|---|---|
| B0 | 混合初始资产 bootstrap（派生型） | 基于 package architecture + 三类代表资产组合 | bootstrap、artifact 写入、hallucination guardrails |
| L1 | 基线机制文献簇 | literature | binary 解析、Concept 落点、trace replay |
| L2 | Ce-Co3O4 主逻辑迁移簇 | literature | 文献→实验桥接、跨 session memory |
| L3 | d-band → 聚合路径跨主题综述簇 | literature | hallucination guardrails、上下文选择 |
| E2 | 第五阶段最小机理闭环 | experiment | Task 组织、artifact 写入、guardrails |
| E3 | 第六阶段高价钴直接证据链 | experiment | binary 解析、Task→Pack 桥接、跨 session memory |
| W1 | 20260305 大组会 Pack | writing | binary 解析、Pack 组织、artifact 写入 |
| W2 | 毕业论文章节反推 Pack | writing | 写作缺口识别、跨 session memory、guardrails |
> 注：B0 不是三类 test case 文件中的原生条目，而是为覆盖 bootstrap 能力而合成的“首次进入 workspace”场景。
## 覆盖理由
### 1. 五类能力必须全部覆盖
第一版 benchmark 明确要求覆盖以下五类能力：
- bootstrap
- binary 解析
- artifact 写入
- 跨 session memory
- hallucination guardrails
上述 8 个 session 的能力覆盖如下：
| Session | bootstrap | binary 解析 | artifact 写入 | 跨 session memory | guardrails |
|---|---:|---:|---:|---:|---:|
| B0 | ✓ |  | ✓ |  | ✓ |
| L1 |  | ✓ | ✓ |  | ✓ |
| L2 |  |  |  | ✓ |  |
| L3 |  |  |  |  | ✓ |
| E2 |  |  | ✓ |  | ✓ |
| E3 |  | ✓ | ✓ | ✓ |  |
| W1 |  | ✓ | ✓ |  |  |
| W2 |  |  | ✓ | ✓ | ✓ |
### 2. 优先保留对象落点清晰的 case
第一版更适合保留可形成明确 memory 产物的 session：
- B0 → `workspace_scope.md` / `project.md`
- L1 → `CONCEPT_*.md`
- E2 / E3 → `TASK_*.md`
- W1 / W2 → `PACK_*.md`
这类 case 更容易定义输入、期望输出、失败模式和评分锚点。
### 3. 优先保留跨层桥接 case
相比单一能力的 case，以下类型更能拉开模型差距：
- 文献 → Concept（L1）
- 文献 → 实验主线（L2）
- 实验 → 写作证据包（E3）
- 工作文档 → Pack / 章节结构（W1, W2）
### 4. 第一版 benchmark 要先保证“可比性”
第一版不宜过早加入大量主观性太强、评分歧义较大的 session；因此优先保留：
- 证据链相对清晰的 case
- 产物类型相对稳定的 case
- 可抽取客观评分点的 case
## 暂缓项
| ID | Session 类型 | 暂缓理由 |
|---|---|---|
| E1 | 第二阶段性能筛选闭环 | **信息重复 / 增益不够高**：与 E2、E3 同属实验线能力，均可覆盖 protocol、claim、evidence 组织；相比之下，E2/E3 的闭环程度和区分度更高，因此 E1 对第一版 benchmark 的边际增益较低。 |
| W3 | 开题报告版本演化 Pack | **太依赖人工判读**：版本优劣、删改是否合理、推进是否得当，较难形成稳定自动评分；同时 W1/W2 已覆盖 Pack 组织与写作缺口识别，W3 在第一版中的增益不够高。 |
### 暂缓项筛选原则总结
第一版先不做的 case，优先符合以下一种或多种情况：
- 与已入选 case **信息重复** 或能力重叠较高
- 任务边界仍然 **不够清晰**
- 评分过度依赖 **人工主观判读**
- 对第一版 benchmark 的 **边际增益不够高**
## 结论
建议以 **8 个核心 session** 构成 benchmark v1：
- B0, L1, L2, L3, E2, E3, W1, W2
建议将 **E1、W3** 作为 v1.1 / v2 的优先扩展项：
- 若从 8 个扩到 9 个，优先加入 **E1**
- 若扩到 10 个，再加入 **W3**
