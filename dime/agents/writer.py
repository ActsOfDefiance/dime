"""
Writer Agent

Transforms approved research notes into a polished article draft.
Context (content_guide) is injected at runtime by the worker layer.
"""

from .base import DimeBaseAgent
from .prompts import WRITER_PROMPT


class WriterAgent(DimeBaseAgent):
    """Agent that transforms research.md into a polished article draft.md."""

    def __init__(self) -> None:
        super().__init__(
            name="writer", model="gemini-2.5-flash", instruction=WRITER_PROMPT
        )
