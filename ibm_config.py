# config/ibm_config.py
import os
from pydantic import BaseSettings

class IBMConfig(BaseSettings):
    # Free Tier Database (Railway, Supabase, or Neon)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@free-tier.postgresql:5432/tbcoin")
    
    # Free Redis (Redis Cloud free tier)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis-cloud:6379")
    
    # IBM Code Engine specific
    CE_REGION: str = "us-south"
    CE_PROJECT: str = "tbcoin-project"
    
    # Free monitoring (UptimeRobot + Healthchecks)
    MONITORING_URL: str = os.getenv("MONITORING_URL", "")
    
    class Config:
        env_file = ".env"

ibm_config = IBMConfig()