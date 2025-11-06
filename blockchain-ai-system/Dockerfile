# Stage 1: build JavaScript SDK artifacts
FROM node:20-alpine AS sdk-builder
WORKDIR /workspace
COPY src/blockchain/sdk ./sdk
RUN cd sdk \
    && npm init -y > /dev/null \
    && npm pkg set name="blockchain-ai-sdk" version="0.1.0" type="module" \
    && npm pack

# Stage 2: install Python dependencies
FROM python:3.10-slim AS python-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 3: runtime image
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=python-base /usr/local /usr/local
COPY --from=python-base /usr/lib /usr/lib
COPY --from=sdk-builder /workspace/sdk/*.tgz /opt/sdk/
COPY src ./src
COPY config ./config
COPY docs ./docs
COPY database ./database
ENV APP_SETTINGS_MODULE=config/ai_models.yaml
EXPOSE 8000
CMD ["gunicorn", "--factory", "src.api.app:create_app", "--bind", "0.0.0.0:8000", "--worker-class", "gthread", "--threads", "4"]
