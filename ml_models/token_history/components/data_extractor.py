from __future__ import annotations

import pandas as pd


class BlockchainDataExtractor:
    """Placeholder extractor for token transfer history.

    Replace with Web3-based extraction for real networks and tokens.
    """

    def __init__(self) -> None:
        pass

    def extract_token_history(self, token_address: str, start_block: int, end_block: int) -> pd.DataFrame:
        # Minimal synthetic dataset for the pipeline to run
        data = [
            {
                "transaction_hash": f"0xdeadbeef{i}",
                "block_number": i,
                "block_timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(hours=i),
                "from_address": f"0xfrom{i%3}",
                "to_address": f"0xto{i%5}",
                "amount": float(i + 1),
                "log_index": i,
                "transaction_index": i,
                "gas_price": 1.0,
            }
            for i in range(256)
        ]
        return pd.DataFrame(data)
