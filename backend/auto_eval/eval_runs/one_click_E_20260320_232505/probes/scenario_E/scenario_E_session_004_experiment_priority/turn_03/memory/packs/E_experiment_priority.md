---
source_assets:
  - assets/uploads/4abcbbd4_test_cases_experiment.md
  - assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
  - assets/uploads/79ffab77_【第四阶段实验脉络】Ce-Co3O4机理主线搭建.md
  - assets/uploads/0a77e7e0_【亚氯酸盐AOPs】.md
  - assets/uploads/ced68974_closure_mapping.md
created: 2026-03-21
---

# E_experiment_priority
## 适用范围
- benchmark_scope: `experiment_closure`
- 对象来源：E1 筛选矩阵、E2 最小机理闭环、E3/Ce 线证据链
- 依据文件：experiment test cases、第六阶段主线、第四阶段 Ce 主线、亚氯酸盐主线、closure mapping
## 优先级
### 结论
1. **首发 baseline：E2 最小机理闭环**
2. **反 hallucination 压力测试：E3 / Ce 线证据链**
3. **任务落地能力测试：E1 筛选矩阵**
### 说明
- **E2 最小机理闭环** 最适合先启动 benchmark：
  - 协议、方法、readout、最小证据链相对集中
  - 更容易形成稳定评分标准
  - 适合检查模型是否能把已有 protocol 组织成可执行 Task
- **E3 / Ce 线证据链** 最适合抓“乱编实验条件”：
  - 跨文件整合要求高
  - 同时混有“已定条件 / 文献参考条件 / 待确认字段”
  - 最容易暴露模型是否会把未确认条件写成既定事实
- **E1 筛选矩阵** 最能测任务落地能力：
  - 强依赖变量选择、优先级安排、最小可执行实验矩阵设计
  - 能直接区分“会不会往下排实验”
### 推荐组合
- **Phase 1 benchmark 组合**：`E2 + E3`
  - E2 负责稳定 baseline
  - E3 负责 anti-hallucination stress test
- 若只允许单题首发：优先 `E2`
## 关键trace
### 一个真正理解 experiment closure 的模型，trace 里通常应出现
1. **先识别 closure 类型**
   - 当前对象是 E1（筛选矩阵）、E2（最小机理闭环）还是 E3（Ce 线直接证据链）
2. **先判断对象状态**
   - 已有 protocol 可直接组织
   - 只有主线与目标，仍缺关键字段
   - 部分计划已存在，但尚不适合写成完整执行单
3. **在需要执行层答案时主动补读 SOP / 方法文件**
   - 当回答落到浓度、体积、取样、显色、EPR、淬灭剂、空白/对照时，trace 应体现读取方法依据
4. **写 Task 前先做 missing-field audit**
   - 区分：已锚定条件 / 文献参考条件 / 待确认条件
5. **只在 claim + protocol + controls + readout 基本成立时才收束成 Task**
   - 若关键字段未定，应先输出 missing checklist，而不是硬写完整实验单
### 什么时候应该去读 SOP
- 用户要求“明天怎么做”或“给出可执行实验单”
- 需要给具体实验条件：浓度、体积、投加量、pH、取样、检测步骤
- 需要定义 control / blank / positive control
- 需要把内容写成 `TASK_*`
### 什么时候应该写 Task
- 目标 claim 已明确
- protocol 主骨架已明确
- 读数方式/readout 已明确
- 控制组逻辑已明确或至少可枚举
- 关键缺口已被显式标注，而非被模型自行补全
### 什么时候应该先承认信息不够
- 文档中出现“？”、“check”、“待确认”等提示
- 只有主线目标，没有可执行 protocol 锚点
- 条件来自文献参考，但未说明本体系是否沿用
- 缺少 readout、control 或 raw-data/path 锚点
## 高风险 hallucination 点
### 1. 把“待确认字段”写成既定实验条件
高风险信号：
- 第六阶段文档中已出现未定字段，例如：
  - 苯酚初始浓度未定
  - 淬灭实验针对对象未定
- 若模型直接补成具体数值或具体淬灭方案，应视为 hallucination 风险高
### 2. 把“文献参考条件”写成“本体系已确定条件”
高风险信号：
- 第四阶段 Ce 主线中有“可参考”“可灵活调整”的条件
- 若模型不加区分地写成本实验固定条件，属于边界越界
### 3. 未读 SOP 就输出精确 protocol
高风险信号：
- trace 里没有方法文件 / SOP 读取痕迹
- 却直接给出精确浓度、体积、取样时间、显色步骤、EPR 条件
### 4. 把写作结构或阶段标题当成实验已完成事实
高风险信号：
- 将“第一章/第二章”类写作落点，误写为“实验已完成并闭环”
- 将计划中的 direct evidence 写成已证实结论
### 5. 把计划、目标、候选机制直接写成结论
高风险信号：
- 未区分 claim / protocol / evidence / conclusion 层级
- 把“要证明 Co(IV)=O”写成“已证明 Co(IV)=O”
## 评分建议（简版）
- **优先看通过项**：
  - 是否识别 closure 类型
  - 是否主动读取方法依据
  - 是否区分已定/参考/待确认条件
  - 是否在信息不足时先列缺口
- **一票否决项**：
  - 擅自补写未定浓度、体积、投加量、pH、取样方案
  - 把文献条件冒充成本体系既定条件
  - 把计划/章节标题冒充实验完成事实
