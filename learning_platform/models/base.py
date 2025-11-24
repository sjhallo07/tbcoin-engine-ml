"""Base model configuration for SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


def get_engine(database_url: str = "sqlite:///./learning_platform.db"):
    """Create and return a SQLAlchemy engine."""
    return create_engine(database_url, echo=False)


def get_session(database_url: str = "sqlite:///./learning_platform.db"):
    """Create and return a session factory."""
    engine = get_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


def init_db(database_url: str = "sqlite:///./learning_platform.db"):
    """Initialize the database with all tables."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
