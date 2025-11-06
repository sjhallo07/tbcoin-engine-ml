# CoinGecko Onchain Metadata (Demo Plan)

Use the CoinGecko public API demo key (`x-cg-demo-api-key`) against `https://api.coingecko.com/api/v3/` to inspect Solana and Polygon token metadata, pools, and pricing snapshots. All endpoints refresh roughly every 60 seconds and are rate-limited to the demo allocation (10k calls/month, 30 RPM).

## Token Metadata Endpoints

### `/onchain/networks/{network}/tokens/{address}/info`

- Provides comprehensive metadata: name, symbol, decimals, image URLs, CoinGecko coin ID, websites, long-form description, GT Score metrics, social links (Twitter, Telegram, Discord), and beta holders data (count plus distribution buckets).
- Supports enhanced metadata coverage for networks such as Solana, Polygon (polygon-pos), Ethereum, BNB Chain, Arbitrum, Optimism, Base, TON, Sui, and Ronin.
- Response structure nests fields under `data.attributes`.

### `/onchain/networks/{network}/tokens/multi/{addresses}`

- Batch query (≤30 addresses) for combined metadata and market metrics: price, volume, FDV, decimals, symbol, CoinGecko coin ID, and optional top pool information (`include=top_pools`).
- Useful for syncing dashboard tiles with fresh liquidity context.

### `/onchain/networks/{network}/pools/{pool_address}/info`

- Returns metadata for the base and quote tokens in a specific pool, including image URLs, websites, descriptions, GT Scores, and holders distribution where available.

## Pool Discovery Endpoint

### `/onchain/networks/{network}/new_pools`

- Lists pools deployed within the last 48 hours (≤20 per page within the demo tier) and exposes price change windows (m5…h24), trade counts, buyers/sellers, and 24h USD volume.
- Pagination beyond 10 pages requires a paid plan.

## Demo Script (`examples/coingecko_onchain_demo.py`)

Command examples after exporting `COINGECKO_DEMO_API_KEY`:

```powershell
# Batch token metadata + market data on Solana (with top pool info)
python examples/coingecko_onchain_demo.py solana multi --include-top-pools <addr1> <addr2>

# Full metadata for a single Polygon token
python examples/coingecko_onchain_demo.py polygon-pos info <token-address>

# Metadata for both assets in a Solana pool
python examples/coingecko_onchain_demo.py solana pool-info <pool-address>

# Discover fresh pools on Solana (page 1)
python examples/coingecko_onchain_demo.py solana new-pools
```

The script normalizes the `data.attributes` payload format, prints social links, description snippets, GT Score breakdowns, and holder distribution percentages when provided.

> **Security reminder:** keep real API keys outside source control (environment variables, secret managers) and rotate regularly.
