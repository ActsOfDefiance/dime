"""
Research Agent

Conducts web research on a given topic and produces structured research notes.
Context (content_guide) is injected at runtime by the worker layer.
"""

from .base import DimeBaseAgent
from .prompts import RESEARCH_PROMPT


class ResearcherAgent(DimeBaseAgent):
    """Agent that conducts web research and produces structured research.md."""

    def __init__(self) -> None:
        super().__init__(
            name="researcher", model="gemini-2.5-flash", instruction=RESEARCH_PROMPT
        )
