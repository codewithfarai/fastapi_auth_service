"""Database configuration and session management for the application."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Will be set in create_application()
engine = None
AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for each request.

    Yields:
        AsyncSession: A new database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
