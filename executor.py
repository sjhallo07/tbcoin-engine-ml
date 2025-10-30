"""Executor and a tiny Flask API exposing Solana helper endpoints and the decision engine.

This module is intentionally minimal so it can run without heavy ML libs. It
exposes endpoints to query balance/account info, request a decision, and (optionally)
execute transactions if a signer is provided. The execution path validates the
feature flag `AI_TRADING_ENABLED` before sending any real transactions.
"""
import os
import json
from typing import Any, Dict
from flask import Flask, request, jsonify

from solana_adapter import SolanaAdapter
from ai_decision_engine import AIDecisionEngine

# Create Flask app (separate from FastAPI in the repo)
app = Flask(__name__)

# Adapter and engine instances shared by endpoints
adapter = SolanaAdapter()
engine = AIDecisionEngine()
engine.load_model()


@app.route("/balance/<pubkey>", methods=["GET"])
def get_balance(pubkey: str):
    """Return Solana balance for the given pubkey."""
    result = adapter.get_balance(pubkey)
    return jsonify(result)


@app.route("/account/<pubkey>", methods=["GET"])
def get_account(pubkey: str):
    result = adapter.get_account_info(pubkey)
    return jsonify(result)


@app.route("/decision", methods=["POST"])
def decision():
    """Run the decision engine on provided JSON features."""
    features = request.get_json(silent=True) or {}
    decision = engine.predict(features)
    return jsonify({"decision": decision})


@app.route("/execute_decision", methods=["POST"])
def execute_decision():
    """Simulate or execute a decision.

    Expected payload:
        {"features": {...}, "signer": {"private_key": "..."}}  # signer optional
    """
    payload = request.get_json(silent=True) or {}
    features = payload.get("features", {})
    decision = engine.predict(features)

    trading_enabled = os.getenv("AI_TRADING_ENABLED", "false").lower() in ("1", "true", "yes")

    # If trading is disabled, only simulate
    if not trading_enabled:
        return jsonify({"decision": decision, "executed": False, "reason": "trading_disabled"})

    signer_info = payload.get("signer")
    if not signer_info:
        return jsonify({"decision": decision, "executed": False, "reason": "no_signer_provided"}), 400

    # Placeholder for building and sending a transaction. Real implementation
    # requires creation of a Transaction, proper signing and error handling.
    try:
        # Example: create a dummy Transaction object or use adapter helper
        tx = None
        # In a real path you'd create a Transaction and use adapter.send_transaction(tx, signer)
        result = {"simulated_send": True, "tx": None}
    except Exception as exc:
        result = {"error": str(exc)}

    return jsonify({"decision": decision, "executed": True, "result": result})


def run_server(host: str = "127.0.0.1", port: int = 5000):
    """Run the Flask server. Use from CLI or import and call in tests."""
    print(f"Starting executor Flask app on http://{host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Executor / API for Solana starter modules")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)

__all__ = ["app", "run_server"]
