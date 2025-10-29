# TB Coin Engine ML

🚀 **AI-Powered Backend Engine for TB Coin Serverless Operations**

A sophisticated backend system that leverages Machine Learning and Large Language Models (LLMs) to provide intelligent coin management, transaction processing, and automated decision-making for the TB Coin cryptocurrency platform.

## 🌟 Features

### Core Functionality
- **Coin Management**: Complete balance tracking, staking, minting, and burning operations
- **Transaction Processing**: Secure and efficient transaction handling with fee management
- **ML-Powered Actions**: Intelligent decision-making using LLM integration

### ML/AI Capabilities
- 🤖 **LLM Integration**: OpenAI GPT-4 integration for intelligent recommendations
- 📊 **Transaction Analysis**: AI-powered fraud detection and risk assessment
- 💡 **Smart Recommendations**: Personalized portfolio optimization suggestions
- 📈 **Market Predictions**: Trend analysis and forecasting
- ⚡ **Transaction Optimization**: Intelligent parameter optimization for transactions

### Deployment Options
- **Local Development**: Run directly with Python/FastAPI
- **Docker**: Containerized deployment with Docker Compose
- **Serverless**: AWS Lambda-ready with Serverless Framework support
- **Cloud-Native**: Kubernetes and cloud provider compatible

## 🆕 New Services (Integration Complete)

We integrated a set of new services to enable autonomous trading, model training, tracking, and enhanced monitoring. Integration is complete — the autonomous agent now runs alongside the core TB Coin services.

- 🧠 Autonomous Agent: AI-powered autonomous trading agent that analyzes markets 24/7, makes multi-model recommendations (LLM + ML + RL), and can execute controlled trades.
- 🤖 ML Worker: Background worker for model training, data processing, and batch jobs.
- 📊 MLflow: Model tracking, experiments, and artifact storage (integrated via MinIO for local runs).
- 📈 Enhanced Monitoring: Prometheus + Grafana dashboards and custom AI performance metrics.

Workflow:
- Continuous Analysis: The agent analyzes market data continuously and produces structured insights.
- AI Decisions: Recommendations are produced by an ensemble of models (technical, LLM, and RL) with confidence & risk scoring.
- Controlled Execution: Trades may be executed manually via the API or automatically when `AI_TRADING_ENABLED=true` and safety checks pass.
- Continuous Learning: Periodic retraining and strategy evolution are performed automatically using historical performance and a strategy evolver.

Status: Integration is complete — the new services are included in `docker-compose.yml` and can be run locally with Docker Compose.


## 🏗️ Architecture

```
tbcoin-engine-ml/
├── app/
│   ├── api/              # API endpoints
│   │   ├── coins.py      # Coin management endpoints
│   │   ├── transactions.py  # Transaction endpoints
│   │   ├── ml_actions.py # ML-powered action endpoints
│   │   └── health.py     # Health check endpoints
│   ├── core/             # Core configuration and security
│   │   ├── config.py     # Application settings
│   │   └── security.py   # Authentication and JWT
│   ├── ml/               # Machine Learning modules
│   │   ├── llm_service.py    # LLM integration service
│   │   └── action_engine.py  # ML action processor
│   ├── models/           # Data models
│   │   └── schemas.py    # Pydantic models
│   └── services/         # Business logic
│       ├── coin_service.py        # Coin operations
│       └── transaction_service.py # Transaction logic
├── main.py               # Application entry point
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── serverless.yml       # Serverless Framework config
└── requirements.txt     # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- (Optional) Docker and Docker Compose
- (Optional) OpenAI API key for LLM features

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/sjhallo07/tbcoin-engine-ml.git
cd tbcoin-engine-ml
```

2. **Set up environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings, especially OPENAI_API_KEY if using LLM features
```

4. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Serverless Deployment (AWS Lambda)

```bash
# Install Serverless Framework
npm install -g serverless

# Install serverless plugins
npm install

# Deploy to AWS
serverless deploy --stage prod

# View logs
serverless logs -f api -t
```

## 📚 API Documentation

### Health Check
```bash
GET /api/v1/health
```

### Coin Management

**Get Balance**
```bash
GET /api/v1/coins/balance/{user_id}
```

**Stake Coins**
```bash
POST /api/v1/coins/stake/{user_id}?amount=100
```

**Mint Coins** (Admin)
```bash
POST /api/v1/coins/mint/{user_id}?amount=1000
```

### Transactions

**Create Transaction**
```bash
POST /api/v1/transactions
Content-Type: application/json

{
  "from_user": "user123",
  "to_user": "user456",
  "amount": 100.0,
  "transaction_type": "send"
}
```

**Quick Send**
```bash
POST /api/v1/transactions/quick-send?from_user=user123&to_user=user456&amount=50
```

**Get User Transactions**
```bash
GET /api/v1/transactions/user/{user_id}
```

### ML-Powered Actions

**Analyze Transaction**
```bash
POST /api/v1/ml/analyze-transaction?from_user=user123&to_user=user456&amount=1000
```

**Get Recommendations**
```bash
POST /api/v1/ml/recommend?user_id=user123&context=I want to optimize my portfolio
```

**Predict Market Trends**
```bash
POST /api/v1/ml/predict-trend
```

**Optimize Transaction**
```bash
POST /api/v1/ml/optimize-transaction?user_id=user123&amount=500&transaction_type=send
```

**Intelligent Transfer**
```bash
POST /api/v1/ml/intelligent-transfer?from_user=user123&to_user=user456&amount=100&auto_execute=true
```

## 🤖 ML/LLM Integration

### LLM Features

The system integrates with OpenAI's GPT-4 for intelligent decision-making:

1. **Transaction Analysis**: Analyzes transactions for fraud detection and risk assessment
2. **Portfolio Recommendations**: Provides personalized advice based on user context
3. **Market Predictions**: Forecasts market trends using historical data
4. **Transaction Optimization**: Suggests optimal timing and parameters

### Fallback Mode

If no OpenAI API key is configured, the system operates in fallback mode using rule-based algorithms:
- Basic risk assessment
- Rule-based recommendations
- Simple trend analysis
- Standard optimization

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# Application
APP_NAME=TB Coin Engine ML
APP_ENV=development
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Coin Settings
INITIAL_COIN_SUPPLY=1000000
MIN_TRANSACTION_AMOUNT=0.01
MAX_TRANSACTION_AMOUNT=1000000
TRANSACTION_FEE_PERCENT=0.5
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Transaction validation and limits
- Fraud detection using ML
- Risk assessment for high-value transactions

## 📊 Data Models

### CoinBalance
- `user_id`: User identifier
- `balance`: Available coin balance
- `staked_balance`: Staked coins
- `last_updated`: Last update timestamp

### Transaction
- `transaction_id`: Unique transaction ID
- `from_user`: Sender
- `to_user`: Receiver
- `amount`: Transaction amount
- `transaction_type`: SEND, MINT, BURN, STAKE, UNSTAKE
- `status`: PENDING, COMPLETED, FAILED, CANCELLED
- `fee`: Transaction fee
- `timestamp`: Creation time

### MLActionResponse
- `action_id`: Action identifier
- `action_type`: Type of ML action
- `result`: Action results
- `confidence`: Confidence score (0-1)
- `reasoning`: Explanation of decision
- `recommendations`: List of suggestions

## 🧪 Testing

```bash
# Run with pytest (when tests are added)
pytest

# Test API endpoints
curl http://localhost:8000/api/v1/health
```

## 📈 Monitoring

The system provides health check endpoints for monitoring:

- `/api/v1/health`: Overall health status
- `/api/v1/health/live`: Liveness probe
- `/api/v1/health/ready`: Readiness probe

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🎯 Roadmap

- [ ] PostgreSQL/MongoDB database integration
- [ ] WebSocket support for real-time updates
- [ ] Advanced ML models for price prediction
- [ ] Multi-currency support
- [ ] Automated testing suite
- [ ] Performance optimization
- [ ] Rate limiting and throttling
- [ ] Advanced analytics dashboard

## 🌐 Deployment Platforms

This backend is compatible with:
- AWS Lambda (via Serverless Framework)
- Google Cloud Functions
- Azure Functions
- Kubernetes clusters
- Traditional VPS/dedicated servers
- Platform-as-a-Service (Heroku, Railway, etc.)

---

Built with ❤️ using FastAPI, Python, and AI
