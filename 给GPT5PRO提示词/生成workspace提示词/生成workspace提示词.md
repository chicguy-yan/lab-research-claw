# 你需要完成的目标
我现在要做这个experiment-research-openclaw，针对材料化学领域的openclaw，你现在要根据这个我给你的资料以及你的知识，帮我生成类似于openclaw的上下文记忆的管理模式的提示词和初始化文档，来支持我的这个research-openclaw。
你需要交付给我一下的一个ZIP文件和一个PRD文档
1、
我在附件有一个ZIP文件openclaw_templates.zip，里面有不少的XXX.md文件，你也需要给我一个ZIP文件叫做experiment-research-openclaw-templates.zip，里面可能有各种对于这个需要组装的project context的初始化内容。experiment-research-openclaw-templates.zip 里面有很多的markdowns，这个是要作为一个工作区的初始化文档的。**这里很有可能需要有不同的文件夹，比如 claims/claim.md,因为这个还可以是不同的路径**
2、
我在附件有一个openclaw_pi_prompt_concat_concise.md, 你需要交付一个PRD文档prompt_prd.md，来告诉模型如何使用这些上下文记忆的管理模式，以及如何在实际的研究中应用这些模式。我会使用这个PRD文档进行agent的开发。这个PRD文档要清楚的说出上下文是如何拼接的，还有一些固定的提示词应该如何写。**并且也给我举出一个例子来，在prompt_prd.md里面**。

# 我给你的东西
1、我会给你一个数据集，这里面是实际的问题，是一个json文件yyq_chlorite_full_lifecycle_180d_300turns.json，这个是一个全生命周期的test用户提问的合集，experiment-research-openclaw的 workspace 主要按照其中的时间梯度解决下面的问题。
2、其目的是方便展示 openclaw 的思考的推理链条和依据：除了openclaw_templates.zip中其他的记忆系统的，六类结构化输入的原子笔记的，其中三件套是基本的用户记忆系统中的原子笔记，这些原子笔记基本上来源于用户的本地文件结构化处理的，并且在workspace中的提问的时候是可以追溯到这些具体的原子笔记，
[Image]
2.1 三件套定义：Concept / Claim / Insight
一句话记忆：Concept 定范围-大致的主题和边界，Claim 定断可证伪的结论，Insight 定自己的实验计划如何验证。
 它们分别对应 UI 顶部链条中的：Concept → Claim → Insight → Protocol → RunResult
Concept（今日验证对象）
- 是什么：一个“验证主题与边界”的容器，用来声明你这段时间研究什么。这个Concept是最后要书写论文的主题和关键词
- 何时创建：开始读文献之前，先选定或新建一个 Concept（比如“pH 窗口是否决定催化活性”）。
- 必须包含：name（主题名）+（可选）scope/keywords（边界与关键词）。
- 和谁相连：一个 Concept 下会聚合多个 Paper 和多条 Claim，是整条链路的起点与筛选器。
Claim（可证伪结论）
- 是什么：从 Paper 中提炼出来的、可以被实验支持或推翻的一句话断言。它不是笔记感想，而是“可验证的命题”。这个Claim是最后要书写论文的核心论点
- 何时创建：Ingest 阶段由系统从 Paper 生成。
- 必须包含：claim_text（claim内容）+ evidence（原文证据摘录）。
- 和谁相连：每条 Claim 必须回链到对应 Paper；后续一个或多个 Insight 会选择某条 Claim 作为验证对象。
判别标准（用户自检）：如果这句话做完实验也无法判断对错，它就不是 Claim。
Insight（验证想法）
- 是什么：针对某条 Claim 的“今天要怎么验证”的具体设想，它把抽象断言转成可执行任务。
- 何时创建：Plan 阶段由用户在选择 Claim 后填写。
- 必须包含：insight_text（验证想法）+ due_date（截止日期）。
- 和谁相连：Insight 必须指向一条 Claim；系统据此生成 Protocol（实验SOP，实验的具体操作步骤） 与后续 RunResult 记录模板。
判别标准（用户自检）：Insight 至少要回答一个问题：我准备改哪个变量/观察哪个指标来判断 Claim？

# 你应该如何做
你首先要阅读测试集和openclaw如何设计workspace的文档，并联网搜索openclaw的上下文评价方式。然后思考下面的问题。
比如这里可能这里concept，claim，insight分别需要有一个独立的文件夹，里面初始化每个concept，claim，insight的模板文件，这些模板文件需要有一些固定的格式，比如多久创建的，是否完成，是否成功验证，还是已经发现没办法验证，对应的实验记录，其他的记录操作，多久做了什么针对性的实验是不是都需要有记录。
除此之外还有什么其他的上下文信息是需要记录的？你需要仔细想一下，但是尽量也要保持通用的记忆。应该是在模仿openclaw的前提下根据我现在要处理的experiment-research-openclaw也就是实验学科研究定制专门的openclaw。



# yyq 修改版本
我想设计一个模仿 openclaw 的 贯穿一个环境学生三个月学习周期的Researchloop-OpenClaw

## 我的目标
以下是我想学习的 openclaw 的设计原则
- 文件即记忆 (File-first Memory)：摒弃不透明的向量数据库，回归最原始、最通用的 Markdown/JSON 文件系统。用户的每一次对话、Agent 的每一次反思，都以人类可读的文件形式存在。—对应我的原子笔记系统
-	技能即插件 (Skills as Plugins)：遵循 Anthropic 的 Agent Skills 范式，通过文件夹结构管理能力，实现“拖入即用”的技能扩展。
- 透明可控：所有的 System Prompt 拼接逻辑、工具调用过程、记忆读写操作对开发者完全透明，拒绝“黑盒”Agent。
由此可以得到
在一个完整的180 天的实验周期中（如 json 所示），用户可以清晰的看到workspace（前端）中Researchloop-OpenClaw是如何拼接上下文（用户问题+agents.md、soul.md、user.md、+tools 和 skill 清单+专属于实验学科定制的记忆系统（如下原子笔记系统）），并引导用户输入相应的实验结果/表征结果/相关的论文，然后清晰地在前端的中间的 chatbot 中看见 agent 的思考过程（其中推理过程+每一步引用了哪个 md 文件+信息不足时需要用户提供什么 context），并将最后的交付结果存档。如果检测到高度重复的存档，则可以沉淀为有用户个人风格的新的 tools 和 skills
初步前端设想（你暂时不需要考虑）：中间是 chatbot 的形式，左边是 layer1 和 layer2 的展示

## 我的产品的用户的记忆压力源+Researchloop-OpenClaw应该记住的东西

阶段性推进（每隔一段时间就要做组会/PPT、复盘卡点、列下一步计划）
你在周期中多次出现“第 N 次阶段汇报”的请求，且会带素材打包路径（如 assets/ppt_pack/R06_20251123，后面还有 R09/R10 等）。

实验闭环压力（今天做了什么，是否能支撑主线，要补什么对照/表征）
典型就是：合成 checklist、参数矩阵、以及“这组 XRD/SEM/XPS 能证明什么不能证明什么”。

机理证据链压力（你反复强调要补齐 Co(IV) / ClO₂ 的“硬证据链”）
你反复在 Close/机理环节追问 “PMSO探针 + DPD显色 + 淬灭剂 + 必要空白/对照” 的组合与判据。

写作结构压力（Results & Discussion 目录树 + 每节中心句 + 主文/SI放图策略）
你多次要“章节逻辑”树形目录，并且强调“每节要证明什么”。

所以你的记忆系统必须能同时做到：

粗粒度：阶段里程碑、主线假设、当前最大不确定性、下一步验证计划

细粒度：每天实验 SOP、编号/污染风险提醒、数据路径、拟合结果、图表产物

跨周期：可追溯的 Claim-evidence、可复用的 Protocol、可累计的 RunResult 反向索引

可沉淀：高重复的交付（比如“按时间顺序 checklist”、“阶段汇报PPT提示词”）自动提炼成 Skill


## 你的参考
- openclaw_pi_prompt_concat_concise.md
这是 openclaw 的上下文拼接方式和原则介绍，你需要学习并参考
- 一个ZIP文件openclaw_templates.zip
里面可能有各种对于这个需要组装的project context的初始化内容，尤其是我的记忆系统中的 md 文件中的 layer1。**这里很有可能需要有不同的文件夹，比如 claims/claim.md,因为这个还可以是不同的路径**

- json文件
json 文件是我模仿用户在workspace 前端中整个周期的提问和输入，这是用户重点的痛点场景
- 记忆系统设计 md 文件
你需要基于这个文件中的内容，将 layer1 、layer2 的文件需要学习到 openclaw 的精髓，layer3 则是需要深度结合 json 中用户昌吉

## 你的输出
请你先深入学习并思考，重点结合 openclaw 的架构和设计原则并深度结合实验用户的场景，然后再一步一步思考和输出
我在附件有一个openclaw_pi_prompt_concat_concise.md, 你需要交付一个PRD文档prompt_prd.md，来告诉模型如何使用这些上下文记忆的管理模式，以及如何在实际的研究中应用这些模式。我会使用这个PRD文档进行agent的开发。这个PRD文档要清楚的说出上下文是如何拼接的，还有一些固定的提示词应该如何写。**并且也给我举出一个例子来，在prompt_prd.md里面**。
我在附件有一个ZIP文件openclaw_templates.zip，里面有不少的XXX.md文件，你也需要给我一个ZIP文件叫做experiment-research-openclaw-templates.zip，里面可能有各种对于这个需要组装的project context的初始化内容。experiment-research-openclaw-templates.zip 里面有很多的markdowns，这个是要作为一个工作区的初始化文档的。**这里很有可能需要有不同的文件夹，比如 claims/claim.md,因为这个还可以是不同的路径**






