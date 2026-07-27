FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements & install dependencies from src/llm-service
COPY src/llm-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source code
COPY src/llm-service/ .

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
