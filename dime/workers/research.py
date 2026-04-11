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


class ResearchWorker(BaseWorker):
    """Consumes 'research' tasks, runs ResearcherAgent, advances to RESEARCH_REVIEW."""

    task_type = "research"

    def __init__(
        self,
        broker: BrokerAdapter,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(broker, session_factory)

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Run the research agent for *article*."""
        from dime.agents.researcher import ResearcherAgent  # noqa: PLC0415

        agent = ResearcherAgent()
        logger.info(
            "ResearchWorker: running agent for article %s — %s",
            article.id,
            article.title,
        )
        # Agent execution via ADK is intentionally thin here; the agent infrastructure
        # (tools, filesystem writes) will be fleshed out in a future issue.
        _ = agent  # agent instance created; real runner invocation is a future concern
        return ArticleState.RESEARCH_REVIEW


def main() -> None:
    """Entry point: run the research worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    worker = ResearchWorker(broker=broker, session_factory=AsyncSessionLocal)
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
