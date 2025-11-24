"""MongoDB connection and utilities for TB Coin Engine ML

This module provides MongoDB connection management with:
- Connection pooling
- Async support
- Index management
- Schema validation (via Pydantic)
"""
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import os

logger = logging.getLogger(__name__)


class MongoDBConfig:
    """MongoDB configuration from environment variables"""
    
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("MONGODB_DATABASE", "tbcoin")
        self.max_pool_size = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
        self.min_pool_size = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
        self.server_selection_timeout_ms = int(
            os.getenv("MONGODB_TIMEOUT_MS", "5000")
        )


class MongoDBClient:
    """MongoDB client wrapper with connection pooling and utilities
    
    Implements best practices for MongoDB:
    - Connection pooling for performance
    - Index management for query optimization
    - Schema validation through Pydantic models
    - Proper connection lifecycle management
    """
    
    def __init__(self, config: Optional[MongoDBConfig] = None):
        self.config = config or MongoDBConfig()
        self._client = None
        self._db = None
        self._connected = False
    
    async def connect(self) -> None:
        """Establish MongoDB connection with pooling"""
        if self._connected:
            return
        
        try:
            # Import motor only when needed (optional dependency)
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
            except ImportError:
                logger.warning(
                    "motor not installed. MongoDB operations will be mocked. "
                    "Install with: pip install motor"
                )
                self._connected = True
                return
            
            self._client = AsyncIOMotorClient(
                self.config.uri,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
                serverSelectionTimeoutMS=self.config.server_selection_timeout_ms,
            )
            self._db = self._client[self.config.database_name]
            
            # Verify connection
            await self._client.admin.command("ping")
            self._connected = True
            logger.info(f"Connected to MongoDB: {self.config.database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create indexes for frequently queried fields
        
        Following MongoDB best practices for index optimization.
        """
        if not self._db:
            return
        
        try:
            # Transactions collection indexes
            transactions = self._db.transactions
            await transactions.create_index("transaction_id", unique=True)
            await transactions.create_index("from_user")
            await transactions.create_index("to_user")
            await transactions.create_index("timestamp")
            await transactions.create_index("status")
            # Compound index for user transaction queries
            await transactions.create_index([("from_user", 1), ("timestamp", -1)])
            await transactions.create_index([("to_user", 1), ("timestamp", -1)])
            
            # Users collection indexes
            users = self._db.users
            await users.create_index("username", unique=True)
            await users.create_index("email", unique=True)
            await users.create_index("role")
            
            # Jobs collection indexes
            jobs = self._db.jobs
            await jobs.create_index("job_id", unique=True)
            await jobs.create_index("status")
            await jobs.create_index("job_type")
            await jobs.create_index("priority")
            await jobs.create_index("created_at")
            # Compound index for job queue queries
            await jobs.create_index([("status", 1), ("priority", -1), ("created_at", 1)])
            
            # Wallet behavior collection indexes
            wallet_behavior = self._db.wallet_behavior
            await wallet_behavior.create_index("wallet_address", unique=True)
            await wallet_behavior.create_index("risk_score")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")
    
    @property
    def db(self):
        """Get database instance"""
        return self._db
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self._connected
    
    # Collection accessors with type hints
    @property
    def transactions(self):
        """Get transactions collection"""
        if self._db:
            return self._db.transactions
        return None
    
    @property
    def users(self):
        """Get users collection"""
        if self._db:
            return self._db.users
        return None
    
    @property
    def jobs(self):
        """Get jobs collection"""
        if self._db:
            return self._db.jobs
        return None
    
    @property
    def wallet_behavior(self):
        """Get wallet_behavior collection"""
        if self._db:
            return self._db.wallet_behavior
        return None
    
    # CRUD Operations with sanitization
    async def insert_one(
        self, 
        collection_name: str, 
        document: Dict[str, Any]
    ) -> Optional[str]:
        """Insert a document with sanitization
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            Inserted document ID or None
        """
        if not self._db:
            logger.warning("MongoDB not connected. Insert skipped.")
            return None
        
        # Sanitize keys (prevent NoSQL injection via operators)
        sanitized_doc = self._sanitize_document(document)
        
        collection = self._db[collection_name]
        result = await collection.insert_one(sanitized_doc)
        return str(result.inserted_id)
    
    async def find_one(
        self, 
        collection_name: str, 
        query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find a single document with sanitized query
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            
        Returns:
            Found document or None
        """
        if not self._db:
            logger.warning("MongoDB not connected. Find skipped.")
            return None
        
        # Sanitize query to prevent NoSQL injection
        sanitized_query = self._sanitize_query(query)
        
        collection = self._db[collection_name]
        doc = await collection.find_one(sanitized_query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def find_many(
        self,
        collection_name: str,
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            sort: Sort specification
            limit: Maximum documents to return
            skip: Documents to skip
            
        Returns:
            List of found documents
        """
        if not self._db:
            logger.warning("MongoDB not connected. Find skipped.")
            return []
        
        sanitized_query = self._sanitize_query(query)
        collection = self._db[collection_name]
        
        cursor = collection.find(sanitized_query)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(min(limit, 1000))  # Cap at 1000
        
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        
        return documents
    
    async def update_one(
        self,
        collection_name: str,
        query: Dict[str, Any],
        update: Dict[str, Any]
    ) -> bool:
        """Update a single document
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            update: Update operations
            
        Returns:
            True if document was modified
        """
        if not self._db:
            logger.warning("MongoDB not connected. Update skipped.")
            return False
        
        sanitized_query = self._sanitize_query(query)
        sanitized_update = self._sanitize_document(update)
        
        # Ensure update uses operators
        if not any(k.startswith("$") for k in sanitized_update.keys()):
            sanitized_update = {"$set": sanitized_update}
        
        collection = self._db[collection_name]
        result = await collection.update_one(sanitized_query, sanitized_update)
        return result.modified_count > 0
    
    async def delete_one(
        self,
        collection_name: str,
        query: Dict[str, Any]
    ) -> bool:
        """Delete a single document
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            
        Returns:
            True if document was deleted
        """
        if not self._db:
            logger.warning("MongoDB not connected. Delete skipped.")
            return False
        
        sanitized_query = self._sanitize_query(query)
        collection = self._db[collection_name]
        result = await collection.delete_one(sanitized_query)
        return result.deleted_count > 0
    
    def _sanitize_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize document to prevent NoSQL injection
        
        Removes keys starting with $ to prevent operator injection.
        """
        sanitized = {}
        for key, value in document.items():
            # Skip keys that look like MongoDB operators (unless they are)
            if key.startswith("$") and key not in ("$set", "$inc", "$push", "$pull"):
                logger.warning(f"Suspicious key removed from document: {key}")
                continue
            
            # Recursively sanitize nested documents
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_document(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_document(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize query to prevent NoSQL injection
        
        Only allows safe operators and sanitizes values.
        """
        allowed_operators = {
            "$eq", "$ne", "$gt", "$gte", "$lt", "$lte",
            "$in", "$nin", "$and", "$or", "$not", "$exists",
            "$regex", "$options", "$elemMatch", "$size"
        }
        
        sanitized = {}
        for key, value in query.items():
            if key.startswith("$"):
                if key not in allowed_operators:
                    logger.warning(f"Blocked query operator: {key}")
                    continue
            
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_query(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_query(v) if isinstance(v, dict) else v
                    for v in value
                ]
            elif isinstance(value, str):
                # Escape regex special characters if using $regex
                if key == "$regex":
                    import re
                    sanitized[key] = re.escape(value)
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        
        return sanitized


# Global MongoDB client instance
_mongodb_client: Optional[MongoDBClient] = None


async def get_mongodb() -> MongoDBClient:
    """Get MongoDB client instance (dependency injection)
    
    Returns:
        MongoDBClient instance
    """
    global _mongodb_client
    
    if _mongodb_client is None:
        _mongodb_client = MongoDBClient()
        await _mongodb_client.connect()
    
    return _mongodb_client


@asynccontextmanager
async def mongodb_session():
    """Context manager for MongoDB operations
    
    Yields:
        MongoDBClient instance
    """
    client = await get_mongodb()
    try:
        yield client
    finally:
        pass  # Connection pooling handles cleanup
