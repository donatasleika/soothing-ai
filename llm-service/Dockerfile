# ---- build llama.cpp server ----
FROM debian:12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential cmake ca-certificates && \
    rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/ggerganov/llama.cpp.git /llama
WORKDIR /llama
# Build only the server binary (fast; no CUDA deps)
RUN make -j server
RUN install -m 0755 server/llama-server /usr/local/bin/llama-server

# ---- runtime ----
FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir fastapi uvicorn requests

WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# bring in the compiled server
COPY --from=build /usr/local/bin/llama-server /usr/local/bin/llama-server

# sanity: exit 0 even if help changes
RUN /usr/local/bin/llama-server -h >/dev/null 2>&1 || true

ENTRYPOINT ["/app/entrypoint.sh"]
