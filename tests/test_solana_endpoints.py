import os
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_decision_endpoint():
    resp = client.post("/api/v1/solana/decision", json={"features": {"price": 100, "trend": 0.02}})
    assert resp.status_code == 200
    data = resp.json()
    assert "decision" in data
    assert data["decision"]["action"] in ("buy", "sell", "hold")


def test_execute_decision_simulation_mode():
    # Ensure simulation mode to avoid accidental sends
    os.environ["SIMULATE_TRADING"] = "true"
    os.environ["AI_TRADING_ENABLED"] = "true"
    resp = client.post("/api/v1/solana/execute_decision", json={"features": {"price": 100, "trend": 0.02}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["executed"] is False
    assert data["reason"] == "simulation_or_trading_disabled"
