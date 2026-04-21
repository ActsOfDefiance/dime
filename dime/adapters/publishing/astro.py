"""
Astro publishing adapter.

Implements PublishingAdapter for the acts-of-defiance Astro site.
Copies images from the local art/ directory into the Astro public/images/
directory and writes a signal file to trigger an Astro build.

Markdown is NOT copied — Astro reads directly from compendium/ at build
time (DECISION-012). Images come from the local art/ filesystem (DECISION-013).
"""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AstroAdapter:
    """PublishingAdapter for the acts-of-defiance Astro site.

    Copies article images from art/{slug}/ into the Astro public images
    directory and touches a signal file to trigger a site rebuild.
    """

    def __init__(
        self,
        art_dir: str,
        acts_of_defiance_public_dir: str,
        signal_file_path: str,
        content_base: str = "",
        preview_host: str = "",
    ) -> None:
        self._art_dir = Path(art_dir)
        self._public_dir = Path(acts_of_defiance_public_dir)
        self._signal_file = Path(signal_file_path)
        self._content_base = content_base
        self._preview_host = preview_host

    async def emit(
        self,
        article_id: uuid.UUID,
        content: str,
        frontmatter: dict[str, Any],
    ) -> None:
        """Copy article images into the Astro public directory.

        Markdown is not touched — Astro reads compendium/ directly at build
        time. Only images referenced in frontmatter['images'] are copied.

        Args:
            article_id: Article UUID (unused — slug comes from frontmatter).
            content: Article markdown body (unused — already in compendium/).
            frontmatter: Article frontmatter dict; must include 'slug' and
                optionally 'images' with filenames sourced from art/.
        """
        slug: str = frontmatter.get("slug", str(article_id))
        images: dict[str, Any] = frontmatter.get("images", {})

        if not images:
            logger.info("AstroAdapter.emit: no images in frontmatter for %s", slug)
            return

        dest_dir = self._public_dir / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        for slot_name, filename in images.items():
            if not filename:
                continue
            src = self._art_dir / slug / filename
            if not src.exists():
                logger.warning(
                    "AstroAdapter.emit: image not found — %s (slot: %s, article: %s)",
                    src,
                    slot_name,
                    slug,
                )
                continue
            dest = dest_dir / filename
            shutil.copy2(src, dest)
            logger.info("AstroAdapter.emit: copied %s → %s", src, dest)

    def signal(self) -> None:
        """Touch the signal file to trigger an Astro build."""
        self._signal_file.parent.mkdir(parents=True, exist_ok=True)
        self._signal_file.touch()
        logger.info("AstroAdapter.signal: touched %s", self._signal_file)

    def preview_url(self) -> str | None:
        """Return the local Astro dev server URL, or None if not configured."""
        if not self._preview_host:
            return None
        return f"http://{self._preview_host}"
