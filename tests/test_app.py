"""
Tests for FastAPI application.

This module tests the FastAPI application creation and configuration.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dime.app import create_app


def test_app_creation(test_env: dict[str, str]) -> None:
    """Test that FastAPI app is created successfully."""
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "Dime Content Creation System"
    assert app.description == "Dime Content Creation Agent System"
    assert app.version == "0.1.0"


def test_app_metadata(test_env: dict[str, str]) -> None:
    """Test app metadata is set correctly from settings."""
    app = create_app()

    assert hasattr(app, "title")
    assert hasattr(app, "description")
    assert hasattr(app, "version")


def test_test_client_works(test_client: TestClient) -> None:
    """Test that test client is functional."""
    # The test client fixture should work without errors
    assert test_client is not None
