#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-${FRONTEND_PORT:-5173}}"
FRONTEND_DIR="${ROOT_DIR}/frontend"

echo "[frontend] Preparing to start Vite on port ${PORT}"

kill_port() {
  local port="$1"

  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti "tcp:${port}" || true)"
    if [[ -n "${pids}" ]]; then
      echo "[frontend] Killing process(es) on port ${port}: ${pids}"
      kill -9 ${pids} || true
    fi
    return
  fi

  if command -v fuser >/dev/null 2>&1; then
    if fuser "${port}/tcp" >/dev/null 2>&1; then
      echo "[frontend] Killing process(es) on port ${port} via fuser"
      fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    fi
    return
  fi

  if command -v ss >/dev/null 2>&1; then
    local pids
    pids="$(ss -lptn "sport = :${port}" 2>/dev/null | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u)"
    if [[ -n "${pids}" ]]; then
      echo "[frontend] Killing process(es) on port ${port}: ${pids}"
      kill -9 ${pids} || true
    fi
    return
  fi

  echo "[frontend] Warning: no supported port cleanup tool found; skipping auto-kill" >&2
}

kill_port "${PORT}"

if ! command -v node >/dev/null 2>&1; then
  echo "[frontend] node is not installed or not in PATH" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "[frontend] npm is not installed or not in PATH" >&2
  exit 1
fi

cd "${FRONTEND_DIR}"

if [[ ! -f package.json ]]; then
  echo "[frontend] package.json not found in ${FRONTEND_DIR}" >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  echo "[frontend] node_modules missing, running npm install"
  npm install
fi

if ! npm exec vite -- --version >/dev/null 2>&1; then
  echo "[frontend] Vite is not available, refreshing frontend dependencies"
  npm install
fi

echo "[frontend] Starting dev server from $(pwd)"
exec npm run dev -- --host 0.0.0.0 --port "${PORT}" --strictPort
