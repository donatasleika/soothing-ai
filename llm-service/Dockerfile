# ---- build llama.cpp server (CMake) ----
FROM debian:12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential cmake ca-certificates pkg-config \
      libcurl4-openssl-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
# canonical repo
RUN git clone https://github.com/ggml-org/llama.cpp.git /llama
WORKDIR /llama
# Build only the server; keep CURL features enabled (we installed dev headers)
RUN cmake -S . -B build -DLLAMA_SERVER=ON -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build -j --target llama-server
RUN install -m 0755 build/bin/llama-server /usr/local/bin/llama-server

# ---- runtime: Python app + server binary ----
FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip ca-certificates curl libcurl4 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# Create venv to avoid PEP 668 issues
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir fastapi uvicorn requests

WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# bring in compiled llama-server
COPY --from=build /usr/local/bin/llama-server /usr/local/bin/llama-server
# non-fatal sanity check
RUN /usr/local/bin/llama-server -h >/dev/null 2>&1 || true

ENTRYPOINT ["/app/entrypoint.sh"]
