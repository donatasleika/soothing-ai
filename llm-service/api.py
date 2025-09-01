from fastapi import FastAPI, Body, HTTPException
import requests, json, os, pathlib

app = FastAPI()
LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8081"))
LLAMA_URL = f"http://127.0.0.1:{LLAMA_PORT}"

@app.get("/healthz")
def healthz():
    try:
        r = requests.get(LLAMA_URL + "/", timeout=2)
        r.raise_for_status()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    

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