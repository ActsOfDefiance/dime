from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dime.adapters.protocols import BrokerAdapter, FileSystemAdapter, PublishingAdapter
from dime.agents.publisher import PublisherAgent
from dime.models.article import Article
from dime.pipeline.states import ArticleState
from dime.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class PublisherWorker(BaseWorker):
    """Consumes 'publish' tasks, calls PublisherAgent, advances to PUBLISHED."""

    task_type = "publish"

    def __init__(
        self,
        broker: BrokerAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        filesystem: FileSystemAdapter,
        publishing: PublishingAdapter,
    ) -> None:
        super().__init__(broker, session_factory, filesystem)
        self._publishing = publishing

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Publish the article via the PublishingAdapter (no LLM)."""
        agent = PublisherAgent(
            publishing=self._publishing,
            filesystem=self._filesystem,
        )

        frontmatter: dict[str, Any] = {
            "title": article.title,
            "slug": article.slug,
            "tags": article.tags,
        }
        if article.published_at:
            frontmatter["date"] = article.published_at.isoformat()

        logger.info(
            "PublisherWorker: publishing article %s — %s",
            article.id,
            article.title,
        )

        result = await agent.publish(
            article_id=article.id,
            article_slug=article.slug,
            frontmatter=frontmatter,
        )

        logger.info(
            "PublisherWorker: publish result for article %s: %s", article.id, result
        )

        return ArticleState.PUBLISHED


def main() -> None:
    """Entry point: run the publisher worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.adapters.filesystem.local import LocalFileSystemAdapter
    from dime.adapters.publishing.hugo import HugoPublishingAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    storage_path = os.environ.get("STORAGE_BASE_PATH", "/tmp/dime-storage")
    hugo_dir = os.environ.get("HUGO_CONTENT_DIR", "/tmp/hugo-content")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    filesystem: FileSystemAdapter = LocalFileSystemAdapter(base_path=storage_path)
    publishing: PublishingAdapter = HugoPublishingAdapter(content_dir=hugo_dir)
    worker = PublisherWorker(
        broker=broker,
        session_factory=AsyncSessionLocal,
        filesystem=filesystem,
        publishing=publishing,
    )
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
