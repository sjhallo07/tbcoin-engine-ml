# config/settings.py
import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Solana Configuration
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_WS_URL: str = "wss://api.mainnet-beta.solana.com"
    TOKEN_MINT_ADDRESS: str
    
    # Database Configuration
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # ML Configuration
    MODEL_SAVE_PATH: str = "./models"
    TRAINING_BATCH_SIZE: int = 1000
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.7
    
    # External APIs
    COINGECKO_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()