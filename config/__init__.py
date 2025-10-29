from .base_config import BaseConfig
from .blockchain_config import BlockchainConfig
from .ai_config import AIConfig
from .trading_config import TradingConfig

class TBCoinConfig(BaseConfig, BlockchainConfig, AIConfig, TradingConfig):
    """Configuración unificada para todo el proyecto TB Coin"""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
config = TBCoinConfig()
