# TASK Template — TASK_<topic>.md

> Task = **一次验证任务**（Claim + Protocol + Run）。  
> 强制：**没有 evidence 或 raw_data_paths 就不能判定“完成”。**

## meta
- `id`: TASK_...
- `concept`: CONCEPT_...
- `status`: planned | running | blocked | done
- `owner`: user | agent
- `created_at`: YYYY-MM-DD
- `last_updated`: YYYY-MM-DD

---

## 1) Claim（要证明什么）

### claim_text
- …

### claim_type
- mechanism | activity | selectivity | stability | characterization | writing | other

### evidence_required（判据引用）
- 参考：`memory/identity/project.md`（写清需要的证据类型）

---

## 2) Evidence（目前有什么证据）

> **没有证据也可以建 Task，但必须保持为空，并在 missing 中追要。**

- Evidence 1:
  - type: figure | table | raw_data | paper | note
  - path_or_citation: assets/... 或 Paper/DOI/链接
  - what_it_supports: …
  - limitations: …

---

## 3) Protocol（怎么做）

### steps[]
1. …
2. …

### checkpoints[]
- CP1：…
- CP2：…

### controls[]
- blank:
- no-catalyst:
- no-oxidant:
- dark/light:
- other:

### contamination_risks
- …

---

## 4) Runs（一次或多次实际执行）

### run_01
- date: YYYY-MM-DD
- raw_data_paths[]:
  - assets/data/...
- quick_results:
  - …
- verdict: supports | weak_support | inconclusive | refutes
- next_action:
  - …

（可追加 run_02/run_03…）

---

## 5) Missing（缺什么信息）

- field: …
  - why_needed: …
  - how_to_provide: …

