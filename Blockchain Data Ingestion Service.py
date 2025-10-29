# services/blockchain_ingestion.py
import asyncio
from solana.rpc.async_api import AsyncClient
from web3 import Web3
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class BlockchainEvent:
    chain: str
    event_type: str
    transaction_hash: str
    block_number: int
    timestamp: int
    data: Dict
    wallet_address: str
    value: Optional[float] = None

class BlockchainDataIngestion:
    def __init__(self, solana_rpc_url: str, ethereum_rpc_url: str):
        self.solana_client = AsyncClient(solana_rpc_url)
        self.ethereum_web3 = Web3(Web3.HTTPProvider(ethereum_rpc_url))
        self.logger = logging.getLogger(__name__)
        
    async def start_solana_listener(self):
        """Real-time Solana event listener"""
        try:
            # Subscribe to program logs for specific token
            subscription_id = await self.solana_client.logs_subscribe(
                filters={"mentions": [TOKEN_MINT_ADDRESS]}
            )
            
            async for response in self.solana_client.logs_subscribe():
                event = await self.parse_solana_event(response)
                await self.process_blockchain_event(event)
                
        except Exception as e:
            self.logger.error(f"Solana listener error: {e}")
            
    async def parse_solana_event(self, log_data: Dict) -> BlockchainEvent:
        """Parse Solana transaction logs into structured events"""
        return BlockchainEvent(
            chain="solana",
            event_type="token_transfer",
            transaction_hash=log_data['signature'],
            block_number=log_data['slot'],
            timestamp=log_data.get('timestamp', int(time.time())),
            data=log_data,
            wallet_address=log_data.get('from', ''),
            value=self.extract_token_amount(log_data)
        )
    
    async def process_blockchain_event(self, event: BlockchainEvent):
        """Process and store blockchain events"""
        # Store in database
        await self.store_event_in_db(event)
        
        # Publish to message queue for ML processing
        await self.publish_to_ml_queue(event)
        
        # Log for monitoring
        self.logger.info(f"Processed {event.chain} event: {event.transaction_hash}")