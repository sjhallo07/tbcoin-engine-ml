"""Simplified client that simulates DeepSeek AI analysis."""

from __future__ import annotations

import math
from typing import Any, Dict


class DeepSeekClient:
    """Mock DeepSeek client that produces deterministic analytics."""

    async def analyze_market(self, coin_data: Dict[str, Any]) -> Dict[str, Any]:
        price_change = float(coin_data.get("price_change_percentage_24h", 0.0))
        volatility_score = min(100.0, abs(price_change) * 2.5)
        sentiment = "bullish" if price_change > 0 else "bearish" if price_change < 0 else "neutral"
        confidence = max(0.2, min(0.95, 0.5 + price_change / 100.0))
        return {
            "summary": f"Price moved {price_change:.2f}% in the last 24h.",
            "sentiment": sentiment,
            "volatility_score": round(volatility_score, 2),
            "confidence": round(confidence, 2),
        }

    async def optimize_gas(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        base_fee = float(network_data.get("base_fee", 0.0))
        pending = float(network_data.get("pending_transactions", 0.0))
        utilisation = float(network_data.get("network_utilization", 0.0))

        recommended_fee = base_fee * (1.0 + utilisation * 0.2)
        wait_time_minutes = max(1.0, math.ceil(pending / 1000.0))

        return {
            "recommended_priority_fee": round(recommended_fee, 2),
            "estimated_confirmation_time": f"{wait_time_minutes} minutes",
            "notes": "Based on network congestion and utilisation metrics.",
        }
