#!/bin/bash
set -euo pipefail

PORT="${PORT:-8080}"
LLAMA_PORT="${LLAMA_PORT:-8081}"
MODEL_PATH="${MODEL_PATH:-/models/llama3.1-8b-q4km@2025-08-12.gguf}"

echo "[boot] PORT=$PORT LLAMA_PORT=$LLAMA_PORT MODEL_PATH=$MODEL_PATH"
echo "[boot] which llama-server: $(command -v llama-server || true)"
ls -lah /models || true

if [[ -f "$MODEL_PATH" ]]; then
  echo "[boot] starting llama-server..."
  /usr/local/bin/llama-server \
    -m "$MODEL_PATH" \
    --host 127.0.0.1 \
    --port "$LLAMA_PORT" \
    -c 2048 \
    --no-webui \
    >/tmp/llama.log 2>&1 &
  LLAMA_PID=$!
  sleep 1
  if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
    echo "[boot][ERROR] llama-server exited"
    tail -n 200 /tmp/llama.log || true
  else
    echo "[boot] llama-server pid=$LLAMA_PID"
  fi
else
  echo "[boot][ERROR] model missing at $MODEL_PATH"
fi

cd /app
exec python3 -m uvicorn api:app \
  --host 0.0.0.0 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips="*"



# echo "[boot] entrypoint running"
# echo "[boot] PORT=${PORT:-}"
# echo "[boot] pwd=$(pwd)"
# ls -lah /app || true
# python3 -V
# python3 -c "import fastapi, uvicorn; print('[boot] fastapi', fastapi.__version__, 'uvicorn', uvicorn.__version__)"

# PORT="${PORT:-8080}"
# cd /app
# exec python3 -m uvicorn api:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"