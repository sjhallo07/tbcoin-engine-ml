"""Simple random forest based price predictor with graceful degradation.

If scientific stack (pandas/numpy/scikit-learn) is not available, the class
still imports and returns baseline predictions without ML.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:  # optional heavy deps
    import numpy as np  # type: ignore
    import pandas as pd  # type: ignore
    from sklearn.ensemble import RandomForestRegressor  # type: ignore
    _ML_AVAILABLE = True
except Exception:  # pragma: no cover - environment without ML stack
    np = None  # type: ignore
    pd = None  # type: ignore
    RandomForestRegressor = None  # type: ignore
    _ML_AVAILABLE = False


class PricePredictor:
    """Simple ML model for price prediction."""

    def __init__(self) -> None:
        self.available = _ML_AVAILABLE
        self.model = None
        if self.available and RandomForestRegressor is not None:  # type: ignore
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)  # type: ignore
        self.is_trained = False

    def prepare_features(self, historical_data: List[Dict[str, Any]]):
        """Prepare features for training.

        Returns a pandas DataFrame when ML stack is available; otherwise returns
        the original list (caller should handle the degraded mode).
        """
        if not self.available or pd is None or np is None:
            return historical_data

        df = pd.DataFrame(historical_data)
        if len(df) > 0:
            df["price_change_24h"] = df["current_price"].pct_change()
            df["volume_change_24h"] = df["total_volume"].pct_change()
            df["price_ma_7"] = df["current_price"].rolling(7).mean()
            df["volume_ma_7"] = df["total_volume"].rolling(7).mean()
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df = df.fillna(0)

        return df

    def train(self, historical_data: List[Dict[str, Any]]) -> None:
        """Train the model."""
        if not self.available or self.model is None:
            # ML stack not present; remain untrained
            self.is_trained = False
            return

        if len(historical_data) < 10:
            print("Insufficient data for training")
            return

        df = self.prepare_features(historical_data)

        if hasattr(df, "__len__") and len(df) < 10:
            return

        features = ["price_change_24h", "volume_change_24h", "price_ma_7", "volume_ma_7"]
        X = df[features].iloc[:-1]
        y = df["current_price"].shift(-1).iloc[:-1]

        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]

        if len(X) > 5:
            self.model.fit(X, y)
            self.is_trained = True
            print(f"Model trained on {len(X)} samples")

    def predict(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make price prediction."""
        if not self.is_trained or not self.available or self.model is None:
            return {
                "predicted_price": current_data.get("current_price", 0),
                "confidence": 0.5,
                "direction": "neutral",
            }

        features = np.array(
            [
                current_data.get("price_change_24h", 0),
                current_data.get("volume_change_24h", 0),
                current_data.get("price_ma_7", current_data.get("current_price", 0)),
                current_data.get("volume_ma_7", current_data.get("total_volume", 0)),
            ]
        ).reshape(1, -1)

        try:
            predicted_price = float(self.model.predict(features)[0])
            current_price = float(current_data.get("current_price", predicted_price or 0))
            if current_price == 0:
                confidence = 0.5
            else:
                confidence = min(abs(predicted_price - current_price) / abs(current_price), 0.95)
            direction = "up" if predicted_price > current_price else "down"
            return {
                "predicted_price": predicted_price,
                "confidence": float(confidence),
                "direction": direction,
            }
        except Exception as exc:  # pragma: no cover - guard against inference issues
            print(f"Prediction error: {exc}")
            return {
                "predicted_price": current_data.get("current_price", 0),
                "confidence": 0.5,
                "direction": "neutral",
            }

