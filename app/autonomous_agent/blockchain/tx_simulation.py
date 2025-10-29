"""Transaction simulation utilities for backtesting and dry-runs."""
from typing import Dict, Any

class TransactionSimulator:
    def simulate(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the outcome of a signed transaction (stub)."""
        return {"status": "simulated", "effect": {}}
