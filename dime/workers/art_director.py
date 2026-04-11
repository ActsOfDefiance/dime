from __future__ import annotations

import asyncio
import logging
from typing import Any


from dime.adapters.protocols import BrokerAdapter, FileSystemAdapter
from dime.agents.runner import run_agent
from dime.agents.tools.filesystem_tools import make_read_tool, make_write_tool
from dime.models.article import Article
from dime.pipeline.states import ArticleState
from dime.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ArtDirectorWorker(BaseWorker):
    """Consumes 'art_brief' tasks, runs ArtDirectorAgent, advances to ART_REVIEW."""

    task_type = "art_brief"

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Run the art director agent for *article* to generate image prompts."""
        from dime.agents.art_director import ArtDirectorAgent

        async with self._session_factory() as db:
            project = await self._load_project(db, article.project_id)
            content_guide = project.content_guide
            style_guide = project.style_guide

        tools: list[Any] = [
            make_read_tool(self._filesystem),
            make_write_tool(self._filesystem),
        ]

        agent = ArtDirectorAgent(
            tools=tools, content_guide=content_guide, style_guide=style_guide
        )

        input_text = (
            f"Create an art brief with image prompts for this article.\n\n"
            f"Title: {article.title}\n\n"
            f"Read the approved draft from '{article.slug}/draft.md' "
            f"and produce '{article.slug}/art_brief.md'."
        )

        logger.info(
            "ArtDirectorWorker: running agent for article %s — %s",
            article.id,
            article.title,
        )

        result = await run_agent(agent, input_text)
        logger.info(
            "ArtDirectorWorker: agent completed for article %s (%d chars output)",
            article.id,
            len(result),
        )

        return ArticleState.ART_REVIEW


def main() -> None:
    """Entry point: run the art director worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.adapters.filesystem.local import LocalFileSystemAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    storage_path = os.environ.get("STORAGE_BASE_PATH", "/tmp/dime-storage")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    filesystem: FileSystemAdapter = LocalFileSystemAdapter(base_path=storage_path)
    worker = ArtDirectorWorker(
        broker=broker, session_factory=AsyncSessionLocal, filesystem=filesystem
    )
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
