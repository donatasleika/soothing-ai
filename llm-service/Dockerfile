# ---------- build stage: compile a STATIC CPU-only llama-server ----------
FROM debian:12 AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /llama
RUN git clone https://github.com/ggml-org/llama.cpp.git /llama

# Static, CPU-only, no curl dependency for the server
# (prevents runtime from needing odd shared libs like libmtmd.so)
RUN cmake -S . -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLAMA_BUILD_SERVER=ON \
      -DGGML_STATIC=ON \
      -DGGML_CURL=OFF \
      -DGGML_OPENMP=OFF \
      -DGGML_METAL=OFF -DGGML_CUDA=OFF -DGGML_VULKAN=OFF -DGGML_OPENCL=OFF \
  && cmake --build build -j \
  && cmake --install build

# ---------- runtime stage ----------
FROM debian:12

# Python + curl for simple probes; venv to avoid PEP 668 issues
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash python3 python3-venv python3-pip ca-certificates curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK (provides gsutil)
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
      > /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
 && apt-get update && apt-get install -y --no-install-recommends google-cloud-cli \
 && rm -rf /var/lib/apt/lists/*


# Copy the statically linked llama-server from build stage
COPY --from=build /usr/local/bin/llama-server /usr/local/bin/llama-server
RUN /usr/local/bin/llama-server --help


# App
WORKDIR /app
COPY api.py /app/api.py
# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Fix line endings, permissions, and verify shebang
RUN sed -i 's/\r$//' /app/entrypoint.sh \
 && chmod 755 /app/entrypoint.sh \
 && head -n 1 /app/entrypoint.sh

RUN /bin/bash -lc 'head -n 1 /app/entrypoint.sh && test -x /app/entrypoint.sh'

# Python deps in an isolated venv (no --break-system-packages)
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir fastapi uvicorn requests

ENV PATH="/opt/venv/bin:${PATH}"

RUN /bin/sh -lc 'ls -lah /app && head -n 2 /app/entrypoint.sh'


# Default entrypoint (Cloud Run will pass PORT)
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]