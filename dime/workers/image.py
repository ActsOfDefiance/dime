from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any


from dime.adapters.protocols import BrokerAdapter, FileSystemAdapter
from dime.agents.runner import run_agent
from dime.agents.tools.filesystem_tools import make_write_tool
from dime.agents.image import ImageAgent
from dime.agents.tools.image_tools import make_image_generation_tool
from dime.models.article import Article
from dime.models.image_slot import ImageSlot
from dime.pipeline.states import ArticleState
from dime.workers.base import BaseWorker

logger = logging.getLogger(__name__)


class ImageWorker(BaseWorker):
    """Consumes 'image' tasks, generates image variants for a slot.

    Does NOT advance article state — the article stays in ART_GENERATING while
    the human iterates. The human approves via the API to advance to FINAL_REVIEW.
    """

    task_type = "image"

    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Generate image variants for one slot; return None (no state transition)."""
        raw_slot_id = payload.get("slot_id")
        if not raw_slot_id:
            raise ValueError("Image task payload missing slot_id")

        slot_id = uuid.UUID(str(raw_slot_id))

        # Load slot and project in a fresh session
        async with self._session_factory() as db:
            slot = await db.get(ImageSlot, slot_id)
            if slot is None:
                raise ValueError(f"ImageSlot not found: {slot_id}")

            project = await self._load_project(db, article.project_id)
            style_guide = project.style_guide

        tools: list[Any] = [
            make_image_generation_tool(article.slug, slot.slot_name),
            make_write_tool(self._filesystem),
        ]

        agent = ImageAgent(tools=tools, style_guide=style_guide)

        input_text = (
            f"Generate image variants for the following slot:\n\n"
            f"Slot: {slot.slot_name}\n"
            f"Dimensions: {slot.width}x{slot.height}\n"
            f"Format: {slot.format}\n"
            f"Prompt: {slot.approved_prompt or 'No approved prompt — use your judgment based on the article.'}\n"
        )

        logger.info(
            "ImageWorker: generating images for article %s, slot %s (%s)",
            article.id,
            slot_id,
            slot.slot_name,
        )

        result = await run_agent(agent, input_text)
        logger.info(
            "ImageWorker: agent completed for article %s, slot %s (%d chars output)",
            article.id,
            slot_id,
            len(result),
        )

        # Returns None — article remains in ART_GENERATING for human iteration.
        return None


def main() -> None:
    """Entry point: run the image worker as a standalone process."""
    import os

    from dime.adapters.broker.redis import RedisBrokerAdapter
    from dime.adapters.filesystem.local import LocalFileSystemAdapter
    from dime.db import AsyncSessionLocal

    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    storage_path = os.environ.get("STORAGE_BASE_PATH", "/tmp/dime-storage")
    broker: BrokerAdapter = RedisBrokerAdapter(url=redis_url)
    filesystem: FileSystemAdapter = LocalFileSystemAdapter(base_path=storage_path)
    worker = ImageWorker(
        broker=broker, session_factory=AsyncSessionLocal, filesystem=filesystem
    )
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
