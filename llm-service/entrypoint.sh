#!/usr/bin/env bash
set -euo pipefail

# Cloud Run provides $PORT. Default to 8080 locally.
PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-model.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

# Start llama-server on an internal port (LLAMA_PORT)
# NOTE: binary path in the base image is usually /usr/local/bin/llama-server
/usr/local/bin/llama-server \
  --model "${MODEL_PATH}" \
  --host 0.0.0.0 \
  --port "${LLAMA_PORT}" \
  --ctx-size 4096 \
  --parallel 1 \
  --mlock \
  --no-webui \
  &
LLAMA_PID=$!

# Simple wait-for on llama-server
echo "Waiting for llama-server on :${LLAMA_PORT}..."
for i in {1..60}; do
  if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null 2>&1; then
    echo "llama-server is up."
    break
  fi
  sleep 1
done

# Exec uvicorn so it becomes PID 1 and receives signals properly
exec python3 -m uvicorn api:app --host 0.0.0.0 --port "${PORT}"