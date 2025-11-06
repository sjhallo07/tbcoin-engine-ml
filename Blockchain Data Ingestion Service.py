# services/blockchain_ingestion.py
import asyncio
import logging
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

# Optional Solana dependency (may be unavailable on some Python versions)
try:
    from solana.rpc.async_api import AsyncClient  # type: ignore
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    class AsyncClient:  # minimal stub to avoid import errors
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Solana AsyncClient unavailable: install 'solana' package on a supported Python version.")
            
# Optional Web3 dependency (may be unavailable)
try:
    from web3 import Web3  # type: ignore
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None  # type: ignore

# Placeholder constant (should be set to the actual token/program ID you want to monitor)
TOKEN_MINT_ADDRESS = "ReplaceWithTokenMintAddress"

@dataclass
class BlockchainEvent:
    chain: str
    event_type: str
    transaction_hash: str
    block_number: int
    timestamp: int
    data: Dict
    wallet_address: str
    value: Optional[float]

class BlockchainIngestionService:
    def __init__(self, solana_client=None, solana_ws_url=None, logger=None):
        self.solana_client = solana_client
        self.solana_ws_url = solana_ws_url
        self.logger = logger or logging.getLogger(__name__)

    async def start_solana_listener(self):
        """Real-time Solana event listener (no-op if Solana unavailable)"""
        if not SOLANA_AVAILABLE or self.solana_client is None:
            self.logger.info("Skipping Solana listener start (dependency unavailable).")
            return
        try:
            # Use WebSocket API for log subscriptions
            from solana.rpc.websocket_api import connect  # type: ignore

            ws_url = self.solana_ws_url or ""
            if not ws_url:
                self.logger.error("Solana WebSocket URL is not configured.")
                return
            async with connect(ws_url) as websocket:
                await websocket.logs_subscribe(filter_={"mentions": [TOKEN_MINT_ADDRESS]})
                subscription_resp = await websocket.recv()
                self.logger.info(f"Subscribed to Solana logs: {subscription_resp}")

                while True:
                    message = await websocket.recv()
                    params = message.get("params", {}) if isinstance(message, dict) else {}
                    result = params.get("result", {})
                    context = result.get("context", {})
                    value = result.get("value", {})

                    log_data = {
                        "signature": value.get("signature", ""),
                        "slot": context.get("slot", 0),
                        "logs": value.get("logs", []),
                    }

                    event = await self.parse_solana_event(log_data)
                    await self.process_blockchain_event(event)
                
        except Exception as e:
            self.logger.error(f"Solana listener error: {e}")
            if self.solana_client:
                try:
                    # HTTP polling fallback if WebSocket subscription is unavailable
                    from solana.publickey import PublicKey  # type: ignore
                    address = PublicKey(TOKEN_MINT_ADDRESS)
                    last_signature: Optional[str] = None
                    while True:
                        try:
                            resp = await self.solana_client.get_signatures_for_address(address, limit=25)  # type: ignore
                        except Exception as poll_exc:
                            self.logger.error(f"Polling error: {poll_exc}")
                            await asyncio.sleep(5)
                            continue

                        if isinstance(resp, dict):
                            entries = resp.get("result") or resp.get("value") or []
                        else:
                            entries = getattr(resp, "value", [])

                        new_items: List[Dict] = []
                        for it in entries or []:
                            sig = it.get("signature")
                            if sig and sig != last_signature:
                                new_items.append(it)
                            else:
                                break

                        for it in reversed(new_items):
                            log_data = {
                                "signature": it.get("signature", ""),
                                "slot": it.get("slot", 0),
                                "timestamp": it.get("blockTime"),
                            }
                            event = await self.parse_solana_event(log_data)
                            await self.process_blockchain_event(event)

                        if entries:
                            last_signature = entries[0].get("signature")
                        await asyncio.sleep(2)
                except Exception as inner_e:
                    self.logger.error(f"Solana HTTP fallback error: {inner_e}")

    async def parse_solana_event(self, log_data: Dict) -> BlockchainEvent:
        """Parse Solana transaction logs into structured events"""
        return BlockchainEvent(
            chain="solana",
            event_type="token_transfer",
            transaction_hash=log_data.get('signature', ''),
            block_number=log_data.get('slot', 0),
            timestamp=log_data.get('timestamp', int(time.time())),
            data=log_data,
            wallet_address=log_data.get('from', ''),
            value=self.extract_token_amount(log_data)
        )

    async def process_blockchain_event(self, event: BlockchainEvent):
        """Process and store blockchain events"""
        await self.store_event_in_db(event)
        await self.publish_to_ml_queue(event)
        self.logger.info(f"Processed {event.chain} event: {event.transaction_hash}")

    async def store_event_in_db(self, event: BlockchainEvent):
        """Stub: implement database persistence"""
        # TODO: replace with real DB logic
        self.logger.debug(f"Storing event in DB: {event.transaction_hash}")

    async def publish_to_ml_queue(self, event: BlockchainEvent):
        """Stub: implement queue publish"""
        # TODO: replace with real queue logic
        self.logger.debug(f"Publishing event to ML queue: {event.transaction_hash}")

    def extract_token_amount(self, log_data: Dict) -> Optional[float]:
        """Extract token amount from log (placeholder logic)"""
        amount = log_data.get("amount")
        try:
            return float(amount) if amount is not None else None
        except (TypeError, ValueError):
            return None