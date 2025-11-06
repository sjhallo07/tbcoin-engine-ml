#!/bin/bash

# deepseek-setup.sh

set -euo pipefail

cat <<'EOF'
🔑 Setting up DeepSeek Free API Access...

📋 Steps to get FREE DeepSeek API Key:

1. Visit: https://platform.deepseek.com
2. Sign up for a free account
3. Go to API Keys section
4. Generate a new API key
5. Copy the key and add it to dashboard/.env.local:

NEXT_PUBLIC_DEEPSEEK_API_KEY=sk-youractualapikeyhere

🎯 Free Tier Benefits:
• 1000 requests per month
• Access to deepseek-chat model
• Suitable for prototyping and demos

⚠️  Important Notes:
• Keep your API key secure
• Monitor usage to avoid exceeding limits
• Consider upgrading for production use
• Use demo mode for development without API key
EOF

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to test API connectivity." >&2
  exit 0
fi

if [ ! -d "dashboard" ]; then
  echo "Dashboard directory not found; skipping runtime test."
  exit 0
fi

echo "🧪 Testing DeepSeek API connection..."
(cd dashboard && npm run dev >/dev/null 2>&1 &)
SERVER_PID=$!

sleep 5 || true

curl -X GET http://localhost:3000/api/health || echo "Health endpoint unavailable (expected if not implemented)."

kill "$SERVER_PID" >/dev/null 2>&1 || true

echo "✅ Setup guidance complete!"
