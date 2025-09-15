# --- build stage ---
FROM debian:12 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /llama
RUN git clone https://github.com/ggml-org/llama.cpp.git /llama
RUN cmake -S . -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLAMA_SERVER=ON \
      -DGGML_STATIC=ON \
      -DGGML_CURL=OFF \
      -DLLAMA_CURL=OFF \
      -DLLAMA_BUILD_EXAMPLES=OFF \
      -DLLAMA_BUILD_TESTS=OFF \
  && cmake --build build -j \
  && cmake --install build

# --- runtime stage ---
FROM debian:12
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*
COPY --from=build /usr/local/bin/llama-server /usr/local/bin/llama-server
WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir fastapi uvicorn requests
ENV PATH="/opt/venv/bin:${PATH}"
ENTRYPOINT ["/app/entrypoint.sh"]
