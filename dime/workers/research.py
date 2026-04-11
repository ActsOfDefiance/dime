from __future__ import annotations

import asyncio
import logging
from typing import Any


from dime.adapters.protocols import BrokerAdapter, FileSystemAdapter
from dime.agents.runner import run_agent
from dime.agents.tools.filesystem_tools import make_read_tool, make_write_tool
from dime.agents.tools.search_tools import make_search_tool
from dime.models.article import Article
from dime.pipeline.states import ArticleState
from dime.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ResearchWorker(BaseWorker):
    """Consumes 'research' tasks, runs ResearcherAgent, advances to RESEARCH_REVIEW."""

    task_type = "research"

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Run the research agent for *article*."""
        from dime.agents.researcher import ResearcherAgent

        async with self._session_factory() as db:
            project = await self._load_project(db, article.project_id)
            content_guide = project.content_guide

        # Build article-scoped filesystem tools
        tools: list[Any] = [
            make_search_tool(),
            make_read_tool(self._filesystem),
            make_write_tool(self._filesystem),
        ]

        agent = ResearcherAgent(tools=tools, content_guide=content_guide)

        input_text = (
            f"Research the following topic and produce research.md:\n\n"
            f"Title: {article.title}\n\n"
            f"Topic Brief:\n{article.topic_brief}"
        )

        logger.info(
            "ResearchWorker: running agent for article %s — %s",
            article.id,
            article.title,
        )

        result = await run_agent(agent, input_text)
        logger.info(
            "ResearchWorker: agent completed for article %s (%d chars output)",
            article.id,
            len(result),
        )

        return ArticleState.RESEARCH_REVIEW


def main() -> None:
    """Entry point: run the research worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.adapters.filesystem.local import LocalFileSystemAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    storage_path = os.environ.get("STORAGE_BASE_PATH", "/tmp/dime-storage")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    filesystem: FileSystemAdapter = LocalFileSystemAdapter(base_path=storage_path)
    worker = ResearchWorker(
        broker=broker, session_factory=AsyncSessionLocal, filesystem=filesystem
    )
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
