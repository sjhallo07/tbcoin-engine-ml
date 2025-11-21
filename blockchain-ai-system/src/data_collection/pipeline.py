from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable, Dict, Iterable, Optional

try:  # pragma: no cover - optional dependency for streaming
    from aiokafka import AIOKafkaProducer
except ImportError:  # pragma: no cover - allow running without Kafka
    AIOKafkaProducer = None  # type: ignore

from .blockchain_apis import BlockchainDataCollector
from ..ai_models.feature_engineering import BlockchainFeatureEngineer


Validator = Callable[[Dict[str, Any]], Dict[str, Any]]


class BlockchainDataPipeline:
    """Streams blockchain telemetry into downstream systems with validation."""

    def __init__(
        self,
        collector: BlockchainDataCollector,
        feature_engineer: BlockchainFeatureEngineer,
        *,
        kafka_bootstrap_servers: Optional[Iterable[str]] = None,
        validator: Optional[Validator] = None,
        poll_interval: float = 15.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._collector = collector
        self._feature_engineer = feature_engineer
        self._kafka_bootstrap_servers = list(kafka_bootstrap_servers or [])
        self._validator = validator or (lambda payload: payload)
        self._poll_interval = poll_interval
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._producer: Optional[AIOKafkaProducer] = None  # type: ignore[assignment]
        self.kafka_topics = ["blockchain-events", "price-feeds", "defi-metrics"]
        self._stopped = asyncio.Event()

    async def start_data_stream(self) -> None:
        if AIOKafkaProducer and self._kafka_bootstrap_servers:
            self._producer = AIOKafkaProducer(bootstrap_servers=self._kafka_bootstrap_servers)
            await self._producer.start()

        try:
            while not self._stopped.is_set():
                await self._collect_and_publish()
                await asyncio.sleep(self._poll_interval)
        finally:
            if self._producer:
                await self._producer.stop()

    async def stop(self) -> None:
        self._stopped.set()

    async def _collect_and_publish(self) -> None:
        ethereum_data = self._collector.fetch_ethereum_data()
        solana_data = self._collector.fetch_solana_data()

        validated_eth = self._validator(ethereum_data)
        validated_sol = self._validator(solana_data)

        await asyncio.gather(
            self._publish("blockchain-events", validated_eth),
            self._publish("blockchain-events", validated_sol),
        )

        try:
            network_features = self._feature_engineer.create_network_metrics({
                "metrics": {},
                "history": [
                    {
                        "timestamp": ethereum_data["collected_at"],
                        "transaction_volume": ethereum_data.get("transaction_metrics", {}).get("transaction_count", 0),
                        "total_value_locked": 1.0,
                        "active_addresses": ethereum_data.get("transaction_metrics", {}).get("transaction_count", 0),
                    }
                ],
            })
        except Exception as exc:
            self._logger.warning("Feature engineering failed: %s", exc)
            network_features = None

        if network_features is not None and not network_features.empty:
            await self._publish("defi-metrics", network_features.iloc[-1].to_dict())

    async def _publish(self, topic: str, payload: Dict[str, Any]) -> None:
        if self._producer:
            await self._producer.send_and_wait(topic, json.dumps(payload).encode("utf-8"))
        else:
            self._logger.debug("Kafka unavailable; logging payload for %s: %s", topic, payload)
