"""Tests for the worker layer.

Unit tests (no markers) use mocks and run in the default test suite.
Integration tests (@pytest.mark.integration) require a real Redis broker.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dime.models.article import Article
from dime.models.image_slot import ImageSlot
from dime.models.project import Project
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

_PROJECT_ID = uuid.uuid4()


def _make_article(
    state: ArticleState = ArticleState.RESEARCHING,
    article_id: uuid.UUID | None = None,
) -> Article:
    return Article(
        id=article_id or uuid.uuid4(),
        project_id=_PROJECT_ID,
        title="Test Article",
        slug="test-article",
        state=state,
        topic_brief="Test topic",
        tags=[],
        created_at=datetime.now(timezone.utc),
    )


def _make_project() -> Project:
    return Project(
        id=_PROJECT_ID,
        name="Test Project",
        slug="test-project",
        content_guide={"audience": "general"},
        style_guide={"palette": "bold"},
        workflow_config_id=uuid.uuid4(),
    )


def _make_session_factory(article: Article | None) -> Any:
    """Return a mock async_sessionmaker that yields a session.

    The session's .get() returns *article* and the worker's _load_project
    returns a test project.
    """
    project = _make_project()
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get = AsyncMock(return_value=article)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    # Mock for _load_project's select().where() pattern
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = project
    mock_session.execute = AsyncMock(return_value=mock_result)

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock()
    mock_factory.return_value = mock_cm
    return mock_factory


def _make_filesystem() -> MagicMock:
    """Return a mock FileSystemAdapter."""
    fs = MagicMock()
    fs.read.return_value = "# Draft content"
    fs.write.return_value = None
    fs.exists.return_value = True
    fs.list.return_value = []
    return fs


def _make_worker(
    cls: type[BaseWorker],
    article: Article | None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Return (worker, mock_broker, mock_filesystem)."""
    broker = AsyncMock()
    factory = _make_session_factory(article)
    filesystem = _make_filesystem()
    worker = cls(
        broker=broker, session_factory=factory, filesystem=filesystem, **kwargs
    )
    return worker, broker, filesystem


# ---------------------------------------------------------------------------
# ResearchWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestResearchWorker:
    @patch("dime.workers.research.run_agent", new_callable=AsyncMock)
    async def test_happy_path_transitions_to_research_review(
        self, mock_run: AsyncMock
    ) -> None:
        mock_run.return_value = "# Research notes\n\nFindings here."
        article = _make_article(state=ArticleState.RESEARCHING)
        worker, _, _ = _make_worker(ResearchWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.RESEARCH_REVIEW
        mock_run.assert_called_once()

    async def test_missing_article_id_does_not_crash(self) -> None:
        worker, _, _ = _make_worker(ResearchWorker, None)
        await worker.handle({})  # no exception

    async def test_invalid_article_id_does_not_crash(self) -> None:
        worker, _, _ = _make_worker(ResearchWorker, None)
        await worker.handle({"article_id": "not-a-uuid"})  # no exception

    async def test_article_not_found_does_not_crash(self) -> None:
        worker, _, _ = _make_worker(ResearchWorker, None)
        await worker.handle({"article_id": str(uuid.uuid4())})  # no exception


# ---------------------------------------------------------------------------
# WritingWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestWritingWorker:
    @patch("dime.workers.writing.run_agent", new_callable=AsyncMock)
    async def test_happy_path_transitions_to_draft_review(
        self, mock_run: AsyncMock
    ) -> None:
        mock_run.return_value = "# Article Draft\n\nContent here."
        article = _make_article(state=ArticleState.WRITING)
        worker, _, _ = _make_worker(WritingWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.DRAFT_REVIEW
        mock_run.assert_called_once()


# ---------------------------------------------------------------------------
# ArtDirectorWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestArtDirectorWorker:
    @patch("dime.workers.art_director.run_agent", new_callable=AsyncMock)
    async def test_happy_path_transitions_to_art_review(
        self, mock_run: AsyncMock
    ) -> None:
        mock_run.return_value = "# Art Brief\n\nImage prompts here."
        article = _make_article(state=ArticleState.ART_BRIEFING)
        worker, _, _ = _make_worker(ArtDirectorWorker, article)

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.ART_REVIEW
        mock_run.assert_called_once()


# ---------------------------------------------------------------------------
# ImageWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestImageWorker:
    @patch("dime.workers.image.run_agent", new_callable=AsyncMock)
    async def test_no_state_change(self, mock_run: AsyncMock) -> None:
        """ImageWorker runs but leaves article in ART_GENERATING."""
        mock_run.return_value = "Generated 3 variants."

        article = _make_article(state=ArticleState.ART_GENERATING)
        worker, _, _ = _make_worker(ImageWorker, article)

        # Mock the slot lookup in run_task's inner session
        slot = ImageSlot(
            id=uuid.uuid4(),
            article_id=article.id,
            slot_name="hero",
            width=1200,
            height=630,
            format="png",
            approved_prompt="A dramatic hero image",
        )
        # Patch the inner session_factory call to also return the slot
        inner_session = AsyncMock(spec=AsyncSession)
        inner_session.get = AsyncMock(return_value=slot)
        inner_result = MagicMock()
        inner_result.scalar_one_or_none.return_value = _make_project()
        inner_session.execute = AsyncMock(return_value=inner_result)

        inner_cm = MagicMock()
        inner_cm.__aenter__ = AsyncMock(return_value=inner_session)
        inner_cm.__aexit__ = AsyncMock(return_value=False)

        # The handle() uses one session, run_task() opens another
        orig_factory = worker._session_factory
        call_count = 0
        original_cm = orig_factory.return_value

        def side_effect_factory() -> Any:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return original_cm  # handle()'s session
            return inner_cm  # run_task()'s inner session

        worker._session_factory = MagicMock(side_effect=side_effect_factory)

        await worker.handle({"article_id": str(article.id), "slot_id": str(slot.id)})

        assert article.state is ArticleState.ART_GENERATING
        mock_run.assert_called_once()


# ---------------------------------------------------------------------------
# PublisherWorker unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestPublisherWorker:
    async def test_happy_path_transitions_to_published(self) -> None:
        article = _make_article(state=ArticleState.PUBLISHING)
        mock_publishing = AsyncMock()
        mock_publishing.emit = AsyncMock()
        mock_publishing.signal = MagicMock()
        mock_publishing.preview_url = MagicMock(return_value=None)

        worker, _, _fs = _make_worker(
            PublisherWorker, article, publishing=mock_publishing
        )

        await worker.handle({"article_id": str(article.id)})

        assert article.state is ArticleState.PUBLISHED
        mock_publishing.emit.assert_called_once()
        mock_publishing.signal.assert_called_once()


# ---------------------------------------------------------------------------
# BaseWorker error handling tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestBaseWorkerErrorHandling:
    async def test_agent_failure_marks_article_failed(self) -> None:
        """When run_task raises, the article should be marked FAILED."""
        article = _make_article(state=ArticleState.RESEARCHING)
        worker, _, _ = _make_worker(ResearchWorker, article)

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
        worker, _, _ = _make_worker(ResearchWorker, article)

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
        worker, _, _ = _make_worker(ResearchWorker, article)

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
        filesystem = _make_filesystem()

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

        worker = ResearchWorker(
            broker=broker, session_factory=factory, filesystem=filesystem
        )

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
        filesystem = _make_filesystem()
        worker = ResearchWorker(
            broker=broker, session_factory=factory, filesystem=filesystem
        )

        # stop() before start() means the loop body never executes
        worker.stop()
        await worker.start()

        broker.consume.assert_not_called()


# ---------------------------------------------------------------------------
# PublisherAgent unit tests (non-LLM)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestPublisherAgent:
    async def test_publish_reads_draft_and_emits(self) -> None:
        """PublisherAgent reads draft from FS and calls publishing adapter."""
        from dime.agents.publisher import PublisherAgent

        mock_fs = MagicMock()
        mock_fs.exists.return_value = True
        mock_fs.read.return_value = "# My Article\n\nContent here."

        mock_pub = AsyncMock()
        mock_pub.emit = AsyncMock()
        mock_pub.signal = MagicMock()
        mock_pub.preview_url = MagicMock(return_value="http://preview.test/my-article")

        agent = PublisherAgent(publishing=mock_pub, filesystem=mock_fs)
        article_id = uuid.uuid4()

        result = await agent.publish(
            article_id=article_id,
            article_slug="my-article",
            frontmatter={"title": "My Article"},
        )

        mock_fs.read.assert_called_once_with("my-article/draft.md")
        mock_pub.emit.assert_called_once()
        mock_pub.signal.assert_called_once()
        assert "preview.test" in result

    async def test_publish_raises_on_missing_draft(self) -> None:
        """PublisherAgent raises FileNotFoundError if draft is missing."""
        from dime.agents.publisher import PublisherAgent

        mock_fs = MagicMock()
        mock_fs.exists.return_value = False
        mock_pub = AsyncMock()

        agent = PublisherAgent(publishing=mock_pub, filesystem=mock_fs)

        with pytest.raises(FileNotFoundError, match="draft not found"):
            await agent.publish(
                article_id=uuid.uuid4(),
                article_slug="missing-article",
                frontmatter={},
            )


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
        from dime.adapters.filesystem.local import LocalFileSystemAdapter

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
        broker = RedisBrokerAdapter(url=redis_url)
        filesystem = LocalFileSystemAdapter(base_path="/tmp/dime-test-storage")

        article = _make_article(state=ArticleState.RESEARCHING)
        db_session.add(article)
        await db_session.flush()

        await broker.dispatch_task("research", {"article_id": str(article.id)})

        session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(  # type: ignore[assignment]
            db_session.bind,
            expire_on_commit=False,  # type: ignore[arg-type]
        )

        worker = ResearchWorker(
            broker=broker, session_factory=session_factory, filesystem=filesystem
        )

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
        from dime.adapters.filesystem.local import LocalFileSystemAdapter

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
        broker = RedisBrokerAdapter(url=redis_url)
        filesystem = LocalFileSystemAdapter(base_path="/tmp/dime-test-storage")

        article = _make_article(state=ArticleState.RESEARCHING)
        db_session.add(article)
        await db_session.flush()

        await broker.dispatch_task("research", {"article_id": str(article.id)})

        session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(  # type: ignore[assignment]
            db_session.bind,
            expire_on_commit=False,  # type: ignore[arg-type]
        )

        worker = ResearchWorker(
            broker=broker, session_factory=session_factory, filesystem=filesystem
        )

        async def failing_run_task(
            art: Article, payload: dict[str, Any]
        ) -> ArticleState | None:
            raise RuntimeError("Simulated agent failure")

        worker.run_task = failing_run_task  # type: ignore[method-assign]

        await broker.consume("research", worker.handle, max_count=1, block_ms=2000)

        await db_session.refresh(article)
        assert article.state is ArticleState.FAILED

        await broker.close()
