from fastapi import FastAPI, Body, HTTPException
import requests, json, os, pathlib

LLAMA = "http://127.0.0.1:8080/completion"
# GBNF = pathlib.Path("schema.gbnf").read_text()

app = FastAPI()

@app.get("/healthz")
def health():
    # best-effort health check
    try:
        r = requests.get("http://127.0.0.1:8080/props", timeout=2)
        r.raise_for_status()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(503, f"llama-server not ready: {e}")

@app.post("/extract")
def extract(text: str = Body(..., embed=True)):
    prompt = (
        'Extract only JSON from the entry. \
        Extract the sentiment and emotional tone of the entry. \
        Really think about if the statements show a positive side or negative side \
        Respond with JSON only as \
        {"sentiment": ["..."]} - (can only be "positive", "neutral", or "negative") and \
        {"tone": ["..."]} and \
        {"keywords": ["..."]} - (get only from the prompt text).' \

        f'Text:\n{text}\nJSON:' \

        # 'If the text entry is just one word then just classify as "illegible" ' \
        
    )
    
    r = requests.post(LLAMA, json={
        "prompt": prompt,
        "n_predict": 64,
        "temperature": 0,
        "top_k": 1,
        # "grammar": GBNF
    }, timeout=120)
    r.raise_for_status()
    return json.loads(r.json()["content"])
