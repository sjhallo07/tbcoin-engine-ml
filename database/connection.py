"""Database connection utilities.

This module provides a minimal async dependency stub so the FastAPI app can
start without a real database integration. Replace the DummyDatabase class with
actual connection management when the persistence layer is implemented.
"""

from typing import AsyncGenerator


class DummyDatabase:
    """Placeholder async database client."""

    async def close(self) -> None:
        """No-op close hook for compatibility with context management."""


async def get_db() -> AsyncGenerator[DummyDatabase, None]:
    """Yield a dummy database client for request scope."""
    db = DummyDatabase()
    try:
        yield db
    finally:
        await db.close()
