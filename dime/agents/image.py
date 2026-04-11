"""
Image Agent

Generates image variants for a single image slot using the approved prompt
and slot specification.
"""

from __future__ import annotations

from typing import Any

from dime.agents.base import DimeBaseAgent
from dime.agents.prompts import IMAGE_PROMPT


class ImageAgent(DimeBaseAgent):
    """Agent that generates image variants for an image slot."""

    def __init__(
        self,
        tools: list[Any] | None = None,
        style_guide: dict[str, Any] | None = None,
    ) -> None:
        instruction = IMAGE_PROMPT + self.format_guide_context(
            style_guide=style_guide,
        )

        super().__init__(
            name="image",
            model="gemini-2.5-flash",
            instruction=instruction,
            tools=tools,
        )
