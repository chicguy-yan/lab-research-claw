---
source_assets:
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
  - assets/uploads/4288b081_research_os_ecosystem_map.md
  - assets/data/53be2d7c_closure_mapping.json
created: 2026-03-22
---

# PACK_bootstrap_kickoff

## meta
- `id`: PACK_bootstrap_kickoff
- `pack_type`: bootstrap_bridge_handoff_pack
- `created_at`: 2026-03-22
- `time_range`: 2026-03-22 ~ 2026-03-22

## purpose
这个 pack 用于完成 workspace 的 bootstrap 初始化：
把当前 workspace 明确定义为 **服务 benchmark / eval system 的跨闭环桥接容器**，而不是普通研究 workspace。

它的第一职责不是重读全部原始材料，
而是先利用 bridge 文件决定：
- `该读什么`
- `暂时不该读什么`
- `下一步交给谁`

## this_pack_measures
### 这个包测什么
这个 seed pack 主要测 4 类能力：
1. **bridge-first 路由能力**
   - 系统能否先基于 bridge 文件判断读取路径，而不是一上来扫描原始全集。
2. **跨闭环识别能力**
   - 系统能否识别文献、实验、写作三条线之间的桥接关系。
3. **read-gating 能力**
   - 系统能否明确说出“该读什么 / 暂不读什么 / 为什么”。
4. **handoff 准备能力**
   - 系统能否把输出组织成后续 benchmark / eval / prompt contract 可接的 seed，而不是散装研究摘要。

## why_it_is_not_the_raw_corpus
### 它为什么不等于原始全集
这个 pack **不是**原始科研资料全集，也**不试图**替代原始资料。

原因有 5 点：
1. 它的目标是 **读取裁剪与桥接决策**，不是内容穷举。
2. 它优先依赖 bridge 文件中的对象映射、闭环映射、生态位地图，而不是先下钻原始文件海。
3. 它只保留对 benchmark / eval system 有高价值的入口、边界和 handoff 信息。
4. 它必须区分：
   - 原始资产
   - 结构化转译层
   - bridge/handoff 决策层
5. 如果把它做成原始全集，就会失去 read-gating 作用，退化成普通资料库或普通研究总结。

## primary_scope
### workspace 当前职责
- 作为 **跨闭环桥接容器**，优先桥接：文献线、实验线、写作线。
- 服务对象是 benchmark / eval system，而不是直接充当研究结论生成器。
- 默认先回答：
  - 当前桥接对象是什么
  - 该读哪组文件
  - 哪些文件先不要读
  - 后续 handoff 给哪个下游模块

## non_goals
### 明确非目标
以下内容不属于本 pack 的 bootstrap 首责：
- 重新读完所有原始材料
- 直接生成普通 Concept / Task / Pack 模板堆砌
- 产出泛系统设计稿
- 把研究计划态、方法态、结果态混写成已验证结论
- 在未完成 bridge 判定前直接下钻全部原始文件

## bridge_entry_priority
### 推荐入口优先级
1. **ecosystem map**
   - 先用于判断系统里有哪些对象域、哪几条桥值得先接。
2. **closure mapping**
   - 再用于识别哪些 closure 可进入 eval 样例池、哪些对象适合 seed 化。
3. **package architecture**
   - 最后用于约束读取顺序、包边界、提示词入口与 handoff 组织。

## next_read_groups
### 下一步先读哪一组文件
#### Group A — 启动索引组（默认先读）
用于建立 bridge 视角，不直接下钻原始材料：
- `assets/uploads/4288b081_research_os_ecosystem_map.md`
- `assets/data/53be2d7c_closure_mapping.json`
- `assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md`

#### Group B — 样例优先组（仅在需要确定 benchmark seed 时再读）
优先围绕 ecosystem map 中的代表样例选择后续对象：
- `第六阶段高价钴直接证据任务`
- `20260305 大组会文献汇报包`
- `第二阶段 M-Co3O4 性能筛选`
- `2023 EST + 2024 PNAS 基线机制文献簇`

> 注：当前 workspace 内只有 bridge 文件已落地；Group B 中的原始科研文件路径需在后续 handoff 场景再按需回溯，不作为 bootstrap 默认读取范围。

#### Group C — 下游治理组（仅在进入实现时再读）
当要生成 benchmark builder / prompt contract / case schema 时，再继续展开：
- benchmark case schema
- prompt contract 草案
- package/handoff 接口定义

## read_gating_rules
### 读取边界规则
1. **先 bridge，后原件**
   - 没有 bridge 判定，不进入原始材料深读。
2. **先回答 why-read，再执行 read**
   - 每次建议读取都要说明目标与下游 handoff 去向。
3. **允许延迟阅读**
   - 若当前问题只需回答对象范围、边界或入口，原始文件应保持 deferred。
4. **禁止“全集冲动”**
   - 不能把“多读一点更保险”当默认策略。
5. **seed 只承载桥接决策**
   - seed 输出不能退化成散装研究笔记。

## bridge_handoff_seed
### bridge/handoff seed 最小定义
一个 seed 至少回答以下 3 个问题：
1. **这个包测什么**
   - 当前要测的是 bridge-first、read-gating、closure routing、还是 writing organization。
2. **它为什么不等于原始全集**
   - 明确它是测试子集 / 索引层 / 桥接层，而不是全量资料库。
3. **下一步先读哪一组文件**
   - 给出明确的 read group，而不是“按需查看更多”。

建议 seed 的最小字段：
- `seed_id`
- `target_capability`
- `bridge_object`
- `source_bridge_docs[]`
- `recommended_read_group`
- `deferred_reads[]`
- `handoff_target`
- `output_contract`
- `stop_condition`

## handoff_targets
### 下游 handoff 入口
当前 bootstrap 后，优先 handoff 给以下下游：
1. `benchmark builder`
   - 用于定义“这个 seed 测什么能力”。
2. `eval case builder`
   - 用于把 closure/object 变成可评测 case。
3. `prompt contract packager`
   - 用于固化读取顺序、禁止事项、输出约束。

## takeaways
- 这个 workspace 已被收敛为 **跨闭环桥接容器**。
- bootstrap 首责是 **决定读什么**，不是 **重读一切**。
- seed pack 必须是 **bridge/handoff seed**，不能是任意研究模板拼装。
- 当前首读顺序为：`ecosystem map -> closure mapping -> package architecture`。

## limitations_and_risks
- 当前判断主要基于 3 份 bridge 文件，尚未下钻原始科研文件验证具体案例细节。
- `closure_mapping.json` 中部分对象仍带有 `needs_manual_review` / `missing_context` / `uncertain` 标签。
- 若后续要进入 case 级 benchmark，仍需补充明确的下游 schema 与 stop condition。

## next_plan
1. 基于本 pack 抽一版 `bridge/handoff seed schema v0`。
2. 定义 benchmark builder 接口最小字段。
3. 定义“何时允许从 bridge 文件回溯到原始文件”的触发条件。
4. 再决定是否生成首批 seed cases。
