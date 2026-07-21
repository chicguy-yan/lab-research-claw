
我给你的md 文件是我的项目开发文档 和 phase1、2 的 plan 和开发情况+图片是我要应聘的岗位，目前开发到 phase3但还没开发（因为这是产品关键部分，我必须强制自己清晰框架才能继续开发），这是我 review项目 tad 和 prd 整理一些新想法，我目前最核心的目是平衡项目的理解和设计和跑通的程度和准备深势科技 ai 产品的面试，这是我对于 phase3 的一些新想法，请你帮我组合一下并提来出我的主逻辑和战略，帮助我规划面试准备和下一步项目开发（按紧急度可可行性排序），如果你觉得任务很难你无法解决，可以让我再给 gpt5pro 的提示词帮助我：phase3 这里有些问题必须澄清一下。
json 数据是模拟用户在使用本 openclaw 的真实提问数据集，这里会对应phase3 开发模块的流向动态示意。
本系统在运行的时候你需要有个一个基本的简单的引导用户
## 尤其是意图识别模块，需要有个基本的 router，但不知道是否符合 prd 和 tad 的要求：
langgraph中的Router 节点将用户问题分类的五个意图分别为：general-query（一般性问题）、additional-query（需要更多信息才能回答的问题）、graphrag-query（需要查询知识库的问题）、image-query（需要解析用户上传图片的问题）、file-query（需要解析用户上传文件的问题）。其中后面两个类别是用规则来识别的。）
## 三层记忆系统+propmt builder
这是返回给当下 workspace 下的内容，你需要引导用户定义一个比较小且能够马上获得闭环的task（json 数据里有很多对话，差不多 5-10 轮对话算一个 task 的最小），并引导他上传初步的assets 文件。
这些文件后续要如何引入到 memory 系统中呢，memory 中的 layer1 和 layer2 都是依赖 openclaw 自己的自进化原则+根据日期自动记忆；
但 layer3 是解决科研场景下痛点的关键，你的一个 workspace必须要满足，你必须逆向到对应的技术路线上！
1) **阶段性推进**：比如每 2–3 周一次阶段汇报（R01…R10），用户会给 `assets/ppt_pack/Rxx_YYYYMMDD/` 素材路径，需要快速汇总。
2) **实验闭环**：比如每天做了什么、是否支撑主线、缺哪些对照/表征（合成 checklist、参数矩阵、XRD/SEM/XPS“能证明什么不能证明什么”）。
3) **机理证据链闭环**：比如Co(IV) / ClO₂ 的硬证据链（PMSO 探针 + DPD 显色 + 淬灭剂 + 必要空白/对照 + 判据）。
4) **写作闭环**：比如Results & Discussion 目录树、每节中心句、主文/SI 放图策略。

## 具体的Layer3：Atom Notes（原子笔记资产层）


#### 3.1 目录

```text
memory/concepts/
  CONCEPT_*.md
memory/tasks/
  TASK_*.md              # 内含 Claim + Protocol + Run（可追加多次 run）
memory/packs/
  PACK_*.md              # stage_report/mechanism/writing/figure 等交付包
```

#### 3.2 对象最小字段（建议）

* `Concept`

  * `id, name, scope, keywords`
  * `north_star`（一句话主线）
  * `active_tasks[]`
* `Task`（Claim + Protocol + Run）

  * Claim：`claim_text` + `evidence`（缺 evidence 禁止入库）
  * Protocol：`steps[]`（带 checkpoint）+ `controls[]`
  * Run：`raw_data_paths[]` + `quick_results` + `verdict`
* `Pack`

  * `pack_type`：`mechanism_pack | stage_report_pack | figure_pack | writing_pack`
  * `task_refs[]`
  * `final_assets[]`（ppt_pack、png、段落等）
  * `takeaways[]`（每张图/每条证据一句话结论）

---


## 单独一次对话的流线
参考/Users/fenke/projects/study_ai/2-未完成项目存档/zly 规划-0219/yyq_chlorite_full_lifecycle_180d_300turns_humanized/yyq_chlorite_full_lifecycle_180d_300turns.json

在一次对话中，你需要完整的经历意图识别-引导用户上传文件+提供必要信息-帮助用户自动将 assets 归类 or 通过交互生成到 concept、task 和 pack 中，这其中是否需要subagent来分工协作参与？但这会不可避免地带来时延的影响，用 subagent的协作是可以解决的吗？

这些原子笔记产出都是 md 文件，应当是可以最后利用一些生成 ppt、论文写作、文献调研 word 或者生成实验机理图的生图的subagent/skill 来实现自由组合，其中 md 文件是这些最终交付物（应该也是在 pack 文件夹下，但是必须展示是利用哪些原子笔记建成的，方便用户一眼溯源并且能够理解这是顺着自己的思路制作的）