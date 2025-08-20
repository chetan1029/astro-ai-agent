FROM python:3.12-slim

# Install system dependencies including ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    gcc \
    python3-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]