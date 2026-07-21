---
source_assets:
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/5ee0c395_test_cases_literature.md
  - assets/uploads/4abcbbd4_test_cases_experiment.md
created: 2026-03-22
---

# E_package_read_order
> 视角：**evaluator / benchmark builder**，不是 researcher。  
> 目标：先建立“可判分的读取路径”，再决定哪些 closure 值得下钻原始资产。
## 一、建议读取顺序
### 1. Layer 0：先读全局 closure registry
**文件：** `assets/uploads/ced68974_closure_mapping.md`
**目的：**
- 先建立 closure 全景，而不是先理解科研内容
- 先看有哪些 closure family：`literature_closure / experiment_closure / writing_closure`
- 先做 benchmark 路由：哪些适合 `context_hit_test / object_landing_test / trace_replay_test / writing_organization_test`
**这一层要确认：**
- closure family 是什么
- `research_line` 是什么
- `object_hint` 指向什么对象
- `suitable_tests` 对应哪些 evaluator 能力
- `status` 和 `uncertainty_tags` 是否允许先入 benchmark 池
- `source_files` 是否存在、是否足以支持后续下钻
---
### 2. Layer 1：再读 family-specific case index
**文件：**
1. `assets/uploads/5ee0c395_test_cases_literature.md`
2. `assets/uploads/4abcbbd4_test_cases_experiment.md`
**目的：**
- 从 closure 全景切到 benchmark seed 池
- 确认每个 case 为什么典型、适合测什么
- 先做 case 选池，不急着开原始件
**推荐顺序：**
- 先 literature index
- 再 experiment index
- 然后按“baseline → stress → challenge”交错读 case
**这一层要确认：**
- 该 case 是否是 benchmark 候选，而不只是研究素材
- case 的典型性来自哪里
- 它更适合做 baseline、stress 还是 challenge
- 该 case 的测试目标是命中、落对象、trace replay，还是写作组织
---
### 3. Layer 2：进入单个 closure / case
**推荐 case 顺序：**
1. **L1 基线机制文献簇**  
2. **E1 第二阶段性能筛选闭环**  
3. **L2 Ce-Co3O4 主逻辑迁移簇**  
4. **E2 第五阶段最小机理闭环**  
5. **E3 第六阶段高价钴直接证据链**  
6. **L3 d-band 到聚合路径跨主题综述簇**
**原因：**
- L1 / E1：最适合做第一批 baseline seed
- L2 / E2：适合做中等难度 stress cases
- E3 / L3：更适合做 challenge / boundary cases
**这一层要确认：**
- 该 closure 对应的具体对象是 literature、experiment，还是 writing pack
- closure 当前是“已形成可判分对象”，还是“只是概念桥 / 计划草图”
- 是否已有稳定 trace spine
- 是否需要继续下钻 `source_files`
---
### 4. Layer 3：优先下钻结构化 source files，而不是原始资产
**优先级：**
1. `source_files` 里的结构化 `.md`
2. 再看是否需要 PDF / PPTX / DOCX / raw outputs
**原则：**
- evaluator 先要最小可判分锚点，不先追求科研全理解
- 结构化 `.md` 足够支持 case card 时，不必默认开原始件
**这一层要确认：**
- object 有没有被钉死
- 输入上下文、目标输出、trace spine 是否可写成 case card
- 当前 source 文件说的是 hypothesis、protocol、result，还是 final pack
- 是否已经足够支持 benchmark 评分
---
### 5. Layer 4：只在触发条件出现时才下钻原始资产
**可能需要的原始资产：**
- PDF
- PPTX
- DOCX
- 原始输出 / 图表 / 运行结果
**这一层要确认：**
- 是否需要精确引用、图号、参数、版本号
- 是否要判定执行真实性
- 是否需要核查结构化 md 是否过度压缩或误转述
---
## 二、每一步要确认的对象
### Step A：读 closure mapping 时
要确认的不是“科学内容是否完整”，而是：
- **对象家族**：literature / experiment / writing
- **对象落点**：object_hint 能落到什么对象
- **测试用途**：适合哪些 evaluator tests
- **风险级别**：`status` + `uncertainty_tags`
- **后续入口**：`source_files` 是否清楚
### Step B：读 test case index 时
要确认：
- 这个 case 是不是 benchmark seed
- 它的“典型性”是否足够稳定
- 它要测的是命中、落对象、trace，还是写作组织
- 它更适合 baseline / stress / challenge 哪一档
### Step C：读单个 closure / source md 时
要确认：
- 具体对象是否已钉死
- case 的输入上下文是否明确
- 预期输出 / 正确落点是否明确
- trace spine 是否真实可复述
- 当前材料是在描述计划、执行，还是成品
### Step D：读原始资产时
要确认：
- 精确证据锚点是否存在
- 参数、图号、页码、版本信息是否可仲裁
- bridge 层总结与原始件是否一致
- case 是否真的达到了可做 hard gold 的程度
---
## 三、停止下钻条件
## 3.1 什么时候说明某个 closure 已经足够清晰，可以停止下钻
### A. 可停在 bridge 层
满足以下条件时，可停在：
- `closure_mapping.md`
- `test_cases_literature.md`
- `test_cases_experiment.md`
**条件：**
1. 当前目标只是 **case 选池 / coverage 规划**
2. closure identity 已经稳定：`research_line`、`object_hint`、case 描述不冲突
3. `suitable_tests` 已经足以映射 evaluator 任务
4. `status` 较稳，优先是 `strong_candidate`
5. `uncertainty_tags = none`
6. 当前不需要判定执行真实性，也不需要精确 quote / 参数 / 图号
**当前最适合这样停的 closure：**
- L1 基线机制文献簇
- E1 第二阶段性能筛选闭环
---
### B. 可停在结构化 source `.md` 层
满足以下条件时，可停在 `source_files` 对应的结构化 markdown，不继续翻原始件：
**条件：**
1. 已能写出最小 case card：object / input / expected landing / suitable tests / trace spine
2. 能分清对象类型：literature、experiment、writing 不混淆
3. 能分清材料是在讲 hypothesis、protocol、result，还是 final pack
4. 当前评分标准不要求 quote、图号、参数、页码、版本号
5. 已足够支持 soft scoring 或 baseline routing
---
## 3.2 什么时候必须离开 bridge 层，不能只停留在 bridge 层
任一条成立，都必须继续往下读：
1. `uncertainty_tags != none`
   - 如：`needs_manual_review / missing_context / uncertain`
2. `status` 提示 closure 仍未闭合
   - 如：`candidate_with_partial_manual_linking`
   - `candidate_missing_raw_output_files`
   - `high_value_but_partly_planned`
   - `conceptual_bridge_candidate`
   - `versioned_pack_candidate`
   - `strong_candidate_with_mixed_draft_status`
3. 你必须区分“计划 / 执行 / 成品”
4. 你要做 `trace_replay_test`，且需要可仲裁
5. bridge 层只能给方向，不能给锚点
6. 你无法明确指出该 closure 的主记录文件或真实对象
**当前必须离开 bridge 层的 closure：**
- L2 Ce-Co3O4 主逻辑迁移簇
- E2 第五阶段最小机理闭环
- E3 第六阶段高价钴直接证据链
- L3 d-band 到聚合路径跨主题综述簇
---
## 3.3 什么时候必须回源文件，不能只停在 bridge 或 source md
任一条成立，都必须继续到 PDF / PPTX / DOCX / raw outputs：
1. 你要做 **adjudicable hard gold**
2. 评分涉及 **精确引用 / 图号 / 参数 / 页码 / 版本号**
3. source `.md` 是摘要转述，而不是证据本体
4. closure 的核心对象本身就是最终件
   - 如 `.pptx` / `.docx`
5. 需要核查 bridge/source 层是否过度压缩、误转述、版本滞后
6. 需要判定执行真实性，而不是只看 protocol 或组织逻辑
7. `missing_context` 指向的缺口就在原始输出
8. 你要防止 benchmark 奖励“脑补式补全”
---
## 3.4 最简执行口令
### 可以停
**对象清楚、测试清楚、风险低，且当前不判执行真伪。**
### 必须离开 bridge 层
**只要出现 manual review / missing context / uncertain / partly planned / mixed draft，就别停。**
### 必须回原始资产
**只要你要判 quote、参数、图号、版本、最终件内容，或者要分清“计划 vs 执行”，就必须开原件。**
