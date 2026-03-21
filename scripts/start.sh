#!/usr/bin/env bash
#
# start.sh — Simple startup script for No Prob Bob.
#
# Does three things:
#   1. Makes sure Ollama is running
#   2. Activates the venv
#   3. Starts the bot server
#
# Usage: bash scripts/start.sh
#        bash scripts/start.sh --background   (detach, log to logs/server.log)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

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
BACKGROUND=false
[[ "${1:-}" == "--background" ]] && BACKGROUND=true

# ── Kill any existing server on the port ─────────────────────
if lsof -ti :"$PORT" >/dev/null 2>&1; then
  echo "Killing existing process on port $PORT..."
  lsof -ti :"$PORT" | xargs kill -9 2>/dev/null
  sleep 1
fi

# ── Check Ollama ─────────────────────────────────────────────
if ! pgrep -qf "ollama"; then
  echo "Starting Ollama..."
  open -a Ollama 2>/dev/null || ollama serve &
  sleep 3
fi

MODEL="${OLLAMA_MODEL:-qwen3:4b}"
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
  echo "Pulling model $MODEL (first time only)..."
  ollama pull "$MODEL"
fi
echo "✓ Ollama running, model $MODEL available"

# ── Activate venv ────────────────────────────────────────────
if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  source "$REPO_ROOT/.venv/bin/activate"
else
  echo "ERROR: .venv not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'"
  exit 1
fi

# ── Start server ─────────────────────────────────────────────
if $BACKGROUND; then
  mkdir -p "$REPO_ROOT/logs"
  echo "Starting server in background (logs: logs/server.log)..."
  nohup python3 -m bot.server > "$REPO_ROOT/logs/server.log" 2>&1 &
  SERVER_PID=$!
  sleep 3

  if lsof -ti :"$PORT" >/dev/null 2>&1; then
    echo ""
    echo "======================================="
    echo "  ✓ Server running on port $PORT"
    echo "  URL: http://localhost:$PORT/chat"
    echo "  PID: $SERVER_PID"
    echo "  Log: tail -f logs/server.log"
    echo "  Stop: kill $SERVER_PID"
    echo "======================================="
  else
    echo "ERROR: Server failed to start. Check logs/server.log"
    exit 1
  fi
else
  echo ""
  echo "======================================="
  echo "  Starting on http://localhost:$PORT/chat"
  echo "  Press Ctrl+C to stop"
  echo "======================================="
  echo ""
  python3 -m bot.server
fi
