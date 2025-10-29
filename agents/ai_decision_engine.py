"""AutonomousDecisionEngine

A robust, dependency-tolerant implementation of the user's provided AI decision engine.
This file intentionally avoids hard failures when optional heavy dependencies (transformers, torch,
scipy, pandas) are not installed — it falls back to simple rule-based behavior.

It integrates with the repository's `app.autonomous_agent` scaffolding where possible:
- RL agent -> `app.autonomous_agent.core.rl_agent.RLAgent`
- Pattern recognizer -> `app.autonomous_agent.core.pattern_recognition.PatternRecognizer`
- Risk manager -> `app.autonomous_agent.strategies.risk_manager.RiskManager`

The public class is `AutonomousDecisionEngine` and provides an async `analyze_market_context` method.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any
import math
import re

# Try to import optional heavy deps only when available
try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore

# Import repository-local components (these were added under app/autonomous_agent)
try:
    from app.autonomous_agent.core.rl_agent import RLAgent
    from app.autonomous_agent.core.pattern_recognition import PatternRecognizer
    from app.autonomous_agent.strategies.risk_manager import RiskManager
except Exception:
    # Provide lightweight local fallbacks if package is not present for any reason.
    class RLAgent:
        def __init__(self):
            self.trained = False

        def train(self, episodes: int = 1000):
            self.trained = True

        def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
            return {"action": "hold", "amount": 0}

    class PatternRecognizer:
        def find_patterns(self, series: List[float]) -> List[Dict[str, Any]]:
            return []

    class RiskManager:
        def __init__(self, max_drawdown: float = 0.2):
            self.max_drawdown = max_drawdown

        async def assess_trade_risk(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"ok": True, "reason": "fallback"}

# The transformers-based LLM components are optional — load only if available
def _try_load_transformers():
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
        import torch  # type: ignore
        return AutoTokenizer, AutoModelForCausalLM, torch
    except Exception:
        return None, None, None

AutoTokenizer, AutoModelForCausalLM, torch = _try_load_transformers()

class AutonomousDecisionEngine:
    """High-level autonomous decision engine combining LLMs, RL, pattern recognition and risk checks.

    Notes:
    - All heavy external calls (LLM) are guarded and will fall back to simple heuristics when not available.
    - Methods are asynchronous to allow parallel I/O in real implementations.
    """

    def __init__(self, llm_model_name: str = "gpt-fallback"):
        self.llm_model_name = llm_model_name
        self.llm_model = None
        if AutoTokenizer and AutoModelForCausalLM and torch:
            self.llm_model = self._load_llm(self.llm_model_name)

        # Use repository RL/Pattern/Risk classes where available
        self.rl_agent = RLAgent()
        self.pattern_analyzer = PatternRecognizer()
        self.risk_manager = RiskManager()

    def _load_llm(self, model_name: str):
        """Try to load a small LLM; return a dict with tokenizer and model or None."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            # Move model to CPU (or GPU if available) — keep simple
            if torch and torch.cuda.is_available():
                model.to("cuda")
            return {"tokenizer": tokenizer, "model": model}
        except Exception:
            return None

    async def analyze_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive market analysis using multiple AI approaches.

        market_data is expected to be a dict with keys such as:
        - 'price_series': List[float]
        - 'volume_series': List[float]
        - optional metadata (symbol, timeframe, etc.)
        """
        # Run sub-analyses concurrently where useful
        technical_task = asyncio.create_task(self.technical_analysis(market_data))
        sentiment_task = asyncio.create_task(self.sentiment_analysis(market_data))

        # Pattern recognition: our PatternRecognizer provides find_patterns(series) -> list
        price_series = market_data.get("price_series") or market_data.get("close") or []
        patterns_task = asyncio.to_thread(self.pattern_analyzer.find_patterns, price_series)

        technical_signals = await technical_task
        sentiment = await sentiment_task
        patterns_list = await patterns_task

        # Normalize pattern output to a simple dict
        patterns = {
            "primary_pattern": patterns_list[0].get("name") if patterns_list else "none",
            "confidence": patterns_list[0].get("confidence", 0) if patterns_list else 0,
            "success_rate": patterns_list[0].get("success_rate", 0) if patterns_list else 0,
        }

        # LLM-based contextual analysis (guarded)
        llm_insight = await self.llm_context_analysis(technical_signals, sentiment, patterns)

        # Risk assessment: could be async
        try:
            risk_assessment = await self.risk_manager.assess_trade_risk(market_data)
        except TypeError:
            # some risk manager implementations may be sync
            risk_assessment = self.risk_manager.assess_trade_risk(market_data)  # type: ignore

        return {
            "technical_score": technical_signals.get("composite_score", 0),
            "sentiment_score": sentiment.get("overall_sentiment", 0),
            "pattern_confidence": patterns.get("confidence", 0),
            "llm_recommendation": llm_insight.get("action", "HOLD"),
            "llm_reasoning": llm_insight.get("reason", None),
            "confidence_level": self.calculate_confidence(technical_signals, sentiment, patterns),
            "risk_assessment": risk_assessment,
        }

    async def llm_context_analysis(self, technical: Dict[str, Any], sentiment: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Use an LLM to generate a contextual trading decision, or fallback to simple heuristics.

        Returns a dict {action: BUY|SELL|HOLD, confidence: float, reason: str}
        """
        # If LLM not available, fallback quickly
        if not self.llm_model:
            return self._fallback_analysis(technical, sentiment, patterns)

        prompt = (
            "As an advanced crypto trading AI, analyze this market situation:\n\n"
            f"TECHNICAL INDICATORS:\n- RSI: {technical.get('rsi', 0)}\n- MACD: {technical.get('macd', 0)}\n- Volume Trend: {technical.get('volume_trend', 'neutral')}\n- Price Momentum: {technical.get('momentum', 0)}\n\n"
            f"MARKET SENTIMENT:\n- Overall: {sentiment.get('overall_sentiment', 'neutral')}\n- Social Volume: {sentiment.get('social_volume', 0)}\n- Fear/Greed: {sentiment.get('fear_greed', 50)}\n\n"
            f"PATTERN RECOGNITION:\n- Detected Pattern: {patterns.get('primary_pattern', 'none')}\n- Confidence: {patterns.get('confidence', 0)}\n- Historical Success: {patterns.get('success_rate', 0)}\n\n"
            "Based on this analysis, recommend one of these actions: BUY, SELL, HOLD. Provide reasoning and confidence level."
        )

        try:
            tokenizer = self.llm_model["tokenizer"]
            model = self.llm_model["model"]
            inputs = tokenizer(prompt, return_tensors="pt")
            if torch and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
                model.to("cuda")

            outputs = model.generate(
                inputs["input_ids"],
                max_length=256,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self._parse_llm_response(response)
        except Exception:
            return self._fallback_analysis(technical, sentiment, patterns)

    async def technical_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute simple technical indicators as a stub.

        Expected keys: 'price_series' or 'close'. Returns a dict with a composite_score in [0,1].
        """
        prices = market_data.get("price_series") or market_data.get("close") or []
        if not prices:
            return {"composite_score": 0.0, "rsi": 50, "macd": 0, "momentum": 0, "volume_trend": "neutral"}

        # Simple momentum and normalized score
        try:
            if np is not None:
                arr = np.array(prices, dtype=float)
                momentum = float(arr[-1] - arr[-2]) if len(arr) >= 2 else 0.0
                rsi = 50.0  # placeholder
                macd = 0.0
                volume_trend = "neutral"
                # Composite score: normalized momentum in [-1,1] -> [0,1]
                composite = 0.5 + (math.tanh(momentum) / 2.0)
            else:
                momentum = float(prices[-1] - prices[-2]) if len(prices) >= 2 else 0.0
                rsi = 50.0
                macd = 0.0
                volume_trend = "neutral"
                composite = 0.5 + (math.tanh(momentum) / 2.0)
        except Exception:
            composite = 0.0
            rsi = 50
            macd = 0
            momentum = 0
            volume_trend = "neutral"

        return {"composite_score": float(max(0.0, min(1.0, composite))), "rsi": rsi, "macd": macd, "momentum": momentum, "volume_trend": volume_trend}

    async def sentiment_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lightweight sentiment stub.

        If `market_data` contains 'sentiment' dict, return it; otherwise return neutral.
        """
        s = market_data.get("sentiment") or {}
        overall = s.get("overall_sentiment", 0) if isinstance(s, dict) else 0
        social_vol = s.get("social_volume", 0)
        fear_greed = s.get("fear_greed", 50)
        return {"overall_sentiment": overall, "social_volume": social_vol, "fear_greed": fear_greed}

    def calculate_confidence(self, technical: Dict[str, Any], sentiment: Dict[str, Any], patterns: Dict[str, Any]) -> float:
        """Combine different signals into a simple confidence score in [0,1]."""
        t = technical.get("composite_score", 0)
        s = (sentiment.get("overall_sentiment") or 0) / 100.0 if isinstance(sentiment.get("overall_sentiment"), (int, float)) else 0
        p = patterns.get("confidence", 0) if isinstance(patterns.get("confidence"), (int, float)) else 0
        # Weighted average with fallbacks
        try:
            conf = 0.6 * float(t) + 0.2 * float(s) + 0.2 * float(p)
            return float(max(0.0, min(1.0, conf)))
        except Exception:
            return 0.0

    def _parse_llm_response(self, text: str) -> Dict[str, Any]:
        """Loose parsing of an LLM response to extract action and confidence.

        Looks for BUY/SELL/HOLD tokens and optional numeric confidence.
        """
        if not text:
            return {"action": "HOLD", "confidence": 0.0, "reason": None}

        text_upper = text.upper()
        action = "HOLD"
        if "BUY" in text_upper and "SELL" not in text_upper:
            action = "BUY"
        elif "SELL" in text_upper and "BUY" not in text_upper:
            action = "SELL"
        elif "HOLD" in text_upper:
            action = "HOLD"

        # Find first percentage-like number
        match = re.search(r"(\d{1,3}(?:\.\d+)?)[ ]?%", text)
        confidence = None
        if match:
            try:
                confidence = float(match.group(1)) / 100.0
            except Exception:
                confidence = None

        reason = text.strip()
        return {"action": action, "confidence": (confidence if confidence is not None else 0.0), "reason": reason}

    def _fallback_analysis(self, technical: Dict[str, Any], sentiment: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based fallback when LLM is unavailable or fails."""
        score = technical.get("composite_score", 0)
        pattern_conf = patterns.get("confidence", 0)

        # Basic rules:
        if score > 0.65 or pattern_conf > 0.6:
            return {"action": "BUY", "confidence": min(0.95, 0.5 + score * 0.5), "reason": "technical+pattern"}
        if score < 0.35 and pattern_conf < 0.4:
            return {"action": "SELL", "confidence": min(0.9, 0.5 + (1 - score) * 0.4), "reason": "weakness"}
        return {"action": "HOLD", "confidence": 0.5, "reason": "neutral"}
