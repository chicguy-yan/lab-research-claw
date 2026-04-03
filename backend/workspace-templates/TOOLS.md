---
title: "TOOLS.md - Researchloop-OpenClaw"
summary: "本机/实验室环境相关的‘小抄’（不会进入论文，但会影响可复现）"
read_when:
  - When you need environment-specific info
---

# TOOLS.md - 环境小抄（Local Notes）

这里放的是“与环境绑定”的信息：机器路径、实验室设备编号、常用脚本位置、WPS/扣子空间使用习惯等。  
技能（skills）定义能力；**TOOLS.md 只记录你的环境细节**，方便可复现。

## 1) 常用路径约定（示例）

- 原始数据：`assets/data/`
- 画图产物：`assets/figures/`
- 组会素材打包：`assets/ppt_pack/Rxx_YYYYMMDD/`

> 具体实验的原始文件路径，建议写进 `memory/tasks/TASK_*.md` 的 `raw_data_paths[]`。

## 2) 常用脚本（示例）

- Python 作图：`scripts/plot_kobs.py`
- XPS 拟合：`scripts/xps_fit/`
- XRD Rietveld：`scripts/xrd_rietveld/`

## 3) WPS AI / 扣子空间（示例偏好）

- PPT 一页最多 2 图 + 2 句结论
- 每 1–2 页插入“导师核心问题”页

## 4) 工具调用约定（System Prompt 对齐）

- `terminal(command, cwd=".", timeout=30)`：执行 shell 命令
- `read_file(path, cwd=".")` / `write_file(path, content, cwd=".")`：相对路径会先基于 `cwd` 再落到 workspace
- `python_repl(code, cwd=".")`：Python 内部相对文件读写也以该 `cwd` 为基准
- `fetch_url(url)`：抓取网页；若某些 provider 错把 URL 字段命名成 `path`，工具层会自动兜底
- `cwd` 必须是 workspace 内的相对目录，默认当前 workspace 根目录
- `timeout` 单位为秒，按需设置；不要把文件路径误传给 `terminal`
- 只有批量列目录、查找文件、执行脚本时才优先考虑 `terminal`
- 实际工具调用时，必须按 schema 传参数对象；不要把示例伪代码当成真实调用格式

示例：

- 列出技能目录：`terminal({"command":"find skills -maxdepth 2 -type f", "cwd":".", "timeout":10})`
- 读取技能正文：`read_file({"path":"SKILL.md", "cwd":"skills/_system/mechanism_evidence_chain"})`
- 写入概念文件：`write_file({"path":"CONCEPT_demo.md", "cwd":"memory/concepts", "content":"# Demo"})`
- 抓 OpenAlex：`fetch_url({"url":"https://api.openalex.org/works?search=high-valent%20cobalt"})`

---

按需更新。越“可复现”，越有价值。
