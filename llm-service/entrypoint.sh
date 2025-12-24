#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_PATH="${MODEL_PATH:-/models/llama3.1-8b-q4km@2025-08-12.gguf}"
LOCAL_MODEL="/tmp/model.gguf"

echo "[boot] PORT=$PORT LLAMA_PORT=$LLAMA_PORT MODEL_PATH=$MODEL_PATH"
ls -lah "$(dirname "$MODEL_PATH")" || true

echo "[boot] copying model to local disk: $LOCAL_MODEL"
cp -f "$MODEL_PATH" "$LOCAL_MODEL"
ls -lah "$LOCAL_MODEL" || true

echo "[boot] starting llama-server..."
/usr/local/bin/llama-server \
  -m "$LOCAL_MODEL" \
  --host 127.0.0.1 \
  --port "$LLAMA_PORT" \
  --no-webui \
  --no-mmap \
  -c 2048 \
  2>&1 &
LLAMA_PID=$!

# fail fast if it dies immediately
sleep 2
if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
  echo "[boot][ERROR] llama-server exited immediately"
  wait "$LLAMA_PID" || true
  exit 1
fi

echo "[boot] waiting for llama OpenAI endpoint..."
READY=0
LAST_ERR=""
for ((i=1; i<=180; i++)); do
  if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/v1/models" >/dev/null 2>&1; then
    READY=1
    echo "[boot] llama ready"
    break
  else
    LAST_ERR="$(curl -fsS "http://127.0.0.1:${LLAMA_PORT}/v1/models" 2>&1 || true)"
  fi

  if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
    echo "[boot][ERROR] llama-server died during startup"
    wait "$LLAMA_PID" || true
    exit 1
  fi

  sleep 1
done

if [[ "$READY" -ne 1 ]]; then
  echo "[boot][ERROR] llama-server not ready after 180s"
  echo "[boot][ERROR] last curl error: ${LAST_ERR}"
  kill "$LLAMA_PID" 2>/dev/null || true
  wait "$LLAMA_PID" 2>/dev/null || true
  exit 1
fi

cd /app
exec python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*"