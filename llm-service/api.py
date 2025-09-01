# api.py
from fastapi import FastAPI, Body, HTTPException
import requests, json, os

app = FastAPI()
LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8081"))
LLAMA_URL = f"http://127.0.0.1:{LLAMA_PORT}"

@app.get("/healthz")
def healthz():
    try:
        r = requests.get(LLAMA_URL + "/", timeout=1.5)
        r.raise_for_status()
        return {"ok": True}
    except Exception as e:
        # Don't crash the container; report not ready
        raise HTTPException(status_code=503, detail=f"llama not ready: {e}")

@app.post("/extract")
def extract(text: str = Body(..., embed=True)):
    prompt = (
        "Extract only JSON from the entry. "
        "Extract the sentiment and emotional tone of the entry. "
        "Decide if statements show a positive, neutral, or negative side. "
        'Respond with JSON only in the shape {"sentiment": "...", "tone": "...", "keywords": ["..."]}. '
        f"Text:\n{text}\nJSON:"
    )

    try:
        # llama.cpp server (classic) -> /completion with {"prompt": ...}
        rr = requests.post(
            LLAMA_URL + "/completion",
            json={
                "prompt": prompt,
                "n_predict": 64,
                "temperature": 0.0,
                "top_k": 1,
            },
            timeout=30,
        )
        rr.raise_for_status()
        data = rr.json()

        # Typical llama.cpp /completion returns {"content": "..."}; adjust if your build differs
        content = data.get("content", "")
        # Try to parse the JSON from the content; fall back with a clear error
        parsed = json.loads(content)
        # Basic shape check
        if not isinstance(parsed, dict) or "sentiment" not in parsed:
            raise ValueError("Model response missing expected keys")
        return parsed
    except requests.HTTPError as e:
        raise HTTPException(status_code=rr.status_code, detail=rr.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"extract failed: {e}")