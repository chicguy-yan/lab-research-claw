# Context Trace（回放）说明

每次启动程序都写一份 JSON，用于前端回放与调试。

- 目录：`./context_trace/`
- 命名：`T0001.json` / `T0002.json` / ...

## 目标

- 让开发者/用户清楚看到：本回合拼接了哪些上下文、怎么用的、缺什么、写回哪里
- 为“重复交付 → 抽象 skill”提供统计依据

## 最小 schema

见 `TRACE_TEMPLATE.json`
