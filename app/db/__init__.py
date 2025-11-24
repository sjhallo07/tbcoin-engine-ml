"""Database package for TB Coin Engine ML

This package provides database connections and models for both
MongoDB (NoSQL) and SQL databases.
"""
from .mongodb import get_mongodb, MongoDBClient
from .sql import get_sql_db, SQLDatabase
from .connection_manager import DatabaseManager

__all__ = [
    "get_mongodb",
    "MongoDBClient",
    "get_sql_db",
    "SQLDatabase",
    "DatabaseManager",
]
