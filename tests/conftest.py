"""
Pytest configuration and shared fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient


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
    }

    # Set test environment variables
    original_env = {}
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
def test_client(test_env) -> Generator[TestClient, None, None]:
    """
    Provide a FastAPI test client.

    Args:
        test_env: Test environment fixture

    Yields:
        TestClient: FastAPI test client instance
    """
    from dime.app import create_app

    app = create_app()
    client = TestClient(app)
    yield client
