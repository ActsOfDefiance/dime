"""
Base Agent Classes

Common functionality and base classes for Dime agents.
"""

from typing import Dict, Any
from google.adk.agents import LlmAgent


class DimeBaseAgent(LlmAgent):
    """Base class for all Dime agents with common functionality."""

    def __init__(
        self,
        name: str,
        model: str = "gemini-2.5-flash",
        instruction: str = "",
        **kwargs: Any,
    ) -> None:
        """Initialize base agent with common settings."""
        super().__init__(name=name, model=model, instruction=instruction, **kwargs)  # pyright: ignore[reportUnknownMemberType]

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for debugging and monitoring."""
        return {
            "name": self.name,
            "model": self.model,
            "type": self.__class__.__name__,
            "status": "active",
        }
