"""Risk management helpers for safe execution.

Implements position sizing and basic risk checks.
"""
from typing import Dict, Any

class RiskManager:
    def __init__(self, max_drawdown: float = 0.2):
        self.max_drawdown = max_drawdown

    def evaluate(self, proposed_trade: Dict[str, Any]) -> bool:
        """Return True if trade is within risk bounds (stub)."""
        return True
