import os
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()

LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8081"))
LLAMA_BASE = f"http://127.0.0.1:{LLAMA_PORT}"

@app.get("/", response_class=PlainTextResponse)
def root():
    return "llama-cpu alive"

@app.get("/healthz/")
async def healthz():
    # Ready only when llama-server is serving the OpenAI-compatible endpoint
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{LLAMA_BASE}/v1/models")
        if r.status_code != 200:
            raise RuntimeError(f"status={r.status_code} body={r.text[:200]}")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"llama not ready: {e}")

@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_v1(path: str, request: Request):
    upstream_url = f"{LLAMA_BASE}/v1/{path}"

    body = await request.body()
    params = dict(request.query_params)

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    headers.pop("connection", None)

    timeout = httpx.Timeout(connect=10.0, read=600.0, write=600.0, pool=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        upstream = await client.request(
            method=request.method,
            url=upstream_url,
            params=params,
            content=body,
            headers=headers,
        )

    # minimal header passthrough
    out_headers = {}
    ct = upstream.headers.get("content-type")
    if ct:
        out_headers["content-type"] = ct

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=out_headers,
    )

@app.get("/diag")
async def diag():
    async with httpx.AsyncClient(timeout=2.0) as client:
        r_root = await client.get(f"{LLAMA_BASE}/")
        return {
            "llama_base": LLAMA_BASE,
            "root_status": r_root.status_code,
            "root_body": r_root.text[:200],
        }
