# OpenClaw → Pi Agent：上下文拼接（简洁版）

> 本文只保留**内容层**的拼接规则：system prompt 如何由固定章节 + extraSystemPrompt + Project Context（工作区 MD 文件全文）组成，以及 user 消息如何拼接“非可信上下文 + 用户正文”。  
> 已移除：安全/合规/沙盒/心跳/静默回复等内容。

---

## 1. 最终会发给 Pi 的两条消息长什么样？

OpenClaw 最终给 Pi 的输入可理解为**两条角色消息**：

1) **system**：框定运行环境与工作区内容，末尾注入 **Project Context（工作区 MD 文件）**  
2) **user**：包含“非可信对话上下文（如引用/转发/最近历史等）”+“用户正文”

关键点：

- **可信入站元信息**（平台/网关提供的结构化元信息）通常放进 system 的 extraSystemPrompt 区块里。
- **非可信对话上下文**（转发、引用、最近聊天记录等）放进 user 消息里，并明确标注为 `untrusted`。

---

## 2. system prompt 的拼接方式（只保留内容相关章节）

system 由以下块**按顺序拼接**；块与块之间使用 **一个空行** 分隔。

### 2.1 章节顺序（从上到下）

1. **身份行（固定开头）**
   - 固定文本（连接词）：  
     `You are a personal assistant running inside OpenClaw.`

2. **工具概览（可选，但通常保留）**
   - 标题连接词：`## Tooling`
   - 工具列表连接结构（逐行）：`- <tool_name>: <tool_summary>`

3. **工作区说明（保留内容导向信息）**
   - 标题连接词：`## Workspace`
   - 常见连接结构（示例）：  
     `Your working directory is: <path>`  
     后续可追加 1~N 段自然语言说明（段落间一个空行）

4. **extraSystemPrompt（群聊/子智能体上下文块）**
   - 标题连接词（二选一）：
     - 群聊：`## Group Chat Context`
     - 子智能体/minimal：`## Subagent Context`
   - 块内推荐连接结构（多段落间一个空行）：
     - 子标题：`## Inbound Context (trusted metadata)`
     - 然后紧跟一个 JSON 代码块（可信元数据）：
       ```json
       { ... }
       ```
     - （可选）群聊长期上下文、首轮激活说明等自然语言段落

5. **Project Context（工作区 MD 文件注入）**
   - 标题连接词（固定）：`# Project Context`
   - 引言连接词（固定）：`The following project context files have been loaded:`
   - 然后按文件顺序逐个注入，每个文件使用统一模板：
     - `## <absolute_path>`
     - 空行
     - `<file_content>`
     - 空行

### 2.2 Project Context：注入哪些文件、按什么顺序？

**读取顺序（按存在性）**通常为：

1. `AGENTS.md`  
2. `SOUL.md`  
3. `TOOLS.md`  
4. `IDENTITY.md`  
5. `USER.md`  
6. `HEARTBEAT.md`（本简洁版不强调，但文件仍可能存在）  
7. `BOOTSTRAP.md`  
8. `MEMORY.md` 或 `memory.md`

### 2.3 裁剪与预算（内容版最小规则）

当文件或总上下文超长时，通常会有两级预算：

- **单文件 maxChars**：每个文件最多注入字符数  
- **整体 totalMaxChars**：所有 Project Context 合计最大字符数

裁剪一般发生在**文件内容尾部**：保留开头与关键段，尾部用 `…` 表示省略，并可附一行注释说明“已截断”。

---

## 3. user 消息的拼接方式（非可信上下文 + 用户正文）

user 消息通常由两段组成（两段之间空一行）：

### 3.1 非可信上下文块（存在才加）

由若干小节组成；每个小节形如：

- 标题连接词（固定短语之一）：
  - `Conversation info (untrusted metadata)`
  - `Sender (untrusted metadata)`
  - `Thread starter (untrusted, for context)`
  - `Replied message (untrusted, for context)`
  - `Forwarded message context (untrusted metadata)`
  - `Chat history since last reply (untrusted, for context)`
- 然后紧跟一个 JSON 代码块：
  ```json
  { ... }
  ```
- 小节与小节之间：**一个空行**

### 3.2 用户正文

- 直接拼接用户输入文本  
- 若无文本但有媒体：使用占位符 `\[User sent media without caption]`

---

## 4. 端到端示例（1 个）

> 下面示例展示：system 如何拼出固定块 + Group Chat Context + Project Context；user 如何拼出 untrusted 块 + 正文。  
> 注意：示例里的路径、文件内容与 JSON 都是演示用。

### 4.1 system（“最终字符串”示例）

````text
You are a personal assistant running inside OpenClaw.

## Tooling
- summary: Summarize text and extract key points
- file: Read/write workspace files

## Workspace
Your working directory is: /home/user/.openclaw/workspace
Use the injected Project Context files as the source of truth for this run.

## Group Chat Context
## Inbound Context (trusted metadata)
```json
{
  "platform": "telegram",
  "chat_id": "123456",
  "thread_id": "987",
  "agent": "pi",
  "model": "gpt-5.2",
  "language": "zh-CN"
}
```

This is a long-lived group chat for the OpenClaw→Pi integration project.
In this run, focus on describing how prompts are assembled and concatenated.

# Project Context
The following project context files have been loaded:

## /home/user/.openclaw/workspace/AGENTS.md

# Session Startup
- Always assemble system + user in that order.
- Inject workspace files under Project Context.

## /home/user/.openclaw/workspace/TOOLS.md

# Tools
- summary: Summarize text
- file: Read/write workspace files
````

### 4.2 user（“最终字符串”示例）

````text
Conversation info (untrusted metadata)
```json
{
  "quoted_message": "Can you show how you build the prompt?",
  "forwarded_from": "someone",
  "timestamp": "2026-02-25T10:00:00+08:00"
}
```

Chat history since last reply (untrusted, for context)
```json
{
  "recent_messages": [
    "User: I need exact concatenation tokens",
    "Assistant: Sure, I will explain"
  ]
}
```

请你说明 system 和 user 的拼接规则，并给出一个示例。
````

---

## 5. 可直接复用的“拼接模板”

### 5.1 system 模板（内容版）

````text
You are a personal assistant running inside OpenClaw.

## Tooling
- <name>: <summary>
- ...

## Workspace
Your working directory is: <path>
<optional paragraphs...>

## Group Chat Context
## Inbound Context (trusted metadata)
```json
{ ... }
```
<optional paragraphs...>

# Project Context
The following project context files have been loaded:

## <absolute_path_1>

<file_1_content>

## <absolute_path_2>

<file_2_content>
````

### 5.2 user 模板

````text
<Untrusted Section Title 1>
```json
{ ... }
```

<Untrusted Section Title 2>
```json
{ ... }
```

<user body or placeholder>
````
