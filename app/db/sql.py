"""SQL database connection and utilities for TB Coin Engine ML

This module provides SQL database management with:
- SQLAlchemy ORM integration
- Connection pooling
- Transaction support
- Parameterized queries for SQL injection prevention
"""
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from contextlib import asynccontextmanager
import os
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()

# Type variable for generic operations
T = TypeVar("T", bound=Base)


class SQLConfig:
    """SQL database configuration from environment variables"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "sqlite:///./tbcoin.db"
        )
        # Convert for async if using PostgreSQL
        if self.database_url.startswith("postgresql://"):
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        elif self.database_url.startswith("sqlite:"):
            self.async_database_url = self.database_url.replace(
                "sqlite:", "sqlite+aiosqlite:"
            )
        else:
            self.async_database_url = self.database_url
        
        self.pool_size = int(os.getenv("SQL_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("SQL_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("SQL_POOL_TIMEOUT", "30"))
        self.echo = os.getenv("SQL_ECHO", "false").lower() == "true"


# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================

class TransactionModel(Base):
    """SQL model for transactions
    
    Follows normalization principles to reduce redundancy.
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_hash = Column(String(255), unique=True, nullable=True)
    chain = Column(String(50), nullable=True)
    from_user = Column(String(100), nullable=False, index=True)
    to_user = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0)
    transaction_type = Column(String(50), default="send")
    status = Column(String(50), default="pending", index=True)
    block_number = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class UserModel(Base):
    """SQL model for users
    
    Stores user authentication and profile data.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", index=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class CoinBalanceModel(Base):
    """SQL model for coin balances"""
    __tablename__ = "coin_balances"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    balance = Column(Float, default=0)
    staked_balance = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class JobModel(Base):
    """SQL model for jobs"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    job_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)
    priority = Column(Integer, default=5, index=True)
    payload_json = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(String(100), nullable=True)
    callback_url = Column(String(500), nullable=True)


class WalletBehaviorModel(Base):
    """SQL model for wallet behavior analytics"""
    __tablename__ = "wallet_behavior"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(255), unique=True, nullable=False, index=True)
    total_transactions = Column(Integer, default=0)
    total_volume = Column(Float, default=0)
    avg_transaction_size = Column(Float, nullable=True)
    first_transaction = Column(DateTime, nullable=True)
    last_transaction = Column(DateTime, nullable=True)
    wallet_age_days = Column(Integer, nullable=True)
    behavior_cluster = Column(Integer, nullable=True)
    risk_score = Column(Float, nullable=True, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ModelPredictionModel(Base):
    """SQL model for ML model predictions"""
    __tablename__ = "model_predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type = Column(String(100), nullable=False, index=True)
    prediction_type = Column(String(100), nullable=False)
    input_features_json = Column(Text, nullable=True)
    prediction_output_json = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actual_outcome_json = Column(Text, nullable=True)


# ============================================================================
# SQL Database Class
# ============================================================================

class SQLDatabase:
    """SQL Database wrapper with connection pooling and ORM support
    
    Implements best practices for SQL:
    - Connection pooling for performance
    - Parameterized queries via ORM
    - Transaction support for atomicity
    - Proper connection lifecycle
    """
    
    def __init__(self, config: Optional[SQLConfig] = None):
        self.config = config or SQLConfig()
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        self._connected = False
    
    def connect_sync(self) -> None:
        """Establish synchronous database connection"""
        if self._engine:
            return
        
        self._engine = create_engine(
            self.config.database_url,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            echo=self.config.echo,
        )
        
        self._session_factory = sessionmaker(bind=self._engine)
        
        # Create tables
        Base.metadata.create_all(self._engine)
        self._connected = True
        logger.info("Connected to SQL database (sync)")
    
    async def connect(self) -> None:
        """Establish async database connection"""
        if self._async_engine:
            return
        
        try:
            self._async_engine = create_async_engine(
                self.config.async_database_url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                echo=self.config.echo,
            )
            
            self._async_session_factory = sessionmaker(
                self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables using sync engine for simplicity
            self.connect_sync()
            
            self._connected = True
            logger.info("Connected to SQL database (async)")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQL database: {e}")
            # Fall back to sync connection
            self.connect_sync()
    
    async def disconnect(self) -> None:
        """Close database connections"""
        if self._async_engine:
            await self._async_engine.dispose()
        if self._engine:
            self._engine.dispose()
        self._connected = False
        logger.info("Disconnected from SQL database")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to database"""
        return self._connected
    
    def get_session(self):
        """Get synchronous session"""
        if not self._session_factory:
            self.connect_sync()
        return self._session_factory()
    
    async def get_async_session(self) -> AsyncSession:
        """Get async session"""
        if not self._async_session_factory:
            await self.connect()
        return self._async_session_factory()
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions
        
        Ensures atomicity - commits on success, rolls back on failure.
        
        Yields:
            AsyncSession: Database session
        """
        session = await self.get_async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            await session.close()
    
    # ========================================================================
    # Generic CRUD Operations (using parameterized queries via ORM)
    # ========================================================================
    
    async def create(
        self, 
        model_class: Type[T], 
        data: Dict[str, Any]
    ) -> T:
        """Create a new record
        
        Uses parameterized queries through ORM to prevent SQL injection.
        
        Args:
            model_class: SQLAlchemy model class
            data: Record data
            
        Returns:
            Created model instance
        """
        async with self.transaction() as session:
            instance = model_class(**data)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            return instance
    
    async def get_by_id(
        self, 
        model_class: Type[T], 
        id_field: str, 
        id_value: Any
    ) -> Optional[T]:
        """Get a record by ID
        
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            model_class: SQLAlchemy model class
            id_field: Name of the ID field
            id_value: Value to search for
            
        Returns:
            Model instance or None
        """
        async with self.transaction() as session:
            from sqlalchemy import select
            stmt = select(model_class).where(
                getattr(model_class, id_field) == id_value
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_many(
        self,
        model_class: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """Get multiple records with filtering and pagination
        
        Args:
            model_class: SQLAlchemy model class
            filters: Field-value pairs for filtering
            order_by: Field to order by (prefix with - for descending)
            limit: Maximum records to return
            offset: Records to skip
            
        Returns:
            List of model instances
        """
        async with self.transaction() as session:
            from sqlalchemy import select, desc
            
            stmt = select(model_class)
            
            # Apply filters (parameterized)
            if filters:
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        stmt = stmt.where(
                            getattr(model_class, field) == value
                        )
            
            # Apply ordering
            if order_by:
                if order_by.startswith("-"):
                    stmt = stmt.order_by(
                        desc(getattr(model_class, order_by[1:]))
                    )
                else:
                    stmt = stmt.order_by(getattr(model_class, order_by))
            
            # Apply pagination
            stmt = stmt.offset(offset).limit(min(limit, 1000))
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def update(
        self,
        model_class: Type[T],
        id_field: str,
        id_value: Any,
        data: Dict[str, Any]
    ) -> Optional[T]:
        """Update a record
        
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            model_class: SQLAlchemy model class
            id_field: Name of the ID field
            id_value: Value to search for
            data: Fields to update
            
        Returns:
            Updated model instance or None
        """
        async with self.transaction() as session:
            from sqlalchemy import select
            stmt = select(model_class).where(
                getattr(model_class, id_field) == id_value
            )
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            
            if instance:
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                await session.flush()
                await session.refresh(instance)
            
            return instance
    
    async def delete(
        self,
        model_class: Type[T],
        id_field: str,
        id_value: Any
    ) -> bool:
        """Delete a record
        
        Args:
            model_class: SQLAlchemy model class
            id_field: Name of the ID field
            id_value: Value to search for
            
        Returns:
            True if record was deleted
        """
        async with self.transaction() as session:
            from sqlalchemy import select
            stmt = select(model_class).where(
                getattr(model_class, id_field) == id_value
            )
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            
            if instance:
                await session.delete(instance)
                return True
            return False


# Global SQL database instance
_sql_database: Optional[SQLDatabase] = None


async def get_sql_db() -> SQLDatabase:
    """Get SQL database instance (dependency injection)
    
    Returns:
        SQLDatabase instance
    """
    global _sql_database
    
    if _sql_database is None:
        _sql_database = SQLDatabase()
        await _sql_database.connect()
    
    return _sql_database


@asynccontextmanager
async def sql_session():
    """Context manager for SQL session
    
    Yields:
        SQLDatabase instance
    """
    db = await get_sql_db()
    try:
        yield db
    finally:
        pass  # Connection pooling handles cleanup
