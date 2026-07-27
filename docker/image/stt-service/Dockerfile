FROM python:3.11-slim

# System dependencies (ffmpeg for Whisper audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements & install dependencies from src/stt-service
COPY src/stt-service/requirements.txt .
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130 || \
    pip install --no-cache-dir torch torchvision torchaudio
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source code
COPY src/stt-service/ .

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
