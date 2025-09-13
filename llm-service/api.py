from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import os, requests

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def root():
    return "llama-cpu alive"

def _probe_llama():
    port = int(os.environ.get("LLAMA_PORT", "8081"))
    r = requests.get(f"http://127.0.0.1:{port}/", timeout=2)
    r.raise_for_status()
    return {"ok": True}

@app.get("/healthz")
@app.get("/healthz/")
def healthz():
    try:
        return _probe_llama()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"llama check failed: {e}")
