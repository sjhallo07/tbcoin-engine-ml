"""
Configuration module for TBCoin Engine Lifecycle Management
"""

from typing import Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class LifecycleConfig:
    """Configuration for lifecycle management."""
    
    # Application settings
    app_name: str = "tbcoin-engine"
    log_level: str = "INFO"
    
    # Model settings
    model_dir: Path = field(default_factory=lambda: Path("./models"))
    model_cleanup_interval_seconds: int = 3600  # 1 hour
    max_model_age_seconds: int = 7200  # 2 hours
    
    # Resource settings
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    # Shutdown settings
    graceful_shutdown_timeout_seconds: int = 30
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "LifecycleConfig":
        """Create config from dictionary."""
        return cls(**config_dict)
        
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "app_name": self.app_name,
            "log_level": self.log_level,
            "model_dir": str(self.model_dir),
            "model_cleanup_interval_seconds": self.model_cleanup_interval_seconds,
            "max_model_age_seconds": self.max_model_age_seconds,
            "enable_health_checks": self.enable_health_checks,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "graceful_shutdown_timeout_seconds": self.graceful_shutdown_timeout_seconds,
        }
