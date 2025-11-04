"""Example script demonstrating CoinGecko public demo API usage.

Public API docs: https://docs.coingecko.com/reference/introduction
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

import requests

DEMO_API_KEY = os.getenv("COINGECKO_DEMO_API_KEY", "YOUR_DEMO_API_KEY")
COINGECKO_PUBLIC_API = "https://api.coingecko.com/api/v3"


def fetch_top_market_caps(vs_currency: str = "usd", per_page: int = 10) -> List[Dict[str, Any]]:
    """Fetch top cryptocurrencies by market cap using the public demo plan."""
    url = f"{COINGECKO_PUBLIC_API}/coins/markets"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": DEMO_API_KEY,
    }
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    try:
        coins = fetch_top_market_caps()
    except requests.HTTPError as exc:  # pragma: no cover - manual demo script
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    for coin in coins:
        name = coin.get("name", "Unknown")
        symbol = coin.get("symbol", "?").upper()
        price = coin.get("current_price", "?")
        market_cap = coin.get("market_cap", 0)

        print(f"{name} ({symbol})")
        print(f"  Price: ${price}")
        print(f"  Market Cap: ${market_cap:,}")
        print()


if __name__ == "__main__":
    main()
