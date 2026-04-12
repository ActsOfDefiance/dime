"""
Researcher Agent

Conducts web research on a given topic and produces structured research
notes in markdown. Context (content_guide) is injected at runtime by
the worker layer.
"""

from __future__ import annotations

from typing import Any

from dime.agents.base import DimeBaseAgent
from dime.agents.prompts import RESEARCH_PROMPT


class ResearcherAgent(DimeBaseAgent):
    """Agent that conducts web research and produces research.md."""

    def __init__(
        self,
        tools: list[Any] | None = None,
        content_guide: dict[str, Any] | None = None,
    ) -> None:
        instruction = RESEARCH_PROMPT + self.format_guide_context(
            content_guide=content_guide,
        )

        super().__init__(
            name="researcher",
            model="gemini-2.5-flash",
            instruction=instruction,
            tools=tools,
        )
