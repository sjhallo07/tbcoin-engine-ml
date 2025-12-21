from __future__ import annotations

import numpy as np
import pandas as pd


BLACKLISTED_ADDRESSES: set[str] = set()
MAX_TOKEN_SUPPLY: float = 1e12


class DataPreprocessor:
    def clean_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # 1. Drop duplicates
        df = df.drop_duplicates(subset=["transaction_hash", "log_index"])  # type: ignore
        # 2. Filter invalid addresses
        df = df[~df["from_address"].isin(BLACKLISTED_ADDRESSES)]
        df = df[~df["to_address"].isin(BLACKLISTED_ADDRESSES)]
        # 3. Validate amounts
        df = df[(df["amount"] > 0) & (df["amount"] < MAX_TOKEN_SUPPLY)]
        # 4. Derive USD placeholder
        df["amount_usd"] = df["amount"].astype(float)
        # 5. Outlier handling (simple clip)
        df["amount"] = df["amount"].clip(lower=0.0, upper=df["amount"].quantile(0.99))
        # 6. Sort by time
        df = df.sort_values("block_timestamp").reset_index(drop=True)
        # Derived temporal helpers
        df["hour"] = df["block_timestamp"].dt.hour
        df["day_of_week"] = df["block_timestamp"].dt.dayofweek
        return df
