"""SQLAlchemy engine and session factory for TB Coin Engine ML."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@lru_cache(maxsize=1)
def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./tbcoin.db")


# Create engine; future=True enables SQLAlchemy 2.0 style
_engine = create_engine(get_database_url(), future=True)

# Session factory
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator:
    """FastAPI-style dependency helper yielding a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
