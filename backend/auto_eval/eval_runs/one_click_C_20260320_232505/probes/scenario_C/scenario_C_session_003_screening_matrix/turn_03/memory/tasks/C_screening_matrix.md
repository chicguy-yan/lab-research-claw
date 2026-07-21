---
source_assets:
  - assets/uploads/d5740e86_【第二阶段实验脉络：Co3O4What？Why？How？】.md
  - assets/uploads/a57679b8_【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md
  - assets/uploads/13b70f39_【Graphpad】性能体系：性能+动力学.md
created: 2026-03-21
---

# C_screening_matrix
## 目的
为第二阶段 `M-Co3O4` 材料筛选建立一套可复现的“性能 + 动力学”比较框架，用于判断：
- 当前是否已经锁定一个**稳定且可复现的 Co3O4 母体平台**；
- 当前候选样（尤其是低掺杂 Cu-Co3O4）是否具备**持续、稳定、可放大的优势**；
- 是否值得进入下一步 **Ce-Co3O4 升级**。
> 当前结论上限：在进入 Ce 之前，应优先区分“元素效应”“合成路线效应”“批次波动效应”。
---
## 材料维度
### 1. 横轴设计原则
横轴不要只写“材料名”，应写成：
`材料家族 × 合成路线 × 掺杂信息 × batch × replicate`
否则后续无法区分：
- Co3O4 本征效应
- 合成路线差异
- 掺杂元素效应
- 独立制样批次波动
### 2. 推荐横轴一级分组
| 编码 | 材料 | 角色 |
|---|---|---|
| X0 | 无催化剂空白 | 判断非催化背景降解 |
| X1 | Co3O4-主线基准样 | 作为所有升级路线的比较基线 |
| X2 | Co3O4-路线替代样 A | 判断路线效应是否大于掺杂效应 |
| X3 | Co3O4-路线替代样 B | 判断形貌/配位史是否值得保留 |
| X4 | Cu-Co3O4（低掺杂优先） | 当前最有希望的非 Ce 候选 |
| X5 | 代表性失败掺杂样 | 证明“不是所有掺杂都有效” |
| X6 | 历史最佳 Co3O4 回标样 | 检验最优结果是否可复现 |
### 3. 必须保留的样品身份字段
每个样必须至少有以下标识字段：
- `sample_id`
- `material_family`
- `route_id`
- `dopant`
- `dopant_nominal`
- `batch_id`
- `replicate_id`
### 4. 推荐样品编码方式
- `Co3O4_H2O_B20260321`
- `Co3O4_NH3_B20260321`
- `CuCo3O4_EG_B20260321`
### 5. Ce 升级前的材料判断门槛
只有同时满足以下条件，才建议推进 Ce-Co3O4：
1. 已锁定一个稳定 Co3O4 母体路线；
2. 候选升级样相对 Co3O4 的优势在多个独立 batch 中方向一致；
3. 当前瓶颈是性能/持续性天花板，而不是制样波动；
4. 能明确说明 Ce 预期解决的问题（如电子缓冲、氧空位调控、高价态稳定等）。
---
## 性能维度
### 1. 纵轴总体原则
纵轴不能只保留一个 `kobs`，至少应覆盖：
- 性能层：快不快、能不能持续、最终上限如何；
- 动力学层：能否用统一窗口可靠比较；
- 可复现性层：优势是否稳定；
- 升级价值层：是否值得进入 Ce。
### 2. 必须保留的性能/动力学指标
| 维度 | 指标 | 是否必须 | 作用 |
|---|---|---|---|
| 性能 | 5 min 去除率 | 必须 | 看启动能力 |
| 性能 | 10 min 去除率 | 必须 | 主筛选时间点 |
| 性能 | 20 min 或 30 min 去除率 | 必须 | 看反应上限 |
| 动力学 | `kobs` | 必须 | 主动力学指标 |
| 动力学 | `R²` | 必须 | 判断拟合是否可靠 |
| 动力学 | 拟合时间窗口 | 必须 | 保证不同样品可比 |
| 动力学 | 初始速率 `v0` 或前 5 min 斜率 | 强烈建议 | 区分前快后慢 |
| 复现性 | 同批平行 CV | 必须 | 看操作波动 |
| 复现性 | 跨批次 CV | 必须 | 看制样稳定性 |
| 稳定性 | 循环保持率 | 强烈建议 | 判断是否只是一次性高活性 |
| 稳定性 | 金属溶出（ICP） | 强烈建议 | 防止以牺牲稳定性换速率 |
| 决策 | 是否值得进入 Ce | 必须 | yes / no / pending |
### 3. 推荐筛选矩阵骨架
| 纵轴 / 横轴 | X0 空白 | X1 Co3O4-基准 | X2 路线A | X3 路线B | X4 Cu-Co3O4 | X5 失败掺杂样 | 备注 |
|---|---:|---:|---:|---:|---:|---:|---|
| 5 min 去除率 |  |  |  |  |  |  | 启动能力 |
| 10 min 去除率 |  |  |  |  |  |  | 主筛选时间点 |
| 20/30 min 去除率 |  |  |  |  |  |  | 上限 |
| `kobs` |  |  |  |  |  |  | 主动力学指标 |
| `R²` |  |  |  |  |  |  | 拟合可靠性 |
| 拟合窗口 |  |  |  |  |  |  | 必须统一 |
| 初始速率 `v0` |  |  |  |  |  |  | 前 5 min |
| 同批 CV |  |  |  |  |  |  | 平行重复性 |
| 跨批 CV |  |  |  |  |  |  | 制样稳定性 |
| 循环保持率 |  |  |  |  |  |  | 稳定性 |
| ICP 溶出 |  |  |  |  |  |  | 应用代价 |
| 值不值得进 Ce |  |  |  |  |  |  | yes / no / pending |
### 4. 最小数据表模板
为保证后续可重画图、重做拟合，建议至少分 6 张表：
#### 4.1 `sample_registry`
记录样品身份主索引：
```text
sample_id,material_family,route_id,dopant,dopant_nominal,batch_id,synthesis_date,calcination_program,notes
```
#### 4.2 `run_metadata`
记录每一次性能测试反应条件：
```text
run_id,sample_id,replicate_id,repeat_type,pollutant,C0_pollutant,C0_unit,oxidant,oxidant_conc,catalyst_dose,solution_volume,pH_initial,temperature_C,stirring_rpm,quench_method,analysis_method,instrument_file,operator,remarks
```
#### 4.3 `raw_timecourse_long`
记录原始时序数据：
```text
run_id,sample_id,replicate_id,time_min,raw_signal,raw_signal_unit,dilution_factor,blank_corrected_signal,Ct,Ct_unit,data_status,raw_file_ref,note
```
#### 4.4 `normalized_curve`
记录归一化降解曲线：
```text
run_id,sample_id,replicate_id,time_min,C0_used,Ct,Ct_over_C0,removal_pct,C0_source,normalization_note
```
#### 4.5 `pfo_fit`
记录伪一级拟合结果：
```text
fit_id,run_id,sample_id,replicate_id,fit_formula_text,y_transform,x_variable,fit_window_start,fit_window_end,included_points,excluded_points,slope,intercept,kobs,kobs_unit,R2,fit_software,graphpad_table_ref,fit_note
```
#### 4.6 `summary_for_plot`
记录均值、误差线与重复实验汇总：
```text
group_id,sample_id,batch_scope,n_replicates,metric_name,mean,sd,se,cv_pct,error_bar_type,points_source,plot_note
```
### 5. 现在不记，后面就很难可靠重画图的关键字段
#### 身份类红线字段
- `sample_id`
- `route_id`
- `batch_id`
- `replicate_id`
#### 反应条件类红线字段
- `pollutant`
- `C0_pollutant`
- `oxidant_conc`
- `catalyst_dose`
- `solution_volume`
- `pH_initial`
- `temperature_C`
- `quench_method`
#### 原始测量类红线字段
- `time_min`
- `raw_signal`
- `dilution_factor`
- `Ct`
- `raw_file_ref`
#### 归一化类红线字段
- `C0_used`
- `C0_source`
- `Ct_over_C0`
#### 拟合类红线字段
- `fit_formula_text`
- `y_transform`
- `fit_window_start`
- `fit_window_end`
- `included_points`
- `excluded_points`
- `kobs`
- `R²`
#### 误差线定义类红线字段
- `n_replicates`
- `error_bar_type`
- `points_source`
---
## GraphPad输出要求
### 1. 必留图与拟合结果
#### 图 1：原始 `C/C0 - t` 曲线
必须保留：
- 所有材料在同一张图上的归一化降解曲线；
- 尽量显示均值 ± SD；
- 如条件允许，保留每个平行点。
用途：
- 比较启动快慢；
- 判断是否存在平台期；
- 识别异常点。
#### 图 2：伪一级线性拟合图
必须保留：
- 明确的 Y 轴变换形式；
- 线性拟合曲线；
- 斜率、截距、`R²`；
- 统一的拟合时间窗口。
关键要求：
- 所有样品使用同一公式、同一单位、同一时间窗口；
- 若某些点被剔除，必须在数据表中记录原因。
#### 图 3：`kobs` 汇总图
建议做成点图或点+均值图，而不是只做柱状图。
必须保留：
- 每个样品的单个 replicate `kobs`；
- 均值 ± SD；
- batch 信息（颜色或分组）。
#### 图 4：batch-to-batch 重复性图
横轴为 `batch_id`，纵轴为 `kobs` 或 10 min 去除率。
用途：
- 判断候选样优势是否稳定；
- 区分“偶然最好”与“可复现更优”。
### 2. GraphPad 结果不能只保留截图
至少要保留以下可追溯结果：
- 原始导入数据表；
- 归一化后数据表；
- 变换后的拟合数据表；
- 拟合公式；
- slope；
- intercept；
- `R²`；
- 若有，标准误或 95% CI；
- 使用的软件版本或文件名；
- `graphpad_table_ref` / `graphpad_file_ref`。
### 3. GraphPad 拟合的最低记录要求
每次拟合至少补记：
- `fit_formula_text`
- `y_transform`
- `fit_window_start`
- `fit_window_end`
- `included_points`
- `excluded_points`
- `kobs`
- `R²`
如果这些字段不记录，后续即使保留了图，也难以严格复现原始拟合。
### 4. 误差线与重复实验的图注要求
图注中必须明确：
- 误差线是 `SD` 还是 `SE`；
- `n` 的定义是同批平行，还是独立 batch；
- `kobs` 是基于单个 replicate 拟合后汇总，还是基于均值曲线拟合。
推荐做法：
- 先对每个 replicate 单独拟合 `kobs`；
- 再对多个 `kobs` 做均值 ± SD；
- 不优先对均值曲线直接拟合唯一 `kobs`。
---
## 当前建议的 go / no-go 逻辑
### 建议继续停留在 Co3O4 平台优化的情形
- 路线差异大于掺杂差异；
- 同一候选样跨 batch 表现方向不一致；
- 当前主要问题是制样和批次波动，而不是性能上限。
### 可以考虑进入 Ce-Co3O4 的情形
- 已锁定稳定的 Co3O4 母体路线；
- 候选样提升方向在多个 batch 中一致；
- `kobs`、固定时间点去除率、循环稳定性都表现出持续优势；
- 已能明确 Ce 的预期作用，而非盲目增加变量。
