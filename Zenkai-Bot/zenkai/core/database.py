from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from zenkai.core.errors import DatabaseError


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str, *, echo: bool = False) -> None:
        options: dict[str, object] = {"echo": echo, "future": True}
        if url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False}
        else:
            options["pool_pre_ping"] = True
        self.engine: AsyncEngine = create_async_engine(url, **options)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def initialize(self) -> None:
        try:
            async with self.engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
        except Exception as exc:
            raise DatabaseError(f"Database initialization failed: {exc}") from exc

    async def ping(self) -> None:
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception as exc:
            raise DatabaseError(f"Database health check failed: {exc}") from exc

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        await self.engine.dispose()
