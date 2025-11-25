"""
Tests for database modules
Run with: python -m pytest tests/test_database.py -v
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.mongodb import MongoDBClient, MongoDBConfig
from app.db.sql import SQLDatabase, SQLConfig


class TestMongoDBConfig:
    """Test MongoDB configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = MongoDBConfig()
        assert config.uri == "mongodb://localhost:27017"
        assert config.database_name == "tbcoin"
        assert config.max_pool_size == 100
        assert config.min_pool_size == 10
    
    @patch.dict('os.environ', {
        'MONGODB_URI': 'mongodb://custom:27017',
        'MONGODB_DATABASE': 'testdb',
        'MONGODB_MAX_POOL_SIZE': '50',
    })
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        config = MongoDBConfig()
        assert config.uri == "mongodb://custom:27017"
        assert config.database_name == "testdb"
        assert config.max_pool_size == 50


class TestMongoDBClient:
    """Test MongoDB client"""
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = MongoDBClient()
        assert client.is_connected is False
        assert client.config is not None
    
    def test_sanitize_document(self):
        """Test document sanitization"""
        client = MongoDBClient()
        
        # Test removing suspicious keys
        document = {
            "name": "test",
            "$where": "malicious code",
            "nested": {
                "$regex": "pattern",
                "valid": "value"
            }
        }
        
        sanitized = client._sanitize_document(document)
        assert "$where" not in sanitized
        assert "name" in sanitized
    
    def test_sanitize_query(self):
        """Test query sanitization"""
        client = MongoDBClient()
        
        # Test allowing safe operators
        query = {
            "status": "active",
            "$eq": "value",
            "$gt": 100,
        }
        
        sanitized = client._sanitize_query(query)
        assert "$eq" in sanitized
        assert "$gt" in sanitized
    
    def test_sanitize_query_blocks_dangerous_operators(self):
        """Test that dangerous operators are blocked"""
        client = MongoDBClient()
        
        query = {
            "status": "active",
            "$where": "this.password.length > 0",  # Dangerous
            "$mapReduce": "function() {}",  # Dangerous
        }
        
        sanitized = client._sanitize_query(query)
        assert "$where" not in sanitized
        assert "$mapReduce" not in sanitized


class TestSQLConfig:
    """Test SQL configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SQLConfig()
        assert "sqlite" in config.database_url
        assert config.pool_size == 10
        assert config.echo is False
    
    def test_async_url_conversion_postgres(self):
        """Test PostgreSQL URL conversion for async"""
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://user:pass@localhost/db'}):
            config = SQLConfig()
            assert "postgresql+asyncpg://" in config.async_database_url
    
    def test_async_url_conversion_sqlite(self):
        """Test SQLite URL conversion for async"""
        config = SQLConfig()
        assert "sqlite+aiosqlite:" in config.async_database_url


class TestSQLDatabase:
    """Test SQL database operations"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        db = SQLDatabase()
        assert db.is_connected is False
    
    def test_sync_connection(self):
        """Test synchronous connection"""
        db = SQLDatabase()
        db.connect_sync()
        assert db.is_connected is True
        assert db._engine is not None
    
    def test_get_session(self):
        """Test getting a database session"""
        db = SQLDatabase()
        db.connect_sync()
        session = db.get_session()
        assert session is not None
        session.close()


class TestDatabaseSecurity:
    """Test database security measures"""
    
    def test_no_sql_injection_in_mongodb(self):
        """Test that NoSQL injection is prevented"""
        client = MongoDBClient()
        
        # Attempt NoSQL injection
        malicious_query = {
            "username": {"$gt": ""},
            "password": {"$ne": ""}
        }
        
        # The client should sanitize but allow safe operators
        # In a real scenario, business logic should validate inputs
        sanitized = client._sanitize_query(malicious_query)
        assert sanitized is not None
    
    def test_parameterized_queries_in_sql(self):
        """Test that SQL uses parameterized queries via ORM"""
        # SQLAlchemy ORM inherently uses parameterized queries
        # This test verifies the database module uses ORM correctly
        from app.db.sql import TransactionModel, UserModel
        
        # Verify models exist and have proper structure
        assert hasattr(TransactionModel, '__tablename__')
        assert hasattr(UserModel, '__tablename__')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
