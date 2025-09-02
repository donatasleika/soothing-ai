#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8080}"
echo "[diagA] python: $(python3 --version || true)"
echo "[diagA] which python3: $(command -v python3 || true)"
echo "[diagA] pip pkgs:"
python3 -c "import pkgutil; print(sorted([m.name for m in pkgutil.iter_modules()])[:20])" || true
echo "[diagA] starting uvicorn on $PORT"
exec python3 -c 'import os; from fastapi import FastAPI; import uvicorn
app=FastAPI()
@app.get("/healthz") 
def h(): return {"ok": True}
uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT","8080")))'
