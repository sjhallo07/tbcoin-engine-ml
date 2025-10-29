#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting TB Coin Phase 1 Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs models/ml_models monitoring/dashboards

# Copy environment file if it exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    exit 1
fi

# Build and start services
echo "🐳 Building Docker images..."
docker-compose build

echo "📦 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec api python -c "
from database.connection import engine
from models.contract_models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully')
"

# Initialize ML models
echo "🤖 Initializing ML models..."
docker-compose exec ml-worker python -c "
from services.supervised_learning import SupervisedLearningEngine
print('✅ ML engine initialized successfully')
"

echo "🎉 TB Coin Phase 1 deployment completed!"
echo "📊 Access points:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"