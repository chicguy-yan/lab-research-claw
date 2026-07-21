#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-${BACKEND_PORT:-8002}}"
BACKEND_DIR="${ROOT_DIR}/backend"
VENV_DIR="${BACKEND_DIR}/.venv"
REQUIREMENTS_FILE="${BACKEND_DIR}/requirements.txt"

kill_port() {
  local port="$1"

  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti tcp:"${port}" || true)"
    if [[ -n "${pids}" ]]; then
      echo "[backend] Killing process(es) on port ${port}: ${pids}"
      kill -9 ${pids} || true
    fi
    return
  fi

  if command -v fuser >/dev/null 2>&1; then
    if fuser "${port}/tcp" >/dev/null 2>&1; then
      echo "[backend] Killing process(es) on port ${port} via fuser"
      fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    fi
    return
  fi

  echo "[backend] Warning: no supported port cleanup tool found; skipping auto-kill" >&2
}

resolve_venv_python() {
  local candidate
  for candidate in \
    "${VENV_DIR}/bin/python" \
    "${VENV_DIR}/bin/python3"
  do
    if [[ -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done

  return 1
}

bootstrap_venv_with_uv() {
  if ! command -v uv >/dev/null 2>&1; then
    echo "[backend] uv not found, cannot auto-create ${VENV_DIR}" >&2
    return 1
  fi

  if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
    echo "[backend] requirements.txt not found in ${BACKEND_DIR}" >&2
    return 1
  fi

  echo "[backend] Bootstrapping virtualenv with uv"
  uv venv "${VENV_DIR}"
  uv pip install --python "${VENV_DIR}/bin/python" -r "${REQUIREMENTS_FILE}"
}

resolve_python() {
  local venv_python

  if venv_python="$(resolve_venv_python)"; then
    printf '%s\n' "${venv_python}"
    return
  fi

  if bootstrap_venv_with_uv; then
    if venv_python="$(resolve_venv_python)"; then
      printf '%s\n' "${venv_python}"
      return
    fi
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  echo "[backend] No usable Python interpreter found" >&2
  exit 1
}

ensure_backend_dependencies() {
  local python_bin="$1"

  if "${python_bin}" -c 'import uvicorn, fastapi, langchain_openai' >/dev/null 2>&1; then
    return
  fi

  if [[ "${python_bin}" == "${VENV_DIR}/bin/python" || "${python_bin}" == "${VENV_DIR}/bin/python3" ]]; then
    if command -v uv >/dev/null 2>&1 && [[ -f "${REQUIREMENTS_FILE}" ]]; then
      echo "[backend] Installing backend dependencies into ${VENV_DIR}"
      uv pip install --python "${python_bin}" -r "${REQUIREMENTS_FILE}"
      return
    fi
  fi

  cat >&2 <<EOF
[backend] Required dependencies are missing for ${python_bin}
[backend] Expected modules: uvicorn, fastapi, langchain_openai
[backend] Fix:
[backend]   cd "${BACKEND_DIR}"
[backend]   uv venv .venv
[backend]   uv pip install --python .venv/bin/python -r requirements.txt
EOF
  exit 1
}

PYTHON_BIN="$(resolve_python)"

echo "[backend] Preparing to start backend on port ${PORT}"
kill_port "${PORT}"

cd "${BACKEND_DIR}"

if [[ ! -f app.py ]]; then
  echo "[backend] app.py not found in ${BACKEND_DIR}" >&2
  exit 1
fi

ensure_backend_dependencies "${PYTHON_BIN}"

echo "[backend] Starting backend from $(pwd)"
echo "[backend] Python: ${PYTHON_BIN}"
exec "${PYTHON_BIN}" -m uvicorn app:app --host 0.0.0.0 --port "${PORT}" --reload
