#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"                # Cloud Run injects this
LLAMA_PORT="${LLAMA_PORT:-8081}"    # internal port for llama-server
MODEL_DIR="${MODEL_DIR:-/models}"   # GCS mount path
MODEL_FILE="${MODEL_FILE:-model.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=${PORT} LLAMA_PORT=${LLAMA_PORT}"
echo "[boot] Listing ${MODEL_DIR}:"
ls -lah "${MODEL_DIR}" || true
echo "[boot] Expecting model at: ${MODEL_PATH}"

# Start llama-server in the background **without blocking**
if [[ -f "${MODEL_PATH}" ]]; then
  /usr/local/bin/llama-server \
    --model "${MODEL_PATH}" \
    --host 0.0.0.0 \
    --port "${LLAMA_PORT}" \
    --ctx-size 4096 \
    --parallel 1 \
    --no-webui \
    >/tmp/llama.log 2>&1 &
  echo "[boot] llama-server started (PID $!) on :${LLAMA_PORT}"
else
  echo "[boot][WARN] Model file not found at ${MODEL_PATH}. API will start but /extract will return 503."
fi

# Optionally: background readiness logger (non-blocking)
(
  for i in {1..60}; do
    if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null 2>&1; then
      echo "[boot] llama-server is responsive."
      exit 0
    fi
    sleep 1
  done
  echo "[boot][WARN] llama-server did not become ready within 60s."
) &

# Finally: exec the API proxy so it binds to $PORT immediately
exec python3 -m uvicorn api:app --host 0.0.0.0 --port "${PORT}"