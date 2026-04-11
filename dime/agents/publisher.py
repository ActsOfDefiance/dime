"""
Publisher Agent

Coordinates the publishing step. Unlike other agents, this is not an LLM
agent — it calls the PublishingAdapter and records the publish event.
The LlmAgent base is retained for ADK compatibility.
"""

from typing import Any

from .base import DimeBaseAgent


class PublisherAgent(DimeBaseAgent):
    """Agent that coordinates publishing via the PublishingAdapter."""

    def __init__(self, sub_agents: list[Any] | None = None) -> None:
        instruction = (
            "You are the publishing coordinator. Your role is to publish "
            "approved articles using the configured publishing adapter and "
            "record the publish event."
        )

        super().__init__(
            name="publisher",
            model="gemini-2.5-flash",
            instruction=instruction,
            description="Agent that coordinates article publishing",
            sub_agents=sub_agents or [],
        )
