from __future__ import annotations

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from src.ai_models.training_pipeline import ModelTrainingPipeline
from src.blockchain.smart_contract_executor import SmartContractOrchestrator


class TestBlockchainAISystem(unittest.TestCase):
    def setUp(self) -> None:
        index = pd.date_range("2024-01-01", periods=120, freq="H")
        self.price_data = pd.DataFrame(
            {
                "close": np.linspace(100, 120, num=120) + np.random.normal(0, 0.5, size=120),
                "high": np.linspace(101, 121, num=120),
                "low": np.linspace(99, 119, num=120),
                "volume": np.random.uniform(1_000, 5_000, size=120),
            },
            index=index,
        )

    @patch("src.ai_models.training_pipeline.PredictiveBlockchainAI.train_price_prediction_model")
    def test_prediction_accuracy(self, mock_train: MagicMock) -> None:
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([110.0])
        mock_train.return_value = mock_model

        pipeline = ModelTrainingPipeline(self.price_data)
        ensemble = pipeline.train_ensemble_model()
        self.assertIn("random_forest", ensemble.members)
        self.assertIn("lstm", ensemble.members)

    @patch.object(SmartContractOrchestrator, "_simulate_transaction", autospec=True)
    @patch("src.blockchain.smart_contract_executor.create_web3_instance")
    def test_smart_contract_execution(self, mock_web3_factory: MagicMock, mock_simulate: MagicMock) -> None:
        async def run_test() -> None:
            mock_web3 = MagicMock()
            mock_web3.eth.chain_id = 1
            mock_web3.eth.get_transaction_count.return_value = 1
            mock_contract_fn = MagicMock()
            mock_contract_fn.build_transaction.return_value = {"nonce": 1, "from": "0xabc"}
            mock_contract = MagicMock()
            mock_contract.functions.trade.return_value = mock_contract_fn
            mock_web3.eth.contract.return_value = mock_contract
            mock_web3.eth.account.sign_transaction.return_value = MagicMock(rawTransaction=b"signed")
            mock_web3.eth.send_raw_transaction.return_value = bytes.fromhex("1234")
            mock_web3.eth.get_transaction_receipt.side_effect = [None, {"blockNumber": 1}]
            mock_web3.eth.get_block.return_value = MagicMock(timestamp=0)
            mock_web3_factory.return_value = mock_web3
            async def simulate(*args, **kwargs):
                return None
            mock_simulate.side_effect = simulate

            orchestrator = SmartContractOrchestrator(
                "ethereum.mainnet",
                {"ethereum": {"mainnet": {"rpc_url": "http://localhost:8545"}}},
                private_key="0x1",
                account_address="0xabc",
            )
            prediction_payload = {
                "contract_address": "0x0000000000000000000000000000000000000001",
                "abi": [{"name": "trade", "type": "function", "stateMutability": "nonpayable"}],
                "function_name": "trade",
                "function_args": ["0x1", 100],
            }
            with patch("src.blockchain.smart_contract_executor.estimate_optimal_gas", return_value={"gas": 21000, "gasPrice": 1}):
                tx_hash = await orchestrator.execute_ai_optimized_trade(prediction_payload)
            self.assertIsInstance(tx_hash, str)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
