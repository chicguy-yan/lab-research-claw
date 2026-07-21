---
source_assets:
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
created: 2026-03-21
---

# E_package_read_order
## Purpose
为 benchmark evaluator 提供一个 **closure package 的读取顺序与下钻阈值**。目标不是像 researcher 一样先读内容细节，而是先判断：
- 哪些 closure 值得入池
- 先读哪层索引
- 每一步要确认什么对象
- 什么时候停止下钻
- 什么时候必须回源文件
---
## 建议读取顺序
### Step 1：先读总索引层
**先读：** `closure_mapping.md`
**目的：**
- 识别 closure family：`literature_closure / experiment_closure / writing_closure`
- 识别每个 closure 的 `object_hint / suitable_tests / uncertainty_tags / status / source_files`
- 先做 evaluator shortlist，而不是先做内容理解
**建议输出：**
- A 档：benchmark 骨架候选
- B 档：扩展题/高价值题
- C 档：边界题/压力题
**本轮建议分档：**
- A 档：`L1`、`E1`
- B 档：`L2`、`E3`
- C 档：`L3`、`E2`
---
### Step 2：再读 case catalog 层
**先读：** `test_cases_literature.md`
**原因：**
- literature case 更适合先校准 `context_hit_test / object_landing_test`
- 对原始输出文件依赖更低，适合先把 benchmark schema 立住
**再读：** `test_cases_experiment.md`
**原因：**
- experiment case 更依赖 protocol / evidence / trace / 状态判断
- 适合在第一版评测框架形成后再引入
---
### Step 3：按 closure 优先级进入分组阅读
#### Literature closure
推荐顺序：`L1 → L2 → L3`
- `L1 基线机制文献簇`
  - 最适合做 literature benchmark 骨架
  - 适合测试：`context_hit_test`, `object_landing_test`, `trace_replay_test`
- `L2 Ce-Co3O4 主逻辑迁移簇`
  - 适合做主线迁移与 object landing 扩展题
- `L3 跨主题迁移簇`
  - 适合做边界题、hard case、over-retrieval 检测
#### Experiment closure
推荐顺序：`E1 → E3 → E2`
- `E1 第二阶段性能筛选闭环`
  - 最适合做 experiment benchmark 骨架
  - 适合测试：`trace_replay_test`, `object_landing_test`
- `E3 第六阶段高价钴直接证据链`
  - 高价值，但带部分计划态，适合第二批扩展
- `E2 第五阶段最小机理闭环`
  - 更适合做 missing-context / protocol-rich case
---
### Step 4：最后才决定是否下钻原始资产
默认原则：
- **先索引，后目录；先 closure，后 raw；先强候选，后困难题。**
- 不默认读所有原始 PDF / PPT / SOP
- 只对最终入选 closure 做最小充分回源
**原始资产下钻优先级：**
1. 先读 md 笔记 / 实验记录
2. 再读 SOP / 工作文档
3. 最后才读 PDF / PPT / docx 原件
---
## 每一步要确认的对象
### Step 1：总索引层要确认的对象
在 `closure_mapping.md` 中先确认：
- 这是哪一类 closure：`literature / experiment / writing`
- `research_line` 是否清楚
- `object_hint` 是否足以判断对象落点
- `suitable_tests` 是否足以确定 benchmark lane
- `status / uncertainty_tags` 是否提示风险
- `source_files` 是否给出了最小回源路径
**此步的对象不是事实内容，而是：**
- `closure identity`
- `评测用途`
- `风险等级`
---
### Step 2：case catalog 层要确认的对象
在 `test_cases_literature.md` / `test_cases_experiment.md` 中确认：
- 为什么这个 case 典型
- 更适合测哪类测试
- 该 case 更像 `Concept / Task / Pack` 中的哪类工作对象
- 是否值得进入第一批 benchmark
**此步的对象是：**
- `case worthiness`
- `object landing expectation`
- `difficulty tier`
---
### Step 3：closure 层要确认的对象
进入某个具体 closure 时，确认：
- closure 边界是否唯一
- 与邻近 closure 是否容易混淆
- 该 closure 的主对象是 `Concept`、`Task` 还是 `Pack`
- 是否需要细化到 trace skeleton
- 当前是否已经足够做 benchmark case card
**推荐主对象判断：**
- `L1`：偏 `Concept`
- `L2`：`Concept` 向实验主线桥接
- `L3`：偏 `Concept/Pack` 边界测试
- `E1`：偏 `Task`
- `E2`：偏 `Task`，但需审计 evidence 缺口
- `E3`：`Task + Pack` 联动
---
### Step 4：raw 层要确认的对象
只有在决定回源后，才确认：
- 该 closure 的 gold anchor 是哪份原始资产
- 是否存在“计划态 / 草图态 / 完成态”混淆
- 是否真有证据链，而不只是 bridge 层组织得漂亮
- trace 顺序是否有唯一或近唯一的最小路径
**此步的对象是：**
- `gold evidence anchor`
- `state validation`
- `minimal trace path`
---
## 停止下钻条件
### A. 可以停止下钻的条件
当以下条件大部分成立时，可以停在 bridge 层，不继续翻更多原始资产：
1. 已能唯一确定 closure 身份
2. 已能判断其适合的测试类型
3. 已能判断主对象应落 `Concept / Task / Pack` 中哪类
4. `status` 稳定，且 `uncertainty_tags` 不提示明显风险
5. 当前 benchmark 只做骨架设计，不做证据级答案键
6. 当前不需要判定“计划态 vs 完成态”
**经验性规则：**
以下 6 项里满足 5 项以上，通常可停：
- closure 名称和边界唯一
- object_hint 足以确定对象落点
- suitable_tests 已清楚
- status/uncertainty 无明显风险
- source_files 已足够描述最小路径
- 当前 benchmark 不要求证据级 gold label
---
### B. 必须回源文件的条件
出现以下任一条，就不能只停留在 bridge 层：
1. `uncertainty_tags` 或 `status` 带风险信号，例如：
   - `needs_manual_review`
   - `missing_context`
   - `uncertain`
   - `candidate_with_partial_manual_linking`
   - `high_value_but_partly_planned`
2. 需要制作可判分的 gold answer / gold anchor
3. 需要区分“计划态 / 草图态 / 已完成态”
4. bridge 层无法唯一决定对象落点
5. 需要评估细粒度 `trace_replay_test`
6. bridge 层信息之间存在张力，无法自行消解
---
### C. 最小充分回源原则
回源不等于全量读完所有原始资产，只做 **最小充分回源**。
#### literature case
优先顺序：
1. 文献笔记 md
2. 1 篇核心 PDF
若已能确认主题边界、机制对象和纳入理由，就停止。
#### experiment case
优先顺序：
1. 实验记录 / 阶段脉络 md
2. 1 份关键 SOP 或方法 md
3. 必要时再看 Pack / PPT / 原始输出
若已能确认任务目标、实验链条、状态边界，就停止。
---
## closure 级执行建议
### 可先停在 bridge 层的 closure
- `L1`：适合先做 literature benchmark 骨架
- `E1`：适合先做 experiment benchmark 骨架
### 默认应回源的 closure
- `L2`：带 `needs_manual_review`，且涉及文献到实验主线桥接
- `L3`：带 `uncertain`，适合边界题，但不能长期停在 bridge 层
- `E2`：带 `missing_context`，要判断 protocol-rich 还是 evidence-complete
- `E3`：带 `high_value_but_partly_planned`，必须区分计划态与完成态
---
## 最终执行口径
### evaluator 的默认顺序
1. `closure_mapping.md`
2. `test_cases_literature.md`
3. `test_cases_experiment.md`
4. 第一批：`L1`, `E1`
5. 第二批：`L2`, `E3`
6. 第三批：`L3`, `E2`
7. 仅对最终入选 closure 做最小充分回源
### evaluator 的默认停手原则
> 能在 bridge 层唯一回答“它是什么、测什么、对象落哪、是否值得入池”时，就停止下钻；
> 一旦要回答“证据锚点是什么、状态是否完成、trace 是否真实”，就必须回源文件。
