#!/bin/bash

# start-ai-blockchain-system.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Complete AI Blockchain Predictive System..."

if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "📝 Please edit .env file with your API keys before continuing"
    else
        echo "❌ .env.template not found. Aborting startup."
    fi
    exit 1
fi

echo "🐳 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

if [ -d dashboard ]; then
  echo "🌐 Starting AI Dashboard..."
  (cd dashboard && npm run dev >/dev/null 2>&1 &) 
  DASHBOARD_PID=$!
else
  echo "⚠️  Dashboard directory not found; skipping dashboard startup."
  DASHBOARD_PID=""
fi

if command -v python >/dev/null 2>&1; then
  echo "🧠 Starting AI Training Worker..."
  (python -m src.ai_models.training_orchestrator --mode=continuous >/dev/null 2>&1 &) 
fi

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
DASHBOARD_STATUS="N/A"
if [ -n "$DASHBOARD_PID" ]; then
  DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
fi

DB_RUNNING=$(docker ps | grep -c postgres || echo "0")

echo ""
echo "✅ AI Blockchain System Started Successfully!"
echo ""
echo "🔗 Access Points:"
echo "   Dashboard:      http://localhost:3000"
echo "   API Server:     http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   Monitoring:     http://localhost:3001"
echo "   Prometheus:     http://localhost:9090"
echo "   Grafana:        http://localhost:3000 (if using Docker)"
echo ""
echo "🎯 System Status:"
echo "   Backend API:    $API_STATUS"
echo "   Dashboard:      $DASHBOARD_STATUS"
echo "   Database:       $DB_RUNNING instance(s) running"
echo ""
echo "🛑 To stop the system: ./stop-system.sh"
echo "📊 To view logs: docker-compose logs -f"

cat > stop-system.sh <<'EOF'
#!/bin/bash
echo "🛑 Stopping AI Blockchain System..."
docker-compose down
pkill -f "npm run dev" || true
pkill -f "training_orchestrator" || true
echo "✅ System stopped successfully"
EOF
chmod +x stop-system.sh
