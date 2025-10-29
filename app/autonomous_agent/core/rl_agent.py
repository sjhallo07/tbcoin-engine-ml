"""Reinforcement Learning agent placeholder.

Responsibilities:
- Train on simulated environment.
- Provide policy action for given state.
"""
from typing import Any, Dict

class RLAgent:
    def __init__(self):
        self.trained = False

    def train(self, episodes: int = 1000):
        """Train the RL agent (stub)."""
        self.trained = True

    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Return an action based on current policy (stub)."""
        return {"action": "buy", "amount": 0}
