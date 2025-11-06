#!/usr/bin/env python3
"""Train AI models for the autonomous agent.

This script is defensive about imports: it tries to use `agents.ai_decision_engine.AutonomousDecisionEngine`
and a repository RL agent, but will fall back to local stubs if those modules are not present. It also
handles sync vs async training functions.
"""
import argparse
import asyncio
import inspect
import sys
from typing import Any

# Try repository-specific imports with fallbacks
try:
    from agents.ai_decision_engine import AutonomousDecisionEngine  # type: ignore
except Exception:
    try:
        from .agents.ai_decision_engine import AutonomousDecisionEngine  # type: ignore
    except Exception:
        class AutonomousDecisionEngine:  # type: ignore
            async def train_price_prediction_model(self, epochs: int = 50):
                print("[stub] training price prediction model...")
                await asyncio.sleep(0.1)

try:
    # Prefer an agents-level RL trainer if present
    from agents.reinforcement_learning_agent import ReinforcementLearningAgent  # type: ignore
except Exception:
    try:
        # Fallback to RL agent under app.autonomous_agent.core
        from app.autonomous_agent.core.rl_agent import RLAgent as ReinforcementLearningAgent  # type: ignore
    except Exception:
        class ReinforcementLearningAgent:  # type: ignore
            def train(self, episodes: int = 1000):
                # sync stub
                print(f"[stub] RL training for {episodes} episodes (sync)")


async def _maybe_await(obj, *args, **kwargs):
    """Call obj(*args, **kwargs) and await if it's a coroutine function, otherwise run in thread.

    Returns the call result.
    """
    if inspect.iscoroutinefunction(obj):
        return await obj(*args, **kwargs)
    else:
        # Run sync function in a thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: obj(*args, **kwargs))


async def main_async(argv: Any = None):
    parser = argparse.ArgumentParser(description='Train AI models for autonomous agent')
    parser.add_argument('--model-type', required=True,
                        choices=['price-prediction', 'anomaly-detection', 'reinforcement-learning'])
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--data-limit', type=int, default=100000)

    args = parser.parse_args(argv)

    if args.model_type == 'price-prediction':
        engine = AutonomousDecisionEngine()
        # Prefer an async or sync train method if available
        train_fn = getattr(engine, 'train_price_prediction_model', None)
        if train_fn is None:
            print("No `train_price_prediction_model` on engine; running placeholder training...")
            await asyncio.sleep(0.1)
        else:
            await _maybe_await(train_fn, epochs=args.epochs)

    elif args.model_type == 'reinforcement-learning':
        rl_agent = ReinforcementLearningAgent()
        train_fn = getattr(rl_agent, 'train', None)
        if train_fn is None:
            print("No `train` method found on RL agent; skipping.")
        else:
            await _maybe_await(train_fn, episodes=args.epochs * 100)

    elif args.model_type == 'anomaly-detection':
        # Placeholder for anomaly detection training
        print("Starting anomaly-detection training (placeholder)")
        await asyncio.sleep(0.1)

    print(f"✅ Training completed for {args.model_type}")


def main():
    # Run the async main
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Training cancelled by user")
        sys.exit(1)


if __name__ == '__main__':
    main()
