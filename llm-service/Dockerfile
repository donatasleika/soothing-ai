FROM ghcr.io/ggerganov/llama.cpp:full
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates curl && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir fastapi uvicorn requests
WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
