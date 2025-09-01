FROM ghcr.io/ggerganov/llama.cpp:full

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN python3 -m pip install --no-cache-dir fastapi uvicorn requests

WORKDIR /app

# App files
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Runtime env
# MODEL_DIR will be provided by Cloud Run via --set-env-vars (e.g., /models)
ENV MODEL_FILE="llama3.1-8b-q4km@2025-08-12.gguf"
ENV LLAMA_PORT=8081

# Do NOT hardcode EXPOSE/ports for Cloud Run; it injects $PORT
CMD ["/app/entrypoint.sh"]
