"""
Tests for CLI interface.

This module tests the command-line interface commands.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from dime.__main__ import main


def test_health_command(
    test_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    """Test the health command output."""
    with patch.object(sys, "argv", ["dime", "health"]):
        main()

    captured = capsys.readouterr()
    assert "✅ Configuration loaded successfully" in captured.out
    assert "📁 Database:" in captured.out
    assert "🤖 Agent:" in captured.out
    assert "🌍 Environment:" in captured.out


def test_health_command_masks_password(
    test_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that health command masks database password."""
    with patch.object(sys, "argv", ["dime", "health"]):
        main()

    captured = capsys.readouterr()
    assert "***" in captured.out
    assert "test_pass" not in captured.out


@patch("dime.__main__.uvicorn.run")
def test_start_command_with_defaults(
    mock_uvicorn: MagicMock, test_env: dict[str, str]
) -> None:
    """Test start command uses default host and port."""
    with patch.object(sys, "argv", ["dime", "start"]):
        main()

    mock_uvicorn.assert_called_once()
    call_kwargs = mock_uvicorn.call_args[1]
    assert call_kwargs["host"] == "0.0.0.0"
    assert call_kwargs["port"] == 8000


@patch("dime.__main__.uvicorn.run")
def test_start_command_with_custom_host_port(
    mock_uvicorn: MagicMock, test_env: dict[str, str]
) -> None:
    """Test start command with custom host and port."""
    with patch.object(
        sys, "argv", ["dime", "start", "--host", "127.0.0.1", "--port", "3000"]
    ):
        main()

    mock_uvicorn.assert_called_once()
    call_kwargs = mock_uvicorn.call_args[1]
    assert call_kwargs["host"] == "127.0.0.1"
    assert call_kwargs["port"] == 3000


@patch("dime.__main__.uvicorn.run")
def test_start_command_default_is_start(
    mock_uvicorn: MagicMock, test_env: dict[str, str]
) -> None:
    """Test that default command is 'start' when no command specified."""
    with patch.object(sys, "argv", ["dime"]):
        main()

    mock_uvicorn.assert_called_once()
