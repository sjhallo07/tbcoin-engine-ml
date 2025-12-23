# API Key Registry

Keep track of external service API keys associated with the TB Coin stack. Rotate keys routinely and avoid committing real credentials to source control.

| Label            | API Key                  | Creation Date | Actions        |
|------------------|--------------------------|---------------|----------------|
| coingeckoapikey  | CG-<demo-key-placeholder>   | 2025-11-04    | Rotate / Revoke |

> **Security note:** store actual keys in your secrets manager or `.env` files, not in plaintext documentation, when working in production environments.

## CoinGecko Demo Plan

- Base URL: `https://api.coingecko.com/api/v3/`
- Required header: `x-cg-demo-api-key`
- Example usage: `python examples/coingecko_demo.py` for market-cap listings, `python examples/coingecko_coin_details.py [coin_id]` for detailed metadata (`bitcoin` default), `python examples/coingecko_onchain_demo.py <network> <command>` for onchain token/pool data (see `coingecko-onchain-metadata.md`)
- Windows PowerShell: `setx COINGECKO_DEMO_API_KEY "CG-icu2MHGS8bkS3maLooybpAQP"`
- Quick curl test:

 ```powershell
 curl --request GET `
  --url https://api.coingecko.com/api/v3/ping `
  --header 'x-cg-demo-api-key: CG-icu2MHGS8bkS3maLooybpAQP'
 ```

## CoinGecko Pro Plan

- Base URL: `https://pro-api.coingecko.com/api/v3`
- Required header: `x-cg-pro-api-key`
- Example usage: `python examples/coingecko_ping.py` to call `/ping` with the official SDK using `COINGECKO_PRO_API_KEY`

---

## Environment variables (API integration)

Use environment files for each service and never commit real secrets.

### Python API (.env at `tbcoin-engine-ml/`)

```env
```

```env
APP_ENV=development
```env
API_PORT=8000

SECRET_KEY=change-me

# Feature flags
AI_AGENT_ENABLED=false
AI_TRADING_ENABLED=false

# LLM / AI (optional)
OPENAI_API_KEY=
LLM_MODEL=gpt-4

# Blockchain
SOLANA_NETWORK=devnet          # devnet | testnet | mainnet-beta
SOLANA_RPC_URL=                # e.g., https://api.devnet.solana.com or your provider
EVM_RPC_URL=                   # e.g., https://eth-sepolia.g.alchemy.com/v2/<key>

# Token defaults (Solana)
MINT_ADDRESS=                  # SPL token mint (Base58)
UPDATE_AUTHORITY=              # Metaplex metadata update authority (Base58)

# External APIs
COINGECKO_DEMO_API_KEY=
COINGECKO_PRO_API_KEY=

# Observability / Storage (optional)
MLFLOW_TRACKING_URI=
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=

# TB Coin cloud API (for Honeycomb/Substrate calls)
TB_API_KEY=
```

Windows PowerShell examples:

```powershell
setx SOLANA_NETWORK "devnet"
setx MINT_ADDRESS "<base58>"
setx UPDATE_AUTHORITY "<base58>"
setx COINGECKO_DEMO_API_KEY "CG-..."
setx TB_API_KEY "tbcoin-..."
```

### Dashboard (.env.local at `tbcoin-engine-ml/dashboard-next/`)

```
PORT=3001
SOLANA_NETWORK=devnet
MINT_ADDRESS=
UPDATE_AUTHORITY=
GITHUB_TOKEN=               # optional, for higher GitHub API limits
COINGECKO_DEMO_API_KEY=
COINGECKO_PRO_API_KEY=
```

### Node backend (.env at `tbcoin-engine-ml/backend-node/`)

```
NODE_ENV=development
NODE_PORT=3000
JWT_SECRET_KEY=change-me
API_KEY=                      # internal service key if used
MONGODB_URI=mongodb://localhost:27017/tbcoin
PYTHON_BACKEND_URL=http://127.0.0.1:8000
```

> Notes
>
> - `TB_API_KEY` is required for hosted TB Coin endpoints like `/api/v1/blockchain/honeycomb/call`.
> - `MINT_ADDRESS` and `UPDATE_AUTHORITY` are for SPL token operations; minting requires mint authority, not update authority.
> - Prefer provider RPC URLs for `SOLANA_RPC_URL`/`EVM_RPC_URL` (Helius/Alchemy/Infura/etc.).
> - In production, store secrets in a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager).
