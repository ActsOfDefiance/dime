"""
Dime Application Settings

Centralized configuration management using Pydantic Settings with direnv integration.
All settings are loaded from environment variables managed by direnv (.envrc).
"""

import os
import re
from typing import Optional, List, Literal
from pydantic import Field, field_validator, SecretStr, model_validator
from pydantic.networks import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)

    url: PostgresDsn = Field(..., description="PostgreSQL database URL")
    pool_size: int = Field(default=10, description="Database connection pool size")
    pool_timeout: int = Field(
        default=30, description="Database connection timeout in seconds"
    )
    echo: bool = Field(default=False, description="Enable SQLAlchemy query logging")


class RedisSettings(BaseSettings):
    """Redis cache configuration settings."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", case_sensitive=False)

    url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    max_connections: int = Field(default=20, description="Maximum Redis connections")


class GoogleADKSettings(BaseSettings):
    """Google ADK configuration settings."""

    model_config = SettingsConfigDict(env_prefix="GOOGLE_ADK_", case_sensitive=False)

    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(default="us-central1", description="Google Cloud region")
    api_key: SecretStr = Field(..., description="Google API key for ADK")


class AgentSettings(BaseSettings):
    """ADK Agent configuration settings."""

    model_config = SettingsConfigDict(env_prefix="AGENT_", case_sensitive=False)

    name: str = Field(default="dime_agent", description="Primary agent name")
    model: str = Field(default="gemini-2.5-flash", description="Default LLM model")
    max_llm_calls: int = Field(default=500, description="Maximum LLM calls per session")
    timeout_seconds: int = Field(default=60, description="Agent operation timeout")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enable_tracing: bool = Field(default=False, description="Enable agent tracing")


class LogfireSettings(BaseSettings):
    """Logfire logging and observability settings."""

    model_config = SettingsConfigDict(env_prefix="LOGFIRE_", case_sensitive=False)

    token: Optional[SecretStr] = Field(
        default=None, description="Logfire API token (optional for development)"
    )
    project_name: str = Field(default="dime", description="Logfire project name")
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)",
    )
    service_name: str = Field(
        default="dime-app", description="Service name for logging"
    )
    send_to_logfire: bool = Field(
        default=True, description="Enable sending logs to Logfire"
    )

    @model_validator(mode="after")
    def validate_send_to_logfire(self):
        """Disable Logfire if no token provided."""
        if self.token is None or (
            isinstance(self.token, SecretStr)
            and not self.token.get_secret_value().strip()
        ):
            self.send_to_logfire = False
        return self


class AuthSettings(BaseSettings):
    """Authentication and authorization settings."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", case_sensitive=False)

    google_oauth_client_id: str = Field(..., description="Google OAuth client ID")
    google_oauth_client_secret: SecretStr = Field(
        ..., description="Google OAuth client secret"
    )
    jwt_secret_key: SecretStr = Field(..., description="JWT signing secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        description="Access token expiration time in minutes",
    )
    session_timeout: int = Field(
        default=86400,  # 24 hours
        description="Session timeout in seconds",
    )


class ApplicationSettings(BaseSettings):
    """Core application settings."""

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    name: str = Field(
        default="Dime Content Creation System", description="Application name"
    )
    version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    host: str = Field(default="0.0.0.0", description="Application host")
    port: int = Field(default=8000, description="Application port")
    allowed_origins: List[str] = Field(
        default=["http://localhost:8000", "http://localhost:3000"],
        description="CORS allowed origins",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def set_debug_for_development(self):
        """Auto-enable debug in development environment."""
        if self.environment == "development":
            self.debug = True
        return self


class StorageSettings(BaseSettings):
    """File storage configuration settings."""

    model_config = SettingsConfigDict(env_prefix="STORAGE_", case_sensitive=False)

    base_path: str = Field(
        default="./storage", description="Base storage directory path"
    )
    research_path: str = Field(
        default="./storage/research", description="Research documents storage path"
    )
    articles_path: str = Field(
        default="./storage/articles", description="Generated articles storage path"
    )
    graphics_path: str = Field(
        default="./storage/graphics", description="Generated graphics storage path"
    )
    exports_path: str = Field(
        default="./storage/exports", description="Final exports storage path"
    )
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")


class DimeSettings(BaseSettings):
    """
    Main application settings container.

    This class combines all configuration sections and provides the main
    settings interface for the Dime application.
    """

    model_config = SettingsConfigDict(case_sensitive=False, env_nested_delimiter="__")

    # Core application settings
    app: ApplicationSettings = Field(default_factory=ApplicationSettings)

    # Database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Redis cache settings
    redis: RedisSettings = Field(default_factory=RedisSettings)

    # Google ADK settings
    google_adk: GoogleADKSettings = Field(default_factory=GoogleADKSettings)

    # Agent settings
    agent: AgentSettings = Field(default_factory=AgentSettings)

    # Logfire settings
    logfire: LogfireSettings = Field(default_factory=LogfireSettings)

    # Authentication settings
    auth: AuthSettings = Field(default_factory=AuthSettings)

    # Storage settings
    storage: StorageSettings = Field(default_factory=StorageSettings)

    def __init__(self, **kwargs):
        """Initialize settings with environment validation."""
        super().__init__(**kwargs)
        self._validate_environment()
        self._ensure_storage_directories()

    def _validate_environment(self) -> None:
        """Validate critical environment configuration."""
        errors = []

        # Check required database URL
        if not self.database.url:
            errors.append("DATABASE_URL is required")

        # Check Google ADK configuration
        if not self.google_adk.project_id:
            errors.append("GOOGLE_ADK_PROJECT_ID is required")

        if (
            not self.google_adk.api_key
            or not self.google_adk.api_key.get_secret_value().strip()
        ):
            errors.append("GOOGLE_ADK_API_KEY is required")

        # Check auth secrets in production
        if self.app.environment == "production":
            if (
                not self.auth.jwt_secret_key
                or not self.auth.jwt_secret_key.get_secret_value().strip()
            ):
                errors.append("AUTH_JWT_SECRET_KEY is required in production")

            if (
                not self.auth.google_oauth_client_secret
                or not self.auth.google_oauth_client_secret.get_secret_value().strip()
            ):
                errors.append(
                    "AUTH_GOOGLE_OAUTH_CLIENT_SECRET is required in production"
                )

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

    def _ensure_storage_directories(self) -> None:
        """Ensure storage directories exist."""
        storage_paths = [
            self.storage.base_path,
            self.storage.research_path,
            self.storage.articles_path,
            self.storage.graphics_path,
            self.storage.exports_path,
        ]

        for path in storage_paths:
            os.makedirs(path, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app.environment == "production"

    def get_database_url(self, hide_password: bool = False) -> str:
        """Get database URL with optional password masking."""
        url = str(self.database.url)
        if hide_password:
            # Simple password masking for logs
            url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
        return url

    def get_logfire_token(self) -> Optional[str]:
        """Get Logfire token safely."""
        if self.logfire.token:
            return self.logfire.token.get_secret_value()
        return None


# Global settings instance
_settings: Optional[DimeSettings] = None


def get_settings() -> DimeSettings:
    """
    Get the global settings instance.

    This function implements the singleton pattern to ensure consistent
    configuration across the application.

    Returns:
        DimeSettings: The global settings instance
    """
    global _settings
    if _settings is None:
        _settings = DimeSettings()
    return _settings


def reload_settings() -> DimeSettings:
    """
    Reload settings from environment.

    Useful for testing or when environment variables change.

    Returns:
        DimeSettings: New settings instance
    """
    global _settings
    _settings = None
    return get_settings()


# Convenience aliases for commonly used settings
def get_database_settings() -> DatabaseSettings:
    """Get database settings."""
    return get_settings().database


def get_agent_settings() -> AgentSettings:
    """Get agent settings."""
    return get_settings().agent


def get_logfire_settings() -> LogfireSettings:
    """Get Logfire settings."""
    return get_settings().logfire


def get_app_settings() -> ApplicationSettings:
    """Get application settings."""
    return get_settings().app
