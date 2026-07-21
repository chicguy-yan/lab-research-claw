# YYQ Chlorite Full-Lifecycle Benchmark 简介

## 一、Benchmark 基本信息

| 字段 | 值 |
|------|-----|
| scenario_id | `yyq_chlorite_full_lifecycle_v1_180d_300turns` |
| 生成时间 | 2026-02-16 |
| 总轮次 | 300 turns（仅含 user 侧，无 assistant 回复） |
| 时间跨度 | 2025-08-27 → 2026-02-22（约 180 天） |
| 数据格式 | 单个 JSON 文件，顶层字段 `scenario_id`、`generated_at`、`conversation_with_source`（数组） |
| 附件总数 | 317 个（image/png 182, text/csv 87, application/pdf 37, image/jpeg 11） |

## 二、场景背景

这是一位环境工程方向硕士研究生（代号 YYQ）在约半年内与 AI 助手的完整交互记录。研究课题为：

> **Ce 掺杂 Co₃O₄ 催化剂激活亚氯酸钠（NaClO₂）选择性降解磺胺甲噁唑（SMX）——基于 OAT/PCET 机理路径**

核心化学体系：Co₃O₄ / 0.5Ce-Co₃O₄ + NaClO₂ → 高价 Co(IV)=O / ClO₂ → 选择性氧化 SMX

该 benchmark 模拟了一个真实科研项目从"开题选方向"到"论文初稿完成"的全生命周期。

## 三、Turn 结构说明

每个 turn 的 JSON 结构如下：

```json
{
  "turn_id": "T0001",
  "timestamp": "2025-08-27T10:19:00+08:00",
  "user": {
    "text": "用户的完整提问文本...",
    "uploads": [
      {
        "path": "assets/png/xxx.png",
        "media_type": "image/png",
        "role": "raw_data"
      }
    ]
  }
}
```

注意：本 benchmark 只包含 user 侧输入，不包含 assistant 回复。
评测时需要你的模型生成回复，再与评分标准对照。

uploads 中的 role 有两种值：
- `"raw_data"`：实验数据、表征图、笔记截图等
- `"paper"`：文献 PDF

## 四、任务类型分布（11 类）

300 个 turn 覆盖科研全流程中 11 种典型任务，分布如下：

| 任务类型 | 轮次数 | 占比 | 说明 |
|----------|--------|------|------|
| 机理证据链设计 | 84 | 28.0% | 围绕"高价 Co(IV) 和 ClO₂ 是否真的生成"设计 PMSO 探针、DPD 显色、淬灭剂对照实验，要求给出浓度/取样时间/停止方式/预期趋势 |
| 活性测试/实验设计 | 64 | 21.3% | SMX 降解动力学实验（60 mL、NaClO₂ 0.2 mM、催化剂 30 mg），要求规划下一步对照变量（浓度/pH/投加量）的最优实验矩阵 |
| 材料合成 SOP | 40 | 13.3% | 将笔记中的合成步骤整理为按时间顺序的 checklist，标注称量量/容器/编号/搅拌条件/水热温度/煅烧参数，提醒交叉污染风险 |
| 数据绘图（Python） | 35 | 11.7% | 读取 CSV，用 matplotlib/seaborn 绘制多样品 C/C₀-t 曲线，做 ln(C/C₀)-t 线性拟合输出 kobs，保存为 png |
| 论文写作（R&D 章节） | 25 | 8.3% | 搭建 Results & Discussion 目录树（表征→性能→活性物种→机理→应用），每小节给中心句，建议主文/SI 图表分配 |
| 文献精读/拆解 | 23 | 7.7% | 对上传 PDF 按"体系设置→活性物种证据→pH/Cl⁻形态影响→对本课题启发"四块拆解，指出最值得复现的 2 个对照实验 |
| 开题/背景写作 | 19 | 6.3% | 将"为什么是亚氯酸盐"写成漏斗结构（AOPs 大背景→选择性氧化痛点→Co₃O₄+NaClO₂ 切入点），列导师追问清单 |
| 文献检索（DeepResearch） | 17 | 5.7% | 生成可直接复制的 OpenAI DeepResearch 提示词，含中英文关键词对齐、期刊/年份限定、输出表格字段、3 个 gap |
| 表征解读 | 14 | 4.7% | 判断 XRD/SEM/XPS 等表征图能证明什么/不能证明什么，建议补测（O1s 拆峰/EPR/Raman）及预期定性趋势 |
| 组会 PPT 汇报 | 11 | 3.7% | 总结阶段进展为 PPT 要点清单，生成给 WPS AI/扣子空间的超详细提示词（≥1000 字），整理素材到 ppt_pack 文件夹 |
| 任务拆解/卡点突破 | 3 | 1.0% | 将笔记中模糊的一句话翻译为 3 个可执行小任务，推动主线向论文闭环靠近 |

> 注：部分 turn 同时命中多个类型，上表按主要意图归类。

## 五、时间线与研究阶段演进

| 时间段 | 大致阶段 | 典型任务 |
|--------|----------|----------|
| 2025-08 ~ 2025-09 | 开题 & 材料筛选 | 背景漏斗写作、合成 SOP、文献检索、第 1-2 次组会汇报 |
| 2025-10 ~ 2025-11 | 活性测试 & 机理探索 | SMX 降解实验矩阵、PMSO/DPD 机理实验设计、表征解读、第 3-6 次组会汇报 |
| 2025-12 ~ 2026-01 | 表征深化 & 数据整理 | XRD/XPS 解读、Python 绘图、kobs 拟合、第 7-9 次组会汇报 |
| 2026-01 ~ 2026-02 | 论文写作 & 投稿准备 | R&D 章节搭建、论文初稿逻辑、补实验清单、第 10 次组会汇报 |

## 六、附件（uploads）体系

附件通过 `uploads` 数组随 turn 一起提供，路径均为相对路径（相对于 benchmark 根目录）：

- **assets/png/**：实验照片、表征图（SEM/XRD/XPS）、笔记截图、流程图等（182 张）
- **assets/csv/**：实验数据表，含降解曲线数据、材料合成参数汇总等（87 个）
- **assets/pdf/**：相关文献 PDF、DeepResearch 报告、开题模板等（37 个）

## 七、评测维度建议

用这个 benchmark 评测科研 AI 助手时，建议关注：

1. **领域知识准确性**：对 AOPs/OAT/PCET 机理、Co₃O₄ 尖晶石结构、Ce 掺杂效应等专业概念的理解
2. **实验设计合理性**：推荐的对照实验、变量扫描顺序、浓度范围是否符合该领域常规
3. **多模态理解**：能否正确解读上传的 XRD/SEM/XPS 表征图并给出有意义的判断
4. **上下文连贯性**：跨 turn 能否记住实验体系参数（60 mL、0.2 mM NaClO₂、30 mg 催化剂）和研究主线
5. **写作辅助质量**：漏斗结构背景、R&D 章节目录树、PPT 提示词的逻辑性和可用性
6. **代码可执行性**：生成的 Python 绘图代码能否直接运行，输出是否符合科研论文图表规范
7. **任务拆解能力**：能否将模糊的笔记片段转化为具体可执行的实验/写作任务

## 八、快速上手

```python
import json

with open("yyq_chlorite_full_lifecycle_180d_300turns.json", "r") as f:
    data = json.load(f)

for turn in data["conversation_with_source"]:
    turn_id = turn["turn_id"]
    timestamp = turn["timestamp"]
    user_text = turn["user"]["text"]
    uploads = turn["user"].get("uploads", [])

    # 你的模型在这里生成回复
    # response = your_model.generate(user_text, uploads)
```
