#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"
LOG_DIR="$ROOT_DIR/logs"
PID_DIR="$ROOT_DIR/run"

BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-4173}"
FRONTEND_DEPLOY_DIR="${FRONTEND_DEPLOY_DIR:-/www/wwwroot/baby.leateen.com}"

mkdir -p "$LOG_DIR" "$PID_DIR"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[ERROR] Required command not found: $cmd"
    exit 1
  fi
}

stop_if_running() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local old_pid
    old_pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && kill -0 "$old_pid" >/dev/null 2>&1; then
      echo "[INFO] Stopping old process: $old_pid"
      kill "$old_pid" || true
      sleep 1
    fi
    rm -f "$pid_file"
  fi
}

require_cmd python3
require_cmd npm

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  echo "[ERROR] backend/ or frontend/ directory not found under: $ROOT_DIR"
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[INFO] Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [[ -f "$BACKEND_DIR/requirements.txt" ]]; then
  echo "[INFO] Installing backend dependencies..."
  "$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
  "$VENV_DIR/bin/python" -m pip install -r "$BACKEND_DIR/requirements.txt"
fi

if [[ ! -f "$BACKEND_DIR/.env" && -f "$BACKEND_DIR/.env.example" ]]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  echo "[INFO] Created backend/.env from .env.example"
fi

if [[ ! -f "$FRONTEND_DIR/.env" && -f "$FRONTEND_DIR/.env.example" ]]; then
  cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
  echo "[INFO] Created frontend/.env from .env.example"
fi

echo "[INFO] Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [[ -f "package-lock.json" ]]; then
  npm ci
else
  npm install
fi

echo "[INFO] Building frontend..."
npm run build:prod

if [[ ! -d "$FRONTEND_DIR/dist" ]]; then
  echo "[ERROR] Frontend dist directory not found after build."
  exit 1
fi

echo "[INFO] Copying frontend dist to $FRONTEND_DEPLOY_DIR ..."
mkdir -p "$FRONTEND_DEPLOY_DIR"
cp -a "$FRONTEND_DIR/dist/." "$FRONTEND_DEPLOY_DIR/"

BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

stop_if_running "$BACKEND_PID_FILE"
stop_if_running "$FRONTEND_PID_FILE"

echo "[INFO] Starting backend on 0.0.0.0:$BACKEND_PORT ..."
nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app --app-dir "$BACKEND_DIR" --host 0.0.0.0 --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$BACKEND_PID_FILE"

echo "[INFO] Starting frontend preview on 0.0.0.0:$FRONTEND_PORT ..."
cd "$FRONTEND_DIR"
nohup npm run preview -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$FRONTEND_PID_FILE"

echo "[OK] Services started."
echo "[OK] Backend:  http://<server-ip>:$BACKEND_PORT"
echo "[OK] Frontend: http://<server-ip>:$FRONTEND_PORT"
echo "[INFO] Logs: $LOG_DIR/backend.log, $LOG_DIR/frontend.log"
echo "[INFO] PIDs: $BACKEND_PID_FILE, $FRONTEND_PID_FILE"
