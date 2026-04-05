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


class ImageWorker(BaseWorker):
    """Consumes 'image' tasks, generates image variants for a slot.

    Does NOT advance article state — the article stays in ART_GENERATING while
    the human iterates. The human approves via the API to advance to FINAL_REVIEW.
    """

    task_type = "image"

    def __init__(
        self,
        broker: BrokerAdapter,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(broker, session_factory)

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Generate image variants for one slot; return None (no state transition)."""
        slot_id = payload.get("slot_id")
        logger.info(
            "ImageWorker: generating images for article %s, slot %s",
            article.id,
            slot_id,
        )
        # ImageAgent will be added in a future agents issue.
        # Returns None — article remains in ART_GENERATING for human iteration.
        return None


def main() -> None:
    """Entry point: run the image worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    worker = ImageWorker(broker=broker, session_factory=AsyncSessionLocal)
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
