"""LearningFeedbackLoop

Provides a feedback loop that analyzes trade performance, extracts insights, adjusts strategy
weights and schedules model retraining when necessary.

This module is tolerant of missing heavy dependencies (pandas) and missing repository-local
components. It provides lightweight fallbacks so it can be imported and exercised in minimal
environments.
"""
from __future__ import annotations

import asyncio
import math
from typing import Dict, List, Any

# Optional heavy dependency
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # type: ignore

# Try to import repo-specific components; provide local fallbacks
try:
    from app.autonomous_agent.self_improvement.self_improvement import SelfImprovementLoop  # type: ignore
except Exception:
    class SelfImprovementLoop:  # type: ignore
        def __init__(self):
            self.history = []

        async def record(self, result: Dict[str, Any]):
            self.history.append(result)


# Performance tracker, optimizer, retrainer fallbacks
try:
    from agents.performance_tracker import PerformanceTracker  # type: ignore
except Exception:
    class PerformanceTracker:  # type: ignore
        async def calculate_metrics(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
            # Minimal metrics calculation
            pnl = float(trade_data.get("pnl", 0.0))
            entry = float(trade_data.get("entry_price", 0.0))
            exit_p = float(trade_data.get("exit_price", 0.0))
            profitability = pnl
            rolling_loss = max(0.0, -pnl) / (abs(entry) + 1e-6)
            return {
                "profitability": profitability,
                "rolling_loss": float(min(1.0, rolling_loss)),
                "entry_timing_score": 0.5,
                "exit_efficiency": 0.5,
                "max_drawdown": 0.0,
            }

try:
    from agents.strategy_optimizer import StrategyOptimizer  # type: ignore
except Exception:
    class StrategyOptimizer:  # type: ignore
        async def adjust_strategy_weights(self, strategy_name: str, metrics: Dict[str, Any]) -> None:
            # Stub: log or no-op
            await asyncio.to_thread(print, f"Adjusting strategy weights for {strategy_name}: {metrics}")

try:
    from agents.model_retrainer import ModelRetrainer  # type: ignore
except Exception:
    class ModelRetrainer:  # type: ignore
        async def schedule_retraining(self) -> None:
            await asyncio.to_thread(print, "Scheduling model retraining (stub)")


class LearningFeedbackLoop:
    """Orchestrates performance analysis, strategy updates and retraining triggers."""

    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.strategy_optimizer = StrategyOptimizer()
        self.model_retrainer = ModelRetrainer()
        self.self_improvement = SelfImprovementLoop()

    async def analyze_trade_performance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trade performance and generate learning insights.

        If performance is poor, this method will run failure analysis, adjust strategy weights
        and schedule retraining when thresholds are exceeded.
        """
        performance_metrics = await self.performance_tracker.calculate_metrics(trade_data)

        # If negative profitability take corrective actions
        if performance_metrics.get("profitability", 0) < 0:
            failure_analysis = await self._analyze_failure_reasons(trade_data, performance_metrics)

            # Update strategy weights (best-effort)
            strategy_used = trade_data.get("strategy_used", "unknown")
            await self.strategy_optimizer.adjust_strategy_weights(strategy_used, performance_metrics)

            # Trigger retraining if rolling loss high
            if performance_metrics.get("rolling_loss", 0) > 0.1:
                await self.model_retrainer.schedule_retraining()

        insights = await self._extract_learning_insights(trade_data, performance_metrics)
        adjustments = await self._calculate_strategy_adjustments(performance_metrics)

        result = {
            "performance_metrics": performance_metrics,
            "learning_insights": insights,
            "strategy_adjustments": adjustments,
        }

        # Record to the self-improvement loop if available
        try:
            await self.self_improvement.record(result)
        except Exception:
            pass

        return result

    async def _analyze_failure_reasons(self, trade_data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Perform lightweight failure analysis and return reasons."""
        # Heuristic checks
        reasons: List[str] = []
        if metrics.get("entry_timing_score", 1.0) < 0.4:
            reasons.append("poor_entry_timing")
        if metrics.get("exit_efficiency", 1.0) < 0.4:
            reasons.append("inefficient_exits")
        if metrics.get("max_drawdown", 0.0) > 0.15:
            reasons.append("high_drawdown")

        analysis = {"reasons": reasons}
        await asyncio.to_thread(print, f"Failure analysis: {analysis}")
        return analysis

    async def _extract_learning_insights(self, trade_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Extract actionable insights from trade performance."""
        insights: List[str] = []
        if metrics.get("entry_timing_score", 1.0) < 0.3:
            insights.append("Poor entry timing detected. Improve market condition analysis.")
        if metrics.get("exit_efficiency", 1.0) < 0.5:
            insights.append("Inefficient exits. Optimize profit-taking and stop-loss strategies.")
        if metrics.get("max_drawdown", 0.0) > 0.15:
            insights.append("High drawdown detected. Strengthen risk management rules.")
        if trade_data.get("strategy_used") == "momentum" and metrics.get("profitability", 0) < 0:
            insights.append("Momentum strategy underperforming in current market regime.")
        return insights

    async def _calculate_strategy_adjustments(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Return suggested numerical adjustments to strategy hyperparameters.

        This is a simple heuristic that suggests tightening stop-loss or reducing position size
        when losses are detected.
        """
        adjustments: Dict[str, Any] = {}
        prof = metrics.get("profitability", 0)
        if prof < 0:
            adjustments["position_size_factor"] = max(0.5, 1.0 - min(0.5, abs(prof)))
            adjustments["stop_loss_tighten_bps"] = 50
        else:
            adjustments["position_size_factor"] = 1.0
            adjustments["stop_loss_tighten_bps"] = 0
        return adjustments


# Demo when run directly
if __name__ == "__main__":
    async def _demo():
        loop = LearningFeedbackLoop()
        sample_trade = {
            "strategy_used": "momentum",
            "pnl": -0.2,
            "entry_price": 100.0,
            "exit_price": 90.0,
        }
        result = await loop.analyze_trade_performance(sample_trade)
        print("Feedback result:", result)

    asyncio.run(_demo())
