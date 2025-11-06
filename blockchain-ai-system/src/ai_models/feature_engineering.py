from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas as pd


class FeatureEngineeringError(RuntimeError):
    """Raised when a feature engineering step fails."""


class BlockchainFeatureEngineer:
    """Generates market, technical, and network-level features for modeling."""

    def __init__(self, *, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def create_technical_indicators(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Augment OHLCV price data with common technical indicators."""
        required_columns = {"close", "high", "low", "volume"}
        missing_columns = required_columns - set(price_data.columns)
        if missing_columns:
            raise FeatureEngineeringError(f"Missing columns for technical indicators: {missing_columns}")

        df = price_data.copy().sort_index()
        df["returns"] = df["close"].pct_change()

        self._logger.debug("Calculating RSI")
        df["rsi_14"] = self._relative_strength_index(df["close"], period=14)

        self._logger.debug("Calculating MACD")
        macd_line, signal_line = self._moving_average_convergence_divergence(df["close"], fast=12, slow=26, signal=9)
        df["macd_line"] = macd_line
        df["macd_signal"] = signal_line

        self._logger.debug("Calculating Bollinger Bands")
        bb_mid, bb_upper, bb_lower = self._bollinger_bands(df["close"], window=20, num_std=2)
        df["bb_mid"] = bb_mid
        df["bb_upper"] = bb_upper
        df["bb_lower"] = bb_lower

        df["rolling_volume_z"] = self._rolling_zscore(df["volume"], window=20)
        df["price_momentum_7"] = df["close"].pct_change(periods=7)
        df["price_momentum_30"] = df["close"].pct_change(periods=30)

        for lag in (1, 3, 5, 10):
            df[f"close_lag_{lag}"] = df["close"].shift(lag)
            df[f"volume_lag_{lag}"] = df["volume"].shift(lag)

        df.dropna(inplace=True)
        return df

    def create_network_metrics(self, blockchain_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform network-level telemetry into modeling features."""
        metrics = blockchain_data.get("metrics", {})
        history: Iterable[Dict[str, Any]] = blockchain_data.get("history", [])

        if not isinstance(metrics, dict):
            raise FeatureEngineeringError("'metrics' entry must be a dictionary")

        records = []
        for sample in history:
            try:
                record = {
                    "timestamp": pd.to_datetime(sample["timestamp"], utc=True),
                    "transaction_velocity": self._transaction_velocity(sample),
                    "active_address_growth": self._active_address_growth(sample),
                    "network_health": self._network_health_score(sample),
                    "mean_fee": float(sample.get("mean_fee", 0.0)),
                    "median_fee": float(sample.get("median_fee", 0.0)),
                }
                records.append(record)
            except KeyError as exc:
                self._logger.warning("Skipping malformed network sample: missing %s", exc)

        df = pd.DataFrame(records).set_index("timestamp") if records else pd.DataFrame(columns=["transaction_velocity", "active_address_growth", "network_health", "mean_fee", "median_fee"])

        if not df.empty:
            df["network_health_ema"] = df["network_health"].ewm(span=10).mean()
            df["velocity_z"] = self._rolling_zscore(df["transaction_velocity"], window=15)

        return df

    @staticmethod
    def _relative_strength_index(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = losses.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(to_replace=0, value=np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.bfill()

    @staticmethod
    def _moving_average_convergence_divergence(series: pd.Series, fast: int, slow: int, signal: int) -> tuple[pd.Series, pd.Series]:
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def _bollinger_bands(series: pd.Series, window: int, num_std: int) -> tuple[pd.Series, pd.Series, pd.Series]:
        rolling_mean = series.rolling(window).mean()
        rolling_std = series.rolling(window).std()
        upper_band = rolling_mean + num_std * rolling_std
        lower_band = rolling_mean - num_std * rolling_std
        return rolling_mean, upper_band, lower_band

    @staticmethod
    def _rolling_zscore(series: pd.Series, window: int) -> pd.Series:
        rolling_mean = series.rolling(window).mean()
        rolling_std = series.rolling(window).std()
        return (series - rolling_mean) / rolling_std.replace(to_replace=0, value=np.nan)

    @staticmethod
    def _transaction_velocity(sample: Dict[str, Any]) -> float:
        tx_volume = float(sample.get("transaction_volume", 0.0))
        value_locked = float(sample.get("total_value_locked", 1.0))
        return tx_volume / value_locked if value_locked else 0.0

    @staticmethod
    def _active_address_growth(sample: Dict[str, Any]) -> float:
        active_addresses = float(sample.get("active_addresses", 0.0))
        prev_active = float(sample.get("previous_active_addresses", active_addresses or 1.0))
        if prev_active == 0:
            return 0.0
        return (active_addresses - prev_active) / prev_active

    @staticmethod
    def _network_health_score(sample: Dict[str, Any]) -> float:
        uptime = float(sample.get("uptime", 0.0))
        failure_rate = float(sample.get("failure_rate", 0.0))
        decentralization = float(sample.get("decentralization_index", 0.0))
        score = 0.5 * uptime + 0.3 * decentralization - 0.2 * failure_rate
        return max(min(score, 1.0), 0.0)
