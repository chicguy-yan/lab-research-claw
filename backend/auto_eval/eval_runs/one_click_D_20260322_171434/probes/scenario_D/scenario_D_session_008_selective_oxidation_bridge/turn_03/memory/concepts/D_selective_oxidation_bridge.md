---
source_assets:
  - assets/uploads/6a403cea_【gpt文献调研：高价钴氧物种生成+聚合证据链】.md
  - assets/ppt_pack/746ff89e_0327大组会-颜雍颀.pptx
  - assets/uploads/647b5227_reaction-pathway-tuning-between-electron-transfer-mediated-degradation-and-polymerization-in-fe-mos2-based-persulfate.pdf
  - assets/ppt_pack/75315785_Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
created: 2026-03-22
---

## id
- CONCEPT_selective_oxidation_bridge
## name
- selective oxidation / polymerization discussion bridge
## scope
- 用于约束 thesis 中 selective oxidation / polymerization 旁支的写作边界。
- 目标不是证明本体系已经发生 polymerization，而是界定哪些内容可作为 discussion bridge、哪些只能写成启发、哪些应禁止进正文。
- 适用对象：Ce-Co3O4 / NaClO2 主线写作，尤其是 thesis discussion、组会讲稿、开题/阶段汇报中的桥接段落。
## keywords
- [ ] selective oxidation
- [ ] polymerization
- [ ] discussion bridge
- [ ] overclaim guardrail
- [ ] mechanism boundary
- [ ] thesis writing
## north_star（一句话）
- 在不越过证据边界的前提下，把 polymerization 作为 selective oxidation 邻近支路来讨论，而不把它写成本体系已证实的主反应路径。
## active_tasks[]
- TASK_pending_bridge_paragraph_drafting
- TASK_pending_overclaim_screening
## related_packs[]
- D_hvco_storyboard
- D_group_meeting_replay
## notes
### 可进入写作的桥
1. **文献层面的安全桥接**
   - 已有外部文献表明，在部分选择性氧化体系中，污染物转化并不一定单向通向深度降解，也可能分叉到表面耦合/聚合等邻近路径。
   - 该类分叉可受底物结构、电子特征、氧化剂量等因素影响。
   - 这类表述适合放在 thesis discussion 中，作为“外部先例 + 机制边界提醒”。
2. **证据门槛层面的安全桥接**
   - 是否存在 polymerization，不能仅凭去除率、TOC 差异、颜色变化、表面变脏等现象判断。
   - 若要把 polymerization 写入正文，需要沉积物、洗脱产物、分子量分布、LC-MS / MALDI / NMR / XPS / FTIR / TGA / 碳平衡等直接证据链支持。
   - 因此可以在讨论中明确写出：本文仅借助外部先例提示存在邻近支路，但本体系尚未完成该证据闭环。
3. **本体系可安全写入的桥接句意**
   - 本研究主线仍是 selective oxidation。
   - polymerization 目前只可作为与 selective oxidation 相邻的候选讨论支路，用于扩展对反应选择性的理解。
   - 不应将其上升为本文已证实的主反应路径。
### 只适合作讨论的桥
1. **跨体系启发，不能直接平移**
   - 其他底物 / 其他氧化剂 / 其他催化剂体系中观察到的 degradation–polymerization bifurcation，可作为启发，但不能直接写成 Ce-Co3O4 / NaClO2 体系已发生相同行为。
2. **底物结构与路径偏好的关系**
   - 分子母体、取代基、电荷分布、电子给受体能力等因素可能影响 selective oxidation 与旁支路径竞争。
   - 这类内容适合在 discussion 里作为解释框架或 future work 提示，不宜写成本文结论。
3. **表面电子结构调控的启发**
   - Ce 掺杂、氧空位、表面电子结构变化，可能影响活性物种生成与反应选择性。
   - 但若缺少本体系直接谱学与产物证据，只能写成“可能相关/值得验证”。
4. **高价钴物种与旁支路径的关联**
   - Co(IV)=O、ClO2 等选择性氧化物种，理论上可能与非自由基选择性转化相关。
   - 但在没有同体系中间体/产物/表面沉积证据前，这只能作为讨论启发，不能写成主导机制。
### 风险语句
1. **默认应自动降级的说法**
   - “本体系已经发生 polymerization” → 降级为“本体系不排除存在与 selective oxidation 邻近的聚合支路，但尚待验证”。
   - “本体系实现了 degradation 向 polymerization 的路径切换” → 降级为“外部文献提示部分体系存在路径切换现象，本体系可借鉴该视角进行后续验证”。
   - “去除并非降解而是聚合去除” → 降级为“当前结果尚不能区分降解、耦合、吸附或表面沉积等贡献”。
   - “Co(IV)=O 已被严格证实并主导聚合支路” → 降级为“现有结果提示高价钴物种可能参与反应选择性调控，仍需进一步证据闭环”。
2. **高风险动词（优先替换）**
   - 证明、证实、表明、说明、导致、主导、决定、实现了切换、排除了、揭示了、已观察到、已形成、已发生。
3. **更安全的替换词**
   - 提示、暗示、与……相一致、不排除、可能相关、可作为启发、可作为外部先例、支持其作为候选解释之一、尚待验证、需要进一步证据支持。
4. **写作刹车规则**
   - 只要结论来自跨体系外推，就默认写成“文献先例/外部启发”，不写成“本体系观察到”。
   - 只要没有直接产物或沉积物证据，就不写“polymerization 已发生”。
   - 只要只有内部 PPT、调研稿或单一探针结果，就不写“证实某活性物种主导某路径”。
   - 凡是 discussion bridge，默认使用“可能相关 / 可启发 / 待验证”的措辞，除非本体系已有多源独立证据闭环。
