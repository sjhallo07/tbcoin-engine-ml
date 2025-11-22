# TB Coin Engine ML - Comprehensive Documentation

Generated: 2025-11-22 18:34:49

## Table of Contents
1. [Overview](#overview)
2. [Python Backend Endpoints](#python-backend-endpoints)
3. [Node.js Frontend Endpoints](#nodejs-frontend-endpoints)
4. [ML/AI Modules](#mlai-modules)
5. [Security Middleware](#security-middleware)
6. [Testing Infrastructure](#testing-infrastructure)
7. [Advanced Features](#advanced-features)

---

## Overview

TB Coin Engine ML is a comprehensive AI-powered trading platform combining:
- **Python FastAPI Backend**: High-performance API with autonomous trading capabilities
- **Node.js Next.js Frontend**: Modern web interface with API routes
- **ML/AI Modules**: Advanced machine learning for market analysis and predictions
- **Security**: Multi-layered security with rate limiting and validation
- **Testing**: Comprehensive test suites for all components

---

## Python Backend Endpoints

### Core Endpoints


#### `GET /`

**Description**: Root endpoint with API information

**Response**:
```json
{
  "message": "string",
  "version": "string",
  "features": "object"
}
```


#### `GET /health`

**Description**: Health check endpoint

**Response**:
```json
{
  "status": "string",
  "autonomous_agent_enabled": "boolean",
  "autonomous_agent_running": "boolean"
}
```


#### `GET /status`

**Description**: Extended status endpoint

**Response**:
```json
{
  "api": "string",
  "database": "string",
  "blockchain": "string",
  "autonomous_agent": "object"
}
```


### Autonomous Agent Endpoints

The autonomous trading agent provides AI-powered market analysis and trading decisions.


#### `POST /api/v1/autonomous/control`

**Description**: Control autonomous trading agent

**Request**:
```json
{
  "action": "string (start|stop|status|analyze)",
  "parameters": "object (optional)"
}
```

**Response**:
```json
"varies by action"
```


#### `POST /api/v1/autonomous/analyze-market`

**Description**: Analyze market using AI

**Request**:
```json
{
  "market_data": "object",
  "strategy": "string (optional)"
}
```

**Response**:
```json
{
  "analysis": "object",
  "recommendation": "string",
  "confidence": "number",
  "risk_assessment": "object"
}
```


#### `GET /api/v1/autonomous/performance`

**Description**: Get agent performance metrics

**Response**:
```json
{
  "performance_metrics": "object",
  "learning_insights": "array",
  "strategy_performance": "object"
}
```


#### `POST /api/v1/autonomous/train-model`

**Description**: Train AI models in background

**Query Parameters**:
```json
{
  "model_type": "string (all|price-prediction|reinforcement-learning)"
}
```

**Response**:
```json
{
  "status": "string",
  "model_type": "string",
  "message": "string"
}
```


---

## Node.js Frontend Endpoints

### TB Coin Data Endpoints


#### `GET /api/tbcoin/data`

**Description**: Get TB Coin data

**Response**:
```json
{
  "status": "success",
  "data": {
    "price": "number",
    "holders": "number",
    "transactions": "number",
    "marketCap": "number",
    "timestamp": "string (ISO 8601)"
  }
}
```

**Features**:
- Real-time price data
- Holder count tracking
- Transaction statistics
- Market cap calculation


### Solana Integration Endpoints


#### `GET /api/solana/price`

**Description**: Get Solana price data

**Response**:
```json
{
  "status": "success",
  "data": {
    "price": "number",
    "change24h": "number",
    "marketCap": "number",
    "volume24h": "number",
    "timestamp": "string (ISO 8601)"
  }
}
```

**Features**:
- Real-time Solana pricing
- 24-hour change tracking
- Market cap data
- Trading volume statistics


#### `POST /api/solana/test`

**Description**: Test endpoint with ML analysis

**Response**:
```json
{
  "status": "success",
  "data": {
    "processed": "boolean",
    "action": "string",
    "timestamp": "string",
    "analysis": {
      "sentiment": "string",
      "confidence": "number",
      "recommendation": "string",
      "riskLevel": "string"
    }
  }
}
```

**Features**:
- AI-powered analysis
- Sentiment detection
- Risk assessment
- Trading recommendations


---

## ML/AI Modules


### Autonomous Decision Engine

**File**: `agents/ai_decision_engine.py`

**Description**: AI-powered decision making engine combining LLM, RL, and pattern recognition

**Features**:
- Market context analysis
- Multi-model recommendation
- Risk assessment
- Pattern recognition
- Reinforcement learning integration


### Autonomous Trading Agent

**File**: `agents/autonomous_agent.py`

**Description**: High-level orchestrator for autonomous trading operations

**Features**:
- Autonomous trading loop
- Market data gathering
- Decision execution
- Performance tracking
- Learning feedback integration


### Learning Feedback Loop

**File**: `agents/learning_feedback_loop.py`

**Description**: Continuous learning and adaptation system

**Features**:
- Trade performance analysis
- Strategy adjustment
- Performance metrics tracking
- Learning insights generation


### Strategy Evolver

**File**: `agents/strategy_evolver.py`

**Description**: Evolutionary strategy optimization

**Features**:
- Strategy evolution
- Parameter optimization
- Fitness evaluation
- Strategy adaptation


---

## Security Middleware

### Node.js Middleware (Next.js)

**File**: `dashboard-next/middleware.js`

**Features**:
- Rate limiting (60 requests per minute)
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Request validation
- CORS handling
- Request logging

**Rate Limiting Configuration**:
- Window: 60 seconds
- Max Requests: 60
- Identifier: API key or IP address

**Security Headers Applied**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security (production only)`

### Python Security Middleware

**File**: `middleware_security.py`

**Features**:
- Rate limiting with Redis
- Security headers
- CORS configuration
- Client identification

---

## Testing Infrastructure

### Python Test Suites

1. **test_comprehensive_endpoints.py**
   - Core endpoint testing
   - Autonomous agent testing
   - Error handling validation
   - Security feature testing
   - End-to-end workflows

2. **test_ml_modules.py**
   - Decision engine testing
   - Autonomous agent testing
   - Learning system validation
   - Risk management testing
   - Pattern recognition testing

### Node.js Test Suites

1. **comprehensive-endpoints.test.js**
   - Core endpoint validation
   - Security header verification
   - Rate limiting testing
   - Data integrity checks
   - Performance testing
   - Concurrent request handling

---

## Advanced Features

### Model Training

**Script**: `scripts/advanced_ml_training.py`

Features:
- Multiple model types (price prediction, technical analysis, sentiment)
- Synthetic data generation for testing
- Model evaluation and metrics
- Training reports generation
- Model versioning and tracking

### Autonomous Trading

The autonomous trading agent provides:
- 24/7 market monitoring
- Multi-model decision making (LLM + ML + RL)
- Risk assessment and management
- Performance tracking and learning
- Strategy evolution

### Machine Learning Pipeline

1. **Data Collection**: Real-time market data gathering
2. **Feature Engineering**: Technical indicators and patterns
3. **Model Training**: Multiple model architectures
4. **Prediction**: Ensemble predictions with confidence scores
5. **Execution**: Controlled trade execution with safety checks
6. **Learning**: Continuous feedback and model improvement

---

## API Usage Examples

### Python Backend

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Market analysis
response = requests.post(
    'http://localhost:8000/api/v1/autonomous/analyze-market',
    json={
        'market_data': {
            'price': 100.0,
            'volume': 1000000,
            'volatility': 0.05
        },
        'strategy': 'composite'
    }
)
print(response.json())
```

### Node.js Frontend

```javascript
// Get Solana price
const response = await fetch('http://localhost:3001/api/solana/price')
const data = await response.json()
console.log(data)

// Test endpoint with analysis
const testResponse = await fetch('http://localhost:3001/api/solana/test', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'analyze',
    symbol: 'SOL'
  })
})
const testData = await testResponse.json()
console.log(testData)
```

---

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

1. **Environment Variables**: Configure all secrets via environment variables
2. **Rate Limiting**: Adjust rate limits based on expected traffic
3. **Monitoring**: Set up Prometheus/Grafana for metrics
4. **Logging**: Configure structured logging for production
5. **Security**: Enable HTTPS and strict security headers
6. **Scaling**: Use horizontal scaling for API services

---

## Support and Contribution

For issues, questions, or contributions, please open an issue on GitHub.

**Repository**: sjhallo07/tbcoin-engine-ml

---

*This documentation was automatically generated by the comprehensive report generator.*
