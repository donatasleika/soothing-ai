#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=$PORT  LLAMA_PORT=$LLAMA_PORT"
echo "[boot] listing $MODEL_DIR"; ls -lah "$MODEL_DIR" || true

# print which llama-server we’ll run
if command -v llama-server >/dev/null 2>&1; then
  echo "[boot] llama-server at: $(command -v llama-server)"
  llama-server -h >/dev/null 2>&1 || true
else
  echo "[boot][ERROR] llama-server not in PATH"; sleep 1
fi

# start API first
python3 -m uvicorn api:app --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# start llama-server if binary and model exist
if command -v llama-server >/dev/null 2>&1 && [[ -f "$MODEL_PATH" ]]; then
  echo "[boot] starting llama-server with -m $MODEL_PATH on :$LLAMA_PORT"
  llama-server -m "$MODEL_PATH" --host 0.0.0.0 --port "$LLAMA_PORT" -c 2048 --no-webui \
    >/tmp/llama.log 2>&1 &
  ( sleep 1; echo '--- tailing /tmp/llama.log ---'; tail -n +1 -F /tmp/llama.log ) &
else
  echo "[boot][WARN] llama-server or model missing; API will run without model."
fi

wait "$API_PID"

