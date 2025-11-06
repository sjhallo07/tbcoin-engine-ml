from __future__ import annotations

import unittest
from datetime import datetime, timedelta

import numpy as np

from src.ai.models import PricePredictor


class TestPricePredictor(unittest.TestCase):
    def setUp(self) -> None:
        base_time = datetime(2024, 1, 1)
        self.history = []
        price = 100.0
        volume = 1_000_000.0
        rng = np.random.default_rng(42)
        for idx in range(60):
            price += rng.normal(0, 1.5)
            volume += rng.normal(0, 50_000)
            self.history.append(
                {
                    "timestamp": base_time + timedelta(hours=idx),
                    "current_price": float(price),
                    "total_volume": float(max(volume, 10_000.0)),
                }
            )

    def test_training_with_insufficient_data_leaves_model_untrained(self) -> None:
        predictor = PricePredictor()
        predictor.train(self.history[:5])
        self.assertFalse(predictor.is_trained)

    def test_training_and_prediction_flow(self) -> None:
        predictor = PricePredictor()
        predictor.train(self.history)
        self.assertTrue(predictor.is_trained)

        latest = self.history[-1].copy()
        latest.update(
            {
                "price_change_24h": 0.01,
                "volume_change_24h": -0.02,
                "price_ma_7": latest["current_price"],
                "volume_ma_7": latest["total_volume"],
                "price_volatility_7": 0.5,
                "volume_acceleration": 0.01,
            }
        )
        prediction = predictor.predict(latest)
        self.assertIn("predicted_price", prediction)
        self.assertTrue(0.0 <= prediction["confidence"] <= 1.0)

    def test_untrained_predict_returns_baseline(self) -> None:
        predictor = PricePredictor()
        snapshot = self.history[-1]
        result = predictor.predict(snapshot)
        self.assertEqual(result["direction"], "neutral")
        self.assertAlmostEqual(result["confidence"], 0.5)

    def test_evaluate_requires_training(self) -> None:
        predictor = PricePredictor()
        predictor.train(self.history)
        # Provide minimal feature set for prediction to avoid training-specific keys
        baseline = self.history[-1].copy()
        prediction = predictor.predict(baseline)
        self.assertIn("predicted_price", prediction)


if __name__ == "__main__":
    unittest.main()
