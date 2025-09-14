# Settings Usage Examples

This document provides practical examples of how to use the Pydantic Settings configuration system in the Dime project.

## Overview

The Dime project uses Pydantic Settings for comprehensive configuration management with direnv integration. All configuration is centralized in `dime.config.settings` with automatic validation and environment variable loading.

## Basic Usage

### Importing Settings

```python
from dime.config import (
    get_settings,
    get_app_settings,
    get_database_settings,
    get_agent_settings,
    get_logfire_settings,
    reload_settings,
)
```

### Getting Complete Settings

```python
# Get the global settings instance
settings = get_settings()

# Access nested configuration sections
app_name = settings.app.name
database_url = settings.database.url
agent_model = settings.agent.model
```

### Getting Specific Settings Sections

```python
# Get application settings only
app_settings = get_app_settings()
debug_mode = app_settings.debug
environment = app_settings.environment

# Get database settings only
db_settings = get_database_settings()
pool_size = db_settings.pool_size
```

## FastAPI Application Integration

### Application Startup

```python
# dime/app.py
from fastapi import FastAPI
from dime.config import get_settings
import logfire

def create_app() -> FastAPI:
    """Create FastAPI application with settings integration."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.app.debug,
    )

    # Configure CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure Logfire if enabled
    if settings.logfire.send_to_logfire:
        logfire.configure(
            token=settings.get_logfire_token(),
            project_name=settings.logfire.project_name,
            environment=settings.logfire.environment,
            service_name=settings.logfire.service_name,
        )
        logfire.instrument_fastapi(app)

    return app
```

### Dependency Injection

```python
# dime/api/dependencies.py
from fastapi import Depends
from dime.config import DimeSettings, get_settings

async def get_settings_dependency() -> DimeSettings:
    """FastAPI dependency for settings injection."""
    return get_settings()

# Usage in endpoints
@router.get("/config")
async def get_config_info(settings: DimeSettings = Depends(get_settings_dependency)):
    """Get sanitized configuration information."""
    return {
        "app_name": settings.app.name,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "debug": settings.app.debug,
        "logfire_enabled": settings.logfire.send_to_logfire,
    }
```

## Database Integration

### SQLAlchemy Engine Configuration

```python
# dime/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from dime.config import get_database_settings

def create_database_engine() -> AsyncEngine:
    """Create async SQLAlchemy engine with settings."""
    db_settings = get_database_settings()

    return create_async_engine(
        str(db_settings.url),
        pool_size=db_settings.pool_size,
        pool_timeout=db_settings.pool_timeout,
        echo=db_settings.echo,
        future=True,
    )
```

### Session Factory

```python
# dime/database/session.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dime.config import get_settings

def create_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create async session factory with database settings."""
    settings = get_settings()
    engine = create_database_engine()

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

## Agent Configuration

### ADK Agent Setup

```python
# agents/dime_agent/agent.py
from google.adk import Agent
from dime.config import get_agent_settings, get_settings

def create_agent() -> Agent:
    """Create ADK agent with configuration."""
    settings = get_settings()
    agent_settings = get_agent_settings()

    return Agent(
        name=agent_settings.name,
        model=agent_settings.model,
        max_llm_calls=agent_settings.max_llm_calls,
        enable_tracing=agent_settings.enable_tracing,
        # Pass Google ADK settings
        project_id=settings.google_adk.project_id,
        location=settings.google_adk.location,
        api_key=settings.google_adk.api_key.get_secret_value(),
    )
```

### Agent Manager Integration

```python
# dime/config/agent_manager.py
from dime.config import get_settings

class DimeAgentManager:
    def __init__(self):
        self.settings = get_settings()
        self.agent_settings = self.settings.agent
        self.google_settings = self.settings.google_adk

    def validate_configuration(self) -> bool:
        """Validate agent configuration."""
        try:
            # Settings validation happens automatically
            # Additional agent-specific validation here
            return True
        except ValueError as e:
            logger.error(f"Agent configuration validation failed: {e}")
            return False
```

## Caching Integration

### Redis Client

```python
# dime/cache/redis_client.py
import redis.asyncio as redis
from dime.config import get_settings

async def create_redis_client() -> redis.Redis:
    """Create Redis client with settings."""
    settings = get_settings()

    return redis.from_url(
        str(settings.redis.url),
        max_connections=settings.redis.max_connections,
        decode_responses=True,
    )

async def get_cache_ttl() -> int:
    """Get default cache TTL from settings."""
    settings = get_settings()
    return settings.redis.cache_ttl
```

## Logging Configuration

### Logfire Setup

```python
# dime/config/logging.py
import logfire
from dime.config import get_logfire_settings

def configure_logfire():
    """Configure Logfire with settings."""
    logfire_settings = get_logfire_settings()

    if not logfire_settings.send_to_logfire:
        # Development mode - local logging only
        logfire.configure(send_to_logfire=False)
        logfire.info("Logfire configured in development mode (no token)")
        return

    # Production mode with token
    logfire.configure(
        token=logfire_settings.token.get_secret_value() if logfire_settings.token else None,
        project_name=logfire_settings.project_name,
        environment=logfire_settings.environment,
        service_name=logfire_settings.service_name,
    )

    logfire.info(
        "Logfire configured for production",
        project=logfire_settings.project_name,
        environment=logfire_settings.environment,
    )
```

### Structured Logging Examples

```python
# Using settings in logging context
from dime.config import get_settings
import logfire

def log_with_context():
    settings = get_settings()

    logfire.info(
        "Application started",
        app_name=settings.app.name,
        version=settings.app.version,
        environment=settings.app.environment,
        debug_mode=settings.app.debug,
    )
```

## Storage Configuration

### File Storage Setup

```python
# dime/services/storage.py
from pathlib import Path
from dime.config import get_settings

class StorageService:
    def __init__(self):
        self.settings = get_settings().storage
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all storage directories exist."""
        for path in [
            self.settings.base_path,
            self.settings.research_path,
            self.settings.articles_path,
            self.settings.graphics_path,
            self.settings.exports_path,
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)

    def get_research_path(self) -> Path:
        return Path(self.settings.research_path)

    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes."""
        return self.settings.max_file_size_mb * 1024 * 1024
```

## Environment-Specific Configuration

### Development vs Production

```python
# Environment-specific behavior
from dime.config import get_settings

def configure_for_environment():
    settings = get_settings()

    if settings.is_development:
        # Development configuration
        configure_debug_logging()
        enable_detailed_tracing()
        use_local_storage()
    elif settings.is_production:
        # Production configuration
        configure_performance_logging()
        enable_security_measures()
        use_cloud_storage()
```

### Feature Flags

```python
# Feature flags based on environment
from dime.config import get_settings

def is_feature_enabled(feature_name: str) -> bool:
    """Check if feature is enabled based on environment."""
    settings = get_settings()

    # Example feature flags
    features = {
        "advanced_analytics": settings.app.environment == "production",
        "debug_tools": settings.is_development,
        "tracing": settings.agent.enable_tracing,
    }

    return features.get(feature_name, False)
```

## Testing Integration

### Test Settings Override

```python
# tests/conftest.py
import pytest
from dime.config import reload_settings, DimeSettings
import os

@pytest.fixture
def test_settings():
    """Override settings for testing."""
    # Set test environment variables
    os.environ.update({
        "APP_ENVIRONMENT": "development",
        "DATABASE_URL": "postgresql://test_user:test_pass@localhost/test_db",
        "REDIS_URL": "redis://localhost:6379/1",
        "LOGFIRE_SEND_TO_LOGFIRE": "false",
    })

    # Reload settings with test values
    settings = reload_settings()
    yield settings

    # Cleanup
    reload_settings()

def test_settings_validation(test_settings):
    """Test settings validation."""
    assert test_settings.app.environment == "development"
    assert test_settings.is_development is True
    assert test_settings.logfire.send_to_logfire is False
```

### Mock Settings

```python
# tests/test_example.py
from unittest.mock import patch
from dime.config import get_settings

@patch('dime.config.get_settings')
def test_with_mock_settings(mock_get_settings):
    """Test with mocked settings."""
    mock_settings = DimeSettings(
        app=ApplicationSettings(name="Test App"),
        database=DatabaseSettings(url="postgresql://test/db"),
    )
    mock_get_settings.return_value = mock_settings

    # Test code that uses settings
    settings = get_settings()
    assert settings.app.name == "Test App"
```

## Error Handling

### Configuration Validation Errors

```python
# Handle configuration errors gracefully
from dime.config import get_settings
import sys

def safe_get_settings():
    """Get settings with error handling."""
    try:
        return get_settings()
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
        print("Please check your .envrc file and environment variables.")
        sys.exit(1)
```

### Missing Environment Variables

```python
# Check for required variables
from dime.config import get_settings

def validate_required_config():
    """Validate critical configuration is present."""
    try:
        settings = get_settings()

        # Check critical settings
        if not settings.google_adk.project_id:
            raise ValueError("GOOGLE_ADK_PROJECT_ID is required")

        if not settings.database.url:
            raise ValueError("DATABASE_URL is required")

        return True
    except Exception as e:
        print(f"Configuration error: {e}")
        return False
```

## Best Practices

### Settings Caching

```python
# Settings are cached by default, but you can reload if needed
from dime.config import reload_settings

def update_configuration():
    """Reload settings after environment changes."""
    # This forces a reload of the singleton
    new_settings = reload_settings()
    return new_settings
```

### Secret Management

```python
# Proper secret handling
from dime.config import get_settings

def get_api_key() -> str:
    """Get API key safely."""
    settings = get_settings()

    # SecretStr automatically handles secure access
    api_key = settings.google_adk.api_key.get_secret_value()

    if not api_key:
        raise ValueError("Google ADK API key not configured")

    return api_key
```

### Configuration Documentation

```python
# Document configuration requirements
from dime.config import get_settings

def print_configuration_summary():
    """Print current configuration summary."""
    settings = get_settings()

    print(f"Application: {settings.app.name} v{settings.app.version}")
    print(f"Environment: {settings.app.environment}")
    print(f"Debug Mode: {settings.app.debug}")
    print(f"Database: {settings.get_database_url(hide_password=True)}")
    print(f"Logfire: {'Enabled' if settings.logfire.send_to_logfire else 'Disabled'}")
```

This comprehensive guide covers all major use cases for the Pydantic Settings system in the Dime project. Refer to this document when implementing new features that require configuration access.