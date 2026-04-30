import requests
import os
from dotenv import load_dotenv
import httpx
import asyncio
import backoff

load_dotenv()

MODEL_URL = os.getenv('LLAMA_BASE')


def _is_retryable(exc):
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (503, 500, 502, 504)
    return isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout))


# def get_completions(entry_data, tag_data):
@backoff.on_exception(
        backoff.expo,
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError),
        max_time = 240,
        giveup=lambda e: not _is_retryable(e)
)
async def get_completions(entry_data, counter=0):
    print(entry_data['description'])
    payload = {
        "model": "test",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a classifier. "
                    "Return ONLY valid JSON as below. "
                    "No prose, no explanations. "
                    "Only use the input text for the keywords. "
                    "Only use 'positive', 'neutral', 'negative' for sentiment"
                    "The JSON schema is:\n"
                    "{"
                    "  \"sentiment\": [string],"
                    "  \"tone\": [string],"
                    "  \"keywords\": [string]"
                    "}" 
                )
            },
            {
                "role": "user",
                "content": (f"{entry_data['description']}") 
                # "content": f"{entry_data['description']}"
                }
            ]
    }
    

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=580.0, write=30.0, pool=5.0)) as client:
        resp = await client.post(MODEL_URL, json=payload)
        
        print("Response object:", resp, flush=True)
        print("Status code:", resp.status_code, flush=True)
        print("Body head:", resp.text[:500], flush=True)

        counter += 1
        print("Tries:", counter, flush=True)

        if resp.status_code in (500, 502, 503, 504):
            raise httpx.HTTPStatusError(
                message="Server Error",
                request=resp.request,
                response=resp
            )
        # print(f'AYOO    {resp.json()}')
        resp.raise_for_status()
        return resp.json()

 

async def paste_recording(recording, counter=0):
    print(recording)
    payload = {
        "model": "test",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "}" 
                ),
            },
            {
                "role": "user",
                "content": (f"{recording}") 
                # "content": f"{entry_data['description']}"
                }
            ]
    }

async def paste_scoped_entries(entries, counter=0):
    payload = {
        "model": "test",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": ('''
                    You are a summarizer, so summarize semi-concisely and assign timestamps but do not invent new stuff" 
                '''),
            },
            {
                "role": "user",
                "content": (f"{entries[0]}") 
                # "content": f"{entry_data['description']}"
                }
            ]
    }


    

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=580.0, write=30.0, pool=5.0)) as client:
        resp = await client.post(MODEL_URL, json=payload)
        
        print("Response object:", resp, flush=True)
        print("Status code:", resp.status_code, flush=True)
        print("Body head:", resp.text[:500], flush=True)

        counter += 1
        print("Tries:", counter, flush=True)

        if resp.status_code in (500, 502, 503, 504):
            raise httpx.HTTPStatusError(
                message="Server Error",
                request=resp.request,
                response=resp
            )
        # print(f'AYOO    {resp.json()}')
        resp.raise_for_status()
        return resp.json()



async def handle(entry_data):
    result_json = await get_completions(entry_data, counter=0)
    print(f'Result from LLM: {result_json}')

    return result_json
        



if __name__ == '__main__':
    entry_data = ''

    # print(get_completions(client_data, entry_data, tag_data))
    print(get_completions(entry_data, counter=0))

# 2. Apply LLM


# 3. Pass over to database