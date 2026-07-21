---
source_assets:
  - assets/uploads/f1494f0d_【开题报告准备脉路】.md
  - assets/uploads/ae04a4a8_【开题报告】.md
  - assets/uploads/b807daff_【开题报告】.md
  - assets/ppt_pack/76bb19d2_开题报告-颜雍颀-V3.pptx
  - assets/uploads/fde1237c_开题报告-颜雍颀(1).docx
  - assets/ppt_pack/75315785_Ce掺杂Co3O4亚氯酸盐高级氧化.pptx
  - assets/ppt_pack/746ff89e_0327大组会-颜雍颀.pptx
  - assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md
  - assets/uploads/99550dc7_【毕业论文】工作文档0305.md
  - assets/uploads/b99056f9_20251230【进度规划】.md
  - assets/uploads/5c66efd3_【20260305大组会】工作文档.md
  - assets/ppt_pack/ca327de5_20260305大组会-颜雍颀-v5_最终交付.pptx
  - assets/ppt_pack/1c8b74da_literature_report_FINAL_v2-1.pptx
  - assets/uploads/1aaf3ec1_示例ppt.pdf
  - assets/ppt_pack/09f99410_文章图片排版【机密】.pptx
  - assets/uploads/6a403cea_【gpt文献调研：高价钴氧物种生成+聚合证据链】.md
created: 2026-03-21
---

# D handoff
## 目的
把当前 writing / literature workspace 交给另一个模型时，先明确：
- 哪些文件可作为各类交付的 **source of truth**
- 哪些文件只是 **版本中间态**
- 哪些文件只能作为 **排版/风格参考**
- 哪些结论当前仍不能写满，哪些写法属于高风险 hallucination
## workspace 边界
- 当前 workspace 是 `literature` 容器。
- 默认偏向 writing / concept 收束，不负责实验排期推进。
- 不负责跨 workspace 素材整合。
---
## 权威来源排序
### 0. 总排序规则
当不同文件互相冲突时，默认按以下顺序处理：
1. **最终正式交付件**
2. **memory 中已收束的 Pack / Master 文件**
3. **原始工作文档 / 版本中间态**
4. **排版/风格参考**
但有一个例外：
- **thesis 当前未看到正式定稿 thesis 文件**，因此 thesis 方向应以 `memory/packs/D_thesis_storyline_master.md` 与 `memory/packs/D_thesis_gapmap.md` 作为当前最高权威。
### 1. Proposal
#### 1.1 权威来源
1. `assets/uploads/fde1237c_开题报告-颜雍颀(1).docx`
   - 正式书面 proposal。
   - 书面写作、研究目标、章节口径以此优先。
2. `assets/ppt_pack/76bb19d2_开题报告-颜雍颀-V3.pptx`
   - 答辩版故事压缩。
   - 若目标是口头讲法、汇报顺序、答辩节奏，以此优先。
3. `memory/packs/D_proposal_revision_matrix.md`
   - 版本关系解释权威。
   - 用于判断某一版到底是准备便签、模板、重构稿、答辩稿还是 final。
#### 1.2 中间态
- `assets/uploads/f1494f0d_【开题报告准备脉路】.md`
- `assets/uploads/b807daff_【开题报告】.md`
- `assets/uploads/ae04a4a8_【开题报告】.md`
这些文件可用于追踪叙事演化，但不能压过 final docx 与答辩 final ppt。
#### 1.3 仅风格/结构参考
- `memory/packs/D_figure_layout_rules.md`
- `assets/uploads/1aaf3ec1_示例ppt.pdf`
---
### 2. Thesis
#### 2.1 当前最高权威
1. `memory/packs/D_thesis_storyline_master.md`
   - thesis 主线、章节桥接、图组映射的当前最高权威。
2. `memory/packs/D_thesis_gapmap.md`
   - thesis 成熟度、缺口优先级、当前最该补哪条证据链的当前最高权威。
#### 2.2 上游支撑与中间态
- `assets/uploads/99550dc7_【毕业论文】工作文档0305.md`
- `assets/uploads/b99056f9_20251230【进度规划】.md`
- `assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md`
- `assets/ppt_pack/75315785_Ce掺杂Co3O4亚氯酸盐高级氧化.pptx`
这些文件提供 thesis 的专题材料、早期组织方式或图版来源，但不应替代 storyline/gapmap 的当前解释权。
#### 2.3 仅风格/图版参考
- `memory/packs/D_figure_layout_rules.md`
- `assets/ppt_pack/09f99410_文章图片排版【机密】.pptx`
---
### 3. Group meeting
#### 3.1 权威来源
1. `assets/ppt_pack/ca327de5_20260305大组会-颜雍颀-v5_最终交付.pptx`
   - 20260305 大组会 final deck。
2. `memory/packs/D_group_meeting_replay.md`
   - 这次组会为什么最终长成当前结构的解释权威。
   - 若要继续改这套组会，应先读 replay，再读 final deck。
#### 3.2 中间态
- `assets/uploads/5c66efd3_【20260305大组会】工作文档.md`
这更像素材池 / 上游底稿，不应直接当作 final 口径重写。
#### 3.3 风格参考
- `assets/uploads/1aaf3ec1_示例ppt.pdf`
- `memory/packs/D_figure_layout_rules.md`
---
### 4. Literature report
#### 4.1 权威来源
1. `assets/ppt_pack/1c8b74da_literature_report_FINAL_v2-1.pptx`
   - literature report final deck。
#### 4.2 中间态 / 支撑材料
- `assets/uploads/6a403cea_【gpt文献调研：高价钴氧物种生成+聚合证据链】.md`
- `assets/uploads/04bbe294_【PACK】高价钴氧物种生成机理链.md`
这些文件适合补主题证据链与文献梳理，但不应替代 final deck。
#### 4.3 风格参考
- `assets/uploads/1aaf3ec1_示例ppt.pdf`
- `memory/packs/D_figure_layout_rules.md`
---
## 仍有冲突的点
### 1. Thesis 对 Ce 作用的表述口径仍未完全统一
当前最需要警惕的是：
- 不能同时保留“Ce 提高 Co 静态价态”
- 又保留“XPS/XANES 口径显示降低价态/不支持该表述”
更稳妥的上限应是：
- **Ce 改变 Co3O4 的局域结构与电子环境，增加氧空位/低配位特征，使其更容易在反应中进入高价态。**
- 但**不能直接写成“Ce 已证明使 Co 静态升价并直接导致高价钴生成”。**
### 2. 高价钴证据链仍未闭环
当前可以写到：
- **多源证据支持高价钴参与且地位关键**
当前不能写满到：
- **已证明只有高价钴主导**
- **已完全排除所有常规 ROS 路径**
### 3. 选择性氧化桥梁仍不够硬
当前叙事容易从：
- 抗生素含富电子位点
- chlorite / 高价钴可能偏好相关位点
直接跳到：
- 本体系具有稳定、普适的选择性优势
中间仍缺：
- 不同底物的结构—反应性对比
- 竞争底物 / DOM / 无机离子情形下的保持性
- 产物分布或路径差异证据
### 4. Proposal 的“答辩口径”与“书面口径”不能混用
- `V3.pptx` 更像口头压缩与叙事版。
- `final docx` 才是书面 proposal 的正式口径。
因此：
- 写答辩稿时可以更强结构化。
- 写正式书面文本时，不能把 PPT 式压缩结论原样搬进 docx/thesis。
### 5. Group meeting 的 final deck 与工作文档不能倒置
- 组会继续修改时，应以 `D_group_meeting_replay.md` + final ppt 为主。
- `【20260305大组会】工作文档.md` 是上游材料，不应倒过来成为最高解释权。
### 6. Thesis 当前没有单一“正式定稿母本”
这意味着：
- 不能假设某个单独 ppt 或单个工作文档就是 thesis final。
- 任何 thesis 写作续写，都应先以 `D_thesis_storyline_master.md` 定主线，再以 `D_thesis_gapmap.md` 限定结论上限。
---
## 后续写作禁区
### 1. 禁止把版本中间态当最终稿
遇到以下命名时，默认不许直接当 final：
- `工作文档`
- `准备脉路`
- `模板`
- `v1 / v2 / v3`
- `整理版`
- `修订版`
- `final_v2`
必须先确认：
- 它是不是最终稿
- 它在版本链中的位置
- 是否存在更高权威源文件
### 2. 禁止把排版/风格文件当内容事实来源
以下类型只能服务表达，不可直接服务事实判断：
- `memory/packs/D_figure_layout_rules.md`
- `示例ppt.pdf`
- 任何版式、布局、风格参考页
它们可以告诉你“怎么讲更清楚”，但不能告诉你“事实已经成立”。
### 3. 禁止从标题句直接升格为论文结论
当只看到了：
- PPT 页标题
- 总结页
- 目录页
- 机制示意图页
却没有看到：
- 原图页
- 条件脚注
- 对照组
- 页内限定语
则不能把标题句直接写成 thesis / proposal 的正式结论。
### 4. 禁止把示意图当证据图
- 机制示意图只能做收束。
- 真正的证据应来自淬灭、探针、谱图、电化学、动力学或原文图页。
- 如果只有示意图，没有对应证据页，应先回原文页或源文献页。
### 5. 禁止把“support / suggest / indicate”写成“prove / demonstrate / establish uniquely”
当前尤其高风险于：
- 高价钴生成
- 主导活性物种归属
- 选择性氧化机制
- Ce 位点重构后的决定性作用
结论上限必须与证据上限一致。
### 6. 禁止拿导出 PDF / 截图 / OCR 结果替代版本源文件
如果目标是：
- 续写正式文稿
- 还原答辩逻辑
- 判断最终口径
则优先级应为：
- 原始 `docx/pptx`
- 其次导出 `pdf`
- 最后才是截图 / OCR / 转述 markdown
### 7. 禁止把口头压缩版与书面正式稿混写
- PPT 更适合“先讲主句，再讲证据”。
- thesis / proposal docx 更需要边界、限定语、完整桥接。
因此：
- 不要把答辩 slide 标题原样拼成书面正文。
- 不要把书面限定语全部删掉去迎合 PPT 风格。
### 8. 禁止在未确认来源页时转引文献图或二手图
如果图来自：
- 别的 PPT
- 综述转引
- 截图搬运
则不能直接据此写出原始文献级结论；应先回原始文献页确认。
### 9. 禁止忽略“页内条件脚注”
当缺少以下信息时，不应写强结论：
- 样品定义
- 反应条件
- 对照设置
- 测试窗口
- 图中比较是否同条件
### 10. 禁止在 thesis 方向默认“平均推进三章”
根据当前收束文件：
- 第一章最接近成章
- 第二章、第三章仍明显偏计划态
因此后续写作若不特别说明，默认：
- 先稳第一章主线
- 再决定第二章、第三章是否扩写
---
## 冲突处理规则
当不同文件说法不一致时，按以下规则处理：
1. **final 交付件 > 中间稿**
2. **memory 收束 pack > 原始工作文档**
3. **书面 final docx > 口头压缩 ppt**（针对正式书面写作）
4. **final ppt > 工作文档**（针对组会续改）
5. **内容证据 > 排版参考**
6. **原始文献页 / 原始证据页 > 二手转述图**
---
## 给下一个模型的最小读取顺序
1. `memory/identity/workspace_scope.md`
2. 按任务类型读取对应主文件：
   - proposal → `memory/packs/D_proposal_revision_matrix.md`
   - thesis → `memory/packs/D_thesis_storyline_master.md` + `memory/packs/D_thesis_gapmap.md`
   - group meeting → `memory/packs/D_group_meeting_replay.md`
3. 再读对应 final 交付件
4. 最后才读工作文档 / 中间态
5. 只有在开始做页和优化表达时，才读取排版/风格参考
---
## 一句话 handoff
这个 workspace 可视为一个 **writing / literature 收束容器**：
- proposal、group meeting、literature report 都已有相对明确的 final/source-of-truth；
- thesis 目前仍应以 `storyline_master + gapmap` 作为最高语义权威；
- 后续任何写作都必须先做版本确认、证据上限确认、来源页确认，避免把中间态、排版参考和口头压缩稿误写成正式结论。