---
source_assets:
  - assets/uploads/6abbf239_C_EXPERIMENT_TASK_BENCHMARK_RATIONALE.md
  - assets/uploads/f26a14af_【第二阶段】材料合成方法汇总.md
  - assets/uploads/d5740e86_【第二阶段实验脉络：Co3O4What？Why？How？】.md
created_at: 2026-03-22
---
# PACK_bootstrap_kickoff
> bootstrap seed pack：用于把当前 workspace 定义成“实验/Task 容器”，先服务本周实验排产与 task 拆解，而不是先进入论文故事或综述收束。
## meta
- `id`: PACK_bootstrap_kickoff
- `pack_type`: stage_report_pack
- `created_at`: 2026-03-22
- `time_range`: bootstrap phase
## task_refs[]
- 待创建：`TASK_week_sample_readiness`
- 待创建：`TASK_week_missing_sample_synthesis`
- 待创建：`TASK_week_performance_screening`
- 待创建：`TASK_week_promotion_gate`
## final_assets[]
- `memory/packs/PACK_bootstrap_kickoff.md`
## 这个包测什么
- 这个包不测“论文叙事是否完整”，而是测：**当前 workspace 能否把第二阶段材料与脉络信息收束成“本周要做什么实验”的 task 容器。**
- 核心判断对象不是综述问题，而是：**下一步该做哪些实验对象、这些对象属于哪类 task、先后顺序怎么排。**
- 这个包优先服务 3 件事：
 1. 明确 `experiment/task` 容器职责边界；
 2. 收敛本周优先实验对象；
 3. 给后续合成 checklist、性能筛选、最小机理闭环、Ce-Co3O4 任务板建立入口。
- 当前包的成功标准不是“讲清楚 Co3O4 的全部故事”，而是：**能把本周实验拆成可执行任务，并知道哪些线暂时不展开。**
## 先做哪类任务
### 1) 样品就绪/批次审计类 task
- 目标：先确认本周真正能上机、能比较、能复现的样品对象。
- 优先对象：`Co3O4 baseline`、`Ce-Co3O4`、`Cu-Co3O4`、`CeO2 control`。
- 作用：防止后续性能筛选建立在“样品未就绪 / 批次不一致 / 对照缺失”上。
### 2) 缺失样品补合成类 task
- 目标：只补本周筛选必须缺的对象，不补全整个材料库。
- 作用：让合成服务于任务落地，而不是把 workspace 变成合成大全或 SOP 仓库。
- 原则：优先补 baseline、关键候选样和必要对照；暂不全面扩展到所有掺杂和形貌分支。
### 3) 首轮性能筛选类 task
- 目标：用统一反应体系比较基线、候选与对照，判断谁值得继续投入。
- 关注指标：活性、重复性、基础稳定性、与对照差异。
- 这是当前最优先的主任务，因为它最直接回答：**接下来该做谁。**
### 4) 升级门槛判定类 task
- 目标：把筛选结果转成下一周动作，明确谁进入最小机理闭环、谁保留、谁暂停。
- 作用：避免“看到一点差异就立刻展开大机制/大综述/大写作”。
- 判定逻辑：至少满足性能差异明确、重复性可接受、对照齐全，才允许升级。
## 暂不展开的线
### A. 暂不展开综述/论文故事线
- 暂不先写 Co3O4 材料生态位综述；
- 暂不先组织论文主线叙事；
- 暂不先做“为什么是 Co3O4 而不是别的材料”的大段写作收束。
### B. 暂不展开全材料库扩张线
- 暂不把所有 0.5 mmol / 0.2 mmol 掺杂样全部纳入本周主线；
- 暂不平行推进过多形貌样、异质结样、碳耦合样；
- 暂不把容器做成“材料宇宙总表”。
### C. 暂不展开全面机理深挖线
- 暂不直接全面铺开 PMSO / ClO2 / EPR / 高价 Co 证据链；
- 暂不在对象未收敛前启动高成本强证据机理任务；
- 最小机理闭环应作为“筛选升级后的第二层任务”，而不是 bootstrap 起手任务。
### D. 暂不展开写作/PPT 交付线
- 暂不优先做组会故事板；
- 暂不优先做论文目录树；
- 暂不把结果整理重心放到对外表达，而优先放到 task 排产。
## takeaways[]
- 当前 workspace 的职责是“实验/Task 容器”，不是综述容器。
- bootstrap 第一优先不是合成大全，也不是机理大全，而是本周实验对象收敛。
- 最合适的起手顺序是：样品就绪审计 → 缺失样品补合成 → 首轮性能筛选 → 升级门槛判定。
- 合成 checklist 应作为对象 task 的附属支持层；最小机理闭环应作为升级后的第二层任务。
## narrative
- 当前阶段不追求讲完整研究故事。
- 叙事骨架只保留到“为什么本周先做这些 task”：
 1. 已有材料与脉络信息足够支持实验对象收敛；
 2. 当前最重要的是把候选样品与对照样整理成可执行 task；
 3. 只有筛选出值得推进的对象，后续才进入最小机理闭环与 Ce-Co3O4 任务板深化。
## limitations & risks
- 现有 `project.md` 仍未填写具体项目主线与量化判据，因此本包只能先定义容器职责与任务优先级，不能替代正式项目定义。
- 上传材料中已有较多综述式与顶层问题脉络，若不加限制，后续很容易重新滑回“研究总结”模式。
- 当前还没有真实落盘的周任务 `TASK_*.md`，因此本包只是 kickoff seed，而不是完整执行板。
## next_plan
1. 新建 `TASK_week_sample_readiness.md`：列出本周必测样品、批次状态、缺失对照。
2. 新建 `TASK_week_missing_sample_synthesis.md`：只补本周筛选缺的样品。
3. 新建 `TASK_week_performance_screening.md`：统一首轮筛选矩阵与记录字段。
4. 新建 `TASK_week_promotion_gate.md`：定义进入最小机理闭环的门槛。
5. 后续再按筛选结果决定是否进入 Ce-Co3O4 重点任务或最小机理闭环。
