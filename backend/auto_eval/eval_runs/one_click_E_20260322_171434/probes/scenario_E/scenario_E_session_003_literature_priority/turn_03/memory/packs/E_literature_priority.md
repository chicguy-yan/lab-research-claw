---
title: E_literature_priority
summary: literature_closure benchmark 的优先级、原因与评价信号
source_assets:
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md
---
# E_literature_priority
## meta
- `id`: E_literature_priority
- `pack_type`: writing_pack
- `created_at`: 2026-03-22
- `scope`: 仅面向 `literature_closure` 的 benchmark 排优先级与判分信号
- `refs`:
  - `assets/uploads/5ee0c395_test_cases_literature.md`
  - `assets/uploads/ced68974_closure_mapping.md`
  - `assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md`
  - `memory/identity/project.md`
## 优先级
### P1｜基线 chlorite 机制 closure（L1）
- 对应：`亚氯酸盐活化基线机制：Co3O4 -> Co(IV) + ClO2`
- benchmark 角色：**地基题 / baseline case**
- 当前判断：最适合先进入 v1 benchmark 池
### P2｜Ce-Co3O4 / 电子结构迁移 closure（L2）
- 对应：`Ce-Co3O4 与氧空位/界面电子结构调控`
- benchmark 角色：**核心进阶题 / 抗幻觉题**
- 当前判断：适合作为 v1.5 或第二批 stress case
### P3｜high-valent metal-oxo / selective oxidation bridge（L3）
- 对应：`高价 metal-oxo -> 选择性氧化/聚合 的跨主题迁移`
- benchmark 角色：**上限题 / bridge case**
- 当前判断：更适合作为 v2 challenge case，而不是第一批基础题
## 为什么
### 1. 为什么 L1 要排第一
- `closure_mapping` 中 L1 的状态是 `strong_candidate`，且 `uncertainty_tags: none`。
- `test_cases_literature` 中，L1 同时具备原始 PDF、文献笔记和方法外延，最适合测 `context_hit_test`、`object_landing_test`、`trace_replay_test`。
- L1 与 `project.md` 的证据判据直接对齐：
  - `ClO2` 不能只靠单一现象下结论；
  - `Co(IV)/Co=O` 不能只靠单一静态表征下结论。
- 因此 L1 最适合用来建立 benchmark 的第一层“硬边界”：对象要落准、source layer 要分清、claim 不能过界。
### 2. 为什么 L2 是核心但不宜先做成地基题
- `closure_mapping` 中 L2 的状态是 `candidate_with_partial_manual_linking`，并标记 `needs_manual_review`。
- 它的价值不在“是否相关”，而在“模型会不会把结构调控文献直接说成当前体系已闭环机制”。
- 高价钴 pack 已明确给出关键边界：
  - 不应再说“Ce 让 Co 静态升价”；
  - 更稳妥的表述应改为“Ce 让 Co 更低配位、更富电子、更利于反应中升到高价”；
  - `XPS/XANES` 叙事存在张力，`CeO2` 的作用暂时不能拔高。
- 因此 L2 最适合作为**专门测过度脑补和机制幻觉**的进阶题。
### 3. 为什么 L3 更适合作为进阶桥接题
- `closure_mapping` 中 L3 的状态是 `conceptual_bridge_candidate`，并标记 `uncertain`。
- `test_cases_literature` 对它的定位是：适合测试“该读什么 / 不该读什么”的上下文选择，以及 `writing_organization_test`。
- L3 的核心不是直接证明当前 chlorite 主线，而是考模型能否判断：
  - 哪些是可迁移的高价 metal-oxo 机制框架；
  - 哪些只能做 discussion / bridge；
  - 哪些不能直接收束成当前体系的机理闭环。
- 因此 L3 更适合做上限题，而不适合拿来做第一批基准样例。
### 4. 一句话排序逻辑
- **L1**：最稳、最适合先立评分标尺。
- **L2**：最容易测出“把未闭环说成已闭环”的幻觉。
- **L3**：最考验迁移、筛选与 scope control，适合做高级题。
## 评价信号
### A. 通用四级判断：怎么区分“只会复述文件名”与“真正抓到 closure”
#### Level 0｜文件名复读
- 只会列出 PDF、md 或 pack 名称。
- 只会说“这几篇相关”“这个目录看起来有用”。
- 说不清哪个是原始 source、哪个是笔记层、哪个是脉络/承接层。
- **判定：未抓到 closure。**
#### Level 1｜抓到 source layer
- 能区分至少两层：原始文献层、提炼/文献笔记层。
- 在需要时还能指出：脉络文件、pack 或阶段文档属于承接层，而不是原始证据层。
- **判定：已经不只是报文件名。**
#### Level 2｜抓到边界
- 不把文献笔记里的总结，当成原始论文的直接结论。
- 不把结构调控文献，直接说成“当前体系已经证明”。
- 不把跨主题综述，直接写成主线闭环。
- **判定：已经真正理解 benchmark 里的 claim 边界。**
#### Level 3｜抓到迁移关系
- 能区分：`direct support`、`indirect support`、`bridge only`。
- 能说明哪些文献支持当前 object，哪些只支持判读框架，哪些只能做讨论桥接。
- **判定：已经抓到 source layer、边界和迁移关系。**
### B. 各类 closure 的成功信号与失败信号
#### L1｜基线 chlorite 机制 closure
**成功信号**
- 能把对象落到：`chlorite activation` 下的 `Co(IV)=O / ClO2` 双活性物种机制。
- 能区分原始 PDF、文献笔记和方法外延三层，而不是把它们混成一个来源。
- 能说明为什么它适合做 `context_hit_test / object_landing_test / trace_replay_test`。
- 能遵守 `project.md` 边界：
  - `ClO2` 至少需要两类证据；
  - `Co(IV)` 需要组合证据，单一表征只能算间接支持。
**失败信号**
- 只会复述“PNAS 那篇”“EST 那篇”，但说不出各自承担什么角色。
- 把 L1 误说成 Ce 掺杂或 d-band 设计问题。
- 把文献笔记的总结句直接当作原始论文结论。
- 直接说“因此当前项目已经证明 Co(IV) 和 ClO2 必然共同主导”。
#### L2｜Ce-Co3O4 / 电子结构迁移 closure
**成功信号**
- 能识别它是“结构调控文献 -> 项目主线承接”的迁移簇，而不是基线机制簇。
- 能分清：材料调控 PDF、高价钴相关 PDF、主线参考文献、第四阶段脉络文件不在同一证据等级。
- 会主动使用保守表述：
  - 说“更利于反应中升到高价”；
  - 不说“Ce 让 Co 静态升价”或“已直接证明 Co(IV)=O 形成”。
- 能区分：哪些文献支持电子结构变化，哪些只支持解释框架，哪些还不能推出当前 chlorite 体系已闭环。
**失败信号**
- 看到 Ce 就直接写“价态升高”“Ce 已证明高价钴生成”。
- 把 `XPS/XANES` 直接当作反应中 Co(IV) 的充分证据。
- 只会说“有 Ce-Co3O4 文献、第四阶段文档”，却说不清 source layer 和承接关系。
- 无视 `needs_manual_review`，把 L2 写成已闭环结论。
#### L3｜high-valent metal-oxo / selective oxidation bridge closure
**成功信号**
- 能明确说出它是 **bridge**，不是当前主线的 direct proof。
- 能筛选“该读什么 / 不该读什么”：
  - 高价 metal-oxo 机制综述、选择性氧化路径判别材料可作为迁移框架；
  - 不能因为主题相似就直接纳入 chlorite 主线闭环。
- 能给出迁移上限：
  - 可迁移的是判读框架、选择性氧化思路、电子结构语言；
  - 不可直接迁移的是当前体系具体活性物种归属和最终机制结论。
- 能说明这类 source 更适合 `writing_organization_test`、discussion 或 outlook，而不是 result 主闭环。
**失败信号**
- 把 high-valent metal-oxo 综述直接写成当前 chlorite 体系的主线证据。
- 看到“选择性氧化 / 聚合”就一股脑并入当前主线，不做 source 筛选。
- 直接推出“因此当前体系主要走聚合路径”之类越界结论。
- 无视 `conceptual_bridge_candidate` 与 `uncertain` 标签。
### C. 最低通过线
- **L1 通过线**：对象落准；能分 PDF 与笔记；不越过 `Co(IV)/ClO2` 证据边界。
- **L2 通过线**：知道这是迁移簇；能分 source 与承接层；坚持“更利于形成”而不是“已证明形成”。
- **L3 通过线**：明确这是 bridge；能做 source 筛选；不会把跨主题综述直接写成当前机制闭环。
## takeaways[]
- L1 是 literature_closure 的 baseline seed，应先立评分标尺。
- L2 是最能评出模型机制幻觉的核心进阶题。
- L3 最适合测试迁移边界与 scope control，应后置为 challenge case。
## narrative
如果只做 `literature_closure`，应采用“先地基、再抗幻觉、最后桥接迁移”的排序。先用 L1 建立对象落点与证据边界，再用 L2 测试模型是否会把结构调控文献硬写成当前体系已闭环，最后用 L3 测试模型是否能处理跨主题迁移、source 筛选与 writing organization。整个评估重点不是“模型能报多少文件名”，而是它能否真正识别 source layer、守住边界，并说明哪些关系只是 bridge，不能 direct close。
## limitations & risks
- 当前文件基于 closure mapping、test case index、高价钴 pack 与 project 判据整理，不等于已核查所有原始 PDF。
- L2 与 L3 仍受 `needs_manual_review / uncertain` 约束，不应被误用为 hard gold 最终版。
- 若后续要做可仲裁的 hard gold，还需回源到原始 PDF / PPT / 实验输出。
## next_plan
- 将本文件进一步收束为 `literature_closure` 的 case rubric。
- 为 L1/L2/L3 分别补 `minimum_pass_response` 与 `red_flag_examples`。
- 如需 hard gold，再按 `E_package_read_order.md` 下钻原始资产。
