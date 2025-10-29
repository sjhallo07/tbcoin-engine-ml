"""Trading strategies package scaffolding.

Contains strategy orchestration and risk management.
"""
from .strategies import StrategyManager
from .risk_manager import RiskManager

__all__ = ["StrategyManager", "RiskManager"]
