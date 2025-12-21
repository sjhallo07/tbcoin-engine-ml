from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd


class SequenceGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.sequence_length = int(config.get("sequence_length", 128))
        self.stride = int(config.get("stride", 1))
        self.min_sequence_length = int(config.get("min_sequence_length", 10))

    def create_sequences(self, df: pd.DataFrame, token_address: str) -> Dict[str, Any]:
        if df.empty:
            return {"sequences": np.array([]), "labels": np.array([]), "metadata": []}
        sequences = []
        labels = []
        metadata = []
        df = df.sort_values("block_timestamp")
        for address in df["from_address"].unique():
            address_df = df[df["from_address"] == address].copy()
            if len(address_df) < self.min_sequence_length:
                continue
            for i in range(0, len(address_df) - self.sequence_length, self.stride):
                seq = address_df.iloc[i : i + self.sequence_length]
                seq_features = self._sequence_features(seq)
                if i + self.sequence_length < len(address_df):
                    next_tx = address_df.iloc[i + self.sequence_length]
                    label = self._label(next_tx)
                    sequences.append(seq_features)
                    labels.append(label)
                    metadata.append({
                        "address": address,
                        "start_time": seq.iloc[0]["block_timestamp"],
                        "end_time": seq.iloc[-1]["block_timestamp"],
                    })
        return {
            "sequences": np.array(sequences),
            "labels": np.array(labels),
            "metadata": metadata,
        }

    def _sequence_features(self, seq_df: pd.DataFrame) -> np.ndarray:
        tx_features = seq_df[[
            "amount",
            "amount_usd",
            "time_since_last_tx",
            "hour_sin",
            "hour_cos",
            "gas_price",
        ]].values
        agg_features = [
            float(seq_df["amount"].mean()),
            float(seq_df["amount"].std() or 0.0),
            float(seq_df["time_since_last_tx"].mean()),
            float(seq_df["time_since_last_tx"].std() or 0.0),
            float(len(seq_df["to_address"].unique())),
            float(seq_df["amount"].sum()),
        ]
        return np.concatenate([tx_features.flatten(), np.array(agg_features, dtype=float)])

    def _label(self, next_tx: pd.Series) -> np.ndarray:
        return np.array([
            float(next_tx["amount"]),
            float(next_tx["gas_price"]),
            float(next_tx["block_timestamp"].value),  # ns timestamp placeholder
        ], dtype=float)
