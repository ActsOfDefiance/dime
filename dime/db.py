from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dime.config.settings import get_settings


def make_async_url(url: str) -> str:
    """Swap postgresql:// scheme to postgresql+asyncpg:// for async engine."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    if url.startswith("postgresql+psycopg://"):
        return "postgresql+asyncpg://" + url[len("postgresql+psycopg://") :]
    return url


def build_engine() -> AsyncEngine:
    settings = get_settings()
    url = make_async_url(str(settings.DATABASE_URL))
    return create_async_engine(
        url,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_timeout=float(settings.DATABASE_POOL_TIMEOUT),
        echo=settings.DATABASE_ECHO,
    )


engine = build_engine()
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
