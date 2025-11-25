"""Database connection manager for TB Coin Engine ML

This module provides a unified interface for managing both
MongoDB and SQL database connections.
"""
import logging
from typing import Optional
from contextlib import asynccontextmanager

from .mongodb import MongoDBClient, get_mongodb
from .sql import SQLDatabase, get_sql_db

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Unified database manager for MongoDB and SQL
    
    Provides a single point of access for all database operations
    and manages connection lifecycle.
    """
    
    def __init__(self):
        self._mongodb: Optional[MongoDBClient] = None
        self._sql: Optional[SQLDatabase] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all database connections"""
        if self._initialized:
            return
        
        logger.info("Initializing database connections...")
        
        try:
            self._mongodb = await get_mongodb()
            logger.info("MongoDB initialized")
        except Exception as e:
            logger.warning(f"MongoDB initialization failed: {e}")
        
        try:
            self._sql = await get_sql_db()
            logger.info("SQL database initialized")
        except Exception as e:
            logger.warning(f"SQL database initialization failed: {e}")
        
        self._initialized = True
        logger.info("Database manager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all database connections"""
        if self._mongodb:
            await self._mongodb.disconnect()
        
        if self._sql:
            await self._sql.disconnect()
        
        self._initialized = False
        logger.info("Database manager shutdown complete")
    
    @property
    def mongodb(self) -> Optional[MongoDBClient]:
        """Get MongoDB client"""
        return self._mongodb
    
    @property
    def sql(self) -> Optional[SQLDatabase]:
        """Get SQL database"""
        return self._sql
    
    @property
    def is_initialized(self) -> bool:
        """Check if manager is initialized"""
        return self._initialized
    
    def get_status(self) -> dict:
        """Get status of all database connections"""
        return {
            "mongodb": {
                "connected": self._mongodb.is_connected if self._mongodb else False
            },
            "sql": {
                "connected": self._sql.is_connected if self._sql else False
            },
            "initialized": self._initialized
        }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    
    return _db_manager


@asynccontextmanager
async def database_lifecycle():
    """Context manager for database lifecycle
    
    Initializes databases on enter and shuts down on exit.
    Useful for application startup/shutdown.
    """
    manager = await get_db_manager()
    try:
        yield manager
    finally:
        await manager.shutdown()
