import os
import whisper
import tempfile
import shutil
from fastapi import Request, UploadFile, File
from nicegui import app, ui
import httpx

MODEL_URL = os.getenv('LLAMA_BASE')

# Wherever you saved the ffmpeg binary (e.g., in your project folder)
os.environ["PATH"] += os.pathsep + "/Users/donatas/Documents/tools"

# Load the Whisper model once (can be "base", "tiny", "medium", "large")
model = whisper.load_model("base")

# This will store the latest transcript to share it with the frontend
latest_pro_transcript = {"pro_text": "", "llm_pro_response": None}

latest_user_transcript = {"user_text": "", "llm_user_response": None}


# WHISPER
async def upload_user_audio(request: Request, file: UploadFile = File(...)):
    # Save the uploaded file to a temp file
    ext = os.path.splitext(file.filename or "")[1].lower() or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Transcribe with Whisper
    try:
        result = model.transcribe(tmp_path)
        text = result.get("user_text", "")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    latest_user_transcript["pro_text"] = text

async def get_transcript_user():
    return {
        "user_text": latest_pro_transcript.get("user_text", ""),
        "llm_user_response": latest_pro_transcript.get("llm_user_response", None),
    }


async def passthrough_text_llm_user(text):
    payload = {
        "model": "test",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": 

                    "You are a helpful assistant." 
                ,
            },
            {
                "role": "user",
                "content": (f"{text}") 
                # "content": f"{entry_data['description']}"
                }
            ]
    }
    

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=580.0, write=30.0, pool=5.0)) as client:
        resp = await client.post(MODEL_URL, json=payload)
        
        print("Response object:", resp, flush=True)
        print("Status code:", resp.status_code, flush=True)
        print("Body head:", resp.text[:500], flush=True)


        if resp.status_code in (500, 502, 503, 504):
            raise httpx.HTTPStatusError(
                message="Server Error",
                request=resp.request,
                response=resp
            )
        # print(f'AYOO    {resp.json()}')
        resp.raise_for_status()
        return resp.json()

async def get_llm_response_user():
    return {"user_response": latest_pro_transcript.get("llm_user_response", "")}


async def upload_pro_audio(request: Request, file: UploadFile = File(...)):
    # Save the uploaded file to a temp file
    ext = os.path.splitext(file.filename or "")[1].lower() or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Transcribe with Whisper
    try:
        result = model.transcribe(tmp_path)
        text = result.get("pro_text", "")
        print(text)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass



    latest_pro_transcript["pro_text"] = text

    model_response = await passthrough_text_llm_pro(text)
    latest_pro_transcript["llm_pro_response"] = model_response

    return {"pro_text": text}

async def get_transcript_pro():
    return {
        "pro_text": latest_pro_transcript.get("pro_text", ""),
        "llm_pro_response": latest_pro_transcript.get("llm_pro_response", None),
    }


async def passthrough_text_llm_pro(text):
    payload = {
        "model": "test",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": 

                    "You are a helpful assistant." 
                ,
            },
            {
                "role": "user",
                "content": (f"{text}") 
                # "content": f"{entry_data['description']}"
                }
            ]
    }
    

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=580.0, write=30.0, pool=5.0)) as client:
        resp = await client.post(MODEL_URL, json=payload)
        
        print("Response object:", resp, flush=True)
        print("Status code:", resp.status_code, flush=True)
        print("Body head:", resp.text[:500], flush=True)


        if resp.status_code in (500, 502, 503, 504):
            raise httpx.HTTPStatusError(
                message="Server Error",
                request=resp.request,
                response=resp
            )
        # print(f'AYOO    {resp.json()}')
        resp.raise_for_status()
        return resp.json()

async def get_llm_response_pro():
    return {"pro_response": latest_pro_transcript.get("llm_pro_response", "")}


def register_audio_ui():
    app.add_api_route("/get_pro_response", get_llm_response_pro, methods=["GET"])
    app.add_api_route("/upload_pro", upload_pro_audio, methods=["POST"])
    app.add_api_route("/get_pro_transcript", get_transcript_pro, methods=["GET"])

    app.add_api_route("/get_user_response", get_llm_response_user, methods=["GET"])
    app.add_api_route("/upload_user", upload_pro_audio, methods=["POST"])
    app.add_api_route("/get_user_transcript", get_transcript_user, methods=["GET"])
