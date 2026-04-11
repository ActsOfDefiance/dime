"""
Image Agent

Generates image variants for a single image slot using the approved prompt
and slot specification.
"""

from .base import DimeBaseAgent
from .prompts import IMAGE_PROMPT


class ImageAgent(DimeBaseAgent):
    """Agent that generates image variants for an image slot."""

    def __init__(self) -> None:
        super().__init__(
            name="image", model="gemini-2.5-flash", instruction=IMAGE_PROMPT
        )
