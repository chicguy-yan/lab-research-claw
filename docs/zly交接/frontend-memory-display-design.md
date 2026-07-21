# frontend 记忆展示设计梳理（迁移参考）

> 目的：总结当前项目 `frontend/index.html` 里“记忆如何展示”的设计思路，方便迁移到另一个相似项目。
>
> 这份文档聚焦前端展示层，不展开后端 trace/schema 的实现细节；重点回答：页面是怎么组织的、记忆如何分类展示、怎样和会话/trace 联动、迁移时哪些设计值得复用。

---

## 1. 一句话概括

当前前端不是把“记忆”做成一个单独页面，而是把它做成了一个**围绕会话工作的三栏工作台**：

- 左侧：长期/结构化记忆（Control Plane + L1/L2）
- 中间：聊天区 + 本轮工具流 + 累计审计
- 右侧：原子笔记（L3：Concepts / Tasks / Packs）

所以它的核心思想不是“展示所有记忆文件”，而是：

> **把记忆放在会话旁边，让用户在对话过程中随时查看上下文，而不是跳到另一个系统里找资料。**

代码主文件：

- [frontend/index.html](../../frontend/index.html)

---

## 2. 页面结构：三栏而不是单页列表

当前页面主结构在：

- [index.html:991-1109](../../frontend/index.html#L991-L1109)

整体分成 3 块：

```text
左栏 panel      中间 chat-stage          右栏 panel
记忆层           当前会话 + 聊天 + trace    原子笔记
```

对应 DOM：

- 左栏：`#leftPanel`
- 中间：`.chat-stage`
- 右栏：`#rightPanel`

见：

- [index.html:991-1018](../../frontend/index.html#L991-L1018)
- [index.html:1020-1081](../../frontend/index.html#L1020-L1081)
- [index.html:1083-1108](../../frontend/index.html#L1083-L1108)

### 这个设计的意义

它其实是在表达一个工作流假设：

- 左边看长期背景
- 中间和 Agent 对话、观察本轮执行
- 右边看具体任务/概念/交付物

也就是说，记忆展示不是“后台资料库 UI”，而是**和实时工作流并排呈现**。

这点很适合迁移到另一个类似项目。

---

## 3. 左栏展示什么：长期记忆 + 项目骨架

左栏标题是：

- `Workspace Memory`
- `记忆层`

见：

- [index.html:993-1007](../../frontend/index.html#L993-L1007)

它不是展示全部 `memory/`，而是重点展示三类：

1. `Control Plane`
2. `Layer 1 · Identity`
3. `Layer 2 · Timeline`

具体加载逻辑在：

- [index.html:1881-1903](../../frontend/index.html#L1881-L1903)

### 3.1 数据来源

左栏会并发请求 3 份树：

```js
/api/files/tree?path=.&max_depth=1
/api/files/tree?path=memory/identity&max_depth=2
/api/files/tree?path=memory/timeline&max_depth=3
```

见：

- [index.html:1883-1886](../../frontend/index.html#L1883-L1886)

### 3.2 Control Plane 的识别方式

它不是后端专门返回“控制层列表”，而是前端自己从 workspace 根目录树里筛：

- 只要是文件
- 文件名是 `.md`
- 且文件名全大写

代码：

- [index.html:1889-1891](../../frontend/index.html#L1889-L1891)

这意味着前端默认把下面这类文件视为“控制层”：

- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `IDENTITY.md`
- `BOOTSTRAP.md`
- `MEMORY.md`
- `TOOLS.md`

### 3.3 为什么左栏这样设计

因为左栏承担的是“背景上下文”的角色，它更偏：

- 长期有效
- 高频查看
- 结构性强
- 适合在会话前/会话中快速翻看

所以它把：

- 项目设定
- 用户偏好
- 时间线记忆

放在一个稳定区域里，而不是和原子任务混在一起。

---

## 4. 右栏展示什么：原子笔记

右栏标题是：

- `Atomic Notes`
- `原子笔记`

见：

- [index.html:1083-1097](../../frontend/index.html#L1083-L1097)

它只展示三类：

1. `Concepts`
2. `Tasks`
3. `Packs`

加载逻辑：

- [index.html:1906-1924](../../frontend/index.html#L1906-L1924)

请求路径：

```js
/api/files/tree?path=memory/concepts&max_depth=2
/api/files/tree?path=memory/tasks&max_depth=2
/api/files/tree?path=memory/packs&max_depth=2
```

### 这个设计的意义

右栏明显被设计成“更细、更具体、更接近当前工作的记忆层”。

如果把左栏理解成“背景和阶段”，那右栏就是：

- 当前主题条目
- 单项任务条目
- 交付打包条目

所以页面在视觉上把记忆拆成了两类：

- **左边：长期背景记忆**
- **右边：原子工作记忆**

这个分法非常利于迁移，因为它比“一个大树全塞进去”更容易让用户理解。

---

## 5. 记忆展示不是富编辑器，而是“树 + 只读预览”

这一版前端没有把记忆展示做成 Monaco/双向编辑器，而是一个更轻的交互：

- 左/右栏先展示文件树
- 点文件后在栏底部打开 `file-viewer`
- 以 `pre` 文本方式只读预览

相关结构：

- 左侧 viewer：[index.html:1008-1017](../../frontend/index.html#L1008-L1017)
- 右侧 viewer：[index.html:1098-1107](../../frontend/index.html#L1098-L1107)
- 打开文件逻辑：[index.html:2034-2052](../../frontend/index.html#L2034-L2052)

### 打开文件的行为

点击树节点文件时：

1. 请求 `/api/files?path=...`
2. 读取文件正文
3. 显示文件路径
4. 显示字符数
5. 在 `<pre>` 里渲染内容

见：

- [index.html:2034-2041](../../frontend/index.html#L2034-L2041)

### 为什么这种交互适合记忆展示

因为“看记忆”这个动作通常是：

- 快速定位
- 打开看一下
- 继续对话

而不是长时间沉浸式编辑。

所以这版 UI 明显优先考虑：

> **低打扰预览，而不是复杂编辑。**

如果你另一个项目现在只是想“让用户能看到记忆”，这套轻量设计足够了。

---

## 6. 记忆树怎么渲染

### 6.1 使用目录树 API，而不是前端硬编码文件列表

前端所有树都来自后端 `/api/files/tree`，不是写死文件名。

这样做的好处：

- 新增文件会自动出现
- 子目录结构可递归展开
- 前端只负责展示，不负责记忆定义

### 6.2 树组件是递归渲染的

核心函数：

- [index.html:1931-2023](../../frontend/index.html#L1931-L2023)

主要由这几个函数组成：

- `renderTreeSection(container, title, items, side)`
- `buildTree(items, side, depth)`
- `countFiles(items)`

### 6.3 交互规则

#### 文件夹

- 默认顶层展开，内层折叠
- 点击可以展开/收起
- 使用 `▶` 箭头 + `📁` 图标

见：

- [index.html:1958-1991](../../frontend/index.html#L1958-L1991)

#### 文件

- 点击后触发 `openFile(item.path, side, row)`
- `.md` 用 `📄` 图标，其它文件用 `📝`
- 当前打开文件会有 `.active` 状态

见：

- [index.html:1992-2017](../../frontend/index.html#L1992-L2017)
- [index.html:2054-2061](../../frontend/index.html#L2054-L2061)

### 这套树设计的优点

1. 足够简单
2. 不依赖框架组件库
3. 层级感明确
4. 和文件系统结构一一对应

对迁移来说，这是一种成本很低但效果不错的设计。

---

## 7. 记忆展示和会话区不是分离的，而是联动的

这是当前页面设计里最值得迁移的一点。

## 7.1 中间区域会持续提示“当前会话 + 当前审计”

中间区域不是纯聊天窗，而是一个“会话工作台”：

- 当前会话名
- message 数
- trace 数
- 聊天流
- 本轮工作流审计
- 历史累计审计
- 原始 trace envelope 查看

相关结构：

- [index.html:1020-1081](../../frontend/index.html#L1020-L1081)

### 这对记忆展示意味着什么

用户不是先去记忆库找资料、再切到聊天。
而是一直在一个界面里：

- 左边看记忆
- 中间问问题
- 右边看原子笔记
- 下方看 trace

这比“记忆系统”和“聊天系统”分成两个页面要高效得多。

---

## 7.2 会话切换后，聊天与 trace 会一起恢复

当用户切换 session：

- 先请求 `/api/sessions/{id}/history`
- 再请求 `context_trace/{sessionId}.json`
- 同时恢复 messages 和 traces

见：

- [index.html:1468-1485](../../frontend/index.html#L1468-L1485)
- [index.html:1488-1502](../../frontend/index.html#L1488-L1502)

这说明前端把“会话内容”和“工具审计”看作同一个上下文单元。

对另一个项目来说，如果你也要做记忆展示，最好也保持这种思路：

> **用户切换到一个工作上下文时，记忆、聊天、审计最好一起就位。**

---

## 8. 中间区怎么把“记忆”变成“可解释工作流”

虽然中间区不直接渲染 memory 文件树，但它通过审计卡片把“本轮用了什么上下文、做了什么工具动作”可视化了。

## 8.1 本轮工作流审计卡片

每次发送消息时，前端会新建一个 assistant turn，其中包含：

- `本轮工作流审计`
- 运行中的状态
- 工具开始/结束事件流
- 最终 trace 审计结果
- assistant 回复内容

创建逻辑：

- [index.html:1559-1616](../../frontend/index.html#L1559-L1616)

实时接收 SSE 时：

- token → 追加 assistant 文本
- tool_start → 追加“调用工具”事件
- tool_end → 追加“工具返回”事件

见：

- [index.html:1709-1719](../../frontend/index.html#L1709-L1719)

### 这个设计的价值

它让用户不只是看到“回答”，还能看到：

- 回答过程中调了哪些工具
- 这些工具返回了什么
- 本轮是否真的形成了 trace 记录

这相当于把“记忆系统的使用痕迹”展示出来了。

---

## 8.2 会话累计审计卡片

历史 traces 会在加载历史后渲染成一个折叠卡片：

- 标题：`会话累计审计`
- 只展示最近 8 条

见：

- [index.html:1748-1785](../../frontend/index.html#L1748-L1785)

这表示前端没有把 trace 直接淹没在消息流里，而是给了一个概览层。

对迁移很有启发：

- **本轮审计**：强调即时反馈
- **会话累计审计**：强调历史回顾

两层都保留，体验会更完整。

---

## 8.3 Trace 详情面板

页面上还有一个按钮：

- `查看 Trace`

点击后会打开右下浮层/面板，直接展示当前会话 envelope 的完整 JSON。

见：

- 按钮：[index.html:980-983](../../frontend/index.html#L980-L983)
- 面板：[index.html:1063-1072](../../frontend/index.html#L1063-L1072)
- 打开逻辑：[index.html:1867-1875](../../frontend/index.html#L1867-L1875)

### 这个设计的意义

这相当于给“普通用户视图”之外，再加一个“调试/审计视图”：

- 平时看卡片化 trace 摘要
- 需要核验时看完整 JSON envelope

如果你另一个项目也有“要让用户看明白，但开发者还想看底层”的需求，这个设计很值得保留。

---

## 9. 记忆展示的几个关键 UX 选择

## 9.1 左右两栏语义明确，不把所有记忆混在一起

左栏不是简单文件树，而是强调：

- Control Plane
- L1
- L2

右栏强调：

- Concepts
- Tasks
- Packs

这种语义化展示，比直接展示 `memory/` 全目录更清晰。

### 为什么适合迁移

因为用户理解的是：

- 这些是背景
- 这些是时间线
- 这些是当前任务与笔记

而不是：

- 这是一个复杂目录树，请自己理解

---

## 9.2 记忆摘要文案是动态的

例如：

- 左栏：`已加载 X 个条目，可直接预览文件。`
- 右栏：`已加载 X 个原子笔记条目。`

见：

- [index.html:1898-1899](../../frontend/index.html#L1898-L1899)
- [index.html:1919-1920](../../frontend/index.html#L1919-L1920)

这是一种小但有用的设计：

- 给用户反馈系统已加载成功
- 给用户一个规模感
- 比“空白树”更有确定性

---

## 9.3 对移动端有降级设计

页面有：

- `openLeftPanelBtn`
- `openRightPanelBtn`
- `panelOverlay`

见：

- [index.html:957](../../frontend/index.html#L957)
- [index.html:984](../../frontend/index.html#L984)
- [index.html:1256-1262](../../frontend/index.html#L1256-L1262)
- [index.html:2078-2088](../../frontend/index.html#L2078-L2088)

说明桌面端是三栏并列，而窄屏时侧栏会变成可开合面板。

如果你另一个项目也要迁移这套记忆展示，建议保留这种响应式思路，不然移动端会非常难用。

---

## 10. 这个前端记忆展示设计最值得迁移的点

## 10.1 不是“做一个记忆页”，而是“把记忆嵌进工作台”

这是最核心的产品思路。

很多系统会把：

- 对话
- 记忆
- 审计

分成三个页面。

而这里把它们放在同一工作台里，用户的操作路径更短。

如果你的另一个项目也强调“边看记忆边工作”，建议直接复制这个方向。

---

## 10.2 记忆按“背景”和“原子工作项”分两边展示

这个拆分很实用：

- 左边看稳定背景
- 右边看细粒度条目

比一个大树更容易形成认知地图。

---

## 10.3 前端不直接定义记忆，只定义“展示规则”

它依赖后端 tree API，前端只是：

- 选路径
- 分栏目
- 渲染树
- 打开文件

这让迁移成本很低。只要另一个项目也有类似的 `files/tree` 和 `files` 接口，前端层几乎能直接照搬。

---

## 10.4 用 trace 把记忆展示和执行过程接起来

这版 UI 一个很好的地方在于：

- 左右栏展示“静态记忆”
- 中间区展示“动态执行”

这样用户能看到：

- 有哪些记忆
- 会话里做了什么
- 真实工具调用是什么

这比纯文件浏览器更接近“可解释 Agent 工作台”。

---

## 11. 如果迁移到另一个项目，我建议的最小复用方案

如果你另一个项目也想显示记忆，但不想一开始就做太复杂，我建议直接迁移下面这套最小版本。

## 11.1 页面结构

保留三栏：

```text
左栏：长期背景记忆
中间：聊天 + 本轮审计 + 会话累计审计
右栏：细粒度任务/笔记/交付
```

## 11.2 后端接口最少准备这些

```text
GET /api/files/tree?path=...&max_depth=...
GET /api/files?path=...
GET /api/sessions
GET /api/sessions/{id}/history
POST /api/chat
```

如果要保留 trace 面板：

```text
GET /api/files?path=context_trace/{sessionId}.json
```

## 11.3 前端最少保留这些组件

1. 左树面板
2. 右树面板
3. 文件预览器
4. 聊天流
5. 本轮工具事件流
6. 会话累计审计卡片
7. Trace 原始 JSON 面板

这样就已经能形成一个完整的“可见记忆工作台”。

---

## 12. 迁移时需要注意的边界

## 12.1 当前 `index.html` 的记忆分类是定制的，不是通用标准

这版页面里：

- 左栏对应 `Control Plane + Identity + Timeline`
- 右栏对应 `Concepts + Tasks + Packs`

这是当前项目/agent 的定制分类，不是所有 OpenClaw 类项目都必须这么分。

迁移时你应该保留的是：

- **左侧展示稳定背景 / 右侧展示细粒度工作项** 这个思想

而不是机械照搬目录名。

---

## 12.2 现在是只读预览，不是完整知识库编辑器

如果你另一个项目需要：

- 重命名文件
- 创建条目
- 拖拽归档
- 富文本编辑

那这版前端还不够，需要继续扩展。

但如果你当前目标只是“先把记忆可视化”，这版已经够用了。

---

## 12.3 记忆展示依赖后端目录语义稳定

前端现在默认知道这些目录：

- `memory/identity`
- `memory/timeline`
- `memory/concepts`
- `memory/tasks`
- `memory/packs`

如果你迁移到另一个项目改了目录名，前端加载逻辑也要一起改。

所以更建议你把这些路径提成配置，而不是硬编码在页面里。

---

## 13. 总结

如果只用一句话总结这个项目里前端“显示记忆”的设计：

> **它不是做了一个独立记忆库，而是做了一个把“长期背景记忆、原子笔记、当前会话、工具审计”放在同一屏里的工作台。**

我认为最值得你迁移到另一个项目的是这 4 个点：

1. **三栏工作台**，而不是记忆单页
2. **左背景 / 右原子笔记** 的展示分层
3. **树 + 只读预览** 的轻量交互
4. **聊天流和 trace 审计并列展示**，让记忆和执行联动

---

## 14. 代码依据

本次总结主要基于：

- [frontend/index.html:991-1109](../../frontend/index.html#L991-L1109)
- [frontend/index.html:1468-1502](../../frontend/index.html#L1468-L1502)
- [frontend/index.html:1559-1745](../../frontend/index.html#L1559-L1745)
- [frontend/index.html:1748-1875](../../frontend/index.html#L1748-L1875)
- [frontend/index.html:1881-2052](../../frontend/index.html#L1881-L2052)
