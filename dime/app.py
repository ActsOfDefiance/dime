"""
Dime FastAPI Application

Main FastAPI application using Google ADK's get_fast_api_app() utility
for automatic agent discovery and web interface integration.
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

from dime.adapters.factory import build_adapters
from dime.api.routes import router as dime_router
from dime.config import get_settings


def create_app() -> FastAPI:
    """
    Create and configure the main FastAPI application.

    Uses ADK's get_fast_api_app() utility which provides:
    - Automatic agent discovery from agents/ directory
    - ADK web interface at root (/)
    - Developer UI at /dev-ui/
    - Session management with database
    - Health endpoints
    - CORS configuration
    """
    settings = get_settings()

    # Use ADK's official FastAPI factory with required parameters
    app: FastAPI = get_fast_api_app(
        agent_dir=os.path.join(os.path.dirname(__file__), "..", "agents"), web=True
    )

    # Compose our lifespan with ADK's existing lifespan so we don't clobber
    # any startup/shutdown behaviour that get_fast_api_app() configured.
    adk_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def composed_lifespan(a: FastAPI) -> AsyncIterator[None]:
        app.state.adapters = build_adapters(settings)
        async with adk_lifespan(a):
            yield

    app.router.lifespan_context = composed_lifespan

    # Configure app metadata
    app.title = settings.APP_NAME
    app.description = "Dime Content Creation Agent System"
    app.version = settings.APP_VERSION

    # Mount dime REST + WebSocket routes
    app.include_router(dime_router, prefix="/api/v1")

    return app


# Create the app instance
app = create_app()
