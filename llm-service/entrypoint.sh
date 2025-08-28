#!/bin/bash
set -euo pipefail

# REQUIRED: set MODEL_URL via Cloud Run env var, e.g.
# gs://my-llama-models-eu/llama3.1-8b-q4km@2025-08-12.gguf
: "${MODEL_URL:?Set MODEL_URL to gs://bucket/path/model.gguf}"

MODEL_DIR="/my_models"
MODEL_PATH="${MODEL_DIR}/model.gguf"
export MODEL_PATH

CTX="${CTX:-8192}"

mkdir -p "$MODEL_DIR"

echo "[startup] ensuring model exists at $MODEL_PATH ..."
if [ ! -f "$MODEL_PATH" ]; then
  echo "[startup] downloading from ${MODEL_URL} via google-cloud-storage"
  python3 - <<'PY'
import os, sys
from urllib.parse import urlparse
from google.cloud import storage

model_url = os.environ["MODEL_URL"]
dest = os.environ["MODEL_PATH"]

parsed = urlparse(model_url)
if parsed.scheme != "gs":
    sys.exit(f"MODEL_URL must be gs://..., got: {model_url}")

bucket_name = parsed.netloc
blob_name = parsed.path.lstrip("/")

client = storage.Client()  # uses ADC / Cloud Run SA
bucket = client.bucket(bucket_name)
blob = bucket.blob(blob_name)

os.makedirs(os.path.dirname(dest), exist_ok=True)
blob.download_to_filename(dest)
print(f"[startup] downloaded {bucket_name}/{blob_name} -> {dest}")
PY
fi

echo "[startup] launching llama-server..."
/llama-server -m "$MODEL_PATH" -c "$CTX" --port 8081 &

echo "[startup] launching FastAPI proxy..."
uvicorn api:app --host 0.0.0.0 --port 8080
