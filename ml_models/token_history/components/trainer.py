from __future__ import annotations

from typing import Dict, Any
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore

from .models import TokenMovementTransformer


class HistoricalModelTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device(config.get("device", "cpu")) if TORCH_AVAILABLE else None

    def train_with_numpy(self, train_seq: np.ndarray, val_seq: np.ndarray):
        """Minimal trainer that builds a model and runs one dummy pass.

        Intended as a placeholder to keep the pipeline runnable.
        """
        model = TokenMovementTransformer(self.config)
        if TORCH_AVAILABLE and hasattr(model, "to"):
            model = model.to(self.device)  # type: ignore[attr-defined]
        # Create dummy batch tensors from numpy sequences
        if train_seq.size == 0:
            return model
        # Infer num_features from flattened sequence window size
        flat_len = train_seq.shape[1]
        num_features = self.config.get("num_features", 16)
        seq_len = max(1, flat_len // num_features)
        if TORCH_AVAILABLE:
            batch = torch.tensor(train_seq[:, : seq_len * num_features], dtype=torch.float32).view(-1, seq_len, num_features)
            outputs = model(batch.to(self.device))  # type: ignore[call-arg]
            # Dummy loss
            loss = outputs["amount"] if isinstance(outputs["amount"], torch.Tensor) else None
            if loss is not None:
                loss = loss.mean() * 0.0
                loss.backward()
        else:
            # No-op pass in torch-less mode
            _ = model(train_seq[:, : seq_len * num_features])
        return model
