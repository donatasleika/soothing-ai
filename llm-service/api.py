from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import PlainTextResponse
import os, requests

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def root():
    return "llama-cpu alive"

def _probe_llama():
    port = int(os.environ.get("LLAMA_PORT","8081"))
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

@app.post("/extract")
def extract(payload: dict = Body(...)):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=422, detail="missing 'text'")
    prompt = (
        'Extract only JSON. Return {"sentiment":"positive|neutral|negative","tone":"...","keywords":["..."]}. '
        f'Text:\\n{text}\\nJSON:'
    )
    port = int(os.environ.get("LLAMA_PORT","8081"))
    try:
        resp = requests.post(
            f"http://127.0.0.1:{port}/completion",
            json={"prompt": prompt, "n_predict": 64, "temperature": 0.0, "top_k": 1},
            timeout=120,
        )
        if not resp.ok:
            raise HTTPException(status_code=502, detail=f"llama error: {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"llama request failed: {e}")
