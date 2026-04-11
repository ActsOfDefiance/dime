"""
Writer Agent

Transforms approved research notes into a polished article draft.
Context (content_guide) is injected at runtime by the worker layer.
"""

from __future__ import annotations

from typing import Any

from dime.agents.base import DimeBaseAgent
from dime.agents.prompts import WRITER_PROMPT


class WriterAgent(DimeBaseAgent):
    """Agent that transforms research.md into a polished article draft.md."""

    def __init__(
        self,
        tools: list[Any] | None = None,
        content_guide: dict[str, Any] | None = None,
    ) -> None:
        instruction = WRITER_PROMPT + self.format_guide_context(
            content_guide=content_guide,
        )

        super().__init__(
            name="writer",
            model="gemini-2.5-flash",
            instruction=instruction,
            tools=tools,
        )
