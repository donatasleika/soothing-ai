from fastapi import FastAPI, HTTPException, Body, Request, Response
from fastapi.responses import PlainTextResponse
import os, requests
import httpx

app = FastAPI()

LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8081"))
LLAMA_BASE = f"http://127.0.0.1:{LLAMA_PORT}"


@app.get("/", response_class=PlainTextResponse)
def root():
    return "llama-cpu alive"

def _probe_llama():
    try:
        r = requests.get(f"{LLAMA_BASE}/v1/models", timeout=2)
        r.raise_for_status()
        return {"ok": True}
    except Exception:
        r = requests.get(f"{LLAMA_BASE}/", timeout=2)
        r.raise_for_status()
        return {"ok": True}

# @app.get("/healthz")
@app.get("/healthz/")
def healthz():
    try:
        return _probe_llama()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"llama check failed: {e}")


# OpenAI-compatible endpoint for text completion
@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_v1(path: str, request:Request):
    upstream_url = f"{LLAMA_BASE}/v1/{path}"

    body = await request.body()
    params = dict(request.query_params)

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    headers.pop("connection", None)

    timeout = httpx.Timeout(connect=10.0, read=600.0, write=600.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.request(
            method=request.method,
            url=upstream_url,
            params=params,
            content=body,
            headers=headers,
        )

    passthrough = {}
    ct = r.headers.get("content-type")
    if ct:
        passthrough["content-type"] = ct

    return Response(content=r.content, status_code=r.status_code, headers=passthrough)

@app.post("/extract")
def extract(payload: dict = Body(...)):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=422, detail="missing 'text'")
    
    prompt = (
        'Extract only JSON. Return {"sentiment":"positive|neutral|negative","tone":"...","keywords":["..."]}. '
        f'Text:\\n{text}\\nJSON:'
    )
    # port = int(os.environ.get("LLAMA_PORT","8081"))
    
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
