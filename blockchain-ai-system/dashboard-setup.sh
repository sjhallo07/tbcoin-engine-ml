#!/bin/bash

# dashboard-setup.sh
# Setup interactive dashboard with CoinGecko and DeepSeek API integrations

set -euo pipefail

echo "🎯 Setting up Interactive Dashboard with API Integrations..."

# Create dashboard directory structure
mkdir -p dashboard/{src,components,pages,styles,public}
mkdir -p dashboard/src/{hooks,utils,services,context,components,app}

# Create dashboard package.json
cat > dashboard/package.json <<'EOF'
{
  "name": "blockchain-ai-dashboard",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.0.0",
    "react-dom": "18.0.0",
    "recharts": "2.8.0",
    "axios": "1.5.0",
    "web3": "4.2.0",
    "ethers": "6.8.0",
    "tailwindcss": "3.3.0",
    "framer-motion": "10.16.0",
    "lucide-react": "0.288.0",
    "socket.io-client": "4.7.0"
  },
  "devDependencies": {
    "@types/node": "20.0.0",
    "@types/react": "18.0.0",
    "@types/react-dom": "18.0.0",
    "autoprefixer": "10.4.0",
    "postcss": "8.4.0",
    "tailwindcss": "3.3.0",
    "typescript": "5.0.0"
  }
}
EOF

# Create Next.js configuration
cat > dashboard/next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY,
    COINGECKO_API_KEY: process.env.COINGECKO_API_KEY,
  },
};

module.exports = nextConfig;
EOF

# Create Tailwind CSS configuration
cat > dashboard/tailwind.config.js <<'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        blockchain: {
          purple: '#8B5CF6',
          blue: '#3B82F6',
          green: '#10B981',
          red: '#EF4444',
          dark: '#1F2937',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
EOF

echo "✅ Dashboard base structure created"
