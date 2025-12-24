# ---------- build stage ----------
FROM debian:12 AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git curl ca-certificates \
    libcurl4-openssl-dev pkg-config \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /llama
RUN git clone https://github.com/ggml-org/llama.cpp.git /llama

RUN cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_CURL=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DGGML_OPENMP=OFF \
    -DGGML_METAL=OFF -DGGML_CUDA=OFF -DGGML_VULKAN=OFF -DGGML_OPENCL=OFF \
  && cmake --build build --target llama-server -j 1

# ---------- runtime stage ----------
FROM debian:12

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash python3 python3-venv python3-pip ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

# Copy llama-server + shared libs built by the build stage
COPY --from=build /llama/build/bin/llama-server /usr/local/bin/llama-server
COPY --from=build /llama/build/bin/*.so* /usr/local/lib/
RUN ldconfig && /usr/local/bin/llama-server --help

WORKDIR /app
COPY api.py /app/api.py
COPY entrypoint.sh /app/entrypoint.sh

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod 755 /app/entrypoint.sh

RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir fastapi uvicorn requests

ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONPATH=/app

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
