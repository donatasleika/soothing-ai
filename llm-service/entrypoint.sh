#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_GCS="${MODEL_GCS:-}"

echo "[boot] PORT=$PORT LLAMA_PORT=$LLAMA_PORT"
mkdir -p "$MODEL_DIR"

# 1) Start API immediately (satisfies Cloud Run)
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# 2) Background: download model + start llama
(
  set -euo pipefail

  if [[ -n "$MODEL_GCS" && ! -f "$MODEL_PATH" ]]; then
    echo "[boot] downloading model from $MODEL_GCS -> $MODEL_PATH"
    gsutil -m cp "$MODEL_GCS" "$MODEL_PATH"
  fi

  if [[ ! -f "$MODEL_PATH" ]]; then
    echo "[boot][ERROR] model file not found at $MODEL_PATH"
    exit 1
  fi

  if ! command -v llama-server >/dev/null 2>&1; then
    echo "[boot][ERROR] llama-server not in PATH"
    exit 1
  fi

  echo "[boot] starting llama-server on 127.0.0.1:$LLAMA_PORT"
  llama-server \
    -m "$MODEL_PATH" \
    --host 127.0.0.1 \
    --port "$LLAMA_PORT" \
    -c 2048 \
    --no-webui \
    >/tmp/llama.log 2>&1

) &

# Optional: stream llama logs to Cloud Run logs
( sleep 1; echo "--- tail /tmp/llama.log ---"; tail -n +1 -F /tmp/llama.log ) &

wait "$API_PID"
