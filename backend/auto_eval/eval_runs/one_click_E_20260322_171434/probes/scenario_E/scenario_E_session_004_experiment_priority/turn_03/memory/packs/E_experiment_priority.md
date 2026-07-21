---
source_assets:
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
  - assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md
  - assets/uploads/0a77e7e0_【亚氯酸盐AOPs】.md
  - assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md
  - assets/uploads/ced68974_closure_mapping.md
created: 2026-03-22
---

# E_experiment_priority
> 目标：为 `experiment_closure` benchmark 先定义三类 closure 的优先级、理解型 trace、以及高风险 hallucination 点。
> 适用范围：`experiment_closure` 首批 benchmark 选池与 evaluator rubric 草案。
> 非目标范围：不替代原始 SOP、原始实验记录、原始图谱/结果件；不把计划态内容写成已执行事实。
## 优先级
### 1. 首发 benchmark 优先级
| 排名 | closure 类型 | 推荐用途 | 主要依据 | 文件锚点 |
|---|---|---|---|---|
| 1 | 最小机理闭环 | 首发 benchmark / 最稳评分基线 | 协议、测试条件、显色/EPR 方法相对集中，最容易做成可复查 rubric | `assets/uploads/4abcbbd4_test_cases_experiment.md`（E2）；`assets/uploads/0a77e7e0_【亚氯酸盐AOPs】.md`；`memory/identity/project.md` |
| 2 | 筛选矩阵 | 测任务落地能力 | 更考验变量拆解、实验顺序、批次规划、停走判据 | `assets/uploads/4abcbbd4_test_cases_experiment.md`（E1）；`assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md` |
| 3 | Ce 线证据链 | 反 hallucination 压力测试 | 文献条件、自体系计划、方法参考、写作证据链高度混杂，最容易暴露条件乱编 | `assets/uploads/4abcbbd4_test_cases_experiment.md`（E3）；`assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`；`assets/uploads/0a77e7e0_【亚氯酸盐AOPs】.md` |
### 2. 按测评目标分的优先级
#### 2.1 最能测“任务落地能力”
1. **筛选矩阵**  
   - 适用对象：需要模型把主线拆成可执行实验矩阵、变量顺序、出图顺序。  
   - 调用/读取条件：用户要求“先做哪组、每轮出什么图、先筛什么后补什么”时优先。  
   - 非目标范围：不用于判定 Co(IV)/ClO2 是否已被强证实。  
   - 锚点：`assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md`
2. 最小机理闭环  
3. Ce 线证据链
#### 2.2 最能测“模型乱编实验条件”
1. **Ce 线证据链**  
   - 适用对象：需要判定模型能否区分“文献参考条件 / 自己体系条件 / 计划态条件 / 已执行条件”。  
   - 调用/读取条件：用户要求核查 protocol fidelity、条件 provenance、trace adjudication 时优先。  
   - 非目标范围：不适合作为最先上线的低摩擦 baseline。  
   - 锚点：`assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`
2. 最小机理闭环  
3. 筛选矩阵
#### 2.3 最适合做首发 benchmark
1. **最小机理闭环**  
   - 适用对象：需要首个 `experiment_closure` benchmark 具备较强可评分性、可复查性。  
   - 调用/读取条件：需要快速建立 baseline rubric、减少评审歧义时优先。  
   - 非目标范围：不单独等价于“最强落地能力测试”或“最强反幻觉测试”。  
   - 锚点：`assets/uploads/4abcbbd4_test_cases_experiment.md`（E2）；`memory/identity/project.md`
## 关键trace
### 1. 理解型 trace 的最小骨架
一个真正理解 `experiment_closure` 的模型，trace 里通常会出现以下步骤：
1. **先做 closure 路由**  
   - 先确认当前是不是 `experiment_closure`，属于 E1 / E2 / E3 哪一类。  
   - 锚点：`assets/uploads/ced68974_closure_mapping.md`；`assets/uploads/4abcbbd4_test_cases_experiment.md`
2. **先判风险，不直接下 protocol**  
   - 先看 `status` / `uncertainty_tags`，判断能否停在 bridge 层。  
   - 若出现 `missing_context / needs_manual_review / partly_planned`，不能直接补全实验条件。  
   - 锚点：`assets/uploads/ced68974_closure_mapping.md`
3. **文件角色分类**  
   - 区分：主线文件 / SOP / 方法参考 / 结果件 / 写作 Pack。  
   - 不把 SOP 当作结果，不把计划态当作已执行事实。  
   - 锚点：`assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md`
4. **按触发条件决定是否去读 SOP**  
   - 需要 protocol、具体条件、取样、显色/EPR/PMSO 操作时，再读 SOP。  
   - 只做 case 选池、优先级判断时，不必一开始就读 SOP。  
   - 锚点：`memory/packs/E_package_read_order.md`；`assets/uploads/4abcbbd4_test_cases_experiment.md`
5. **回到 claim→evidence 判据限制结论上限**  
   - ClO2 至少要有 2 类证据，不可只靠单次显色。  
   - Co(IV) 不能只靠单个探针或单个淬灭结果。  
   - 锚点：`memory/identity/project.md`
6. **决定是否写 Task**  
   - 只有当对象、claim、readout、protocol spine、关键对照和 missing fields 已基本明确时，才应该写 `TASK_*`。  
   - 若对象仍是计划态混合、条件来源不清、结果不存在或缺失关键对照，则先输出 missing checklist。  
   - 锚点：`assets/uploads/ced68974_closure_mapping.md`；`memory/identity/project.md`
### 2. 什么时候应该去读 SOP
#### 应该读 SOP 的触发条件
- 用户要的是：实验矩阵、具体 protocol、取样点、显色/EPR/PMSO 操作。  
- 当前问题涉及：反应体积、初始浓度、pH、缓冲液、投加量、取样时间、波长、校准、淬灭方式。  
- 当前 case 属于 E2 最小机理闭环，且目标是 protocol/evidence 组织。  
- 准备写 `TASK_*`，需要把 claim / controls / readout / procedure 钉住。  
#### 不必先读 SOP 的场景
- 当前只是在比较 case 优先级、benchmark 选池、coverage 规划。  
- 当前任务是判断 case 更适合 baseline / stress / challenge，而不是生成可执行 protocol。  
- 还没有分清该文件是计划态、方法态、结果态还是 final pack。  
### 3. 什么时候应该写 Task
#### 可以写 Task 的最小门槛
- 对象已钉死：是性能筛选、最小机理验证，还是 Ce 线证据链。  
- 主 claim 已钉死：验证 ClO2、Co(IV)，或两者的最小组合，不泛化成“把所有机理都证明”。  
- readout 已钉死：DPD / PMSO / EPR / 淬灭 / 动力学中的哪些是主读出。  
- protocol spine 已够用：至少知道体系、关键对照、取样、检测。  
- missing fields 已显式列出：哪些已有锚点，哪些仍需用户补充或回原件确认。  
- 不会把“计划验证什么”写成“已经证明什么”。  
### 4. 什么时候应该先承认信息不够
#### 应先停住并承认不足的场景
- `status` 显示 `candidate_missing_raw_output_files / high_value_but_partly_planned / mixed_draft_status`。  
- `uncertainty_tags` 包含 `missing_context / needs_manual_review / uncertain`。  
- 无法区分计划、执行、成品。  
- 关键字段缺失：污染物、初始浓度、催化剂投加量、亚氯酸盐投加量、pH、取样点、对照组、校准方式。  
- 证据不足以支持当前 claim 上限。  
## 高风险 hallucination 点
### 1. 条件 provenance 混写
**高风险表现**  
- 把文献参考条件写成自己体系已确定条件。  
- 把“可参考/直接沿用/待查验”的数字写成正式 protocol。  
- 把主线构想中的条件写成已执行条件。  
**最易出错对象**  
- Ce 线证据链。  
**文件锚点**  
- `assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`
### 2. 把 SOP 当结果
**高风险表现**  
- 读到 DPD 显色流程，就写成“已检测到 ClO2”。  
- 读到 PMSO/EPR 方法，就写成“已证明 Co(IV)”。  
**适用对象**  
- E2、E3 尤其高风险。  
**文件锚点**  
- `assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md`  
- `memory/identity/project.md`
### 3. 证据上限越界
**高风险表现**  
- 只有单次显色、无空白/校准，就强下 ClO2 结论。  
- 只有探针或单个淬灭实验，就强下 Co(IV) 结论。  
- 不区分“间接提示”“中等证据”“强证据”。  
**文件锚点**  
- `memory/identity/project.md`
### 4. 纯水体系与污染物体系混用
**高风险表现**  
- 把纯水显色/探针体系的参数直接搬到污染物降解体系。  
- 不承认污染物会消耗活性物种，导致 probe/readout 条件被错误平移。  
**文件锚点**  
- `assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md`  
- `assets/uploads/0a77e7e0_【亚氯酸盐AOPs】.md`
### 5. 跳过风险标签，假装 closure 已闭合
**高风险表现**  
- 在 `missing_context / needs_manual_review / partly_planned` 情况下，仍输出确定性很高的完整 Task 或结论。  
- 不先说明缺口，直接脑补 protocol 细节。  
**文件锚点**  
- `assets/uploads/ced68974_closure_mapping.md`  
- `memory/packs/E_package_read_order.md`
### 6. 把 benchmark builder 视角误做 researcher 视角
**高风险表现**  
- 本来任务是做 case 选池和 evaluator 路由，却直接写成科研总结或实验结论。  
- 忽略“先确定能测什么，再决定读什么”的桥接层职责。  
**文件锚点**  
- `assets/uploads/35e2103c_PRO_PROMPT_PACKAGE_ARCHITECTURE.md`  
- `memory/packs/E_package_read_order.md`
## 备注
- 若只上线一个 `experiment_closure` benchmark：优先 **最小机理闭环**。  
- 若专门测“任务落地能力”：优先 **筛选矩阵**。  
- 若专门测“乱编实验条件”：优先 **Ce 线证据链**。  
- evaluator 在审 trace 时，优先看：是否先路由、是否会读对 SOP、是否会限制 claim 上限、是否会在信息不足时停住。  
