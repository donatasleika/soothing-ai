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

echo "[boot] starting llama-server (background)..."
/usr/local/bin/llama-server \
  -m "$LOCAL_MODEL" \
  --host 127.0.0.1 \
  --port "$LLAMA_PORT" \
  --no-webui \
  --no-mmap \
  -c 2048 \
  2>&1 &
LLAMA_PID=$!

echo "[boot] starting uvicorn immediately (foreground readiness for Cloud Run)..."
cd /app
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# If either process exits, crash the container so Cloud Run restarts it.
wait -n "$LLAMA_PID" "$API_PID"
code=$?
echo "[boot][ERROR] process exited (code=$code)"
exit "$code"
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

echo "[boot] starting llama-server (background)..."
/usr/local/bin/llama-server \
  -m "$LOCAL_MODEL" \
  --host 127.0.0.1 \
  --port "$LLAMA_PORT" \
  --no-webui \
  --no-mmap \
  -c 2048 \
  2>&1 &
LLAMA_PID=$!

echo "[boot] starting uvicorn immediately (foreground readiness for Cloud Run)..."
cd /app
python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*" &
API_PID=$!

# If either process exits, crash the container so Cloud Run restarts it.
wait -n "$LLAMA_PID" "$API_PID"
code=$?
echo "[boot][ERROR] process exited (code=$code)"
exit "$code"