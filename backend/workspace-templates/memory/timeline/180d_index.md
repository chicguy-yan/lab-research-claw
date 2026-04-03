# Layer2 / 180d_index.md — 180 天总览（阶段划分、里程碑、风险雷达）

> 目的：把“我在做什么”写成一条可追溯主线。  
> 每次阶段汇报前，Agent 应从这里定位“本阶段应该交付什么”。

## 0) 项目北极星（引用 Layer1）

- 参考：`memory/identity/project.md` 的 North Star + KPI

## 1) 阶段划分（可改）

- **P01 Bootstrapping（第 1–14 天）**  
  完成：材料路线图、样品编号体系、第一版实验矩阵、第一份组会模板
- **P02 Material Screening（第 15–60 天）**  
  完成：材料筛选结果、锁定对比样、初步选择性/基质耐受
- **P03 Parameter Optimization（第 61–110 天）**  
  完成：关键参数窗口（pH/剂量/NaClO2/基质）、批次差异排查
- **P04 Mechanism Closure（第 111–150 天）**  
  完成：Co(IV)/ClO₂ 硬证据链、OAT/PCET 机理叙事、关键对照闭环
- **P05 Writing & Submission（第 151–180 天）**  
  完成：Results & Discussion 目录树、主文/SI 放图策略、投稿清单

> 对应详细说明见：`memory/timeline/phases/P0x_*.md`

## 2) 阶段里程碑（Milestones）

| 日期/范围 | 里程碑 | 交付物（Pack） | 风险 |
|---|---|---|---|
| … | … | `PACK_stage_report_Rxx` | … |

## 3) 阶段汇报节奏（建议）

> 你在真实场景中会反复出现“第 N 次阶段汇报 + ppt_pack 路径”。  
> 这里记录约定，便于自动化生成。

- R01 / R02 / ...：每 2–3 周一次
- 素材打包路径：`assets/ppt_pack/Rxx_YYYYMMDD/`
- 汇报文件：`memory/timeline/stage_reports/Rxx_YYYYMMDD.md`

## 4) 风险雷达（持续更新）

- **样品编号混乱/交叉污染**：高
- **机理证据链不闭合**：高
- **写作结构拖延**：中
- **数据路径丢失**：高

## 5) 当前所在阶段（手动维护）

- `current_phase`: P01 / P02 / P03 / P04 / P05
- `current_focus`: …

