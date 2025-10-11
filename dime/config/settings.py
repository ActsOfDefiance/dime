"""
Dime Application Settings

Centralized configuration management using Pydantic Settings with direnv integration.
All settings are loaded from environment variables managed by direnv (.envrc).
"""

import os
import re
from typing import Optional, List, Literal, Annotated, Union
from pydantic import Field, field_validator, SecretStr, model_validator
from pydantic.networks import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode


class DimeSettings(BaseSettings):
    """
    Main application settings container.

    Uses automatic field-to-environment-variable mapping:
    - database_url → DATABASE_URL
    - google_adk_project_id → GOOGLE_ADK_PROJECT_ID
    - app_allowed_origins → APP_ALLOWED_ORIGINS
    etc.
    """

    model_config = SettingsConfigDict(case_sensitive=True, env_nested_delimiter="__")

    # ==========================================================================
    # Database Configuration
    # ==========================================================================
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ==========================================================================
    # Redis Cache Configuration
    # ==========================================================================
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_MAX_CONNECTIONS: int = 20

    # ==========================================================================
    # Google ADK Configuration
    # ==========================================================================
    GOOGLE_ADK_PROJECT_ID: str
    GOOGLE_ADK_LOCATION: str = "us-central1"
    GOOGLE_ADK_API_KEY: SecretStr

    # ==========================================================================
    # Agent Configuration
    # ==========================================================================
    AGENT_NAME: str = "dime_agent"
    AGENT_MODEL: str = "gemini-2.5-flash"
    AGENT_MAX_LLM_CALLS: int = 500
    AGENT_TIMEOUT_SECONDS: int = 60
    AGENT_MAX_RETRIES: int = 3
    AGENT_ENABLE_TRACING: bool = False

    # ==========================================================================
    # Logfire Configuration
    # ==========================================================================
    LOGFIRE_TOKEN: Optional[SecretStr] = None
    LOGFIRE_PROJECT_NAME: str = "dime"
    LOGFIRE_ENVIRONMENT: str = "development"
    LOGFIRE_SERVICE_NAME: str = "dime-app"
    LOGFIRE_SEND_TO_LOGFIRE: bool = True

    @model_validator(mode="after")
    def validate_send_to_logfire(self):
        """Disable Logfire if no token provided."""
        if self.LOGFIRE_TOKEN is None or (
            isinstance(self.LOGFIRE_TOKEN, SecretStr)
            and not self.LOGFIRE_TOKEN.get_secret_value().strip()
        ):
            self.LOGFIRE_SEND_TO_LOGFIRE = False
        return self

    # ==========================================================================
    # Authentication Configuration
    # ==========================================================================
    AUTH_GOOGLE_OAUTH_CLIENT_ID: str
    AUTH_GOOGLE_OAUTH_CLIENT_SECRET: SecretStr
    AUTH_JWT_SECRET_KEY: SecretStr
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    AUTH_SESSION_TIMEOUT: int = 86400  # 24 hours

    # ==========================================================================
    # Application Configuration
    # ==========================================================================
    APP_NAME: str = "Dime Content Creation System"
    APP_VERSION: str = "0.1.0"
    APP_ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = False
    APP_LOG_LEVEL: str = "INFO"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Only use Field() where we need special handling
    APP_ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = Field(
        default=["http://localhost:8000", "http://localhost:3000"]
    )

    @field_validator("APP_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse allowed origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError(
                f"APP_ALLOWED_ORIGINS must be a string or list, got {type(v)}"
            )

    @model_validator(mode="after")
    def set_debug_for_development(self):
        """Auto-enable debug in development environment."""
        if self.APP_ENVIRONMENT == "development":
            self.APP_DEBUG = True
        return self

    # ==========================================================================
    # Storage Configuration
    # ==========================================================================
    STORAGE_BASE_PATH: str = "./storage"
    STORAGE_RESEARCH_PATH: str = "./storage/research"
    STORAGE_ARTICLES_PATH: str = "./storage/articles"
    STORAGE_GRAPHICS_PATH: str = "./storage/graphics"
    STORAGE_EXPORTS_PATH: str = "./storage/exports"
    STORAGE_MAX_FILE_SIZE_MB: int = 50

    def __init__(self, **kwargs):
        """Initialize settings with environment validation."""
        super().__init__(**kwargs)
        self._validate_environment()
        self._ensure_storage_directories()

    def _validate_environment(self) -> None:
        """Validate critical environment configuration."""
        errors = []

        # Check required database URL
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")

        # Check Google ADK configuration
        if not self.GOOGLE_ADK_PROJECT_ID:
            errors.append("GOOGLE_ADK_PROJECT_ID is required")

        if (
            not self.GOOGLE_ADK_API_KEY
            or not self.GOOGLE_ADK_API_KEY.get_secret_value().strip()
        ):
            errors.append("GOOGLE_ADK_API_KEY is required")

        # Check auth secrets in production
        if self.APP_ENVIRONMENT == "production":
            if (
                not self.AUTH_JWT_SECRET_KEY
                or not self.AUTH_JWT_SECRET_KEY.get_secret_value().strip()
            ):
                errors.append("AUTH_JWT_SECRET_KEY is required in production")

            if (
                not self.AUTH_GOOGLE_OAUTH_CLIENT_SECRET
                or not self.AUTH_GOOGLE_OAUTH_CLIENT_SECRET.get_secret_value().strip()
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
            self.STORAGE_BASE_PATH,
            self.STORAGE_RESEARCH_PATH,
            self.STORAGE_ARTICLES_PATH,
            self.STORAGE_GRAPHICS_PATH,
            self.STORAGE_EXPORTS_PATH,
        ]

        for path in storage_paths:
            os.makedirs(path, exist_ok=True)

    # ==========================================================================
    # Convenience Properties
    # ==========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENVIRONMENT == "production"

    def get_database_url(self, hide_password: bool = False) -> str:
        """Get database URL with optional password masking."""
        url = str(self.DATABASE_URL)
        if hide_password:
            # Simple password masking for logs
            url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
        return url

    def get_logfire_token(self) -> Optional[str]:
        """Get Logfire token safely."""
        if self.LOGFIRE_TOKEN:
            return self.LOGFIRE_TOKEN.get_secret_value()
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


# Convenience functions for backward compatibility
def get_database_settings() -> DimeSettings:
    """Get database settings (returns main settings for compatibility)."""
    return get_settings()


def get_agent_settings() -> DimeSettings:
    """Get agent settings (returns main settings for compatibility)."""
    return get_settings()


def get_logfire_settings() -> DimeSettings:
    """Get Logfire settings (returns main settings for compatibility)."""
    return get_settings()


def get_app_settings() -> DimeSettings:
    """Get application settings (returns main settings for compatibility)."""
    return get_settings()
