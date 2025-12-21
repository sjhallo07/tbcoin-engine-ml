from __future__ import annotations

import numpy as np
import pandas as pd


class TemporalFeatureEngineer:
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # Cyclical features
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        # Inter-transaction intervals
        df = df.sort_values("block_timestamp").copy()
        df["time_since_last_tx"] = (
            df["block_timestamp"].diff().dt.total_seconds().fillna(0.0)
        )
        return df
