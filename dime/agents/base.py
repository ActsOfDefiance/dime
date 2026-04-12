"""
Base Agent Classes

Common functionality and base classes for Dime agents.
"""

from __future__ import annotations

import json
from typing import Any

from google.adk.agents import LlmAgent


class DimeBaseAgent(LlmAgent):
    """Base class for all Dime agents with common functionality."""

    def __init__(
        self,
        name: str,
        model: str = "gemini-2.5-flash",
        instruction: str = "",
        tools: list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize base agent with common settings."""
        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            name=name,
            model=model,
            instruction=instruction,
            tools=tools or [],
            **kwargs,
        )

    def get_agent_info(self) -> dict[str, Any]:
        """Get agent information for debugging and monitoring."""
        return {
            "name": self.name,
            "model": self.model,
            "type": self.__class__.__name__,
            "status": "active",
        }

    @staticmethod
    def format_guide_context(
        content_guide: dict[str, Any] | None = None,
        style_guide: dict[str, Any] | None = None,
    ) -> str:
        """Format content_guide and/or style_guide as context to append to instructions.

        Args:
            content_guide: The project's content guide (audience, voice, standards).
            style_guide: The project's style guide (image slots, visual tokens).

        Returns:
            A formatted string to append to the agent's instruction.
        """
        parts: list[str] = []
        if content_guide:
            parts.append(
                "\n\n---\n## Content Guide (from project configuration)\n\n"
                f"```json\n{json.dumps(content_guide, indent=2)}\n```"
            )
        if style_guide:
            parts.append(
                "\n\n---\n## Style Guide (from project configuration)\n\n"
                f"```json\n{json.dumps(style_guide, indent=2)}\n```"
            )
        return "".join(parts)
