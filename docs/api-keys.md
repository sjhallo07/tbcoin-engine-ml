# API Key Registry

Keep track of external service API keys associated with the TB Coin stack. Rotate keys routinely and avoid committing real credentials to source control.

| Label            | API Key                  | Creation Date | Actions        |
|------------------|--------------------------|---------------|----------------|
| coingeckoapikey  | CG-icu2MHGS8bkS3maLooybpAQP | 2025-11-04    | Rotate / Revoke |

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
