#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8002}"
BACKEND_PORT="${BACKEND_PORT:-8002}"
BENCHMARK_ROOT="${BENCHMARK_ROOT:-/Users/fenke/projects/study_ai/2-未完成项目存档/zly 规划-0219/benchmark 测试集}"
NO_PROXY_VALUE="${NO_PROXY:-127.0.0.1,localhost}"
export NO_PROXY="${NO_PROXY_VALUE}"
export no_proxy="${NO_PROXY_VALUE}"

# Keep parity with the Windows helper: this lets the backend boot with runtime stubs
# when the current environment is missing some optional imports.
export PYTHONPATH="${BACKEND_DIR}/auto_eval/tests/runtime_stubs${PYTHONPATH:+:${PYTHONPATH}}"

resolve_python() {
  if [[ -x "${BACKEND_DIR}/.venv/bin/python" ]]; then
    printf '%s\n' "${BACKEND_DIR}/.venv/bin/python"
    return
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  echo "[ERROR] No usable Python interpreter found." >&2
  exit 1
}

find_dataset_root() {
  local prefix="$1"
  find "${ROOT_DIR}" -type d -name "${prefix}_*" 2>/dev/null | while read -r dir; do
    if find "${dir}" -type d -name '*obsidian*' -print -quit | grep -q .; then
      printf '%s\n' "${dir}"
      return 0
    fi
  done
  return 1
}

wait_backend_ready() {
  local attempts=60
  local i
  for ((i=1; i<=attempts; i++)); do
    if curl -fsS --max-time 2 "${BACKEND_URL}/" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

run_scenario() {
  local letter="$1"
  local source_root="$2"
  local run_id="$3"

  echo "=================================================="
  echo "[RUN] Scenario ${letter}"
  echo "=================================================="
  "${PYTHON_BIN}" -m auto_eval.cli \
    --backend-url "${BACKEND_URL}" \
    --scenario "${letter}" \
    --source-root "${source_root}" \
    --run-id "${run_id}" \
    --run-root "auto_eval/eval_runs/${run_id}"
}

if [[ ! -f "${BACKEND_DIR}/auto_eval/cli.py" ]]; then
  echo "[ERROR] ${BACKEND_DIR}/auto_eval/cli.py not found" >&2
  exit 1
fi

PYTHON_BIN="$(resolve_python)"
RUN_STAMP="$(date '+%Y%m%d_%H%M%S')"
RUN_B="one_click_B_${RUN_STAMP}"
RUN_C="one_click_C_${RUN_STAMP}"
RUN_D="one_click_D_${RUN_STAMP}"
RUN_E="one_click_E_${RUN_STAMP}"

B_SRC="${B_SRC:-${BENCHMARK_ROOT}/B_文献与Concept}"
C_SRC="${C_SRC:-${BENCHMARK_ROOT}/C_实验与Task}"
D_SRC="${D_SRC:-${BENCHMARK_ROOT}/D_写作与Pack}"
E_SRC="${E_SRC:-${BENCHMARK_ROOT}/E_跨闭环桥接}"

if [[ ! -d "${B_SRC}" ]]; then B_SRC="$(find_dataset_root B || true)"; fi
if [[ ! -d "${C_SRC}" ]]; then C_SRC="$(find_dataset_root C || true)"; fi
if [[ ! -d "${D_SRC}" ]]; then D_SRC="$(find_dataset_root D || true)"; fi
if [[ ! -d "${E_SRC}" ]]; then E_SRC="$(find_dataset_root E || true)"; fi

if [[ -z "${B_SRC}" || -z "${C_SRC}" || -z "${D_SRC}" || -z "${E_SRC}" ]]; then
  cat >&2 <<EOF
[ERROR] Could not locate all scenario dataset roots automatically.

Provide them explicitly, for example:
  B_SRC="/path/to/B_dataset_root" \
  C_SRC="/path/to/C_dataset_root" \
  D_SRC="/path/to/D_dataset_root" \
  E_SRC="/path/to/E_dataset_root" \
  ./auto_eval_one_click_run.sh
EOF
  exit 1
fi

echo "[DATA] B = ${B_SRC}"
echo "[DATA] C = ${C_SRC}"
echo "[DATA] D = ${D_SRC}"
echo "[DATA] E = ${E_SRC}"

if curl -fsS --max-time 2 "${BACKEND_URL}/" >/dev/null 2>&1; then
  echo "[STEP] Backend already responding at ${BACKEND_URL}"
else
  echo "=================================================="
  echo "[STEP] Starting backend on ${BACKEND_URL}"
  echo "=================================================="
  (
    cd "${ROOT_DIR}"
    ./start_backend.sh "${BACKEND_PORT}"
  ) >/tmp/auto_eval_backend_${BACKEND_PORT}.log 2>&1 &
  BACKEND_PID=$!
  echo "[STEP] Backend pid=${BACKEND_PID}, log=/tmp/auto_eval_backend_${BACKEND_PORT}.log"
  echo "[STEP] Waiting for backend to become ready..."
  if ! wait_backend_ready; then
    echo "[ERROR] Backend did not become ready within timeout." >&2
    exit 1
  fi
fi

echo "[STEP] Backend is ready."

cd "${BACKEND_DIR}"
run_scenario B "${B_SRC}" "${RUN_B}"
run_scenario C "${C_SRC}" "${RUN_C}"
run_scenario D "${D_SRC}" "${RUN_D}"
run_scenario E "${E_SRC}" "${RUN_E}"

echo
echo "[DONE] All four scenarios finished."
echo "Reports are under backend/auto_eval/eval_runs/one_click_*"
