"""
Art Director Agent

Creates image generation prompts for each image slot based on the approved
article draft and the project's style guide.
"""

from __future__ import annotations

from typing import Any

from dime.agents.base import DimeBaseAgent
from dime.agents.prompts import ART_DIRECTOR_PROMPT


class ArtDirectorAgent(DimeBaseAgent):
    """Agent that produces art_brief.md with per-slot image prompts."""

    def __init__(
        self,
        tools: list[Any] | None = None,
        content_guide: dict[str, Any] | None = None,
        style_guide: dict[str, Any] | None = None,
    ) -> None:
        instruction = ART_DIRECTOR_PROMPT + self.format_guide_context(
            content_guide=content_guide,
            style_guide=style_guide,
        )

        super().__init__(
            name="art_director",
            model="gemini-2.5-flash",
            instruction=instruction,
            tools=tools,
        )
