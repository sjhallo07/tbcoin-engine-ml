from __future__ import annotations

import asyncio
import logging
import time
from http import HTTPStatus
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from ..blockchain.smart_contract_executor import SmartContractOrchestrator
from ..blockchain.web3_helpers import create_web3_instance, estimate_optimal_gas
from ..data_collection.blockchain_apis import BlockchainDataCollector
from ..utils.security_manager import SecurityManager

api_blueprint = Blueprint("api", __name__)
LOGGER = logging.getLogger(__name__)
_RATE_LIMIT_BUCKET: Dict[str, list[float]] = {}
_RATE_LIMIT_MAX = 60
_RATE_LIMIT_WINDOW = 60.0


class TooManyRequests(RuntimeError):
    pass


def _rate_limit(key: str) -> None:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    bucket = _RATE_LIMIT_BUCKET.setdefault(key, [])
    bucket[:] = [timestamp for timestamp in bucket if timestamp >= window_start]
    if len(bucket) >= _RATE_LIMIT_MAX:
        raise TooManyRequests
    bucket.append(now)


def _get_collector() -> BlockchainDataCollector:
    system_cache = current_app.config.setdefault("SERVICE_CACHE", {})
    collector = system_cache.get("collector")
    if collector is None:
        networks = current_app.config["SYSTEM_CONFIG"]["networks"]
        collector = BlockchainDataCollector(networks)
        system_cache["collector"] = collector
    return collector


def _get_security_manager() -> SecurityManager:
    system_cache = current_app.config.setdefault("SERVICE_CACHE", {})
    manager = system_cache.get("security_manager")
    if manager is None:
        manager = SecurityManager()
        system_cache["security_manager"] = manager
    return manager


@api_blueprint.route("/api/v1/predictions/gas-optimization", methods=["POST"])
def gas_optimization_prediction():
    client_key = request.remote_addr or "anonymous"
    try:
        _rate_limit(client_key)
    except TooManyRequests:
        return jsonify({"error": "Rate limit exceeded"}), HTTPStatus.TOO_MANY_REQUESTS

    payload = request.get_json(force=True) or {}
    network = payload.get("network", "ethereum.mainnet")

    networks_cfg = current_app.config["SYSTEM_CONFIG"]["networks"]
    network_parts = network.replace(":", ".").split(".")
    root = network_parts[0]
    tier = network_parts[1] if len(network_parts) > 1 else "mainnet"
    network_cfg = networks_cfg.get(root, {}).get(tier, {})

    if not network_cfg:
        return jsonify({"error": f"Network configuration not found for {network}"}), HTTPStatus.BAD_REQUEST

    collector = _get_collector()
    telemetry = collector.fetch_ethereum_data() if root == "ethereum" else collector.fetch_solana_data()

    try:
        web3 = create_web3_instance(network, rpc_url=network_cfg.get("rpc_url"))
        gas_estimate = estimate_optimal_gas({"web3": web3, "from": network_cfg.get("default_account")})
    except Exception as exc:
        LOGGER.exception("Gas estimation failed")
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    response = {
        "network": network,
        "telemetry": telemetry,
        "gas": gas_estimate,
        "timestamp": time.time(),
    }
    return jsonify(response), HTTPStatus.OK


@api_blueprint.route("/api/v1/execute/smart-contract", methods=["POST"])
def execute_smart_contract():
    client_key = request.remote_addr or "anonymous"
    try:
        _rate_limit(client_key)
    except TooManyRequests:
        return jsonify({"error": "Rate limit exceeded"}), HTTPStatus.TOO_MANY_REQUESTS

    payload = request.get_json(force=True) or {}
    network = payload.get("network", "ethereum.mainnet")
    prediction_data = payload.get("prediction_data", {})

    networks_cfg = current_app.config["SYSTEM_CONFIG"]["networks"]
    network_parts = network.replace(":", ".").split(".")
    root = network_parts[0]
    tier = network_parts[1] if len(network_parts) > 1 else "mainnet"
    network_cfg = networks_cfg.get(root, {}).get(tier, {})

    private_key = payload.get("private_key") or network_cfg.get("private_key") or None
    account_address = payload.get("account_address") or network_cfg.get("default_account")

    if not private_key or not account_address:
        return jsonify({"error": "Private key and account address are required"}), HTTPStatus.BAD_REQUEST

    security_manager = _get_security_manager()
    if not security_manager.validate_smart_contract(prediction_data.get("contract_address"), prediction_data.get("abi", [])):
        return jsonify({"error": "Smart contract validation failed"}), HTTPStatus.BAD_REQUEST

    try:
        orchestrator = SmartContractOrchestrator(
            network,
            networks_cfg,
            private_key=private_key,
            account_address=account_address,
        )
        tx_hash = asyncio.run(orchestrator.execute_ai_optimized_trade(prediction_data))
    except Exception as exc:
        LOGGER.exception("Smart contract execution failed")
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({"transaction_hash": tx_hash}), HTTPStatus.OK
