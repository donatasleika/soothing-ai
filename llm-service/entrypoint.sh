#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-model.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "Listing ${MODEL_DIR}:"
ls -lah "${MODEL_DIR}" || true
echo "Expecting model at: ${MODEL_PATH}"

if [[ ! -f "${MODEL_PATH}" ]]; then
  echo "FATAL: Model file not found at ${MODEL_PATH}" >&2
  exit 1
fi

# Start llama-server on an internal port
/usr/local/bin/llama-server \
  --model "${MODEL_PATH}" \
  --host 0.0.0.0 \
  --port "${LLAMA_PORT}" \
  --ctx-size 4096 \
  --parallel 1 \
  --no-webui &
LLAMA_PID=$!

# Wait until llama-server responds
for i in {1..60}; do
  if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null; then
    echo "llama-server is up on :${LLAMA_PORT}"
    break
  fi
  echo "Waiting for llama-server... ($i/60)"
  sleep 1
done

# Exec the API proxy that binds to $PORT
exec python3 -m uvicorn api:app --host 0.0.0.0 --port "${PORT}"