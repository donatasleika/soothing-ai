#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"                 # Cloud Run port
LLAMA_PORT="${LLAMA_PORT:-8081}"     # internal llama server port
MODEL_DIR="${MODEL_DIR:-/models}"    # GCS mount
MODEL_FILE="${MODEL_FILE:-model.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=${PORT}  LLAMA_PORT=${LLAMA_PORT}"
echo "[boot] Listing ${MODEL_DIR} ..."
ls -lah "${MODEL_DIR}" || true
echo "[boot] Expecting model at: ${MODEL_PATH}"

# ---- locate llama-server binary ----
LLAMA_BIN=""
if command -v llama-server >/dev/null 2>&1; then
  LLAMA_BIN="$(command -v llama-server)"
elif [[ -x "/usr/local/bin/llama-server" ]]; then
  LLAMA_BIN="/usr/local/bin/llama-server"
elif [[ -x "/app/build/bin/llama-server" ]]; then
  LLAMA_BIN="/app/build/bin/llama-server"
else
  # last resort: search once (can be slow but runs only at boot)
  LLAMA_BIN="$(/usr/bin/find / -type f -name llama-server 2>/dev/null | head -n1 || true)"
fi

if [[ -z "${LLAMA_BIN}" ]]; then
  echo "[boot][FATAL] llama-server binary not found in image."
  echo "[boot] PATH=${PATH}"
  exit 1
fi
echo "[boot] Using llama-server at: ${LLAMA_BIN}"

# ---- start llama-server in background if model present ----
if [[ -f "${MODEL_PATH}" ]]; then
  set +e
  "${LLAMA_BIN}" \
    -m "${MODEL_PATH}" \
    --host 0.0.0.0 \
    --port "${LLAMA_PORT}" \
    -c 4096 \
    --no-webui \
    >/tmp/llama.log 2>&1 &
  LLAMA_PID=$!
  set -e
  echo "[boot] llama-server started (PID ${LLAMA_PID}) on :${LLAMA_PORT}"
else
  echo "[boot][WARN] Model file NOT found at ${MODEL_PATH} — API will start; /extract will 503."
fi

# non-blocking readiness logger
( for i in {1..60}; do
    if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null 2>&1; then
      echo "[boot] llama-server is responsive."
      exit 0
    fi
    sleep 1
  done
  echo "[boot][WARN] llama-server did not become ready within 60s. Tail /tmp/llama.log in logs."
) &

# ---- run API (must bind to $PORT fast) ----
exec python3 -m uvicorn api:app --host 0.0.0.0 --port "${PORT}"
