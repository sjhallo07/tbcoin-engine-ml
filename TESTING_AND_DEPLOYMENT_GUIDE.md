# Testing and Deployment Guide
## TB Coin Engine ML - Comprehensive Testing & Deployment

Generated: 2025-11-22

---

## Overview

This guide provides comprehensive instructions for testing and deploying all components of the TB Coin Engine ML platform.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Python Backend Testing](#python-backend-testing)
3. [Node.js Frontend Testing](#nodejs-frontend-testing)
4. [ML Model Training](#ml-model-training)
5. [Security Testing](#security-testing)
6. [Performance Testing](#performance-testing)
7. [Deployment](#deployment)
8. [Monitoring](#monitoring)

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Docker (optional)
docker --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/sjhallo07/tbcoin-engine-ml.git
cd tbcoin-engine-ml

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-ml.txt  # For ML features

# Install Node.js dependencies
cd dashboard-next
npm install
cd ..
```

---

## Python Backend Testing

### Run All Tests

```bash
# Run all Python tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test suite
python -m pytest tests/test_comprehensive_endpoints.py -v
python -m pytest tests/test_ml_modules.py -v
```

### Test Categories

#### 1. Core Endpoint Tests
```bash
python -m pytest tests/test_comprehensive_endpoints.py::TestCoreEndpoints -v
```

Tests:
- Root endpoint (/)
- Health check (/health)
- Status endpoint (/status)
- Messages endpoint (/messages)

#### 2. Autonomous Agent Tests
```bash
python -m pytest tests/test_comprehensive_endpoints.py::TestAutonomousAgentEndpoints -v
```

Tests:
- Agent status and control
- Market analysis
- Performance metrics
- Model training endpoints

#### 3. Error Handling Tests
```bash
python -m pytest tests/test_comprehensive_endpoints.py::TestErrorHandling -v
```

Tests:
- Invalid actions
- Missing parameters
- Non-existent endpoints

#### 4. Security Tests
```bash
python -m pytest tests/test_comprehensive_endpoints.py::TestSecurityFeatures -v
```

Tests:
- CORS headers
- Relay simulation
- Input validation

### Manual API Testing

```bash
# Start the API server
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/status
curl -X POST http://localhost:8000/api/v1/autonomous/control \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}'
```

---

## Node.js Frontend Testing

### Run All Tests

```bash
cd dashboard-next

# Run comprehensive endpoint tests
npm run test:endpoints

# Or run directly
node test/comprehensive-endpoints.test.js

# Run Jest tests
npm test
```

### Test Categories

The comprehensive endpoint test suite includes:

1. **Core Endpoints**: Solana price, TBCoin data, test POST
2. **Security Headers**: X-Content-Type-Options, X-Frame-Options, etc.
3. **Validation**: Content-Type validation, JSON parsing
4. **Error Handling**: 404, 405 responses
5. **Rate Limiting**: Rate limit header verification
6. **Data Integrity**: Consistent structure, valid timestamps
7. **Performance**: Response time, concurrent requests

### Manual Testing

```bash
# Start the Next.js development server
npm run dev

# In another terminal, test endpoints
curl http://localhost:3001/api/solana/price
curl http://localhost:3001/api/tbcoin/data
curl -X POST http://localhost:3001/api/solana/test \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze", "symbol": "SOL"}'
```

---

## ML Model Training

### Advanced Training Script

```bash
# Run comprehensive training
python scripts/advanced_ml_training.py

# This will:
# - Generate synthetic training data
# - Train 4 model types (price prediction, technical analysis, sentiment, ensemble)
# - Evaluate each model
# - Generate training reports
# - Save model metadata
```

### Training Output

Models and reports are saved to:
- `ml_models/*.json` - Model metadata and metrics
- `ml_models/training_report_*.json` - Comprehensive training reports

### Model Types

1. **Price Prediction Model**
   - Predicts future price movements
   - Metrics: Accuracy, MAE, RMSE

2. **Technical Analysis Model**
   - Analyzes technical indicators
   - Metrics: Accuracy, Precision, Recall, F1

3. **Sentiment Analysis Model**
   - Analyzes market sentiment
   - Metrics: Accuracy, Precision, Recall, AUC-ROC

4. **Ensemble Model**
   - Combines all models
   - Weighted predictions with confidence scores

---

## Security Testing

### Rate Limiting

```bash
# Test rate limiting (Node.js middleware)
# Run 70 requests rapidly to trigger rate limit
for i in {1..70}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3001/api/solana/price
  sleep 0.1
done

# Expected: First 60 return 200, rest return 429
```

### Security Headers

```bash
# Check security headers
curl -I http://localhost:3001/api/solana/price

# Should include:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: <number>
```

### Input Validation

```bash
# Test invalid input
curl -X POST http://localhost:8000/api/v1/autonomous/control \
  -H "Content-Type: application/json" \
  -d '{"action": "invalid_action"}'

# Expected: 400 Bad Request
```

---

## Performance Testing

### Python Backend

```bash
# Install load testing tool
pip install locust

# Create locustfile.py (basic example)
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class TBCoinUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task
    def status(self):
        self.client.get("/status")
    
    @task(3)
    def analyze_market(self):
        self.client.post("/api/v1/autonomous/analyze-market", 
            json={"market_data": {"price": 100, "volume": 1000000}})
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 1
```

### Node.js Frontend

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install ab  # macOS

# Run benchmark
ab -n 1000 -c 10 http://localhost:3001/api/solana/price

# -n: number of requests
# -c: concurrency
```

---

## Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Production Deployment

#### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with production values
nano .env

# Required variables:
# - SECRET_KEY
# - JWT_SECRET_KEY
# - OPENAI_API_KEY (optional, for LLM features)
# - DATABASE_URL (if using external database)
# - REDIS_URL (if using external Redis)
```

#### 2. Python API Deployment

```bash
# Using Gunicorn (production WSGI server)
pip install gunicorn

# Run API
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -

# Or using PM2 (process manager)
npm install -g pm2
pm2 start "uvicorn api.main:app --host 0.0.0.0 --port 8000" --name tbcoin-api
```

#### 3. Node.js Frontend Deployment

```bash
cd dashboard-next

# Build for production
npm run build

# Start production server
npm start

# Or using PM2
pm2 start npm --name tbcoin-frontend -- start
```

#### 4. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/tbcoin

upstream api_backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3001;
}

server {
    listen 80;
    server_name yourdomain.com;

    # API proxy
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend proxy
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Cloud Deployment (AWS/GCP/Azure)

#### AWS Lambda (Serverless)

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy
serverless deploy --stage prod

# View logs
serverless logs -f api -t
```

#### Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tbcoin-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tbcoin-api
  template:
    metadata:
      labels:
        app: tbcoin-api
    spec:
      containers:
      - name: api
        image: your-registry/tbcoin-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: tbcoin-secrets
              key: secret-key
```

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Check status
kubectl get pods
kubectl logs -f deployment/tbcoin-api
```

---

## Monitoring

### Prometheus + Grafana

```bash
# Start monitoring stack
docker-compose up -d prometheus grafana

# Access Grafana
open http://localhost:3000

# Default credentials: admin/admin
```

### Application Metrics

The API exposes metrics at `/metrics` (if Prometheus client is configured):

```bash
curl http://localhost:8000/metrics
```

### Logging

```bash
# View application logs
tail -f logs/tbcoin.log

# Docker logs
docker-compose logs -f api

# PM2 logs
pm2 logs tbcoin-api
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3001/api/solana/price

# Docker health checks
docker-compose ps
```

---

## Documentation Generation

### Generate Comprehensive Documentation

```bash
# Generate all documentation
python scripts/generate_comprehensive_report.py

# Output:
# - reports/COMPREHENSIVE_DOCUMENTATION.md
# - reports/comprehensive_report.json
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

#### 2. Port Already in Use

```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9  # API port
lsof -ti:3001 | xargs kill -9  # Frontend port
```

#### 3. Database Connection Issues

```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres
```

#### 4. Rate Limiting Too Strict

Edit `dashboard-next/middleware.js`:
```javascript
const MAX_REQUESTS_PER_WINDOW = 120  // Increase from 60
```

---

## Best Practices

### Development

1. **Use Virtual Environments**: Always use Python venv for isolation
2. **Run Tests Before Committing**: Ensure all tests pass
3. **Update Documentation**: Keep docs in sync with code changes
4. **Use Environment Variables**: Never commit secrets
5. **Run Linters**: Use `black`, `flake8` for Python; `eslint` for JavaScript

### Production

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Set Strong Secrets**: Generate secure random keys
3. **Configure Rate Limiting**: Adjust based on expected traffic
4. **Monitor Logs**: Set up centralized logging
5. **Backup Data**: Regular database backups
6. **Update Dependencies**: Keep packages up to date
7. **Use Process Managers**: PM2, Supervisor, or systemd
8. **Set Up Alerts**: Configure monitoring alerts

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/sjhallo07/tbcoin-engine-ml/issues
- Documentation: See `reports/COMPREHENSIVE_DOCUMENTATION.md`

---

*Last updated: 2025-11-22*
