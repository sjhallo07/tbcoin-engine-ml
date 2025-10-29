#!/usr/bin/env python3
"""Run a single market analysis cycle using the AutonomousTradingAgent.

This script is defensive: if the `agents.autonomous_agent.AutonomousTradingAgent` class
is not importable it falls back to a minimal local stub that provides `_gather_market_data`
and a `decision_engine` with `analyze_market_context`.
"""
import asyncio
import sys
from typing import Dict, Any

# Try to import the real agent, otherwise provide a lightweight fallback
try:
    from agents.autonomous_agent import AutonomousTradingAgent  # type: ignore
except Exception:
    try:
        from .agents.autonomous_agent import AutonomousTradingAgent  # type: ignore
    except Exception:
        class _StubDecisionEngine:
            async def analyze_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
                # Return a neutral analysis
                return {
                    "confidence_level": 0.0,
                    "llm_recommendation": "HOLD",
                    "risk_assessment": {"score": 0.0, "level": "LOW"},
                }

        class AutonomousTradingAgent:  # type: ignore
            def __init__(self):
                self.decision_engine = _StubDecisionEngine()

            async def _gather_market_data(self) -> Dict[str, Any]:
                # Minimal market snapshot
                return {"price_series": [100.0, 100.5, 101.0], "close": [100.0, 100.5, 101.0], "symbol": "TBCOIN"}


async def main():
    agent = AutonomousTradingAgent()

    # Run single market analysis cycle
    try:
        market_data = await agent._gather_market_data()
    except Exception:
        # If gather function is missing or sync, try calling directly
        gather = getattr(agent, "_gather_market_data", None)
        if callable(gather):
            maybe = gather()
            if asyncio.iscoroutine(maybe):
                market_data = await maybe
            else:
                market_data = maybe
        else:
            market_data = {"price_series": [], "close": [], "symbol": "TBCOIN"}

    # Safe analyze call
    analyze = getattr(agent, "decision_engine", None)
    if analyze is None:
        print("No decision engine available on agent.")
        sys.exit(1)

    analyze_fn = getattr(analyze, "analyze_market_context", None)
    if not callable(analyze_fn):
        print("Decision engine missing `analyze_market_context` method.")
        sys.exit(1)

    analysis = analyze_fn(market_data)
    if asyncio.iscoroutine(analysis):
        analysis = await analysis

    # Pretty-print results
    conf = analysis.get("confidence_level", analysis.get("confidence", 0.0))
    recommendation = analysis.get("llm_recommendation", "HOLD")
    risk = analysis.get("risk_assessment", {"score": 0.0})

    print("📊 Market Analysis Completed:")
    try:
        print(f"   Confidence: {float(conf):.2f}")
    except Exception:
        print(f"   Confidence: {conf}")
    print(f"   Recommendation: {recommendation}")
    try:
        print(f"   Risk Score: {float(risk.get('score', 0.0)):.2f}")
    except Exception:
        print(f"   Risk Score: {risk}")


if __name__ == "__main__":
    asyncio.run(main())
