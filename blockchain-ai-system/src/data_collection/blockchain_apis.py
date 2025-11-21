from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


JSONDict = Dict[str, Any]


class BlockchainAPIError(RuntimeError):
    """Raised when a blockchain API call fails after retries."""


@dataclass(slots=True)
class CollectorStats:
    """Container for diagnostics about a collection cycle."""

    started_at: float
    completed_at: float
    api_calls: int
    errors: int


class BlockchainDataCollector:
    """Collects blockchain metrics from public RPC endpoints and explorer APIs."""

    def __init__(
        self,
        config: Mapping[str, Any],
        *,
        session: Optional[Session] = None,
        logger: Optional[logging.Logger] = None,
        request_timeout: float = 10.0,
    ) -> None:
        self._config = config
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._session = session or self._build_session(request_timeout=request_timeout)
        self._session.headers.update({"User-Agent": "BlockchainDataCollector/1.0"})
        self._request_timeout = request_timeout

    @staticmethod
    def _build_session(*, request_timeout: float) -> Session:
        retry_strategy = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(408, 425, 429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.request = BlockchainDataCollector._with_timeout(session.request, request_timeout)  # type: ignore[attr-defined]
        return session

    @staticmethod
    def _with_timeout(request_fn, request_timeout: float):
        def wrapper(method: str, url: str, **kwargs: Any):
            kwargs.setdefault("timeout", request_timeout)
            return request_fn(method, url, **kwargs)

        return wrapper

    def fetch_ethereum_data(self) -> JSONDict:
        """Fetches Ethereum metrics including gas, throughput, and market context."""
        network_cfg = self._config.get("ethereum", {}).get("mainnet")
        if not network_cfg:
            raise BlockchainAPIError("Missing Ethereum mainnet configuration")

        etherscan_key = os.getenv("ETHERSCAN_API_KEY")
        if not etherscan_key:
            self._logger.warning("ETHERSCAN_API_KEY not set; falling back to RPC-only metrics")

        rpc_url: Optional[str] = network_cfg.get("rpc_url")
        explorer_api: Optional[str] = network_cfg.get("explorer_api")

        stats = {"api_calls": 0, "errors": 0}
        started_at = time.time()

        gas_metrics: JSONDict = {}
        tx_metrics: JSONDict = {}
        market_metrics: JSONDict = {}

        if rpc_url:
            try:
                gas_metrics = self._fetch_ethereum_gas_metrics(rpc_url)
                stats["api_calls"] += 1
            except BlockchainAPIError as exc:
                self._logger.error("Ethereum gas metrics failed: %s", exc)
                gas_metrics = {"status": "error", "detail": str(exc)}
                stats["errors"] += 1

            try:
                tx_metrics = self._fetch_ethereum_transaction_metrics(rpc_url)
                stats["api_calls"] += 1
            except BlockchainAPIError as exc:
                self._logger.error("Ethereum transaction metrics failed: %s", exc)
                tx_metrics = {"status": "error", "detail": str(exc)}
                stats["errors"] += 1

        if explorer_api and etherscan_key:
            try:
                market_metrics = self._fetch_etherscan_market_metrics(explorer_api, etherscan_key)
                stats["api_calls"] += 1
            except BlockchainAPIError as exc:
                self._logger.error("Ethereum market metrics failed: %s", exc)
                market_metrics = {"status": "error", "detail": str(exc)}
                stats["errors"] += 1

        completed_at = time.time()
        collector_stats = CollectorStats(
            started_at=started_at,
            completed_at=completed_at,
            api_calls=stats["api_calls"],
            errors=stats["errors"],
        )

        return {
            "network": "ethereum",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "gas_metrics": gas_metrics,
            "transaction_metrics": tx_metrics,
            "market_metrics": market_metrics,
            "stats": collector_stats.__dict__,
        }

    def fetch_solana_data(self) -> JSONDict:
        """Fetches Solana metrics using the configured RPC endpoint."""
        solana_cfg = self._config.get("solana", {}).get("mainnet", {})
        rpc_url: Optional[str] = solana_cfg.get("rpc_url")
        market_api: Optional[str] = solana_cfg.get("market_api")

        if not rpc_url:
            raise BlockchainAPIError("Missing Solana RPC configuration")

        stats = {"api_calls": 0, "errors": 0}
        started_at = time.time()

        tps_metrics: JSONDict = {}
        market_metrics: JSONDict = {}

        try:
            tps_metrics = self._fetch_solana_performance(rpc_url)
            stats["api_calls"] += 1
        except BlockchainAPIError as exc:
            self._logger.error("Solana TPS metrics failed: %s", exc)
            tps_metrics = {"status": "error", "detail": str(exc)}
            stats["errors"] += 1

        if market_api:
            try:
                market_metrics = self._fetch_solana_market_metrics(market_api)
                stats["api_calls"] += 1
            except BlockchainAPIError as exc:
                self._logger.error("Solana market metrics failed: %s", exc)
                market_metrics = {"status": "error", "detail": str(exc)}
                stats["errors"] += 1

        completed_at = time.time()
        collector_stats = CollectorStats(
            started_at=started_at,
            completed_at=completed_at,
            api_calls=stats["api_calls"],
            errors=stats["errors"],
        )

        return {
            "network": "solana",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "performance_metrics": tps_metrics,
            "market_metrics": market_metrics,
            "stats": collector_stats.__dict__,
        }

    def _fetch_ethereum_gas_metrics(self, rpc_url: str) -> JSONDict:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_feeHistory",
            "params": [10, "latest", [10, 30, 50]],
        }
        response = self._post_json(rpc_url, payload)
        fee_history = response.get("result")
        if not fee_history:
            raise BlockchainAPIError("Empty fee history response")
        base_fees = [int(fee, 16) for fee in fee_history.get("baseFeePerGas", [])]
        rewards = fee_history.get("reward", [])
        reward_per_gwei = [int(tier[-1], 16) for tier in rewards if tier]
        return {
            "base_fee_mean": sum(base_fees) / len(base_fees) if base_fees else None,
            "reward_high_percentile": reward_per_gwei[-1] if reward_per_gwei else None,
            "suggested_priority_fee": reward_per_gwei[1] if len(reward_per_gwei) > 1 else None,
            "block_count": len(base_fees),
        }

    def _fetch_ethereum_transaction_metrics(self, rpc_url: str) -> JSONDict:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_getBlockByNumber",
            "params": ["latest", True],
        }
        latest_block = self._post_json(rpc_url, payload).get("result")
        if not latest_block:
            raise BlockchainAPIError("No latest block found")
        transactions = latest_block.get("transactions", [])
        gas_used = int(latest_block.get("gasUsed", "0x0"), 16)
        gas_limit = int(latest_block.get("gasLimit", "0x1"), 16)
        utilization = gas_used / gas_limit if gas_limit else 0.0
        return {
            "block_number": int(latest_block["number"], 16),
            "transaction_count": len(transactions),
            "gas_utilization": utilization,
            "timestamp": int(latest_block.get("timestamp", "0x0"), 16),
        }

    def _fetch_etherscan_market_metrics(self, explorer_api: str, api_key: str) -> JSONDict:
        params = {
            "module": "stats",
            "action": "ethprice",
            "apikey": api_key,
        }
        response = self._session.get(f"{explorer_api}/api", params=params)
        if not response.ok:
            raise BlockchainAPIError(f"Etherscan market metrics failed: {response.status_code}")
        payload = response.json()
        if payload.get("status") != "1":
            raise BlockchainAPIError(f"Etherscan reported error: {payload.get('message')}")
        result = payload.get("result", {})
        return {
            "ethusd": float(result.get("ethusd", 0.0)),
            "ethbtc": float(result.get("ethbtc", 0.0)),
            "timestamp": int(result.get("ethusd_timestamp", 0)),
        }

    def _fetch_solana_performance(self, rpc_url: str) -> JSONDict:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getRecentPerformanceSamples",
            "params": [5],
        }
        response = self._post_json(rpc_url, payload)
        samples = response.get("result", [])
        if not samples:
            raise BlockchainAPIError("No Solana performance samples")
        avg_tps = sum(sample.get("numTransactions", 0) / sample.get("samplePeriodSecs", 1) for sample in samples) / len(samples)
        return {
            "average_tps": avg_tps,
            "sample_count": len(samples),
            "latest_slot": samples[0].get("slot", 0),
        }

    def _fetch_solana_market_metrics(self, market_api: str) -> JSONDict:
        response = self._session.get(market_api)
        if not response.ok:
            raise BlockchainAPIError(f"Solana market API returned {response.status_code}")
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise BlockchainAPIError(f"Invalid market payload: {exc}") from exc
        return {
            "price_usd": float(payload.get("price", 0.0)),
            "volume_24h": float(payload.get("volume", 0.0)),
            "change_24h": float(payload.get("change", 0.0)),
        }

    def _post_json(self, url: str, payload: JSONDict) -> JSONDict:
        try:
            response = self._session.post(url, json=payload)
        except requests.RequestException as exc:
            raise BlockchainAPIError(str(exc)) from exc
        if not response.ok:
            raise BlockchainAPIError(f"HTTP error {response.status_code} for {url}")
        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise BlockchainAPIError(f"Invalid JSON response: {exc}") from exc
        if "error" in data:
            raise BlockchainAPIError(str(data["error"]))
        return data

    def close(self) -> None:
        self._session.close()
