"""
Publisher Agent

Coordinates the publishing step. Unlike other agents, this is not an LLM
agent — it calls the PublishingAdapter directly and records the publish event.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from dime.adapters.protocols import FileSystemAdapter, PublishingAdapter

logger = logging.getLogger(__name__)


class PublisherAgent:
    """Non-LLM agent that publishes articles via the PublishingAdapter.

    This agent is deterministic — no LLM calls. It reads the final article
    from the filesystem, calls the PublishingAdapter to emit content, and
    signals a rebuild.
    """

    def __init__(
        self,
        publishing: PublishingAdapter,
        filesystem: FileSystemAdapter,
    ) -> None:
        self._publishing = publishing
        self._filesystem = filesystem

    async def publish(
        self,
        article_id: uuid.UUID,
        article_slug: str,
        frontmatter: dict[str, Any],
    ) -> str:
        """Publish an article by reading its draft and emitting via the adapter.

        Args:
            article_id: The article's UUID.
            article_slug: The article's URL slug (used to locate files).
            frontmatter: Metadata dict for the publishing target.

        Returns:
            The preview URL if available, or a confirmation message.
        """
        draft_path = f"{article_slug}/draft.md"

        if not self._filesystem.exists(draft_path):
            msg = f"Cannot publish: draft not found at '{draft_path}'"
            logger.error(msg)
            raise FileNotFoundError(msg)

        content = self._filesystem.read(draft_path)

        await self._publishing.emit(
            article_id=article_id,
            content=content,
            frontmatter=frontmatter,
        )

        self._publishing.signal()

        preview_url = self._publishing.preview_url()
        if preview_url:
            logger.info("Published article %s — preview: %s", article_id, preview_url)
            return preview_url

        logger.info("Published article %s", article_id)
        return f"Article {article_id} published successfully."
