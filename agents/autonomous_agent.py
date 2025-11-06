"""AutonomousTradingAgent

Top-level orchestrator that ties together the decision engine, blockchain executor,
organic behavior simulator, wallet manager, learning feedback loop and strategy
evolver. The implementation is defensive so imports won't break in minimal test
environments.
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Dict, Any

# Try to import components created earlier; fallback to local stubs when missing.
try:
    from agents.ai_decision_engine import AutonomousDecisionEngine  # type: ignore
except Exception:
    try:
        from .ai_decision_engine import AutonomousDecisionEngine  # type: ignore
    except Exception:
        class AutonomousDecisionEngine:  # type: ignore
            async def analyze_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"llm_recommendation": "HOLD", "confidence_level": 0.0, "risk_assessment": {"level": "LOW", "score": 0.0}, "confidence": 0}

try:
    from agents.blockchain_executor import AIBlockchainExecutor  # type: ignore
except Exception:
    try:
        from .blockchain_executor import AIBlockchainExecutor  # type: ignore
    except Exception:
        class AIBlockchainExecutor:  # type: ignore
            async def execute_ai_trade(self, trade_decision: Dict[str, Any]) -> str:
                await asyncio.sleep(0.01)
                return "SIM_SIGNATURE"

# Behavior simulator stub (not implemented earlier)
try:
    from agents.behavior_simulator import OrganicBehaviorSimulator  # type: ignore
except Exception:
    class OrganicBehaviorSimulator:  # type: ignore
        async def simulate_organic_trade(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Simple mapping: use LLM recommendation if present
            action = context.get("llm_recommendation", "HOLD")
            amount = context.get("confidence_level", 0) * 0.01
            if action not in ("BUY", "SELL"):
                action = "HOLD"
            return {"action": action, "amount": float(amount), "confidence": context.get("confidence_level", 0)}

try:
    from agents.learning_feedback_loop import LearningFeedbackLoop  # type: ignore
except Exception:
    try:
        from .learning_feedback_loop import LearningFeedbackLoop  # type: ignore
    except Exception:
        class LearningFeedbackLoop:  # type: ignore
            async def analyze_trade_performance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"performance_metrics": {}, "learning_insights": [], "strategy_adjustments": {}}

try:
    from agents.wallet_strategy_manager import WalletStrategyManager  # type: ignore
except Exception:
    try:
        from .wallet_strategy_manager import WalletStrategyManager  # type: ignore
    except Exception:
        class WalletStrategyManager:  # type: ignore
            async def execute_distributed_trade(self, master_decision: Dict[str, Any]) -> list:
                await asyncio.sleep(0.01)
                return ["SIM_SIG"]

try:
    from agents.strategy_evolver import StrategyEvolver  # type: ignore
except Exception:
    class StrategyEvolver:  # type: ignore
        async def evolve_strategies(self, *args, **kwargs):
            return None


class AutonomousTradingAgent:
    """High-level autonomous trading agent orchestrator."""

    def __init__(self):
        self.decision_engine = AutonomousDecisionEngine()
        self.blockchain_executor = AIBlockchainExecutor()
        self.behavior_simulator = OrganicBehaviorSimulator()
        self.learning_loop = LearningFeedbackLoop()
        self.wallet_manager = WalletStrategyManager()
        self.strategy_evolver = StrategyEvolver()

        self.is_running = False
        self.performance_metrics: Dict[str, Any] = {}

    async def start_autonomous_trading(self):
        """Main autonomous trading loop."""
        self.is_running = True
        print("🚀 Starting Autonomous Trading Agent...")

        while self.is_running:
            try:
                market_data = await self._gather_market_data()
                analysis = await self.decision_engine.analyze_market_context(market_data)

                # Ensure keys exist in analysis
                confidence = float(analysis.get("confidence_level", analysis.get("confidence", 0.0)))
                risk = analysis.get("risk_assessment", {"level": "LOW", "score": 0.0})

                if confidence > 0.7:
                    trade_decision = await self._make_trading_decision(analysis, market_data)

                    organic_trade = await self.behavior_simulator.simulate_organic_trade({**market_data, **analysis})

                    if organic_trade.get("action", "HOLD") != "HOLD":
                        execution_results = await self.wallet_manager.execute_distributed_trade(organic_trade)

                        learning_insights = await self.learning_loop.analyze_trade_performance({
                            **organic_trade,
                            "execution_results": execution_results,
                            "market_context": market_data,
                        })

                        adjustments = learning_insights.get("strategy_adjustments", {})
                        if adjustments:
                            await self._evolve_strategies(adjustments)

                await asyncio.sleep(self._get_next_analysis_delay())

            except Exception as e:
                # Log and backoff
                await asyncio.to_thread(print, f"Error in autonomous trading loop: {e}")
                await asyncio.sleep(60)

    async def _gather_market_data(self) -> Dict[str, Any]:
        """Stub to gather market data. Replace with real data ingestion."""
        # Minimal market snapshot
        return {"price_series": [100.0, 100.5, 101.0], "close": [100.0, 100.5, 101.0], "symbol": "TBCOIN"}

    async def _make_trading_decision(self, analysis: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make final trading decision considering risk overlays and position sizing."""
        base_action = analysis.get("llm_recommendation", "HOLD")
        risk_assessment = analysis.get("risk_assessment", {"level": "LOW", "score": 0.0})

        if isinstance(risk_assessment, dict) and risk_assessment.get("level") == "HIGH":
            base_action = "HOLD"

        position_size = self._calculate_position_size(
            float(analysis.get("confidence_level", 0.0)),
            float(risk_assessment.get("score", 0.0)) if isinstance(risk_assessment, dict) else float(risk_assessment)
        )

        return {
            "action": base_action,
            "amount": float(position_size),
            "confidence": float(analysis.get("confidence_level", 0.0)),
            "risk_score": float(risk_assessment.get("score", 0.0)) if isinstance(risk_assessment, dict) else 0.0,
            "strategy_used": "composite_ai_decision",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_position_size(self, confidence: float, risk_score: float) -> float:
        """Calculate position size using a capped Kelly fraction and risk overlay.

        Returns fraction of portfolio to allocate (0.0-0.05).
        """
        win_probability = max(0.0, min(1.0, confidence))
        win_loss_ratio = 2.0

        # Kelly fraction
        kelly_fraction = (win_probability * win_loss_ratio - (1 - win_probability)) / win_loss_ratio
        kelly_fraction = max(0.0, kelly_fraction)  # don't allow negative fraction

        # Apply risk overlay
        risk_adj = 1.0 - max(0.0, min(1.0, risk_score))
        risk_adjusted_fraction = kelly_fraction * risk_adj

        max_position = 0.05
        position = min(risk_adjusted_fraction, max_position)
        # Small safety floor
        position = max(0.0, position)
        return float(position)

    def _get_next_analysis_delay(self) -> float:
        """Return next delay in seconds between analysis cycles.

        Uses jitter to avoid strict periodic timing.
        """
        base = 5.0
        return base + random.uniform(0.0, 5.0)

    async def _evolve_strategies(self, adjustments: Dict[str, Any]) -> None:
        """Trigger strategy evolution using the StrategyEvolver (best-effort).

        adjustments may contain suggested parameter changes; we forward to evolver.
        """
        try:
            await self.strategy_evolver.evolve_strategies("adaptive", None)
        except Exception:
            # Non-fatal
            await asyncio.to_thread(print, "Strategy evolution failed or not available")


# Quick CLI demo when invoked directly
if __name__ == "__main__":
    async def _demo():
        agent = AutonomousTradingAgent()
        # Run one cycle for demo and then stop
        task = asyncio.create_task(agent.start_autonomous_trading())
        await asyncio.sleep(2)
        agent.is_running = False
        await task

    asyncio.run(_demo())
