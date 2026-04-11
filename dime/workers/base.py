from __future__ import annotations

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dime.adapters.protocols import BrokerAdapter
from dime.models.article import Article
from dime.pipeline.state_machine import InvalidTransitionError, transition
from dime.pipeline.states import ArticleState

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Worker base class: consume a broker task type, run an agent, update article state.

    Subclasses implement run_task() to perform the actual agent work and return the
    target ArticleState on success.
    """

    #: Broker task type this worker consumes (e.g. "research").
    task_type: str

    def __init__(
        self,
        broker: BrokerAdapter,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._broker = broker
        self._session_factory = session_factory
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        """Signal the consume loop to exit after the current batch completes."""
        self._stop_event.set()

    @abstractmethod
    async def run_task(
        self, article: Article, payload: dict[str, Any]
    ) -> ArticleState | None:
        """Execute agent work for *article* and return the target state on success.

        Return None to leave the article state unchanged (e.g. image worker runs
        multiple times within ART_GENERATING without advancing state).
        Raise any exception on failure — BaseWorker.handle() will catch it and
        mark the article as FAILED.
        """

    async def _mark_failed(self, article_id: uuid.UUID) -> None:
        """Open a fresh session and mark *article_id* as FAILED."""
        try:
            async with self._session_factory() as fail_db:
                fail_article = await fail_db.get(Article, article_id)
                if fail_article is not None:
                    transition(fail_article.state, ArticleState.FAILED)
                    fail_article.state = ArticleState.FAILED
                    await fail_db.commit()
                    logger.info("Article %s marked as failed", article_id)
        except Exception:  # noqa: BLE001
            logger.exception("Could not mark article %s as failed", article_id)

    async def handle(self, payload: dict[str, Any]) -> None:
        """Process one task payload: run agent, apply transition, persist.

        Design note: exceptions from run_task() are caught here and the article is
        marked FAILED rather than re-raised. This is intentional — per spec, agent
        failures are permanent (the human restarts the pipeline via the API). The
        broker message is acknowledged so we avoid infinite retry loops on hard
        failures (e.g. a corrupt article record). Transient infrastructure errors
        (network timeouts, etc.) should ideally be retried inside run_task() itself.
        """
        raw_id = payload.get("article_id")
        if not raw_id:
            logger.error("Task payload missing article_id: %s", payload)
            return

        try:
            article_id = uuid.UUID(str(raw_id))
        except ValueError:
            logger.error("Task payload has invalid article_id: %s", raw_id)
            return

        async with self._session_factory() as db:
            article = await db.get(Article, article_id)
            if article is None:
                logger.error("Article not found: %s", article_id)
                return

            try:
                target_state = await self.run_task(article, payload)
                if target_state is not None:
                    transition(article.state, target_state)
                    article.state = target_state
                    await db.commit()
                    logger.info(
                        "Article %s transitioned to %s", article_id, target_state.value
                    )
                else:
                    await db.commit()
                    logger.info(
                        "Article %s: no state change (worker completed in place)",
                        article_id,
                    )
            except InvalidTransitionError as exc:
                # run_task() returned an invalid target state — treat as a worker bug
                # and mark the article FAILED so it surfaces for human review.
                logger.error(
                    "Invalid transition for article %s: %s — marking FAILED",
                    article_id,
                    exc,
                )
                await db.rollback()
                await self._mark_failed(article_id)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Agent failure for article %s: %s", article_id, exc)
                await db.rollback()
                await self._mark_failed(article_id)

    async def start(self, max_count: int = 10, block_ms: int = 5000) -> None:
        """Run the consume loop until stop() is called."""
        logger.info(
            "Worker %s started, consuming '%s'", type(self).__name__, self.task_type
        )
        while not self._stop_event.is_set():
            await self._broker.consume(
                self.task_type,
                self.handle,
                max_count=max_count,
                block_ms=block_ms,
            )
