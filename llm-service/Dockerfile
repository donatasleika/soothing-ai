FROM ghcr.io/ggerganov/llama.cpp:full
RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install fastapi uvicorn requests google-cloud-storage
WORKDIR /app
COPY entrypoint.sh api.py /app/
RUN chmod +x /app/entrypoint.sh
EXPOSE 8080
CMD ["/app/entrypoint.sh"]