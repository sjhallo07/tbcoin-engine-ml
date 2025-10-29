# Dockerfile.ml.ibm
FROM python:3.11-slim

WORKDIR /app

# Install minimal ML dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements-ml.txt .
RUN pip install --no-cache-dir -r requirements-ml.txt

COPY . .

RUN useradd -m -u 1001 mluser && chown -R mluser:mluser /app
USER mluser

CMD ["python", "services/ml_worker.py"]