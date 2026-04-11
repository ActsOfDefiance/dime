from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dime.adapters.protocols import BrokerAdapter
from dime.models.article import Article
from dime.pipeline.states import ArticleState
from dime.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ArtDirectorWorker(BaseWorker):
    """Consumes 'art_brief' tasks, runs ArtDirectorAgent, advances to ART_REVIEW."""

    task_type = "art_brief"

    def __init__(
        self,
        broker: BrokerAdapter,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(broker, session_factory)

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Run the art director agent for *article* to generate image prompts."""
        logger.info(
            "ArtDirectorWorker: running agent for article %s — %s",
            article.id,
            article.title,
        )
        # ArtDirectorAgent will be added in a future agents issue.
        return ArticleState.ART_REVIEW


def main() -> None:
    """Entry point: run the art director worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    worker = ArtDirectorWorker(broker=broker, session_factory=AsyncSessionLocal)
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
