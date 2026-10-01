FROM python:3.12-slim

WORKDIR /app

# Install standard native system-level dependencies required for compiling wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./

# Pre-install dependencies to utilize Docker caching layers
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . --only-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "ingest_pipeline:app", "--host", "0.0.0.0", "--port", "8000"]
