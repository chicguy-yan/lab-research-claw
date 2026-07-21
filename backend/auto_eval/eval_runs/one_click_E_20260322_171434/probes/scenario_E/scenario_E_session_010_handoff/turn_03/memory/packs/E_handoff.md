---
source_assets:
  - assets/uploads/ced68974_closure_mapping.md
  - assets/uploads/5c66efd3_【20260305大组会】工作文档.md
  - assets/uploads/192d5149_【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）.md
  - assets/uploads/45307a7c_test_cases_writing.md
created: 2026-03-23
---

# E_handoff
## 先实现什么
### 第一优先：Stage6 的“对象落地 + 写作桥接”最小闭环
先不要做泛化大系统，先打通一条真实链路：
**输入**
- `closure_mapping` 中与第六阶段相关的 closure object
- `【20260305大组会】工作文档`
- `【第六阶段】Co(IV)=O的选择性生成（第一章）+苯酚活性图&淬灭实验（第二章）`
- `writing test cases`
**最小输出**
1. `ClosureObject`：把第六阶段对象正式注册为可评测对象
2. `GapReport`：区分“已做 / 已写 / 未写入结构 / 仍待补证据”
3. `WritingPackSpec`：把研究对象转成可直接交给写作/PPT流程的结构化规格
4. `EvalResult`：至少先支持 `object_landing_test` 与 `writing_organization_test`
### 建议的最小模块
1. **Object Registry Parser**
   - 从 `closure_mapping.md` 提取 `research_line / object_hint / status / suitable_tests / source_files`
2. **Stage6 Bridge Builder**
   - 从第六阶段主线中提取 `章节目标 / 当前证据 / 计划实验 / 缺口`
3. **Writing Spec Renderer**
   - 按 `0305 工作文档` 的逐页规则渲染页面结构
4. **Gap Detector**
   - 优先发现“做了但还没写进去”的断裂
### 推荐实现顺序
- Sprint 1：Parser + Bridge Builder + Writing Spec + 2 个最小 eval
- Sprint 2：状态追踪、trace replay、Pack 级输出
---
## 可模板化部分
### 1. Closure Object 模板
最适合直接模板化，字段稳定、跨对象复用强：
- `research_line`
- `object_hint`
- `status`
- `suitable_tests`
- `source_files`
- `uncertainty_tags`
### 2. 写作 / PPT 页面模板
`0305 工作文档` 已经给出很强的页面 schema，建议固化为统一 `PageSpec`：
- 页面标题
- 页面目标
- 对应文献位置 / 图号
- 页面布局
- 页面文案
- 关键定量结果
- 脚注
- 演讲衔接
- 素材说明
- `待核对` 标记
### 3. 章节 - 证据 - 缺口 模板
适合用于第六阶段两章主线：
- `chapter_name`
- `target_claim`
- `current_evidence`
- `planned_experiments`
- `missing_evidence`
- `next_figure_targets`
### 4. Eval Case 模板
先把 test case 做成结构化对象，不要一开始自动生成：
- `id`
- `files`
- `why_typical`
- `applicable_tests`
- `expected_output_shape`
---
## 不要做错的事情
### 1. 不要一开始做“全局知识图谱”
当前更需要的是对象卡片、缺口报告、写作规格，而不是实体关系大系统。
### 2. 不要把“模板产物”误说成“对象落地产物”
只有当输出真正绑定了第六阶段对象、证据锚点和缺口时，才算 object-grounded；否则只是模板草案。
### 3. 不要把“计划”写成“结果”
第六阶段材料里同时包含已完成项与待做项；系统必须明确区分：
- 已观察
- 已写入
- 计划中
- 待核对
### 4. 不要过早做全自动 PPT 成品生成器
第一阶段先输出 `SlideSpec / WritingPackSpec` 即可；版式渲染不是当前 bridge/eval 的关键价值。
### 5. 不要让 judge 或 reporter 自动升级事实等级
禁止以下自动升级：
- `planned -> done`
- `candidate -> confirmed`
- `suggests -> proves`
### 6. 不要把单 case 成功外推成系统能力
W2 跑通只能说明该 case 可用，不能据此宣称整套 bridge/eval 已泛化完成。
### 7. 不要静默补全缺失信息
图号、作者、数据、实验条件、机制结论如不确定，必须保留为 `待核对 / unknown`，不能为了让输出完整而脑补。
---
## 给 Codex 的一句话 handoff
先不要做“会思考一切的泛化系统”，先做“能把 Stage6 从 closure object 落成可写、可测、可发现缺口的桥接层”。
