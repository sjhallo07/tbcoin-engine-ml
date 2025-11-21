from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from .feature_engineering import BlockchainFeatureEngineer, FeatureEngineeringError


@dataclass(slots=True)
class PredictionSummary:
    """Metadata captured during a prediction cycle."""

    mae: float
    confidence: float
    recommendation: str
    supporting_signals: Dict[str, Any]


class LSTMRegressor(BaseEstimator, RegressorMixin):
    """Minimal Keras-backed LSTM wrapped as an sklearn estimator."""

    def __init__(self, input_shape: tuple[int, int], epochs: int = 50, batch_size: int = 32, patience: int = 5) -> None:
        self.input_shape = input_shape
        self.epochs = epochs
        self.batch_size = batch_size
        self.patience = patience
        self._model = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LSTMRegressor":
        try:
            from tensorflow import keras
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("TensorFlow is required for LSTMRegressor") from exc

        model = keras.Sequential(
            [
                keras.layers.Input(shape=self.input_shape),
                keras.layers.LSTM(128, return_sequences=True),
                keras.layers.Dropout(0.2),
                keras.layers.LSTM(64),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mae")
        early_stop = keras.callbacks.EarlyStopping(monitor="val_loss", patience=self.patience, restore_best_weights=True)
        model.fit(
            X,
            y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=0,
            validation_split=0.2,
            callbacks=[early_stop],
            shuffle=False,
        )
        self._model = model
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("Model has not been trained")
        predictions = self._model.predict(X, verbose=0)
        return predictions.reshape(-1)


class PredictiveBlockchainAI:
    """Coordinates feature engineering, model training, and inference for blockchain analytics."""

    def __init__(
        self,
        price_history: pd.DataFrame,
        *,
        feature_engineer: Optional[BlockchainFeatureEngineer] = None,
        config: Optional[Mapping[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._price_history = price_history
        self._feature_engineer = feature_engineer or BlockchainFeatureEngineer()
        self._config = config or {}
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._trained_models: Dict[str, Any] = {}
        self._inference_frame: Optional[pd.DataFrame] = None
        self._latest_summary: Optional[PredictionSummary] = None

    def train_price_prediction_model(self) -> BaseEstimator:
        """Train an LSTM-based regressor for price prediction with backtesting feedback."""
        try:
            enriched = self._feature_engineer.create_technical_indicators(self._price_history)
        except FeatureEngineeringError as exc:
            raise RuntimeError("Unable to engineer features for price model") from exc

        target_column = self._config.get("target_column", "close")
        lookback = int(self._config.get("lookback_window", 30))
        forecast_horizon = int(self._config.get("forecast_horizon", 1))

        if target_column not in enriched:
            raise RuntimeError(f"Target column '{target_column}' missing from enriched dataset")

        features = enriched.drop(columns=[target_column])
        target = enriched[target_column].shift(-forecast_horizon).dropna()
        features = features.loc[target.index]

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        sequences, labels = self._build_sequences(scaled_features, target.to_numpy(), lookback)
        if sequences.size == 0:
            raise RuntimeError("Insufficient data to build training sequences")

        lstm = LSTMRegressor(input_shape=(sequences.shape[1], sequences.shape[2]))
        lstm.fit(sequences, labels)

        tscv = TimeSeriesSplit(n_splits=min(5, len(sequences) - 1))
        mae_scores = []
        for train_idx, test_idx in tscv.split(sequences):
            model = LSTMRegressor(input_shape=(sequences.shape[1], sequences.shape[2]))
            model.fit(sequences[train_idx], labels[train_idx])
            preds = model.predict(sequences[test_idx])
            mae_scores.append(mean_absolute_error(labels[test_idx], preds))

        avg_mae = float(np.mean(mae_scores)) if mae_scores else float("nan")
        self._trained_models["price_prediction"] = lstm
        self._trained_models["price_scaler"] = scaler
        self._trained_models["lookback"] = lookback
        self._trained_models["mae"] = avg_mae
        return lstm

    def predict_optimal_transaction_timing(self) -> Dict[str, Any]:
        """Suggest an optimal execution window based on trained models and current metrics."""
        if "price_prediction" not in self._trained_models:
            raise RuntimeError("Price model not trained")
        if self._inference_frame is None or self._inference_frame.empty:
            raise RuntimeError("Inference features not set; call 'update_inference_frame' first")

        lookback = int(self._trained_models["lookback"])
        scaler: StandardScaler = self._trained_models["price_scaler"]  # type: ignore[assignment]
        model: LSTMRegressor = self._trained_models["price_prediction"]  # type: ignore[assignment]

        frame = self._inference_frame.copy().sort_index()
        if len(frame) < lookback:
            raise RuntimeError("Not enough inference samples for prediction")

        feature_matrix = scaler.transform(frame.to_numpy())
        latest_sequence = self._build_sequences(feature_matrix, np.zeros(len(feature_matrix)), lookback)[0][-1]
        prediction = float(model.predict(latest_sequence[np.newaxis, ...])[0])

        current_price = float(self._price_history[self._config.get("target_column", "close")].iat[-1])
        expected_move = prediction - current_price
        confidence = max(0.0, 1.0 - abs(expected_move) / max(current_price, 1e-9))
        recommendation = "delay" if expected_move < 0 else "execute"

        summary = PredictionSummary(
            mae=float(self._trained_models.get("mae", float("nan"))),
            confidence=confidence,
            recommendation=recommendation,
            supporting_signals={
                "expected_move": expected_move,
                "predicted_price": prediction,
                "current_price": current_price,
            },
        )
        self._latest_summary = summary
        return {
            "prediction": prediction,
            "current_price": current_price,
            "expected_move": expected_move,
            "confidence": confidence,
            "recommendation": recommendation,
            "mae": summary.mae,
            "lookback": lookback,
        }

    def update_inference_frame(self, feature_frame: pd.DataFrame) -> None:
        """Provide up-to-date engineered features for online inference."""
        if feature_frame.empty:
            raise ValueError("Feature frame must not be empty")
        self._inference_frame = feature_frame

    @staticmethod
    def _build_sequences(features: np.ndarray, target: np.ndarray, lookback: int) -> tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for idx in range(lookback, len(features)):
            X.append(features[idx - lookback : idx])
            if target.size > idx:
                y.append(target[idx])
        return np.asarray(X), np.asarray(y)

    @property
    def latest_summary(self) -> Optional[PredictionSummary]:
        return self._latest_summary
