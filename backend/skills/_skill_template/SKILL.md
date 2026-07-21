---
name: <skill_id>
description: <一句话描述这个 skill 解决什么问题、输出什么结果>
allowed-tools: Read Write Edit Bash
license: Internal
---

# <Skill Name>

## Overview

这个 skill 用于处理**<核心任务类型>**任务。

它适用于这样的问题：<描述典型使用场景>。

这个 skill 的重点不是<不做什么>，而是输出一个**<核心产物描述>**。

---

## When to Use This Skill

当满足以下任一情况时使用本 skill：

- <场景 1>
- <场景 2>
- <场景 3>

---

## When NOT to Use This Skill

以下情况不要使用本 skill：

- <排除场景 1>
- <排除场景 2>
  - 这类问题更适合交给 <其他 skill 类型>

---

## Required Inputs

### Minimum Inputs

至少需要以下输入之一的组合：

- <最低输入 1>
- <最低输入 2>

### Optional Inputs

以下输入会显著提升结果质量：

- <增强输入 1>
- <增强输入 2>

### Supported Material Types

- pdf
- md
- figure screenshots

---

## Expected Outputs

本 skill 应输出以下类型的结构化结果：

- `<output_field_1>`
  - <说明>
- `<output_field_2>`
  - <说明>
- `<narrative_spine>`
  - 用 3 到 6 句串起当前最稳的叙事骨架

输出形式可以是：

- <形式 1>
- <形式 2>

---

## Workflow

### Step 1. <步骤名>

<步骤说明>

### Step 2. <步骤名>

<步骤说明>

### Step N. 输出结构化结果

将结果整理为一个可复用的分析产物。

---

## Boundary with Sibling Skills

使用本 skill 时，注意与相邻 skill 的边界：

- 当重点是**<本 skill 核心场景>**时，优先使用本 skill
- 当重点是**<其他场景>**时，优先转给 <其他 skill 类型>

---

## Quality Checks

在输出前检查以下内容：

- [ ] <检查项 1>
- [ ] <检查项 2>
- [ ] `<narrative_spine>` 是否足够短、稳、可接入下游

---

## Common Failure Modes

使用本 skill 时，尤其要避免以下问题：

- <典型错误 1>
- <典型错误 2>

---

## Red Flags / Escalation Notes

出现以下情况时，应降低结论强度或提示转交：

- <红线场景 1>
- <红线场景 2>

---

## Example Patterns

### Example Pattern 1 · <场景名>

#### Typical User Ask
"<典型提问>"

#### Typical Inputs
- <输入 1>
- <输入 2>

#### Expected Output Shape
- `<field_1>`
- `<field_2>`

#### Boundary Notes
- <边界说明>

---

## Example Requests

以下请求适合调用本 skill：

- "<请求 1>"
- "<请求 2>"

---

## Related Skills

- `<sibling_skill_1>`
- `<sibling_skill_2>`
