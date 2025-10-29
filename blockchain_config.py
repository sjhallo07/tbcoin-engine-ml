# config/blockchain_config.py
from pydantic import BaseSettings
from typing import Dict, Any
import os

class BlockchainConfig(BaseSettings):
    # Honeycomb Protocol
    HONEYCOMB_RPC_URL: str = "https://edge.test.honeycombprotocol.com"
    HONEYCOMB_WS_URL: str = "wss://edge.test.honeycombprotocol.com"
    
    # Solana Configuration
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_WS_URL: str = "wss://api.mainnet-beta.solana.com"
    
    # Ethereum Configuration
    ETHEREUM_RPC_URL: str = "https://mainnet.infura.io/v3/your-project-id"
    ETHEREUM_WS_URL: str = "wss://mainnet.infura.io/ws/v3/your-project-id"
    
    # Security
    MAX_STORAGE_DEPOSIT: int = 1000000000000  # 1 UNIT
    DEFAULT_GAS_LIMIT: int = 1000000
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # Contract Defaults
    DEFAULT_MANIFEST_PATH: str = "./contracts/Cargo.toml"
    CONTRACT_ARTIFACTS_PATH: str = "./artifacts"
    
    class Config:
        env_file = ".env"

blockchain_config = BlockchainConfig()