#!/usr/bin/env bash
#
# run.sh — Unified launcher with health checks, watchdog, and Ollama pre-check.
#
# Ported from iphone-and-companion-transcribe-mode/scripts/run.sh.
#
# Features:
#   - .env loading (handles inline comments and # in values)
#   - Ollama pre-check: starts, pulls model, warms into memory
#   - caffeinate: prevents Mac sleep while running
#   - Watchdog: health checks every 60s, auto-restarts on failure
#
# Usage: bash scripts/run.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Load .env ────────────────────────────────────────────────
if [ -f "$REPO_ROOT/.env" ]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    key="${line%%=*}"
    value="${line#*=}"
    value="$(echo "$value" | sed 's/[[:space:]][[:space:]]*#.*$//' | sed 's/[[:space:]]*$//')"
    export "$key=$value"
  done < "$REPO_ROOT/.env"
fi

PORT="${PORT:-1203}"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/server.log"

mkdir -p "$LOG_DIR"

# PIDs to clean up
SERVER_PID=""
CAFFEINATE_PID=""
TAIL_PID=""

cleanup() {
  echo ""
  echo "Shutting down..."
  [ -n "$TAIL_PID" ] && kill "$TAIL_PID" 2>/dev/null || true
  if [ -n "$SERVER_PID" ]; then
    echo "  Stopping server (PID $SERVER_PID)..."
    kill "$SERVER_PID" 2>/dev/null || true
    sleep 1
    if kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "  Force-killing server..."
      kill -9 "$SERVER_PID" 2>/dev/null || true
    fi
  fi
  [ -n "$CAFFEINATE_PID" ] && kill "$CAFFEINATE_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ── Python detection ─────────────────────────────────────────
find_python() {
  local venv_py="$REPO_ROOT/.venv/bin/python3"
  if [ -x "$venv_py" ]; then
    echo "$venv_py"
    return 0
  fi

  local candidates=("python3" "python" "/usr/bin/python3" "/usr/local/bin/python3")
  for py in "${candidates[@]}"; do
    if command -v "$py" >/dev/null 2>&1 || [ -x "$py" ]; then
      echo "$py"
      return 0
    fi
  done
  return 1
}

echo "=== Customer Discovery Agent ==="
echo ""
echo "Finding Python..."

PYTHON=$(find_python) || {
  echo "ERROR: No Python found."
  echo "  Install Python 3.11+ or create a venv: python3 -m venv .venv"
  exit 1
}
echo "  Using: $PYTHON ($($PYTHON --version 2>&1))"
echo ""

# ── Ollama pre-check ──────────────────────────────────────
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:4b}"

echo "Checking Ollama ($OLLAMA_MODEL)..."
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "  Ollama not running — starting it..."
  open -a Ollama 2>/dev/null || ollama serve >/dev/null 2>&1 &
  for i in $(seq 1 15); do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  WARNING: Ollama still not responding. LLM calls will fail."
  else
    echo "  Ollama started"
  fi
else
  echo "  Ollama running"
fi

# Verify model
if curl -sf http://localhost:11434/api/tags 2>/dev/null | grep -q "\"$OLLAMA_MODEL\""; then
  echo "  Model $OLLAMA_MODEL: available"
else
  echo "  Model $OLLAMA_MODEL not found — pulling..."
  ollama pull "$OLLAMA_MODEL" 2>&1 | tail -1
fi

# Warm model
echo "  Warming model into memory..."
curl -sf http://localhost:11434/api/generate -d "{\"model\":\"$OLLAMA_MODEL\",\"prompt\":\"hi\",\"stream\":false}" >/dev/null 2>&1 &
echo ""

# ── Prevent Mac sleep ─────────────────────────────────────
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -s -w $$ &
  CAFFEINATE_PID=$!
  echo "  caffeinate enabled — Mac will stay awake"
fi

WATCHDOG_INTERVAL="${WATCHDOG_INTERVAL:-60}"
RESTART_COUNT=0

# ═══════════════════════════════════════════════════════════
# Main service loop
# ═══════════════════════════════════════════════════════════
while true; do

if [ "$RESTART_COUNT" -gt 0 ]; then
  echo ""
  echo "[watchdog] === Restart #$RESTART_COUNT ==="
  echo ""
fi
RESTART_COUNT=$((RESTART_COUNT + 1))
SERVER_PID=""
TAIL_PID=""

# ── Start server ─────────────────────────────────────────────
if lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "  Server already running on port $PORT"
else
  echo "  Starting server on port $PORT..."
  cd "$REPO_ROOT"

  echo "--- server start $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG_FILE"
  "$PYTHON" -m bot.server >> "$LOG_FILE" 2>&1 &
  SERVER_PID=$!
  echo "  Server PID: $SERVER_PID"

  # Wait for port
  echo "  Waiting for port $PORT..."
  for i in $(seq 1 10); do
    if lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done

  if ! lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "ERROR: Server failed to bind port $PORT after 5s."
    echo "  Check: $LOG_FILE"
    if [ "$RESTART_COUNT" -le 1 ]; then
      exit 1
    fi
    echo "[watchdog] Will retry..."
    sleep 3
    continue
  fi
fi

# ── Health check ─────────────────────────────────────────────
echo "  Running health check..."
HEALTH_OK=false
for i in $(seq 1 5); do
  if curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
    HEALTH_OK=true
    break
  fi
  sleep 1
done

if $HEALTH_OK; then
  echo "  Health check PASSED"
else
  echo "  Health check FAILED"
  echo "  Check: $LOG_FILE"
  if [ "$RESTART_COUNT" -le 1 ]; then
    exit 1
  fi
  echo "[watchdog] Will retry..."
  kill "$SERVER_PID" 2>/dev/null || true
  SERVER_PID=""
  sleep 3
  continue
fi

# ── Display ──────────────────────────────────────────────────
echo ""
echo "======================================="
echo "  URL: http://localhost:$PORT/chat"
echo "======================================="
echo ""

# Open browser (first run only)
if [ "$RESTART_COUNT" -le 1 ]; then
  if command -v open >/dev/null 2>&1; then
    open "http://localhost:$PORT/chat"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$PORT/chat"
  fi
fi

# ── Tail logs ────────────────────────────────────────────────
echo "=== Watchdog active — health check every ${WATCHDOG_INTERVAL}s (Ctrl+C to stop) ==="
echo ""
tail -f "$LOG_FILE" &
TAIL_PID=$!

# ── Watchdog loop ────────────────────────────────────────
while true; do
  sleep "$WATCHDOG_INTERVAL"

  HEALTHY=true
  REASON=""

  if [ -n "$SERVER_PID" ] && ! kill -0 "$SERVER_PID" 2>/dev/null; then
    HEALTHY=false
    REASON="server process (PID $SERVER_PID) died"
  fi

  if $HEALTHY && ! curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
    HEALTHY=false
    REASON="health endpoint unresponsive"
  fi

  if ! $HEALTHY; then
    echo ""
    echo "[watchdog] $(date '+%Y-%m-%d %H:%M:%S') FAILURE: $REASON"
    echo "[watchdog] Tearing down for clean restart..."

    kill "$TAIL_PID" 2>/dev/null || true
    TAIL_PID=""

    if [ -n "$SERVER_PID" ]; then
      kill "$SERVER_PID" 2>/dev/null || true
      SERVER_PID=""
    fi

    echo "[watchdog] Waiting for port $PORT to free..."
    for i in $(seq 1 10); do
      if ! lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done

    echo "[watchdog] Restarting in 3s..."
    sleep 3
    break
  fi
done

done  # End main service loop
