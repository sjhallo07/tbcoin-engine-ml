# Dockerfile.listener
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies including Solana CLI tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && wget -O /tmp/solana-release.tar.bz2 "https://github.com/solana-labs/solana/releases/download/v1.14.18/solana-release-x86_64-unknown-linux-gnu.tar.bz2" \
    && tar jxf /tmp/solana-release.tar.bz2 -C /usr/local --strip-components=1 \
    && rm -rf /var/lib/apt/lists/* /tmp/solana-release.tar.bz2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "services/blockchain_listener.py"]