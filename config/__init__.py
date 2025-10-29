try:
    from .base_config import BaseConfig
except ImportError:
    from config.base_config import BaseConfig

try:
    from .blockchain_config import BlockchainConfig
except ImportError:
    from config.blockchain_config import BlockchainConfig

try:
    from .ai_config import AIConfig
except ImportError:
    from config.ai_config import AIConfig

try:
    from .trading_config import TradingConfig
except ImportError:
    from config.trading_config import TradingConfig

class TBCoinConfig(BaseConfig, BlockchainConfig, AIConfig, TradingConfig):
    """Configuración unificada para todo el proyecto TB Coin"""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
config = TBCoinConfig()
