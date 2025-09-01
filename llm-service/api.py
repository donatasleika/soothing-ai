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
        raise HTTPException(status_code=503, detail=f"llama not ready: {e}")

@app.post("/extract")
def extract(text: str = Body(..., embed=True)):
    prompt = (
        "Extract only JSON from the entry. "
        "Extract the sentiment and emotional tone of the entry. "
        'Respond with JSON only as {"sentiment":"positive|neutral|negative","tone":"...","keywords":["..."]}. '
        f"Text:\n{text}\nJSON:"
    )
    try:
        rr = requests.post(
            LLAMA_URL + "/completion",
            json={"prompt": prompt, "n_predict": 64, "temperature": 0.0, "top_k": 1},
            timeout=45,
        )
        rr.raise_for_status()
        data = rr.json()
        content = data.get("content", "")
        return json.loads(content)
    except requests.HTTPError as e:
        raise HTTPException(status_code=rr.status_code, detail=rr.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"extract failed: {e}")