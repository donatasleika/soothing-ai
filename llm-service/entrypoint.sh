#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_DIR="${MODEL_DIR:-/models}"
MODEL_FILE="${MODEL_FILE:-llama3.1-8b-q4km@2025-08-12.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

echo "[boot] PORT=$PORT  LLAMA_PORT=$LLAMA_PORT"
echo "[boot] listing $MODEL_DIR"; ls -lah "$MODEL_DIR" || true

MODEL_GCS="${MODEL_GCS:-}"
if [[ -n "$MODEL_GCS" ]]; then
  echo "[boot] downloading model from $MODEL_GCS"
  mkdir -p "$MODEL_DIR"
  gsutil -m cp "$MODEL_GCS" "$MODEL_PATH"
fi


# Start llama first
if [[ -f "$MODEL_PATH" ]] && command -v llama-server >/dev/null 2>&1; then
  echo "[boot] starting llama-server -m $MODEL_PATH on 127.0.0.1:$LLAMA_PORT"
  llama-server -m "$MODEL_PATH" --host 127.0.0.1 --port "$LLAMA_PORT" -c 2048 --no-webui \
    >/tmp/llama.log 2>&1 &
    LLAMA_PID=$!


# Launch llama-server if possible and tail its log
if [[ -f "$MODEL_PATH" ]] && command -v llama-server >/dev/null 2>&1; then
  echo "[boot] starting llama-server with -m $MODEL_PATH on :$LLAMA_PORT"
  llama-server -m "$MODEL_PATH" --host 127.0.0.1 --port "$LLAMA_PORT" -c 2048 --no-webui \
    >/tmp/llama.log 2>&1 &
    LLAMA_PID=$!


    sleep 1
    if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
      echo "[boot][ERROR] llama-server exited immediately"
      echo '--- tailing /tmp/llama.log ---'
      cat /tmp/llama.log || true
      exit 1
    fi

    echo "[boot] waiting for llama-server socket"
    for i in $(seq 1 120); do
      if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null 2>&1; then
        echo "[boot] llama-server is up"
        break
      fi
      sleep 0.5
    done

    ( echo '--- tailing /tmp/llama.log ---'; tail -n +1 -F /tmp/llama.log ) &
else
  echo "[boot][WARN] llama-server or model missing; API will run without model."
fi



# Start API (proxy headers fix scheme/redirects)
exec python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*"