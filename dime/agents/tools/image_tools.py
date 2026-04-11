"""
Image generation tools for agents.

Provides a stub image generation tool. The real Imagen 3 integration
is a deployment concern — this module defines the tool interface.
"""

from __future__ import annotations

import uuid


def make_image_generation_tool(article_slug: str, slot_name: str) -> object:
    """Create an image generation tool for a specific image slot.

    Args:
        article_slug: The article's URL slug, used for output path.
        slot_name: The image slot name (e.g. "hero", "thumbnail").
    """

    def generate_image(
        prompt: str, width: int, height: int, image_format: str = "png"
    ) -> str:
        """Generate an image from a text prompt.

        Args:
            prompt: Detailed image generation prompt.
            width: Target image width in pixels.
            height: Target image height in pixels.
            image_format: Output format (png, jpg, webp).

        Returns:
            The file path where the generated image was saved,
            or an error message if generation failed.
        """
        variant_id = uuid.uuid4().hex[:8]
        output_path = (
            f"art/{article_slug}/{slot_name}/variant_{variant_id}.{image_format}"
        )

        # Stub: in production, this calls Imagen 3 or similar API.
        # The stub returns the path that *would* be used, allowing the
        # rest of the pipeline to proceed for testing.
        return (
            f"[Image generation stub] Would generate {width}x{height} "
            f"{image_format} image at '{output_path}'. "
            f"Prompt: {prompt[:100]}..."
        )

    return generate_image
