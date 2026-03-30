"""
Pytest configuration and shared fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from dime.adapters.factory import AdapterSet
from dime.adapters.filesystem.local import LocalFileSystemAdapter
from dime.adapters.notification.websocket import WebSocketNotificationAdapter
from dime.adapters.publishing.hugo import HugoPublishingAdapter
from dime.api.deps import get_adapters, get_db
from dime.app import app as dime_app, create_app
from dime.db import make_async_url
from dime.models.base import Base


@pytest.fixture
def test_env() -> Generator[dict[str, str], None, None]:
    """
    Provide test environment variables.

    Yields:
        dict: Dictionary of test environment variables
    """
    test_vars = {
        "DATABASE_URL": "postgresql://test_user:test_pass@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/1",
        "GOOGLE_ADK_PROJECT_ID": "test-project",
        "GOOGLE_ADK_API_KEY": "test-api-key",
        "AUTH_GOOGLE_OAUTH_CLIENT_ID": "test-client-id",
        "AUTH_GOOGLE_OAUTH_CLIENT_SECRET": "test-client-secret",
        "AUTH_JWT_SECRET_KEY": "test-jwt-secret",
        "APP_ENVIRONMENT": "development",
        "LOGFIRE_TOKEN": "",  # Disable Logfire in tests
        "HUGO_CONTENT_DIR": "/tmp/test-hugo-content",
    }

    # Set test environment variables
    original_env: dict[str, str | None] = {}
    for key, value in test_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_vars

    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def test_client(test_env: dict[str, str]) -> Generator[TestClient, None, None]:
    """
    Provide a FastAPI test client.

    Args:
        test_env: Test environment fixture

    Yields:
        TestClient: FastAPI test client instance
    """
    app = create_app()
    client = TestClient(app)
    yield client


# ---------------------------------------------------------------------------
# Database fixtures for API integration tests
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_engine(
    test_env: dict[str, str],
) -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine with all tables; drop them on teardown."""
    url = make_async_url(test_env["DATABASE_URL"])
    engine = create_async_engine(url, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session; rollback uncommitted changes after the test."""
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def api_client(
    test_env: Any,
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    """
    AsyncClient wired to the dime app with:
    - get_db overridden to use the test engine
    - get_adapters overridden to return a mock AdapterSet
    """
    mock_broker: AsyncMock = AsyncMock()
    mock_adapters = AdapterSet(
        broker=mock_broker,
        filesystem=LocalFileSystemAdapter(base_path="/tmp/test-storage"),
        publishing=HugoPublishingAdapter(content_dir="/tmp/test-hugo"),
        notification=WebSocketNotificationAdapter(),
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(db_engine, expire_on_commit=False) as session:
            yield session

    def override_get_adapters() -> AdapterSet:
        return mock_adapters

    dime_app.dependency_overrides[get_db] = override_get_db
    dime_app.dependency_overrides[get_adapters] = override_get_adapters

    async with AsyncClient(
        transport=ASGITransport(app=dime_app), base_url="http://test"
    ) as client:
        yield client

    dime_app.dependency_overrides.clear()
