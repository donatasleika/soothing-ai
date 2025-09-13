#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=$PORT  LLAMA_PORT=$LLAMA_PORT"
echo "[boot] listing $MODEL_DIR"; ls -lah "$MODEL_DIR" || true

# 1) Start API first so Cloud Run sees a listener
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*"

# 2) Start llama-server if present
LLAMA_BIN="$(command -v llama-server || true)"
if [[ -z "$LLAMA_BIN" ]]; then
  echo "[boot][WARN] llama-server not found; API will run without model."
elif [[ -f "$MODEL_PATH" ]]; then
  echo "[boot] starting llama-server with -m $MODEL_PATH on :$LLAMA_PORT"
  "$LLAMA_BIN" -m "$MODEL_PATH" --host 0.0.0.0 --port "$LLAMA_PORT" -c 4096 --no-webui >/tmp/llama.log 2>&1 &
else
  echo "[boot][WARN] model not found at $MODEL_PATH; skipping llama start."
fi

wait "$API_PID"
