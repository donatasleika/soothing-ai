#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/my_models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_GCS="${MODEL_GCS:-}"

echo "[boot] PORT=$PORT LLAMA_PORT=$LLAMA_PORT"
echo "[boot] which python=$(which python3)"
echo "[boot] which gsutil=$(command -v gsutil || echo MISSING)"
echo "[boot] which llama-server=$(command -v llama-server || echo MISSING)"
mkdir -p "$MODEL_DIR"

# Start API immediately (must bind PORT fast)
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# Background worker: download + start llama, never kills API if it fails
(
  set -euo pipefail

  if [[ -n "$MODEL_GCS" && ! -f "$MODEL_PATH" ]]; then
    echo "[boot] downloading model from $MODEL_GCS -> $MODEL_PATH"
    gsutil -m cp "$MODEL_GCS" "$MODEL_PATH"
  fi

  if [[ ! -f "$MODEL_PATH" ]]; then
    echo "[boot][ERROR] model missing at $MODEL_PATH"
    exit 0
  fi

  if ! command -v llama-server >/dev/null 2>&1; then
    echo "[boot][ERROR] llama-server missing"
    exit 0
  fi

  echo "[boot] starting llama-server on 127.0.0.1:$LLAMA_PORT"
  llama-server -m "$MODEL_PATH" --host 127.0.0.1 --port "$LLAMA_PORT" -c 2048 --no-webui \
    >/tmp/llama.log 2>&1

) || true &

( sleep 1; echo "--- tail /tmp/llama.log ---"; tail -n +1 -F /tmp/llama.log ) &

wait "$API_PID"