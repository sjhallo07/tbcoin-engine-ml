"""StrategyEvolver

Evolves trading strategies using a genetic algorithm when DEAP is available, otherwise
falls back to a lightweight random-search-based optimizer so the module remains usable
in minimal environments.

Public class: StrategyEvolver
"""
from __future__ import annotations

import asyncio
import random
import math
from typing import Dict, Any, Optional

# Optional dependencies
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # type: ignore

try:
    from deap import base, creator, tools, algorithms  # type: ignore
    _DEAP_AVAILABLE = True
except Exception:
    _DEAP_AVAILABLE = False


class StrategyEvolver:
    def __init__(self):
        self.strategy_pool = self._initialize_strategy_pool()

    def _initialize_strategy_pool(self) -> Dict[str, Dict[str, Any]]:
        """Initialize diverse trading strategies with default hyperparameters."""
        return {
            "mean_reversion": {
                "rsi_period": 14,
                "oversold_threshold": 30,
                "overbought_threshold": 70,
                "position_size": 0.1,
                "weight": 0.25,
            },
            "momentum": {
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "momentum_period": 10,
                "weight": 0.25,
            },
            "breakout": {
                "support_resistance_period": 20,
                "breakout_confirmation_bars": 2,
                "volatility_threshold": 0.02,
                "weight": 0.25,
            },
            "volume_profile": {
                "volume_sma_period": 20,
                "volume_spike_threshold": 2.0,
                "price_volume_confirmation": True,
                "weight": 0.25,
            },
        }

    async def evolve_strategies(self, market_regime: str, performance_data: Optional[Any] = None) -> float:
        """Evolve trading strategies and update the strategy pool.

        If DEAP is available and `performance_data` looks like a DataFrame, use a GA. Otherwise
        run a lightweight random search to propose improvements.

        Returns the fitness (float) of the best found strategy.
        """
        # If DEAP is available and user provided DataFrame-like data, prefer GA
        if _DEAP_AVAILABLE and pd is not None and isinstance(performance_data, pd.DataFrame):
            return await self._run_deap_ga(performance_data)
        else:
            # Fallback optimizer: random search
            return await self._run_random_search(performance_data)

    async def _run_deap_ga(self, performance_data: "pd.DataFrame") -> float:  # type: ignore
        """Run a DEAP-based genetic algorithm to evolve parameter sets.

        This is a minimal example: it builds individuals from a flattened vector of numeric
        parameters and evaluates using `_calculate_strategy_fitness`.
        """
        # Build a parameter template from current strategies (flatten numeric params)
        params, bounds = self._flatten_strategy_params()

        # DEAP setup
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        # Attribute generator within bounds
        def _attr(i):
            lo, hi = bounds[i]
            return random.uniform(lo, hi)

        for i in range(len(params)):
            toolbox.register(f"attr_{i}", lambda idx=i: _attr(idx))

        toolbox.register("individual", tools.initCycle, creator.Individual, [toolbox.register], n=1)  # placeholder

        # Instead create individuals manually
        def gen_individual():
            return creator.Individual([_attr(i) for i in range(len(params))])

        toolbox.register("population", tools.initRepeat, list, gen_individual)

        def evaluate(individual):
            # Map individual back to strategy dict and compute fitness
            strategy_cfg = self._unflatten_to_strategy(individual, params)
            fitness = self._calculate_strategy_fitness(strategy_cfg, performance_data)
            return (fitness,)

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        pop_size = 30
        ngen = 20

        pop = toolbox.population(n=pop_size)

        # Run evolution (synchronous blocking call); wrap in thread to not block event loop
        def _ea():
            algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=ngen, verbose=False)
            best = tools.selBest(pop, 1)[0]
            return best

        best_individual = await asyncio.to_thread(_ea)
        best_strategy = self._unflatten_to_strategy(best_individual, params)
        best_fitness = float(best_individual.fitness.values[0])

        # Update pool weights from best strategy (best-effort async)
        await self._update_strategy_weights(best_strategy)
        return best_fitness

    async def _run_random_search(self, performance_data: Optional[Any]) -> float:
        """Fallback random search: perturb existing strategies and keep best candidate."""
        iterations = 100
        best_cfg = None
        best_score = float("-inf")

        base_params, _ = self._flatten_strategy_params()

        for _ in range(iterations):
            candidate = self._random_perturb()
            score = self._calculate_strategy_fitness(candidate, performance_data)
            if score > best_score:
                best_score = score
                best_cfg = candidate

        if best_cfg is not None:
            await self._update_strategy_weights(best_cfg)
        return float(best_score)

    def _flatten_strategy_params(self):
        """Flatten strategy parameters into a list of (name, value) and bounds for numeric params.

        Returns (params, bounds) where params is a list of tuples (strategy_name, param_name, value)
        and bounds is a list of (lo, hi) per numeric parameter.
        """
        params = []
        bounds = []
        for sname, cfg in self.strategy_pool.items():
            for pname, pval in cfg.items():
                if isinstance(pval, (int, float)) and pname != "weight":
                    params.append((sname, pname, float(pval)))
                    # Create generic bounds around the parameter
                    lo = float(pval) * 0.5 if pval != 0 else -1.0
                    hi = float(pval) * 1.5 if pval != 0 else 1.0
                    # Ensure sensible bounds
                    if lo == hi:
                        lo -= 1.0
                        hi += 1.0
                    bounds.append((lo, hi))
        return params, bounds

    def _unflatten_to_strategy(self, individual, params_template):
        """Map a flattened individual (list of numbers) back to a nested strategy config dict."""
        strategy_cfg = {k: dict(v) for k, v in self.strategy_pool.items()}  # shallow copy
        for idx, val in enumerate(individual):
            sname, pname, _ = params_template[idx]
            # Assign numeric value back
            strategy_cfg[sname][pname] = float(val)
        return strategy_cfg

    def _random_perturb(self) -> Dict[str, Any]:
        """Create a random candidate by perturbing current pool parameters."""
        candidate = {k: dict(v) for k, v in self.strategy_pool.items()}
        for sname, cfg in candidate.items():
            for pname, pval in cfg.items():
                if isinstance(pval, (int, float)) and pname != "weight":
                    # Perturb by up to +/-20%
                    factor = random.uniform(0.8, 1.2)
                    candidate[sname][pname] = float(pval) * factor
        return candidate

    def _calculate_strategy_fitness(self, strategy_cfg: Dict[str, Any], performance_data: Optional[Any]) -> float:
        """Compute a fitness score for a strategy configuration given historical performance data.

        If `performance_data` is a DataFrame that contains a 'return' column, compute a simple
        risk-adjusted return (mean / std). Otherwise return a heuristic score derived from the
        parameter values to allow the optimizer to make progress.
        """
        try:
            if pd is not None and isinstance(performance_data, pd.DataFrame) and not performance_data.empty:
                # Simple proxy: mean return / volatility across performance_data
                returns = performance_data.get("return") if "return" in performance_data else performance_data.iloc[:, 0]
                mean = float(returns.mean())
                vol = float(returns.std()) if float(returns.std()) > 0 else 1e-6
                sharpe = mean / vol
                # Bonus if parameters indicate more aggressive sizing
                size_bonus = 0.0
                for sname, cfg in strategy_cfg.items():
                    pos = cfg.get("position_size") or cfg.get("position_size", 0)
                    try:
                        size_bonus += float(pos) * 0.1
                    except Exception:
                        pass
                return float(sharpe + size_bonus)
            else:
                # Heuristic scoring: prefer moderate parameter magnitudes (avoid extreme values)
                score = 0.0
                for sname, cfg in strategy_cfg.items():
                    for pname, pval in cfg.items():
                        if isinstance(pval, (int, float)):
                            score -= abs(math.log1p(abs(pval)))  # penalize large values
                # Add small randomness to break ties
                score += random.uniform(-0.1, 0.1)
                return float(score)
        except Exception:
            return float(-1e6)

    async def _update_strategy_weights(self, best_strategy: Dict[str, Any]) -> None:
        """Update the internal strategy_pool weights based on a best strategy candidate.

        This is a simple heuristic: increase the weight of strategies that appear in the best
        configuration and normalize weights to sum to 1.
        """
        # Increase weight for strategies that improved
        for sname in self.strategy_pool.keys():
            if sname in best_strategy:
                self.strategy_pool[sname]["weight"] = min(0.9, self.strategy_pool[sname].get("weight", 0.0) + 0.05)

        # Normalize
        total = sum(cfg.get("weight", 0.0) for cfg in self.strategy_pool.values())
        if total <= 0:
            # Reset to equal weights
            n = len(self.strategy_pool)
            for cfg in self.strategy_pool.values():
                cfg["weight"] = 1.0 / n
            return

        for cfg in self.strategy_pool.values():
            cfg["weight"] = float(cfg.get("weight", 0.0) / total)

        await asyncio.to_thread(print, f"Updated strategy weights: { {k: v['weight'] for k, v in self.strategy_pool.items()} }")


# Demo when run directly
if __name__ == "__main__":
    async def _demo():
        evolver = StrategyEvolver()
        # Run random-search demo
        best = await evolver.evolve_strategies("bull", None)
        print("Best fitness (demo):", best)

    asyncio.run(_demo())
