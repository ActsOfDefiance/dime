"""
Tests for configuration module.

This module tests the settings validation and configuration loading.
"""

import os
import pytest
from dime.config import reload_settings


def test_settings_loads_from_environment(test_env):
    """Test that settings load correctly from environment variables."""
    settings = reload_settings()

    assert settings.DATABASE_URL is not None
    assert settings.GOOGLE_ADK_PROJECT_ID == "test-project"
    assert settings.APP_ENVIRONMENT == "development"
    assert settings.APP_DEBUG is True  # Auto-enabled in development


def test_settings_database_url_masking(test_env):
    """Test database URL password masking."""
    settings = reload_settings()

    masked_url = settings.get_database_url(hide_password=True)
    assert "***" in masked_url
    assert "test_pass" not in masked_url


def test_settings_allowed_origins_parsing(test_env):
    """Test APP_ALLOWED_ORIGINS parsing from string."""
    os.environ["APP_ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8000"
    settings = reload_settings()

    assert len(settings.APP_ALLOWED_ORIGINS) == 2
    assert "http://localhost:3000" in settings.APP_ALLOWED_ORIGINS
    assert "http://localhost:8000" in settings.APP_ALLOWED_ORIGINS


def test_settings_logfire_disabled_without_token(test_env):
    """Test that Logfire is disabled when no token is provided."""
    os.environ["LOGFIRE_TOKEN"] = ""
    settings = reload_settings()

    assert settings.LOGFIRE_SEND_TO_LOGFIRE is False


def test_settings_development_debug_auto_enabled(test_env):
    """Test that debug is auto-enabled in development."""
    os.environ["APP_ENVIRONMENT"] = "development"
    os.environ["APP_DEBUG"] = "false"
    settings = reload_settings()

    assert settings.APP_DEBUG is True


def test_settings_validation_requires_database_url():
    """Test that DATABASE_URL is required."""
    from pydantic import ValidationError

    # Remove DATABASE_URL
    original_url = os.environ.pop("DATABASE_URL", None)

    try:
        with pytest.raises(ValidationError):
            reload_settings()
    finally:
        if original_url:
            os.environ["DATABASE_URL"] = original_url


def test_settings_validation_requires_google_adk_config():
    """Test that Google ADK configuration is required."""
    from pydantic import ValidationError

    original_project_id = os.environ.pop("GOOGLE_ADK_PROJECT_ID", None)

    try:
        with pytest.raises(ValidationError):
            reload_settings()
    finally:
        if original_project_id:
            os.environ["GOOGLE_ADK_PROJECT_ID"] = original_project_id
