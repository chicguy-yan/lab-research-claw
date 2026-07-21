---
source_assets:
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md
created: 2026-03-21
---

# E_literature_priority

## meta
- id: `E_literature_priority`
- pack_type: `writing_pack`
- created_at: `2026-03-21`
- scope: `literature_closure benchmark 优先级与评价信号`
- basis:
  - `assets/uploads/5ee0c395_test_cases_literature.md`
  - `assets/uploads/ced68974_closure_mapping.md`
  - `assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md`

## 优先级

### 主排序（建议先做什么）
1. **基线 chlorite 机制**
2. **Ce-Co3O4 / 电子结构迁移**
3. **high-valent metal-oxo / selective oxidation bridge**

### 若按 benchmark 目标重排
- **立标尺**：基线 chlorite 机制
- **抓主线内幻觉**：Ce-Co3O4 / 电子结构迁移
- **测迁移上限**：high-valent metal-oxo / selective oxidation bridge

### 简版判断
- **最核心**：基线 chlorite 机制
- **最容易稳定评出模型幻觉**：Ce-Co3O4 / 电子结构迁移
- **最适合作为进阶题**：high-valent metal-oxo / selective oxidation bridge

## 为什么

### 1) 基线 chlorite 机制排第一
- `closure_mapping` 中该类为 `strong_candidate`，且 `uncertainty_tags = none`。
- `test_cases_literature` 中该类同时包含原始 PDF、文献笔记和方法外延，最适合做 `context_hit_test`、`object_landing_test`、`trace_replay_test`。
- 其对象落点明确：`亚氯酸盐活化下的 Co(IV)=O / ClO2 双活性物种机制`。
- 这是后续 Ce 作用、高价钴证明与 bridge 迁移的母题；如果连这类都命不中，后面两类的评测结果会失真。
- 评分稳定性最高，最适合先作为 literature_closure benchmark 的基准题。

### 2) Ce-Co3O4 / 电子结构迁移排第二
- `closure_mapping` 中该类为 `candidate_with_partial_manual_linking`，且 `uncertainty_tags = needs_manual_review`。
- 它不是“没有文献”，而是“有锚点，但不能自动说满”，因此特别适合测模型会不会把候选关系误写成已闭环关系。
- 该类 source layer 天然混合：既有材料结构调控 paper，也有实验脉络文档和高价钴 pack，最容易暴露模型是否会把组织层文件误当成原始证据。
- 高价钴 pack 已明确提出叙事约束：**不能直接说“Ce 让 Co 静态升价”**，更稳妥的口径是“Ce 让 Co 更低配位/更富电子/更利于反应中升到高价”。
- 该类还天然带有“XPS / XANES 张力 + PMSO/H2^18O/EPR/CV 待补证据”结构，因此很适合做 hallucination audit。

### 3) high-valent metal-oxo / selective oxidation bridge 排第三
- `closure_mapping` 中该类为 `conceptual_bridge_candidate`，且 `uncertainty_tags = uncertain`。
- 其本质是跨主题迁移题，不是同主题直接闭环题；更适合测“该读什么 / 不该读什么”“能迁移什么 / 不能迁移什么”。
- 这类题最容易诱发高级幻觉：把别的氧化体系、高价 metal-oxo 综述或写作框架，直接迁移成当前主线里的已证实机制。
- 它的辨别力很强，但评分稳定性低于前两类，因此更适合作为进阶题或 generalization 题，而非首批基准题。

## 评价信号

### A. 通用硬指标：区分“文件名复读”与“真正 closure”

#### 1. source layer
**成功信号**
- 能主动区分：
  - **原始证据层**：paper / PDF
  - **解释整理层**：文献笔记
  - **组织与路由层**：closure mapping、pack、阶段脉络文档
- 能说明每层文件在 closure 中的作用，而不是只报文件名。

**失败信号**
- 只会列出文件路径或标题，不说明谁是原始证据、谁是解释层、谁只是组织层。
- 把 pack、mapping、阶段脉络文档直接当成机制已证实的原始依据。

#### 2. boundary
**成功信号**
- 能明确说出当前 closure **能回答什么**、**不能回答什么**。
- 不把基线题自动外推到 Ce 调控，也不把 bridge 题自动外推到主线已闭环。

**失败信号**
- 看到关键词相似就一路串联，默认同词即同证据。
- 从 L1 直接跳到 Ce 作用成立，从 L3 直接跳到聚合/选择性氧化已成立。

#### 3. transfer
**成功信号**
- 能区分：
  - **直接证据支持**
  - **同主题辅助支撑**
  - **跨主题概念桥接**
- 能写清“迁移的是框架/候选因果链”还是“迁移的是已证实结论”。

**失败信号**
- 只要两个文件都提到“高价钴”“d-band”“选择性氧化”，就默认可直接互证。
- 把跨体系类比写成当前体系的已证实结论。

#### 4. object landing + trace replay
**成功信号**
- 能把回答落到 `object_hint`，而不是只停留在主题词层面。
- 能说明阅读顺序和各文件分工，例如“哪篇是主机制 paper，哪篇是补 OAT/PCET/pH，哪篇只是组织层文档”。

**失败信号**
- 只能说“相关文件有 A/B/C”，却不能说明读它们的先后、角色与支撑范围。

---

### B. 各类 closure 的成功信号 / 失败信号

### 1) 基线 chlorite 机制
**成功信号**
- 命中成对的 **原始 PDF + 文献笔记**，识别其为同主题标准簇。
- 对象稳定落到：`Co(IV)=O / ClO2 双活性物种机制`。
- 能说明 OAT、PCET、pH、Cl 形态等在该簇中的功能分工。
- 能做 `trace replay`：知道哪篇更像主机制，哪篇更像机制外延或补充。
- 不越界去证明 Ce 作用或 selective oxidation / polymerization bridge。

**失败信号**
- 只会念 PNAS / EST 文件名，却不能说明 paper 与文献笔记的层级关系。
- 不能把对象落到 `Co(IV)=O / ClO2`，而是泛泛而谈“高价钴很重要”。
- 直接把基线机制外推成 Ce 调控已经成立。
- 把 chlorite 主线与 bridge 写作题混讲。

### 2) Ce-Co3O4 / 电子结构迁移
**成功信号**
- 能识别这是“有文献锚点，但需要人工审查”的主逻辑迁移簇。
- 能区分：
  - paper = 原始依据
  - 第四阶段实验脉络 = 主线连接层
  - 高价钴 pack = 推理组织层 / 待补证据链说明
- 会主动收束口径：不说“Ce 让 Co 静态升价”，而说“Ce 让 Co 更低配位/更富电子/更利于反应中升到高价”。
- 会指出 XPS / XANES 之间存在张力，不强行抹平。
- 会把 PMSO + H2^18O、冻淬 EPR、CV 识别为关键补证，而不是装作已经完成。

**失败信号**
- 把 `【PACK】高价钴氧物种生成机理链.md` 当成直接机制证据。
- 直接宣称“Ce 已证明让 Co 价态升高，因此更易形成高价钴”。
- 把 `needs_manual_review` 题说成已经稳闭环。
- 不提 XPS / XANES 张力和待补证据。

### 3) high-valent metal-oxo / selective oxidation bridge
**成功信号**
- 会明确标注其为 `conceptual_bridge_candidate` / `uncertain`。
- 能区分：
  - high-valent metal-oxo 文献 = 机制概念源
  - 文献笔记 = 解释整理层
  - 聚合/选择性氧化框架文档 = 写作组织层
- 会说明：这里可迁移的是**概念框架、术语与候选路径语言**，不可直接迁移的是**体系特异结论、已证实机制与定量贡献占比**。
- 能体现“该读什么 / 不该读什么”的选择能力：当问题是 chlorite 主线机制时，该类只能作概念补充；当问题是写作组织或第二章桥接时，该类才进入前台。

**失败信号**
- 把跨主题 bridge 直接说成当前体系的直接证据。
- 把聚合框架或 GPT 文档当成科学事实证明。
- 只因都提到 high-valent metal-oxo / d-band，就默认 polymerization 或 selective oxidation 已成立。
- 不承认该类 closure 的 `uncertain` 属性。

## 结论
- **baseline 负责立尺子**：先校准检索命中、对象落点和 trace replay。
- **Ce-Co3O4 负责抓幻觉**：重点看模型是否误把候选证据说成已闭环，以及是否混淆 source layer。
- **bridge 负责测上限**：重点看模型是否会有限迁移，而不是跨体系乱借机制。

如果只先做一轮 `literature_closure` benchmark，建议采用：
1. 基线 chlorite 机制 × 2–3 题
2. Ce-Co3O4 / 电子结构迁移 × 2 题
3. bridge × 1 题（作为 advanced / exploratory）
