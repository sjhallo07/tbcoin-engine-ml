"""Blockchain interaction layer for the Autonomous AI Trading Agent.

Contains:
- smart_contracts
- wallet
- tx_simulation
"""
from .smart_contracts import SmartContractExecutor
from .wallet import WalletManager
from .tx_simulation import TransactionSimulator

__all__ = ["SmartContractExecutor", "WalletManager", "TransactionSimulator"]
