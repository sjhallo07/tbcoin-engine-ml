#!/bin/bash

# install-dashboard.sh

set -euo pipefail

echo "🚀 Installing AI Blockchain Dashboard..."

cd "$(dirname "$0")/dashboard"

echo "📦 Installing dependencies..."
npm install

mkdir -p public/images
mkdir -p src/types

cat > src/types/index.ts <<'EOF'
export interface CoinData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d: number;
  total_volume: number;
  sparkline_in_7d: { price: number[] };
}

export interface AIPrediction {
  prediction: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
  factors: string[];
}

export interface GasRecommendation {
  optimal_gas_price: number;
  confidence: number;
  expected_confirmation: string;
  recommendation: string;
}
EOF

echo "✅ Dashboard installation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Get your FREE DeepSeek API key from: https://platform.deepseek.com/api_keys"
echo "2. Add the key to dashboard/.env.local"
echo "3. Run: npm run dev"
echo "4. Open: http://localhost:3000"
echo ""
echo "📚 DeepSeek Free Tier Limits:"
echo "   - 1000 requests per month"
echo "   - Suitable for demo and development"
echo "   - Upgrade for production use"
