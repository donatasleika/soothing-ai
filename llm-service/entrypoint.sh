#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=$PORT  LLAMA_PORT=$LLAMA_PORT"
echo "[boot] listing $MODEL_DIR"; ls -lah "$MODEL_DIR" || true

# Start API (proxy headers fix scheme/redirects)
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# Verify llama-server binary & linkage
if command -v llama-server >/dev/null 2>&1; then
  BIN="$(command -v llama-server)"
  echo "[boot] llama-server at: $BIN"
  (ldd "$BIN" || true) | sed 's/^/[ldd] /'
else
  echo "[boot][ERROR] llama-server not in PATH"
fi

# Launch llama-server if possible and tail its log
if [[ -f "$MODEL_PATH" ]] && command -v llama-server >/dev/null 2>&1; then
  echo "[boot] starting llama-server with -m $MODEL_PATH on :$LLAMA_PORT"
  llama-server -m "$MODEL_PATH" --host 0.0.0.0 --port "$LLAMA_PORT" -c 2048 --no-webui \
    >/tmp/llama.log 2>&1 &
  ( sleep 1; echo '--- tailing /tmp/llama.log ---'; tail -n +1 -F /tmp/llama.log ) &
else
  echo "[boot][WARN] llama-server or model missing; API will run without model."
fi

wait "$API_PID"
