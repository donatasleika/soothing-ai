# ---- build llama.cpp server (CMake) ----
FROM debian:12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential cmake ca-certificates pkg-config \
    && rm -rf /var/lib/apt/lists/*
# llama.cpp moved under ggml-org; ggerganov redirects, but use the new canonical repo
RUN git clone https://github.com/ggml-org/llama.cpp.git /llama
WORKDIR /llama
# Build the server target
RUN cmake -S . -B build -DLLAMA_SERVER=ON -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build -j
# Install the server binary into a standard path
RUN install -m 0755 build/bin/llama-server /usr/local/bin/llama-server

# ---- runtime ----
FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir fastapi uvicorn requests

WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# bring in the compiled server
COPY --from=build /usr/local/bin/llama-server /usr/local/bin/llama-server

# quick sanity check (non-fatal)
RUN /usr/local/bin/llama-server -h >/dev/null 2>&1 || true

ENTRYPOINT ["/app/entrypoint.sh"]

