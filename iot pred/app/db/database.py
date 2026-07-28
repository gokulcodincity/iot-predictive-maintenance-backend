"""Central database connection layer for TimescaleDB/PostgreSQL."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class DatabaseManager:
    """Manages async database connections and session lifecycle."""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ):
        """Initialize database manager with connection pool configuration.

        Args:
            database_url: PostgreSQL connection URL (async driver)
            pool_size: Number of connections to keep in pool
            max_overflow: Maximum connections above pool_size
            pool_recycle: Recycle connections after N seconds (default 1 hour)
            pool_pre_ping: Test connections before using them
            echo: Log all SQL statements (for debugging)
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.echo = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    async def initialize(self) -> None:
        """Initialize async engine and session factory.

        Raises:
            ValueError: If database URL is invalid
            Exception: If connection cannot be established
        """
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        try:
            # Create async engine with connection pooling
            self._engine = create_async_engine(
                self.database_url,
                echo=self.echo,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=self.pool_pre_ping,
                connect_args={
                    "server_settings": {
                        "jit": "off",  # Disable JIT for predictable performance
                    },
                    "timeout": 30,  # Connection timeout in seconds
                    "command_timeout": 30,  # Command timeout in seconds
                },
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            logger.info("Database manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database manager: {str(e)}")
            raise

    async def get_session(self) -> AsyncSession:
        """Get a new async database session.

        Returns:
            AsyncSession for database operations

        Raises:
            RuntimeError: If database manager not initialized
        """
        if not self._session_factory:
            raise RuntimeError(
                "Database manager not initialized. Call initialize() first."
            )

        return self._session_factory()

    @asynccontextmanager
    async def session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for automatic session cleanup.

        Yields:
            AsyncSession for use within context

        Example:
            async with db_manager.session_context() as session:
                result = await session.execute(...)
        """
        session = await self.get_session()
        try:
            yield session
        finally:
            await session.close()

    async def check_connection(self) -> bool:
        """Check if database connection is healthy.

        Returns:
            True if connection successful, False otherwise
        """
        if not self._engine:
            logger.warning("Database engine not initialized")
            return False

        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection health check passed")
            return True
        except Exception as e:
            logger.error(f"Database connection health check failed: {str(e)}")
            return False

    async def close(self) -> None:
        """Close database engine and connection pool.

        Should be called on application shutdown.
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def initialize_database() -> DatabaseManager:
    """Initialize global database manager.

    Should be called during application startup.

    Returns:
        Initialized DatabaseManager instance

    Raises:
        ValueError: If DATABASE_URL not configured
        Exception: If connection fails
    """
    global _db_manager

    db_manager = DatabaseManager(
        database_url=settings.DATABASE_URL,
        pool_size=getattr(settings, "DB_POOL_SIZE", 20),
        max_overflow=getattr(settings, "DB_MAX_OVERFLOW", 10),
        pool_recycle=getattr(settings, "DB_POOL_RECYCLE", 3600),
        pool_pre_ping=True,
        echo=getattr(settings, "DB_ECHO", False),
    )

    await db_manager.initialize()
    _db_manager = db_manager

    # Verify connection
    if not await db_manager.check_connection():
        raise Exception("Failed to establish database connection")

    return db_manager


async def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance.

    Returns:
        DatabaseManager instance

    Raises:
        RuntimeError: If database not initialized
    """
    if not _db_manager:
        raise RuntimeError(
            "Database manager not initialized. Call initialize_database() first."
        )
    return _db_manager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting async session.

    Yields:
        AsyncSession for use in endpoint

    Example:
        @app.post("/predictions")
        async def create_prediction(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    db_manager = await get_database_manager()
    async with db_manager.session_context() as session:
        yield session


async def shutdown_database() -> None:
    """Shutdown database manager.

    Should be called during application shutdown.
    """
    global _db_manager

    if _db_manager:
        await _db_manager.close()
        _db_manager = None
        logger.info("Database manager shut down")
