#!/bin/bash
set -euo pipefail

echo "[boot] entrypoint running"
echo "[boot] PORT=${PORT:-}"
echo "[boot] pwd=$(pwd)"
ls -lah /app || true
python3 -V
python3 -c "import fastapi, uvicorn; print('[boot] fastapi', fastapi.__version__, 'uvicorn', uvicorn.__version__)"

PORT="${PORT:-8080}"
cd /app
exec python3 -m uvicorn api:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"