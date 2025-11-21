from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from web3 import Web3
from web3.contract import ContractFunction
from web3.exceptions import ContractLogicError, TransactionNotFound

from .web3_helpers import create_web3_instance, estimate_optimal_gas


@dataclass(slots=True)
class ExecutionResult:
    """Details about a transaction execution attempt."""

    transaction_hash: str
    simulation_passed: bool
    gas_used: Optional[int]
    network: str


class SmartContractOrchestrator:
    """Executes smart contract transactions based on AI predictions with safety checks."""

    def __init__(
        self,
        network: str,
        config: Mapping[str, Any],
        *,
        private_key: str,
        account_address: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._network = network
        self._config = config
        self._private_key = private_key
        self._account_address = account_address
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._network_cfg = self._resolve_network_config()
        self._web3: Web3 = create_web3_instance(network, rpc_url=self._network_cfg.get("rpc_url"))

    async def execute_ai_optimized_trade(self, prediction_data: Dict[str, Any]) -> str:
        """Execute a smart contract call using AI-optimized parameters."""
        contract_address = prediction_data.get("contract_address")
        abi = prediction_data.get("abi")
        function_name = prediction_data.get("function_name")
        function_args = prediction_data.get("function_args", [])

        if not contract_address or not abi or not function_name:
            raise ValueError("Prediction payload missing contract execution details")

        contract = self._web3.eth.contract(address=self._web3.toChecksumAddress(contract_address), abi=abi)
        contract_fn: ContractFunction = getattr(contract.functions, function_name)(*function_args)

        nonce = self._web3.eth.get_transaction_count(self._account_address)
        tx_params: Dict[str, Any] = {
            "from": self._account_address,
            "nonce": nonce,
            "chainId": self._web3.eth.chain_id,
        }

        if gas_params := prediction_data.get("gas_parameters"):
            tx_params.update(gas_params)
        else:
            tx_params.update(estimate_optimal_gas({"web3": self._web3, "from": self._account_address}))

        if "value" in prediction_data:
            tx_params["value"] = prediction_data["value"]

        from web3.types import TxParams  # Add this import at the top if not already present
        built_tx = contract_fn.build_transaction(tx_params if isinstance(tx_params, dict) else dict(tx_params))  # type: ignore[arg-type]
        await self._simulate_transaction(dict(built_tx))

        signed_tx = self._web3.eth.account.sign_transaction(built_tx, private_key=self._private_key)
        tx_hash = await self._send_transaction(signed_tx.rawTransaction)
        self._logger.info("Submitted transaction %s on %s", tx_hash, self._network)
        return tx_hash

    async def _simulate_transaction(self, transaction: Dict[str, Any]) -> None:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._web3.eth.call, transaction)
        except ContractLogicError as exc:
            self._logger.error("Simulation failed: %s", exc)
            raise RuntimeError("Transaction simulation failed") from exc

    async def _send_transaction(self, raw_tx: bytes) -> str:
        loop = asyncio.get_running_loop()
        tx_hash = await loop.run_in_executor(None, self._web3.eth.send_raw_transaction, raw_tx)
        hex_hash = tx_hash.hex()
        await self._await_receipt(hex_hash)
        return hex_hash

    async def _await_receipt(self, tx_hash: str, *, timeout: int = 120, poll_interval: float = 5.0) -> None:
        loop = asyncio.get_running_loop()
        start_block = await loop.run_in_executor(None, self._web3.eth.get_block, "latest")
        start_time = start_block.get("timestamp", 0)
        while True:
            try:
                from eth_typing.encoding import HexStr
                receipt = await loop.run_in_executor(None, self._web3.eth.get_transaction_receipt, HexStr(tx_hash))
                if receipt:
                    self._logger.debug("Transaction %s confirmed in block %s", tx_hash, receipt["blockNumber"])
                    return
            except TransactionNotFound:
                pass

            latest_block = await loop.run_in_executor(None, self._web3.eth.get_block, "latest")
            latest_timestamp = latest_block.get("timestamp", 0)
            if latest_timestamp - start_time > timeout:
                raise TimeoutError(f"Timed out waiting for transaction {tx_hash}")
            await asyncio.sleep(poll_interval)

    def _resolve_network_config(self) -> Mapping[str, Any]:
        parts = self._network.replace(":", ".").split(".")
        base = parts[0]
        tier = parts[1] if len(parts) > 1 else "mainnet"
        return self._config.get(base, {}).get(tier, {})
