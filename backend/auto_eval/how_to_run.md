# auto_eval 如何运行

## 1. 先决条件

- 在 `backend` 目录运行。
- 后端依赖已安装。
- `backend/.env` 里有可用的 `OPENAI_API_KEY`。
- 如果当前 Python 环境缺 `html2text`、`langchain_openai` 之类依赖，先切到后端实际运行用的解释器再执行。

## 2. 启动后端 FastAPI

在 `backend` 目录执行：

```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8002
```

如果你当前环境缺 `html2text`，但只是想先跑 `auto_eval` 验证链路，可以临时加测试 stub：

```powershell
$env:PYTHONPATH='d:\ai_software\yyq_project\backend\auto_eval\tests\runtime_stubs'
python -m uvicorn app:app --host 127.0.0.1 --port 8002
```

启动后可检查：

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8002/
```

返回 `200` 说明后端已起来。

## 3. 先跑 smoke 场景

在另一个终端进入 `backend`，执行：

```powershell
$env:NO_PROXY='127.0.0.1,localhost'
python -m auto_eval.cli `
  --backend-url http://127.0.0.1:8002 `
  --scenario auto_eval/tests/fixtures/smoke_scenario `
  --source-root auto_eval/tests/fixtures/smoke_scenario `
  --run-id actual_backend_smoke `
  --run-root auto_eval/eval_runs/actual_backend_smoke `
  --session-limit 1
```

这条命令会真实调用：

- `POST /api/workspaces`
- `POST /api/workspaces/{id}/bootstrap/start`
- `POST /api/chat`
- `GET /api/sessions/{id}/history`
- `GET/POST /api/files`

终端会持续打印每一步，例如：

- `[SCENARIO][START]`
- `[WORKSPACE][CREATED]`
- `[BOOTSTRAP][START]`
- `[TURN][START]`
- `[STREAM][TOKEN]`
- `[STREAM][TOOL_START]`
- `[STREAM][TOOL_END]`
- `[TURN][DONE]`
- `[RUN][DONE]`

## 4. 看结果

本地结果目录：

- [backend/auto_eval/eval_runs](d:/ai_software/yyq_project/backend/auto_eval/eval_runs)

重点文件：

- [report.md](d:/ai_software/yyq_project/backend/auto_eval/eval_runs/actual_backend_smoke/reports/report.md)
- [overall_summary.json](d:/ai_software/yyq_project/backend/auto_eval/eval_runs/actual_backend_smoke/reports/overall_summary.json)
- [terminal_replay.txt](d:/ai_software/yyq_project/backend/auto_eval/eval_runs/actual_backend_smoke/reports/terminal_replay.txt)
- [completed_turns.json](d:/ai_software/yyq_project/backend/auto_eval/eval_runs/actual_backend_smoke/checkpoints/completed_turns.json)

同时还会把 markdown summary 写回真实 workspace 的：

- `memory/packs/EVAL_RUN_<run_id>_INDEX.md`
- `memory/packs/EVAL_RUN_<run_id>_SCOREBOARD.md`
- `memory/packs/EVAL_RUN_<run_id>_<SCENARIO>_SUMMARY.md`

## 5. 跑内置 B/C/D/E

CLI 支持直接指定内置场景字母：

```powershell
$env:NO_PROXY='127.0.0.1,localhost'
python -m auto_eval.cli --backend-url http://127.0.0.1:8002 --scenario B
python -m auto_eval.cli --backend-url http://127.0.0.1:8002 --scenario C
python -m auto_eval.cli --backend-url http://127.0.0.1:8002 --scenario D
python -m auto_eval.cli --backend-url http://127.0.0.1:8002 --scenario E
```

也可以一次跑多个：

```powershell
$env:NO_PROXY='127.0.0.1,localhost'
python -m auto_eval.cli `
  --backend-url http://127.0.0.1:8002 `
  --scenario B `
  --scenario C `
  --scenario D `
  --scenario E `
  --source-root <你的真实资料根目录>
```

注意：

- B/C/D/E 里的 `user_upload` 路径是按真实资料库写的。
- 如果这些文件在本机不存在，runner 会在上传阶段直接报 `Upload source not found`。
- 所以全量跑之前，必须用 `--source-root` 指到真实资料根目录，保证 scenario JSON 里的相对路径能解析到实际文件。

## 6. 常用参数

- `--scenario`：可重复，支持 `B/C/D/E` 或自定义 scenario 目录。
- `--source-root`：真实资料根目录。
- `--run-id`：手动指定 run id。
- `--run-root`：手动指定结果输出目录。
- `--session-limit`：只跑前几个 session。
- `--turn-limit`：只跑每个 session 的前几个 turn。
- `--resume`：从 checkpoint 恢复。
- `--no-mirror`：不把 summary 回写到 workspace。
- `--judge-mode off`：关闭启发式 judge，便于只验证链路。

## 7. 断点恢复

如果 run 中断，可用同一个 `run_id` 和 `run_root` 恢复：

```powershell
$env:NO_PROXY='127.0.0.1,localhost'
python -m auto_eval.cli `
  --backend-url http://127.0.0.1:8002 `
  --scenario auto_eval/tests/fixtures/smoke_scenario `
  --source-root auto_eval/tests/fixtures/smoke_scenario `
  --run-id actual_backend_smoke `
  --run-root auto_eval/eval_runs/actual_backend_smoke `
  --resume
```

checkpoint 在：

- `backend/auto_eval/eval_runs/<run_id>/checkpoints/completed_turns.json`

## 8. 先自测

集成测试命令：

```powershell
python -m unittest auto_eval.tests.test_http_smoke_runner
```

这个测试会起一个最小 FastAPI 假后端，然后用真正的 `auto_eval` CLI 通过 HTTP 跑完整 smoke 流程。

## 9. 出错时先看哪里

- 后端没起来：先检查 `http://127.0.0.1:8002/` 是否返回 `200`。
- 本地请求走代理：设置 `NO_PROXY=127.0.0.1,localhost`。
- 真实后端导入失败：优先看缺的 Python 依赖，比如 `html2text`。
- 场景资料找不到：检查 `--source-root` 和 scenario JSON 里的 `user_upload` 相对路径。
- 结果不完整：看 `events.jsonl`、`terminal_replay.txt`、`completed_turns.json`。
