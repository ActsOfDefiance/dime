"""Tests for the worker layer.

Unit tests (no markers) use mocks and run in the default test suite.
Integration tests (@pytest.mark.integration) require a real Redis broker.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dime.models.article import Article
from dime.pipeline.states import ArticleState
from dime.workers.art_director import ArtDirectorWorker
from dime.workers.base import BaseWorker
from dime.workers.image import ImageWorker
from dime.workers.publisher import PublisherWorker
from dime.workers.research import ResearchWorker
from dime.workers.writing import WritingWorker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_article(
    state: ArticleState = ArticleState.RESEARCHING,
    article_id: uuid.UUID | None = None,
) -> Article:
    return Article(
        id=article_id or uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="Test Article",
        slug="test-article",
        state=state,
        topic_brief="Test topic",
        tags=[],
        created_at=datetime.now(timezone.utc),
    )


def _make_session_factory(article: Article | None) -> Any:
    """Return a mock async_sessionmaker that yields a session returning *article* on .get()."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get = AsyncMock(return_value=article)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock()
    mock_factory.return_value = mock_cm
    return mock_factory


def _make_worker(
    cls: type[BaseWorker],
    article: Article | None,
) -> tuple[Any, Any]:
    """Return (worker, mock_broker)."""
    broker = AsyncMock()
    factory = _make_session_factory(article)
    worker = cls(broker=broker, session_factory=factory)
    return worker, broker


# ---------------------------------------------------------------------------
# ResearchWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestResearchWorker:
    async def test_happy_path_transitions_to_research_review(self) -> None:
        article = _make_article(state=ArticleState.RESEARCHING)
        worker, _ = _make_worker(ResearchWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.RESEARCH_REVIEW

    async def test_missing_article_id_does_not_crash(self) -> None:
        worker, _ = _make_worker(ResearchWorker, None)
        await worker.handle({})  # no exception

    async def test_invalid_article_id_does_not_crash(self) -> None:
        worker, _ = _make_worker(ResearchWorker, None)
        await worker.handle({"article_id": "not-a-uuid"})  # no exception

    async def test_article_not_found_does_not_crash(self) -> None:
        worker, _ = _make_worker(ResearchWorker, None)
        await worker.handle({"article_id": str(uuid.uuid4())})  # no exception


# ---------------------------------------------------------------------------
# WritingWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestWritingWorker:
    async def test_happy_path_transitions_to_draft_review(self) -> None:
        article = _make_article(state=ArticleState.WRITING)
        worker, _ = _make_worker(WritingWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.DRAFT_REVIEW


# ---------------------------------------------------------------------------
# ArtDirectorWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestArtDirectorWorker:
    async def test_happy_path_transitions_to_art_review(self) -> None:
        article = _make_article(state=ArticleState.ART_BRIEFING)
        worker, _ = _make_worker(ArtDirectorWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.ART_REVIEW


# ---------------------------------------------------------------------------
# ImageWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestImageWorker:
    async def test_no_state_change(self) -> None:
        """ImageWorker runs but leaves article in ART_GENERATING."""
        article = _make_article(state=ArticleState.ART_GENERATING)
        worker, _ = _make_worker(ImageWorker, article)

        await worker.handle(
            {"article_id": str(article.id), "slot_id": str(uuid.uuid4())}
        )

        assert article.state is ArticleState.ART_GENERATING

    async def test_no_db_commit_on_no_state_change(self) -> None:
        article = _make_article(state=ArticleState.ART_GENERATING)
        broker = AsyncMock()
        factory = _make_session_factory(article)
        worker = ImageWorker(broker=broker, session_factory=factory)

        await worker.handle({"article_id": str(article.id)})

        # Session commit should NOT have been called — no state change
        session = factory.return_value.__aenter__.return_value
        session.commit.assert_not_called()


# ---------------------------------------------------------------------------
# PublisherWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestPublisherWorker:
    async def test_happy_path_transitions_to_published(self) -> None:
        article = _make_article(state=ArticleState.PUBLISHING)
        worker, _ = _make_worker(PublisherWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.PUBLISHED


# ---------------------------------------------------------------------------
# BaseWorker error handling tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestBaseWorkerErrorHandling:
    async def test_agent_failure_marks_article_failed(self) -> None:
        """When run_task raises, the article should be marked FAILED."""
        article = _make_article(state=ArticleState.RESEARCHING)
        worker, _ = _make_worker(ResearchWorker, article)

        async def bad_run_task(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            raise RuntimeError("Gemini API error")

        worker.run_task = bad_run_task  # type: ignore[method-assign]

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.FAILED

    async def test_agent_failure_does_not_crash(self) -> None:
        """Worker loop must survive agent failures."""
        article = _make_article(state=ArticleState.RESEARCHING)
        worker, _ = _make_worker(ResearchWorker, article)

        async def bad_run_task(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            raise ValueError("unexpected error")

        worker.run_task = bad_run_task  # type: ignore[method-assign]

        # Should complete without raising
        await worker.handle({"article_id": str(article.id)})

    async def test_invalid_transition_marks_article_failed(self) -> None:
        """If run_task returns an invalid target state, the article is marked FAILED."""
        article = _make_article(
            state=ArticleState.QUEUED
        )  # QUEUED → PUBLISHED is invalid
        worker, _ = _make_worker(ResearchWorker, article)

        async def bad_transition(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            return ArticleState.PUBLISHED  # invalid from QUEUED

        worker.run_task = bad_transition  # type: ignore[method-assign]

        await worker.handle({"article_id": str(article.id)})

        # Article should be marked FAILED (invalid transition = worker logic bug)
        assert article.state is ArticleState.FAILED

    async def test_failure_during_failed_mark_does_not_crash(self) -> None:
        """If marking the article as FAILED also fails, the worker should not crash."""
        article = _make_article(state=ArticleState.RESEARCHING)
        broker = AsyncMock()

        # First session: article found, run_task raises
        session1 = AsyncMock(spec=AsyncSession)
        session1.get = AsyncMock(return_value=article)
        session1.rollback = AsyncMock()
        cm1 = MagicMock()
        cm1.__aenter__ = AsyncMock(return_value=session1)
        cm1.__aexit__ = AsyncMock(return_value=False)

        # Second session (failure path): also raises
        session2 = AsyncMock(spec=AsyncSession)
        session2.get = AsyncMock(side_effect=RuntimeError("DB down"))
        cm2 = MagicMock()
        cm2.__aenter__ = AsyncMock(return_value=session2)
        cm2.__aexit__ = AsyncMock(return_value=False)

        factory = MagicMock()
        factory.side_effect = [cm1, cm2]

        worker = ResearchWorker(broker=broker, session_factory=factory)

        async def bad_run_task(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            raise RuntimeError("agent crashed")

        worker.run_task = bad_run_task  # type: ignore[method-assign]

        # Should complete without raising
        await worker.handle({"article_id": str(article.id)})

    async def test_stop_event_prevents_additional_iterations(self) -> None:
        """stop() should cause the consume loop to exit after the current batch."""
        broker = AsyncMock()
        broker.consume = AsyncMock()
        factory = _make_session_factory(None)
        worker = ResearchWorker(broker=broker, session_factory=factory)

        # stop() before start() means the loop body never executes
        worker.stop()
        await worker.start()

        broker.consume.assert_not_called()


# ---------------------------------------------------------------------------
# Integration tests — real Redis broker
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
class TestResearchWorkerIntegration:
    async def test_consumes_task_and_transitions_state(
        self, db_session: AsyncSession
    ) -> None:
        """Put a research task on Redis; run worker once; verify state transition."""
        import os

        from sqlalchemy.ext.asyncio import async_sessionmaker

        from dime.adapters.broker.redis import RedisBrokerAdapter

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
        broker = RedisBrokerAdapter(url=redis_url)

        article = _make_article(state=ArticleState.RESEARCHING)
        db_session.add(article)
        await db_session.flush()

        await broker.dispatch_task("research", {"article_id": str(article.id)})

        session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(  # type: ignore[assignment]
            db_session.bind,
            expire_on_commit=False,  # type: ignore[arg-type]
        )

        worker = ResearchWorker(broker=broker, session_factory=session_factory)

        # Consume one batch (single message), block up to 2s
        await broker.consume("research", worker.handle, max_count=1, block_ms=2000)

        await db_session.refresh(article)
        assert article.state is ArticleState.RESEARCH_REVIEW

        await broker.close()

    async def test_agent_failure_marks_article_failed_integration(
        self, db_session: AsyncSession
    ) -> None:
        """Agent failure via real Redis should mark article FAILED without crashing."""
        import os

        from sqlalchemy.ext.asyncio import async_sessionmaker

        from dime.adapters.broker.redis import RedisBrokerAdapter

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
        broker = RedisBrokerAdapter(url=redis_url)

        article = _make_article(state=ArticleState.RESEARCHING)
        db_session.add(article)
        await db_session.flush()

        await broker.dispatch_task("research", {"article_id": str(article.id)})

        session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(  # type: ignore[assignment]
            db_session.bind,
            expire_on_commit=False,  # type: ignore[arg-type]
        )

        worker = ResearchWorker(broker=broker, session_factory=session_factory)

        async def failing_run_task(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            raise RuntimeError("Simulated agent failure")

        worker.run_task = failing_run_task  # type: ignore[method-assign]

        await broker.consume("research", worker.handle, max_count=1, block_ms=2000)

        await db_session.refresh(article)
        assert article.state is ArticleState.FAILED

        await broker.close()
