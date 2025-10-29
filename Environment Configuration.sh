# .env
# Database
DATABASE_URL=postgresql://tbcoin_user:password@localhost:5432/tbcoin
REDIS_URL=redis://localhost:6379

# Solana
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com
TOKEN_MINT_ADDRESS=YOUR_TOKEN_MINT_HERE

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Security
JWT_SECRET=your-super-secret-jwt-key-here
API_RATE_LIMIT=100

# External APIs
COINGECKO_API_KEY=your-coingecko-api-key
TWITTER_API_KEY=your-twitter-api-key

# IBM Cloud (for future scaling)
IBM_API_KEY=your-ibm-cloud-api-key