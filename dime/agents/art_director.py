"""
Art Director Agent

Creates image generation prompts for each image slot based on the approved
article draft and the project's style guide.
"""

from .base import DimeBaseAgent
from .prompts import ART_DIRECTOR_PROMPT


class ArtDirectorAgent(DimeBaseAgent):
    """Agent that produces art_brief.md with per-slot image prompts."""

    def __init__(self) -> None:
        super().__init__(
            name="art_director",
            model="gemini-2.5-flash",
            instruction=ART_DIRECTOR_PROMPT,
        )
