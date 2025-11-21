# TB Coin Engine ML - Deployment Guide

## 🚀 Quick Start Guide

### Local Development

1. **Clone and Setup**
```bash
git clone https://github.com/sjhallo07/tbcoin-engine-ml.git
cd tbcoin-engine-ml
python quickstart.py
```

2. **Manual Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file with your settings

# Run the server
python main.py
```

3. **Access the API**
- API Root: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### AWS Lambda (Serverless)

```bash
# Install Serverless Framework
npm install -g serverless

# Install plugins
npm install serverless-python-requirements

# Deploy
serverless deploy --stage prod

# Environment variables
# Set in serverless.yml or AWS Console:
# - OPENAI_API_KEY
# - SECRET_KEY
# - DATABASE_URL
```

#### Recommended runtime and environment

- Prefer AWS Lambda Python 3.11 (or newer supported by Lambda).
- Keep the Lambda package lean. Use `requirements-serverless.txt` for Mangum + FastAPI minimal runtime.
- Heavy ML dependencies (numpy, pandas, scikit-learn, xgboost, lightgbm) should not be bundled into a ZIP-based Lambda due to size. Run them in a separate service or container image, or use Lambda Layers if strictly needed.

#### Local serverless setup on Windows PowerShell

```powershell
./scripts/setup_serverless_env.ps1
```

This provisions `.venv_serverless` and installs `requirements-serverless.txt`.

#### Container image alternative

If you need heavy ML, build a Lambda container image based on `public.ecr.aws/lambda/python:3.11` and install the full requirements. Set the handler to `serverless_handler.lambda_handler`.

#### Handler entrypoint

`serverless_handler.py` exposes `lambda_handler` using `Mangum(app, lifespan="off")` wrapping the FastAPI `app` from `main.py`.

## 📡 API Endpoints Overview

### Health & Status
- `GET /api/v1/health` - System health check
- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/ready` - Readiness probe

### Coin Management
- `GET /api/v1/coins/balance/{user_id}` - Get balance
- `POST /api/v1/coins/mint/{user_id}` - Mint coins (admin)
- `POST /api/v1/coins/burn/{user_id}` - Burn coins
- `POST /api/v1/coins/stake/{user_id}` - Stake coins
- `POST /api/v1/coins/unstake/{user_id}` - Unstake coins
- `GET /api/v1/coins/balances` - Get all balances (admin)

### Transactions
- `POST /api/v1/transactions` - Create transaction
- `POST /api/v1/transactions/{id}/execute` - Execute transaction
- `GET /api/v1/transactions/{id}` - Get transaction
- `GET /api/v1/transactions/user/{user_id}` - User transactions
- `POST /api/v1/transactions/quick-send` - Quick send
- `GET /api/v1/transactions/stats/summary` - Statistics

### ML/AI Actions
- `POST /api/v1/ml/action` - Generic ML action
- `POST /api/v1/ml/analyze-transaction` - Analyze transaction
- `POST /api/v1/ml/recommend` - Get recommendations
- `POST /api/v1/ml/predict-trend` - Predict market trends
- `POST /api/v1/ml/optimize-transaction` - Optimize parameters
- `POST /api/v1/ml/intelligent-transfer` - Smart transfer

## 🤖 ML Features Configuration

### OpenAI Integration

To enable full LLM capabilities:

1. Get API key from https://platform.openai.com/api-keys
2. Set in .env:
```env
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

### Fallback Mode

Without OpenAI API key, the system operates with:
- Rule-based transaction analysis
- Basic recommendations
- Simple trend predictions
- Standard optimization

## 🔐 Security Configuration

### Generate Secure Keys

```python
# Python
import secrets
print(secrets.token_urlsafe(32))
```

```bash
# Bash
openssl rand -base64 32
```

### Set in .env

```env
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
API_KEY=your-api-key
```

## 📊 Database Configuration

### SQLite (Default)
```env
DATABASE_URL=sqlite:///./tbcoin.db
```

### PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tbcoin
```

### MongoDB
```env
DATABASE_URL=mongodb://localhost:27017/tbcoin
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/ -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html

# Run demo
python examples/api_demo.py
```

## 📈 Monitoring & Logging

### Health Checks
```bash
curl http://localhost:8000/api/v1/health
```

### Logs
```bash
# Docker
docker-compose logs -f tbcoin-api

# Serverless
serverless logs -f api -t
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### LLM Not Working
- Check OPENAI_API_KEY is set correctly
- Verify API key is valid
- Check OpenAI service status
- System will fall back to rule-based mode

## 🌐 Production Deployment

### Environment Variables
Set these in production:
- `APP_ENV=production`
- `DEBUG=False`
- Strong `SECRET_KEY` and `JWT_SECRET_KEY`
- Valid `OPENAI_API_KEY`
- Production `DATABASE_URL`

### CORS Configuration
Update in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting
Consider adding rate limiting for production:
```bash
pip install slowapi
```

### HTTPS
Always use HTTPS in production:
- Use reverse proxy (Nginx, Traefik)
- Enable SSL/TLS certificates
- Configure secure headers

## 📚 Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- OpenAI API: https://platform.openai.com/docs
- Docker: https://docs.docker.com
- Serverless Framework: https://www.serverless.com/framework/docs

## 🆘 Support

For issues or questions:
1. Check documentation: README.md
2. Review examples: examples/api_demo.py
3. Open GitHub issue
4. Contact repository maintainer
