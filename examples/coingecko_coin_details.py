"""Fetch detailed CoinGecko data for a specific coin using the public demo API key."""

from __future__ import annotations

import os
import sys
from typing import Any, Dict

import requests

DEMO_API_KEY = os.getenv("COINGECKO_DEMO_API_KEY", "YOUR_DEMO_API_KEY")
COINGECKO_PUBLIC_API = "https://api.coingecko.com/api/v3"


def _bool_param(value: bool) -> str:
    """CoinGecko expects lowercase string boolean query parameters."""
    return "true" if value else "false"


def fetch_coin_details(
    coin_id: str,
    localization: bool = True,
    tickers: bool = True,
    market_data: bool = True,
    community_data: bool = True,
    developer_data: bool = True,
    sparkline: bool = False,
) -> Dict[str, Any]:
    """Retrieve a detailed payload for the requested coin."""
    url = f"{COINGECKO_PUBLIC_API}/coins/{coin_id}"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": DEMO_API_KEY,
    }
    params = {
        "localization": _bool_param(localization),
        "tickers": _bool_param(tickers),
        "market_data": _bool_param(market_data),
        "community_data": _bool_param(community_data),
        "developer_data": _bool_param(developer_data),
        "sparkline": _bool_param(sparkline),
    }

    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def print_coin_summary(data: Dict[str, Any]) -> None:
    """Print a concise summary of the coin payload."""
    market_data = data.get("market_data", {})
    current_price = market_data.get("current_price", {}).get("usd", "?")
    market_cap = market_data.get("market_cap", {}).get("usd")
    total_volume = market_data.get("total_volume", {}).get("usd")

    print(f"Name: {data.get('name', 'Unknown')}")
    print(f"Symbol: {data.get('symbol', '?')}")
    print(f"Current Price (USD): ${current_price}")

    if market_cap is not None:
        print(f"Market Cap: ${market_cap:,}")
    else:
        print("Market Cap: ?")

    if total_volume is not None:
        print(f"24h Volume: ${total_volume:,}")
    else:
        print("24h Volume: ?")

    print(f"Market Cap Rank: {data.get('market_cap_rank', '?')}")


def main() -> None:
    coin_id = sys.argv[1] if len(sys.argv) > 1 else "bitcoin"

    try:
        data = fetch_coin_details(coin_id)
    except requests.HTTPError as exc:  # pragma: no cover - manual demo script
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print_coin_summary(data)


if __name__ == "__main__":
    main()
