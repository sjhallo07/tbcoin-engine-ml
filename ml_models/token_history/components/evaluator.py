from __future__ import annotations

from typing import Dict, Any
import numpy as np


class HistoricalModelEvaluator:
    def evaluate_numpy_model(self, model, test_seq: np.ndarray) -> Dict[str, Any]:
        if test_seq.size == 0:
            return {"samples": 0, "status": "no_test_data"}
        return {"samples": int(len(test_seq)), "status": "ok"}
