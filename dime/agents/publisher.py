"""
Publisher Agent

Main coordinator agent for the content creation system.
Manages the research and writing workflow for political liberation content.
"""

from .base import DimeBaseAgent
from typing import List, Any


class PublisherAgent(DimeBaseAgent):
    """Agent that coordinates research and writing for political liberation content."""

    def __init__(self, sub_agents: List[Any] | None = None) -> None:
        """Initialize publisher agent with specialized instruction."""
        instruction = (
            "You are the publisher of a journal which focuses on the history of liberation struggles. "
            "Your journal cares deeply about citing sources and accuracy, as such you require vigorous "
            "research to be done and on any topic before producing an article. However your target audience "
            "is the common man and so the output research needs to be condensed down into blog articles. "
        )

        super().__init__(
            name="publisher",
            model="gemini-2.0-flash",
            instruction=instruction,
            description="Agent that coordinates research and writing for political liberation content",
            sub_agents=sub_agents or [],
        )
