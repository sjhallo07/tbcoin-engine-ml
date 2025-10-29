"""Smoke test to ensure the autonomous agent package imports and basic classes instantiate."""
from app.autonomous_agent.core.llm_engine import LLMDecisionEngine
from app.autonomous_agent.core.rl_agent import RLAgent
from app.autonomous_agent.blockchain.wallet import WalletManager
from app.autonomous_agent.strategies.strategies import StrategyManager
from app.autonomous_agent.self_improvement.self_improvement import SelfImprovementLoop


def test_import_and_instantiate():
    llm = LLMDecisionEngine()
    rl = RLAgent()
    wallet = WalletManager()
    strategies = StrategyManager()
    loop = SelfImprovementLoop()

    assert llm is not None
    assert rl is not None
    assert wallet is not None
    assert strategies is not None
    assert loop is not None
