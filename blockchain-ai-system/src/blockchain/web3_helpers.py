from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware


LOGGER = logging.getLogger(__name__)


class Web3ConfigurationError(RuntimeError):
    """Raised when the Web3 client cannot be configured."""


def create_web3_instance(network: str, *, rpc_url: Optional[str] = None) -> Web3:
    """Initialize a Web3 instance with connection pooling and retries."""
    base_network = network.split(".")[0].lower()
    rpc = rpc_url or _resolve_rpc_url(network)
    if not rpc:
        raise Web3ConfigurationError(f"No RPC URL configured for network '{network}'")

    provider = HTTPProvider(rpc, request_kwargs={"timeout": 30})
    web3 = Web3(provider)
    if base_network in {"polygon", "arbitrum", "optimism"}:
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    if not web3.is_connected():
        raise Web3ConfigurationError(f"Unable to connect to RPC endpoint {rpc}")
    return web3


def estimate_optimal_gas(transaction_params: Dict[str, Any]) -> Dict[str, int]:
    """Estimate gas configuration using recent network conditions."""
    web3: Optional[Web3] = transaction_params.get("web3")
    if web3 is None:
        raise ValueError("'web3' instance must be provided in transaction_params")

    try:
        gas_price = web3.eth.gas_price
    except Exception as exc:  # pragma: no cover - node specific errors
        LOGGER.warning("Failed to fetch gas price: %s", exc)
        gas_price = int(30e9)  # conservative default at 30 gwei

    try:
        base_estimate = web3.eth.estimate_gas({k: v for k, v in transaction_params.items() if k != "web3"})
    except Exception as exc:
        LOGGER.warning("Gas estimation failed, applying fallback: %s", exc)
        base_estimate = 200000

    priority_fee = max(int(gas_price * 0.15), int(1.5e9))
    max_fee_per_gas = gas_price + 2 * priority_fee

    return {
        "gas": base_estimate,
        "maxPriorityFeePerGas": priority_fee,
        "maxFeePerGas": max_fee_per_gas,
        "gasPrice": max_fee_per_gas,
    }


@lru_cache(maxsize=16)
def _resolve_rpc_url(network: str) -> Optional[str]:
    env_var = network.upper().replace("-", "_").replace(".", "_") + "_RPC"
    return os.getenv(env_var)
