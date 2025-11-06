"""Asynchronous client for fetching market data from the CoinGecko API."""

from __future__ import annotations

from typing import Any, Dict, List

import aiohttp

_COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


class CoinGeckoClient:
    """Lightweight wrapper around the CoinGecko markets endpoint."""

    async def get_top_cryptos(self, limit: int = 20) -> List[Dict[str, Any]]:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": max(1, min(limit, 250)),
            "page": 1,
            # Enable sparkline to support dashboard charts
            "sparkline": "true",
            "price_change_percentage": "24h",
        }

        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(_COINGECKO_URL, params=params, timeout=timeout) as response:
                response.raise_for_status()
                payload = await response.json()

        data: List[Dict[str, Any]] = []
        for entry in payload:
            # Preserve CoinGecko's sparkline shape for the dashboard component
            sparkline = entry.get("sparkline_in_7d") or {}
            data.append(
                {
                    "id": entry.get("id"),
                    "symbol": entry.get("symbol"),
                    "name": entry.get("name"),
                    "current_price": entry.get("current_price", 0.0),
                    "market_cap": entry.get("market_cap", 0.0),
                    "total_volume": entry.get("total_volume", 0.0),
                    "price_change_percentage_24h": entry.get("price_change_percentage_24h", 0.0),
                    "sparkline_in_7d": {"price": sparkline.get("price", [])},
                }
            )
        return data
