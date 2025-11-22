"""
Comprehensive Report Generator
Generates detailed documentation for all endpoints, ML modules, and testing results
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ComprehensiveReportGenerator:
    """Generate comprehensive documentation and reports"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.report_data = {
            'generated_at': datetime.now().isoformat(),
            'endpoints': {},
            'ml_modules': {},
            'testing': {},
            'features': {}
        }
    
    def analyze_python_endpoints(self) -> Dict[str, Any]:
        """Analyze Python FastAPI endpoints"""
        endpoints = {
            'core_endpoints': [
                {
                    'path': '/',
                    'method': 'GET',
                    'description': 'Root endpoint with API information',
                    'response': {
                        'message': 'string',
                        'version': 'string',
                        'features': 'object'
                    }
                },
                {
                    'path': '/health',
                    'method': 'GET',
                    'description': 'Health check endpoint',
                    'response': {
                        'status': 'string',
                        'autonomous_agent_enabled': 'boolean',
                        'autonomous_agent_running': 'boolean'
                    }
                },
                {
                    'path': '/status',
                    'method': 'GET',
                    'description': 'Extended status endpoint',
                    'response': {
                        'api': 'string',
                        'database': 'string',
                        'blockchain': 'string',
                        'autonomous_agent': 'object'
                    }
                }
            ],
            'autonomous_agent_endpoints': [
                {
                    'path': '/api/v1/autonomous/control',
                    'method': 'POST',
                    'description': 'Control autonomous trading agent',
                    'request': {
                        'action': 'string (start|stop|status|analyze)',
                        'parameters': 'object (optional)'
                    },
                    'response': 'varies by action'
                },
                {
                    'path': '/api/v1/autonomous/analyze-market',
                    'method': 'POST',
                    'description': 'Analyze market using AI',
                    'request': {
                        'market_data': 'object',
                        'strategy': 'string (optional)'
                    },
                    'response': {
                        'analysis': 'object',
                        'recommendation': 'string',
                        'confidence': 'number',
                        'risk_assessment': 'object'
                    }
                },
                {
                    'path': '/api/v1/autonomous/performance',
                    'method': 'GET',
                    'description': 'Get agent performance metrics',
                    'response': {
                        'performance_metrics': 'object',
                        'learning_insights': 'array',
                        'strategy_performance': 'object'
                    }
                },
                {
                    'path': '/api/v1/autonomous/train-model',
                    'method': 'POST',
                    'description': 'Train AI models in background',
                    'query_params': {
                        'model_type': 'string (all|price-prediction|reinforcement-learning)'
                    },
                    'response': {
                        'status': 'string',
                        'model_type': 'string',
                        'message': 'string'
                    }
                }
            ],
            'blockchain_endpoints': [
                {
                    'path': '/api/v1/blockchain/transactions',
                    'method': 'GET',
                    'description': 'Get blockchain transaction data',
                    'query_params': {
                        'wallet_address': 'string (optional)',
                        'start_time': 'integer (optional)',
                        'end_time': 'integer (optional)',
                        'limit': 'integer (default: 1000)',
                        'offset': 'integer (default: 0)'
                    }
                },
                {
                    'path': '/api/v1/blockchain/wallet/{wallet_address}/behavior',
                    'method': 'GET',
                    'description': 'Get wallet behavior analysis'
                },
                {
                    'path': '/api/v1/blockchain/predict',
                    'method': 'POST',
                    'description': 'Make prediction using trained ML models'
                },
                {
                    'path': '/api/v1/blockchain/model/metrics',
                    'method': 'GET',
                    'description': 'Get current model performance metrics'
                }
            ]
        }
        
        return endpoints
    
    def analyze_nodejs_endpoints(self) -> Dict[str, Any]:
        """Analyze Node.js Next.js API endpoints"""
        endpoints = {
            'tbcoin_endpoints': [
                {
                    'path': '/api/tbcoin/data',
                    'method': 'GET',
                    'description': 'Get TB Coin data',
                    'response': {
                        'status': 'success',
                        'data': {
                            'price': 'number',
                            'holders': 'number',
                            'transactions': 'number',
                            'marketCap': 'number',
                            'timestamp': 'string (ISO 8601)'
                        }
                    },
                    'features': [
                        'Real-time price data',
                        'Holder count tracking',
                        'Transaction statistics',
                        'Market cap calculation'
                    ]
                }
            ],
            'solana_endpoints': [
                {
                    'path': '/api/solana/price',
                    'method': 'GET',
                    'description': 'Get Solana price data',
                    'response': {
                        'status': 'success',
                        'data': {
                            'price': 'number',
                            'change24h': 'number',
                            'marketCap': 'number',
                            'volume24h': 'number',
                            'timestamp': 'string (ISO 8601)'
                        }
                    },
                    'features': [
                        'Real-time Solana pricing',
                        '24-hour change tracking',
                        'Market cap data',
                        'Trading volume statistics'
                    ]
                },
                {
                    'path': '/api/solana/test',
                    'method': 'POST',
                    'description': 'Test endpoint with ML analysis',
                    'request': {
                        'action': 'string',
                        'symbol': 'string (optional)'
                    },
                    'response': {
                        'status': 'success',
                        'data': {
                            'processed': 'boolean',
                            'action': 'string',
                            'timestamp': 'string',
                            'analysis': {
                                'sentiment': 'string',
                                'confidence': 'number',
                                'recommendation': 'string',
                                'riskLevel': 'string'
                            }
                        }
                    },
                    'features': [
                        'AI-powered analysis',
                        'Sentiment detection',
                        'Risk assessment',
                        'Trading recommendations'
                    ]
                }
            ]
        }
        
        return endpoints
    
    def analyze_ml_modules(self) -> Dict[str, Any]:
        """Analyze ML/AI modules"""
        modules = {
            'autonomous_decision_engine': {
                'name': 'Autonomous Decision Engine',
                'file': 'agents/ai_decision_engine.py',
                'description': 'AI-powered decision making engine combining LLM, RL, and pattern recognition',
                'features': [
                    'Market context analysis',
                    'Multi-model recommendation',
                    'Risk assessment',
                    'Pattern recognition',
                    'Reinforcement learning integration'
                ],
                'key_methods': [
                    'analyze_market_context(market_data)',
                    '_load_llm(model_name)',
                    'Technical analysis integration',
                    'Risk scoring'
                ]
            },
            'autonomous_trading_agent': {
                'name': 'Autonomous Trading Agent',
                'file': 'agents/autonomous_agent.py',
                'description': 'High-level orchestrator for autonomous trading operations',
                'features': [
                    'Autonomous trading loop',
                    'Market data gathering',
                    'Decision execution',
                    'Performance tracking',
                    'Learning feedback integration'
                ],
                'components': [
                    'Decision Engine',
                    'Blockchain Executor',
                    'Behavior Simulator',
                    'Learning Loop',
                    'Wallet Manager',
                    'Strategy Evolver'
                ]
            },
            'learning_feedback_loop': {
                'name': 'Learning Feedback Loop',
                'file': 'agents/learning_feedback_loop.py',
                'description': 'Continuous learning and adaptation system',
                'features': [
                    'Trade performance analysis',
                    'Strategy adjustment',
                    'Performance metrics tracking',
                    'Learning insights generation'
                ]
            },
            'strategy_evolver': {
                'name': 'Strategy Evolver',
                'file': 'agents/strategy_evolver.py',
                'description': 'Evolutionary strategy optimization',
                'features': [
                    'Strategy evolution',
                    'Parameter optimization',
                    'Fitness evaluation',
                    'Strategy adaptation'
                ]
            }
        }
        
        return modules
    
    def analyze_middleware(self) -> Dict[str, Any]:
        """Analyze security middleware"""
        middleware = {
            'security_middleware': {
                'file': 'dashboard-next/middleware.js',
                'features': [
                    'Rate limiting (60 requests per minute)',
                    'Security headers (X-Content-Type-Options, X-Frame-Options, etc.)',
                    'Request validation',
                    'CORS handling',
                    'Request logging'
                ],
                'rate_limiting': {
                    'window': '60 seconds',
                    'max_requests': 60,
                    'identifier': 'API key or IP address',
                    'headers': [
                        'X-RateLimit-Limit',
                        'X-RateLimit-Remaining',
                        'X-RateLimit-Reset'
                    ]
                },
                'security_headers': [
                    'X-Content-Type-Options: nosniff',
                    'X-Frame-Options: DENY',
                    'X-XSS-Protection: 1; mode=block',
                    'Referrer-Policy: strict-origin-when-cross-origin',
                    'Permissions-Policy: geolocation=(), microphone=(), camera=()',
                    'Strict-Transport-Security (production only)'
                ]
            },
            'python_security': {
                'file': 'middleware_security.py',
                'features': [
                    'Rate limiting with Redis',
                    'Security headers',
                    'CORS configuration',
                    'Client identification'
                ]
            }
        }
        
        return middleware
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        python_endpoints = self.analyze_python_endpoints()
        nodejs_endpoints = self.analyze_nodejs_endpoints()
        ml_modules = self.analyze_ml_modules()
        middleware = self.analyze_middleware()
        
        markdown = f"""# TB Coin Engine ML - Comprehensive Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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

"""
        
        for endpoint in python_endpoints['core_endpoints']:
            markdown += f"""
#### `{endpoint['method']} {endpoint['path']}`

**Description**: {endpoint['description']}

**Response**:
```json
{json.dumps(endpoint['response'], indent=2)}
```

"""
        
        markdown += """
### Autonomous Agent Endpoints

The autonomous trading agent provides AI-powered market analysis and trading decisions.

"""
        
        for endpoint in python_endpoints['autonomous_agent_endpoints']:
            markdown += f"""
#### `{endpoint['method']} {endpoint['path']}`

**Description**: {endpoint['description']}

"""
            if 'request' in endpoint:
                markdown += f"""**Request**:
```json
{json.dumps(endpoint['request'], indent=2)}
```

"""
            if 'query_params' in endpoint:
                markdown += f"""**Query Parameters**:
```json
{json.dumps(endpoint['query_params'], indent=2)}
```

"""
            if 'response' in endpoint:
                markdown += f"""**Response**:
```json
{json.dumps(endpoint['response'], indent=2)}
```

"""
        
        markdown += """
---

## Node.js Frontend Endpoints

### TB Coin Data Endpoints

"""
        
        for endpoint in nodejs_endpoints['tbcoin_endpoints']:
            markdown += f"""
#### `{endpoint['method']} {endpoint['path']}`

**Description**: {endpoint['description']}

**Response**:
```json
{json.dumps(endpoint['response'], indent=2)}
```

**Features**:
"""
            for feature in endpoint['features']:
                markdown += f"- {feature}\n"
            
            markdown += "\n"
        
        markdown += """
### Solana Integration Endpoints

"""
        
        for endpoint in nodejs_endpoints['solana_endpoints']:
            markdown += f"""
#### `{endpoint['method']} {endpoint['path']}`

**Description**: {endpoint['description']}

**Response**:
```json
{json.dumps(endpoint['response'], indent=2)}
```

**Features**:
"""
            for feature in endpoint['features']:
                markdown += f"- {feature}\n"
            
            markdown += "\n"
        
        markdown += """
---

## ML/AI Modules

"""
        
        for module_key, module in ml_modules.items():
            markdown += f"""
### {module['name']}

**File**: `{module['file']}`

**Description**: {module['description']}

**Features**:
"""
            for feature in module['features']:
                markdown += f"- {feature}\n"
            
            markdown += "\n"
        
        markdown += """
---

## Security Middleware

### Node.js Middleware (Next.js)

**File**: `dashboard-next/middleware.js`

**Features**:
"""
        for feature in middleware['security_middleware']['features']:
            markdown += f"- {feature}\n"
        
        markdown += f"""
**Rate Limiting Configuration**:
- Window: {middleware['security_middleware']['rate_limiting']['window']}
- Max Requests: {middleware['security_middleware']['rate_limiting']['max_requests']}
- Identifier: {middleware['security_middleware']['rate_limiting']['identifier']}

**Security Headers Applied**:
"""
        for header in middleware['security_middleware']['security_headers']:
            markdown += f"- `{header}`\n"
        
        markdown += """
### Python Security Middleware

**File**: `middleware_security.py`

**Features**:
"""
        for feature in middleware['python_security']['features']:
            markdown += f"- {feature}\n"
        
        markdown += """
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
"""
        
        return markdown
    
    def save_report(self):
        """Save comprehensive report"""
        # Generate markdown
        markdown_content = self.generate_markdown_report()
        
        # Save markdown
        markdown_path = self.output_dir / "COMPREHENSIVE_DOCUMENTATION.md"
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        
        print(f"✅ Comprehensive documentation saved to: {markdown_path}")
        
        # Save JSON report
        json_path = self.output_dir / "comprehensive_report.json"
        with open(json_path, 'w') as f:
            json.dump({
                'generated_at': self.report_data['generated_at'],
                'python_endpoints': self.analyze_python_endpoints(),
                'nodejs_endpoints': self.analyze_nodejs_endpoints(),
                'ml_modules': self.analyze_ml_modules(),
                'middleware': self.analyze_middleware()
            }, f, indent=2)
        
        print(f"✅ JSON report saved to: {json_path}")
        
        return markdown_path, json_path


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE REPORT GENERATOR")
    print("  TB Coin Engine ML - Documentation Generator")
    print("="*70 + "\n")
    
    generator = ComprehensiveReportGenerator(output_dir="./reports")
    markdown_path, json_path = generator.save_report()
    
    print("\n" + "="*70)
    print("  ✅ Report Generation Complete!")
    print("="*70)
    print(f"\nMarkdown: {markdown_path}")
    print(f"JSON: {json_path}")
    print("\n")


if __name__ == "__main__":
    main()
