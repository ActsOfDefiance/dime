"""
Dime Configuration Module

This module provides centralized configuration management for the Dime application
using Pydantic Settings with direnv integration.

Main components:
- DimeSettings: Main configuration class
- get_settings(): Global settings accessor
- Environment-specific settings classes
"""

from .settings import (
    DimeSettings,
    ApplicationSettings,
    DatabaseSettings,
    RedisSettings,
    GoogleADKSettings,
    AgentSettings,
    LogfireSettings,
    AuthSettings,
    StorageSettings,
    get_settings,
    reload_settings,
    get_database_settings,
    get_agent_settings,
    get_logfire_settings,
    get_app_settings,
)

__all__ = [
    "DimeSettings",
    "ApplicationSettings",
    "DatabaseSettings",
    "RedisSettings",
    "GoogleADKSettings",
    "AgentSettings",
    "LogfireSettings",
    "AuthSettings",
    "StorageSettings",
    "get_settings",
    "reload_settings",
    "get_database_settings",
    "get_agent_settings",
    "get_logfire_settings",
    "get_app_settings",
]
