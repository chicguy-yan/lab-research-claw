---
source_assets:
  - assets/uploads/d5740e86_【第二阶段实验脉络：Co3O4What？Why？How？】.md
  - assets/uploads/a57679b8_【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md
  - assets/uploads/13b70f39_【Graphpad】性能体系：性能+动力学.md
created: 2026-03-22
---

# C_screening_matrix — 第二阶段性能+动力学筛选矩阵

> 目的：把“材料做出来”推进到“能否作为 Ce-Co3O4 升级底座”的筛选层。  
> 依据来源：
> - `assets/uploads/d5740e86_【第二阶段实验脉络：Co3O4What？Why？How？】.md`
> - `assets/uploads/a57679b8_【第二阶段实验记录：M-Co3O4亚氯酸盐活化选择性降解污染物】.md`
> - `assets/uploads/13b70f39_【Graphpad】性能体系：性能+动力学.md`
> - `memory/identity/project.md`

---

## 一、材料维度

### 1.1 主筛选横轴：不要只按“材料名”，要按“材料类型 × 批次”展开

建议主矩阵横轴保留以下 4 组：

1. **Co3O4-baseline**  
   - 作用：当前所有升级路线的基线材料。  
   - 必须保留理由：后续 Ce-Co3O4、Cu-Co3O4、路线优化都需要相对它判断是否真实提升。

2. **Cu-Co3O4**  
   - 作用：当前已有过性能亮点的轻掺杂候选。  
   - 已知风险：第二阶段记录提示其在 0.2 mmol 时曾筛出，但后续批次又出现明显波动，甚至不再优于 Co3O4。  
   - 结论：不能只看一次亮点，必须强制纳入批次重复。

3. **H2O-route / 纯水路线 Co3O4**  
   - 作用：合成路线对照。  
   - 用途：判断“路线效应”是否大于“掺杂效应”。

4. **NH3-route Co3O4**  
   - 作用：碱供给/配位史对照。  
   - 用途：判断表面位点化学、配位环境和规整度是否影响动力学与稳定性。

### 1.2 每种材料至少分 3 个独立批次

每种材料建议至少记录：
- `Batch-1`
- `Batch-2`
- `Batch-3`

原因：第二阶段实验记录已经表明，当前最大的风险不是“有没有单次更快”，而是**材料效应是否会被批次效应盖掉**。

### 1.3 暂不放入主矩阵的材料

以下对象不建议挤入主筛选主表，可放附录：
- 0.5 mmol 掺杂后普遍抑制的材料
- 只有单次亮点、没有重复批次的数据
- 反应条件不一致的数据

原因：主矩阵的任务是做 Go / No-Go 决策，而不是回收所有历史样品。

### 1.4 对 Ce-Co3O4 升级的直接启示

只有在以下前提满足时，才值得把 Ce 加进来：
- Co3O4 基线材料的活性与重复性已经稳定；
- 现有改性（尤其 Cu）的问题已经明确是“位点/高价态/稳定性瓶颈”，而不是“合成路线噪声”；
- 不同路线样品在统一条件下已经完成横向比较。

---

## 二、性能维度

性能纵轴建议分为 **性能主指标、动力学拟合质量、真实性指标、重复性指标** 四层。

### 2.1 性能主指标

以下指标建议进入主矩阵：

| 指标 | 是否必须 | 作用 |
|---|---|---|
| 去除率 @ 固定时间（如 10/20/30 min） | 必须 | 最直观比较不同材料启动与终点表现 |
| `k_obs` | 必须 | 主动力学指标，用于横向筛选 |
| `t50` / `t90` | 推荐 | 比单点去除率更稳，便于汇报 |
| 初始速率（前 5–10 min 斜率） | 推荐 | 区分“启动快”与“后期拖尾” |
| 诱导期 `t_lag` | 发现即必须记录 | 用于识别位点形成/重构/活化延迟 |

### 2.2 动力学拟合质量

GraphPad 笔记强调：**动力学比较必须同时保留反应条件与所用公式**。因此至少保留：

| 指标 | 是否必须 | 说明 |
|---|---|---|
| 拟合公式 | 必须 | 例如伪一级：`ln(C0/Ct) = k_obs * t` |
| 斜率 / `k_obs` | 必须 | 主筛选参数 |
| 截距 | 必须 | 用于判断起点是否偏移 |
| `R²` | 必须 | 判断线性质量 |
| 拟合时间窗 | 必须 | 明确哪些时间点被纳入拟合 |
| 点剔除规则 | 必须 | 防止后续无法复核 |
| `SE` / `95% CI` | 推荐 | 用于评估不同材料差异是否真实 |
| 残差观察 | 推荐 | 判断是否存在前快后慢却被硬拟合成直线 |

### 2.3 真实性指标：防止“快但不值得升级”

| 指标 | 是否必须 | 用途 |
|---|---|---|
| 无催化剂空白 | 必须 | 排除 NaClO2 自身反应 |
| 无氧化剂空白 | 必须 | 排除吸附或材料本身去除 |
| 氧化剂背景自耗 | 推荐 | 判断是否只是“白耗氧化剂” |
| 单位氧化剂效率 | 推荐 | 评价是否值得继续做材料升级 |
| 单位催化剂效率 | 推荐 | 排除只是靠加大投加量获得表观优势 |

### 2.4 重复性 / 可升级性指标

第二阶段实验记录表明，这一层和 `k_obs` 一样重要。

| 指标 | 是否必须 | 用途 |
|---|---|---|
| 批内平行误差 | 必须 | 判断单次结果是否稳定 |
| 批间 CV | 必须 | 判断材料是否可复现 |
| 循环后活性保持率 | 推荐 | 判断是否值得走稳定化升级路线 |
| Co 溶出 | 推荐 | 与项目“稳定性/安全性”KPI 对齐 |
| 结构保持（最小 XRD/XPS） | 推荐 | 判断活性是否来自严重重构/溶出 |

### 2.5 主矩阵建议结构

| 指标 \ 材料 | Co3O4-B1 | Co3O4-B2 | Co3O4-B3 | Cu-Co3O4-B1 | Cu-Co3O4-B2 | Cu-Co3O4-B3 | H2O-Co3O4-B1~B3 | NH3-Co3O4-B1~B3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 去除率@10 min |  |  |  |  |  |  |  |  |
| 去除率@30 min |  |  |  |  |  |  |  |  |
| `k_obs` |  |  |  |  |  |  |  |  |
| `t50/t90` |  |  |  |  |  |  |  |  |
| `t_lag` |  |  |  |  |  |  |  |  |
| `R²` |  |  |  |  |  |  |  |  |
| 氧化剂背景自耗 |  |  |  |  |  |  |  |  |
| 单位氧化剂效率 |  |  |  |  |  |  |  |  |
| 批内误差 |  |  |  |  |  |  |  |  |
| 批间 CV |  |  |  |  |  |  |  |  |
| 循环保持率 |  |  |  |  |  |  |  |  |
| Co 溶出 |  |  |  |  |  |  |  |  |

### 2.6 Ce-Co3O4 升级的 Go / No-Go 判据

**建议 Go 的情形：**
- Co3O4 基线在 3 个独立批次上稳定；
- Cu 或路线变化虽然可能提速，但不能同时兼顾重复性/稳定性；
- 当前瓶颈明确落在位点电子结构、高价 Co 稳定性或氧空位/缺陷控制上。

**建议 No-Go 的情形：**
- 批次效应大于材料效应；
- 只有单次去除率亮点，没有稳定 `k_obs` 优势；
- 不同材料比较时反应条件或拟合公式不统一；
- 空白对照未做齐。

---

## 三、GraphPad 输出要求

### 3.1 必保留的图

至少保留以下 6 类图：

1. **原始降解曲线：`C/C0 - time`**  
   - 用途：直观看谁更快、是否有诱导期、是否存在后期拖尾。

2. **伪一级线性拟合图：`ln(C0/Ct) - time`**  
   - 用途：展示 `k_obs` 的计算基础。  
   - 必须与拟合公式和时间窗一起保存。

3. **`k_obs` 汇总图（点图/柱状图 + SD）**  
   - 用途：比较均值与波动，避免只看平均值。

4. **批次重复性图**  
   - x 轴建议为 `Batch-1/2/3`，y 轴为 `k_obs` 或固定时间去除率。  
   - 用途：识别批次噪声是否掩盖材料效应。

5. **空白/对照图**  
   - 至少包含：无催化剂 + NaClO2、催化剂 + 无 NaClO2、主筛材料 + NaClO2。  
   - 用途：证明活性不是来自吸附或氧化剂自反应。

6. **单位氧化剂效率或背景自耗图**  
   - 用途：判断材料是否只是“跑得快但浪费氧化剂”。

### 3.2 必保留的拟合结果字段

GraphPad 输出不应只保留图片，至少要留以下字段：

| 字段 | 是否必须 | 说明 |
|---|---|---|
| 原始时间-浓度/峰面积表 | 必须 | 所有后续重算的基础 |
| 归一化后的 `Ct/C0` 表 | 必须 | 用于重画性能曲线 |
| 线性变换后的 `ln(C0/Ct)` 表 | 必须 | 用于复核拟合输入 |
| 拟合公式 | 必须 | 防止不同批次采用不同模型 |
| 斜率 / `k_obs` | 必须 | 主结论参数 |
| 截距 | 必须 | 判断起点是否存在偏差 |
| `R²` | 必须 | 判断拟合是否可信 |
| `SE` / `95% CI` | 推荐 | 判断组间差异强弱 |
| 拟合时间窗 | 必须 | 防止选点偏差 |
| 剔除点说明 | 必须 | 保持可审计 |
| 反应条件全文 | 必须 | 脱离条件的 `k_obs` 无法比较 |

### 3.3 最小数据表模板：分别放在哪里

建议最少建立 7 张表：

1. `00_run_registry`：实验主索引  
2. `01_raw_signal_long`：原始时间-信号表  
3. `02_normalized_curve_long`：归一化曲线表  
4. `03_pfo_fit_input_long`：伪一级拟合输入表  
5. `04_fit_summary`：拟合结果总表  
6. `05_plot_summary`：误差线与汇总图专用表  
7. `06_exclusion_log`：删点/异常说明表

### 3.4 各表最小职责

#### `00_run_registry`
记录一次实验到底是什么，至少包括：
- `run_id`
- `material_code`
- `sample_id`
- `batch_id`
- `replicate_id`
- `control_type`
- `synthesis_route`
- `dopant`
- `target_pollutant`
- `oxidant`
- `catalyst_dose`
- `oxidant_dose`
- `pollutant_c0_nominal`
- `pH_initial`
- `quench_method`
- `detection_method`
- `signal_type`
- `calibration_id`

#### `01_raw_signal_long`
放所有原始时间点：
- `run_id`
- `sample_id`
- `batch_id`
- `replicate_id`
- `time_min_actual`
- `raw_signal`
- `signal_unit`
- `dilution_factor`
- `point_flag`
- `point_note`

#### `02_normalized_curve_long`
放归一化后的降解曲线：
- `run_id`
- `sample_id`
- `batch_id`
- `replicate_id`
- `time_min_actual`
- `c0_value`
- `ct_value`
- `c_over_c0`
- `removal_percent`
- `normalization_rule`
- `c0_source`

#### `03_pfo_fit_input_long`
放真正进入伪一级拟合的点：
- `run_id`
- `sample_id`
- `batch_id`
- `replicate_id`
- `time_min_actual`
- `ln_c0_over_ct`
- `fit_include`
- `fit_window_label`
- `exclude_reason`
- `formula_used`

#### `04_fit_summary`
放最终拟合输出：
- `fit_id`
- `run_id`
- `sample_id`
- `batch_id`
- `replicate_id`
- `formula_used`
- `fit_window_start_min`
- `fit_window_end_min`
- `n_points_fit`
- `slope`
- `intercept`
- `kobs_min_inv`
- `r_squared`
- `se_kobs`
- `ci95_low`
- `ci95_high`
- `fit_pass`

#### `05_plot_summary`
放误差线与汇总：
- `group_id`
- `time_min`
- `n_reps`
- `mean_c_over_c0`
- `sd_c_over_c0`
- `sem_c_over_c0`
- `mean_removal_percent`
- `sd_removal_percent`
- `mean_kobs`
- `sd_kobs`
- `cv_kobs_percent`

#### `06_exclusion_log`
放异常与删点说明：
- `record_id`
- `run_id`
- `sample_id`
- `batch_id`
- `replicate_id`
- `time_min_actual`
- `issue_type`
- `action_taken`
- `reason_detail`

### 3.5 现在不记，后面就很难可靠重画图的字段

以下字段视为硬性必填：
- `sample_id`
- `batch_id`
- `replicate_id`
- `control_type`
- `time_min_actual`
- `signal_type`
- `raw_signal`
- `dilution_factor`
- `c0_source`
- `formula_used`
- `fit_include`
- `exclude_reason`

补充高优先级字段：
- `quench_method`
- `calibration_id`
- `pH_initial`
- `oxidant_dose`

### 3.6 GraphPad 实操提醒

根据当前 GraphPad 笔记，至少要同步保存：
- 反应条件说明；
- 线性化所用的 Y 轴公式；
- 线性拟合结果页；
- 图形导出时所对应的数据表名。

不能只保留最终美化后的图片，否则后续无法复核 `k_obs` 的来源。

---

## 四、当前阶段的执行建议

1. 先把 Co3O4、Cu-Co3O4、H2O-route Co3O4、NH3-route Co3O4 统一到同一反应条件。  
2. 每种材料先做 3 个独立批次，再谈 Ce 升级。  
3. 所有性能图必须同时配套 `k_obs`、`R²`、拟合时间窗和空白对照。  
4. 若 Cu 的问题主要是乙二醇体系不稳定，应先把“路线噪声”排干净，再决定是否引入 Ce。  
5. Ce-Co3O4 不应作为“继续加元素试试看”，而应作为“在基线稳定后，针对高价态稳定性/重复性瓶颈的定向升级”。
