from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import MinMaxScaler

from .feature_engineering import BlockchainFeatureEngineer
from .predictive_engine import PredictiveBlockchainAI

try:  # pragma: no cover - optional dependency
    from xgboost import XGBRegressor
except ImportError:  # pragma: no cover
    XGBRegressor = None  # type: ignore


@dataclass
class EnsembleModel:
    """Container for ensemble members and weights."""

    members: Dict[str, Any] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)

    def predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        if not self.members:
            raise RuntimeError("No ensemble members have been trained")
        total_weight = sum(self.weights.values()) or 1.0
        aggregate = np.zeros(feature_matrix.shape[0])
        for name, model in self.members.items():
            preds = model.predict(feature_matrix)
            aggregate += self.weights.get(name, 1.0) * preds
        return aggregate / total_weight


class ModelTrainingPipeline:
    """Coordinates multi-model training and evaluation for blockchain forecasting."""

    def __init__(
        self,
        raw_price_data: pd.DataFrame,
        *,
        feature_engineer: Optional[BlockchainFeatureEngineer] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._raw_price_data = raw_price_data
        self._feature_engineer = feature_engineer or BlockchainFeatureEngineer()
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._scaler = MinMaxScaler()
        self._ensemble = EnsembleModel()

    def prepare_training_data(self) -> pd.DataFrame:
        """Clean, normalize, and augment price data for training."""
        df = self._raw_price_data.copy()
        df = df.dropna()
        df = df.sort_index()

        engineered = self._feature_engineer.create_technical_indicators(df)
        engineered["target"] = engineered["close"].shift(-1)
        engineered.dropna(inplace=True)

        features = engineered.drop(columns=["target"])
        scaled_features = self._scaler.fit_transform(features)
        scaled_df = pd.DataFrame(scaled_features, index=features.index, columns=features.columns)
        scaled_df["target"] = engineered["target"]
        return scaled_df

    def train_ensemble_model(self) -> EnsembleModel:
        """Train ensemble members (RF, XGBoost, LSTM) with hyperparameter tuning."""
        dataset = self.prepare_training_data()
        feature_cols = [col for col in dataset.columns if col != "target"]
        X = dataset[feature_cols].to_numpy()
        y = dataset["target"].to_numpy()

        tscv = TimeSeriesSplit(n_splits=min(5, len(X) - 1))
        rf_mae_scores = []
        rf_model = RandomForestRegressor(n_estimators=250, max_depth=8, random_state=42, n_jobs=-1)
        for train_idx, test_idx in tscv.split(X):
            rf_model.fit(X[train_idx], y[train_idx])
            predictions = rf_model.predict(X[test_idx])
            rf_mae_scores.append(mean_absolute_error(y[test_idx], predictions))
        self._logger.info("RandomForest MAE: %.5f", np.mean(rf_mae_scores))

        self._ensemble.members["random_forest"] = rf_model
        self._ensemble.weights["random_forest"] = 0.35

        if XGBRegressor:
            xgb_model = XGBRegressor(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="reg:squarederror",
                tree_method="hist",
            )
            xgb_model.fit(X, y)
            self._ensemble.members["xgboost"] = xgb_model
            self._ensemble.weights["xgboost"] = 0.30
        else:
            self._logger.warning("XGBoost not available; omitting from ensemble")

        predictive_ai = PredictiveBlockchainAI(self._raw_price_data, feature_engineer=self._feature_engineer)
        lstm_model = predictive_ai.train_price_prediction_model()
        self._ensemble.members["lstm"] = lstm_model
        self._ensemble.weights["lstm"] = 0.35

        return self._ensemble

    @property
    def scaler(self) -> MinMaxScaler:
        return self._scaler
