#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_PATH="${MODEL_PATH:-/models/llama3.1-8b-q4km@2025-08-12.gguf}"
LOCAL_MODEL="/tmp/model.gguf"

echo "[boot] PORT=$PORT LLAMA_PORT=$LLAMA_PORT MODEL_PATH=$MODEL_PATH"
ls -lah "$(dirname "$MODEL_PATH")" || true

# 1) Start llama-server (but only after copying model locally)
echo "[boot] copying model to local disk: $LOCAL_MODEL"
cp -f "$MODEL_PATH" "$LOCAL_MODEL"
ls -lah "$LOCAL_MODEL"

echo "[boot] starting llama-server..."
/usr/local/bin/llama-server \
  -m "$LOCAL_MODEL" \
  --host 127.0.0.1 \
  --port "$LLAMA_PORT" \
  --no-webui \
  --no-mmap \
  -c 2048 \
  > /tmp/llama.log 2>&1 &
LLAMA_PID=$!

# Stream llama logs to Cloud Run logs
tail -n +1 -F /tmp/llama.log &
TAIL_PID=$!

# 2) Wait until llama responds 200 on "/"
echo "[boot] waiting for llama-server..."
for i in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${LLAMA_PORT}/" >/dev/null 2>&1; then
    echo "[boot] llama-server ready"
    break
  fi
  if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
    echo "[boot][ERROR] llama-server exited"
    tail -n 200 /tmp/llama.log || true
    exit 1
  fi
  sleep 1
done

# 3) Start API (foreground)
cd /app
exec python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*"