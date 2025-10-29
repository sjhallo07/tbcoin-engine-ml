"""Core configuration module"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "TB Coin Engine ML"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "change-this-secret-key"
    API_KEY: str = ""
    JWT_SECRET_KEY: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # Database
    DATABASE_URL: str = "sqlite:///./tbcoin.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Coin settings
    INITIAL_COIN_SUPPLY: float = 1000000
    MIN_TRANSACTION_AMOUNT: float = 0.01
    MAX_TRANSACTION_AMOUNT: float = 1000000
    TRANSACTION_FEE_PERCENT: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
