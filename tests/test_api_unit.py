"""
Unit tests for the API layer — no database or network required.

Covers:
- State machine logic (dime/api/state_machine.py)
- Schema validation (dime/api/schemas/)
- Route handlers via direct function calls with AsyncMock sessions
- Key 404/422 responses validated against mock DB returning None
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dime.api.routes.articles import (
    approve_article,
    create_article,
    get_article,
    get_article_package,
    reject_article,
    start_article,
    update_article,
    worker_state_transition,
)
from dime.api.routes.images import list_image_slots, regenerate_image_slot
from dime.api.routes.projects import (
    create_project,
    get_content_guide,
    get_project,
    list_project_articles,
    list_projects,
    update_project,
)
from dime.api.schemas.article import (
    ApproveRequest,
    ArticleCreate,
    ArticleRead,
    ArticleUpdate,
    RejectRequest,
    StateTransitionRequest,
)
from dime.api.schemas.image import ImageSlotRead
from dime.api.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from dime.api.state_machine import (
    APPROVE_TRANSITIONS,
    VALID_TRANSITIONS,
    WORKER_TASKS,
    get_worker_task,
    is_valid_transition,
)
from dime.models.article import Article
from dime.models.image_slot import ImageSlot
from dime.models.project import Project
from dime.pipeline.states import ArticleState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_db() -> AsyncMock:
    """Return a fresh AsyncMock wired as an AsyncSession."""
    db = AsyncMock(spec=AsyncSession)
    # flush() and commit() are no-ops by default via AsyncMock
    return db


def _mock_adapters() -> MagicMock:
    """Return a mock AdapterSet with an AsyncMock broker and notification."""
    adapters = MagicMock()
    adapters.broker.dispatch_task = AsyncMock()
    adapters.notification.notify = AsyncMock()
    return adapters


def _article(state: ArticleState = ArticleState.QUEUED) -> Article:
    return Article(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="Test",
        slug="test",
        state=state,
        topic_brief="brief",
        tags=[],
        created_at=datetime.now(timezone.utc),
    )


def _project() -> Project:
    wf_id = uuid.uuid4()
    return Project(
        id=uuid.uuid4(),
        name="Proj",
        slug="proj",
        style_guide={},
        content_guide={},
        workflow_config_id=wf_id,
        created_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


class TestStateMachine:
    def test_valid_transition_queued_to_researching(self) -> None:
        assert (
            is_valid_transition(ArticleState.QUEUED, ArticleState.RESEARCHING) is True
        )

    def test_invalid_transition_queued_to_published(self) -> None:
        assert is_valid_transition(ArticleState.QUEUED, ArticleState.PUBLISHED) is False

    def test_invalid_transition_same_state(self) -> None:
        assert is_valid_transition(ArticleState.QUEUED, ArticleState.QUEUED) is False

    def test_all_valid_transitions_are_reachable(self) -> None:
        assert len(VALID_TRANSITIONS) == 35

    def test_approve_transitions_cover_all_review_states(self) -> None:
        expected = {
            ArticleState.RESEARCH_REVIEW,
            ArticleState.DRAFT_REVIEW,
            ArticleState.ART_REVIEW,
            ArticleState.ART_GENERATING,
            ArticleState.FINAL_REVIEW,
        }
        assert set(APPROVE_TRANSITIONS.keys()) == expected

    def test_worker_tasks_for_worker_states(self) -> None:
        assert get_worker_task(ArticleState.RESEARCHING) == "research"
        assert get_worker_task(ArticleState.WRITING) == "write"
        assert get_worker_task(ArticleState.ART_BRIEFING) == "art_brief"
        assert get_worker_task(ArticleState.PUBLISHING) == "publish"

    def test_get_worker_task_returns_none_for_non_worker_state(self) -> None:
        assert get_worker_task(ArticleState.QUEUED) is None
        assert get_worker_task(ArticleState.RESEARCH_REVIEW) is None
        assert get_worker_task(ArticleState.PUBLISHED) is None

    def test_research_review_approve_leads_to_writing(self) -> None:
        assert APPROVE_TRANSITIONS[ArticleState.RESEARCH_REVIEW] == ArticleState.WRITING

    def test_final_review_approve_leads_to_approved(self) -> None:
        assert APPROVE_TRANSITIONS[ArticleState.FINAL_REVIEW] == ArticleState.APPROVED

    def test_worker_tasks_dict_has_four_entries(self) -> None:
        assert len(WORKER_TASKS) == 5


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class TestProjectSchemas:
    def test_project_create_defaults(self) -> None:
        p = ProjectCreate(name="n", slug="s", workflow_config_id=uuid.uuid4())
        assert p.style_guide == {}
        assert p.content_guide == {}
        assert p.default_adapter is None

    def test_project_update_all_none_by_default(self) -> None:
        p = ProjectUpdate()
        assert p.name is None
        assert p.style_guide is None

    def test_project_read_from_orm(self) -> None:
        proj = _project()
        read = ProjectRead.model_validate(proj)
        assert read.name == proj.name


class TestArticleSchemas:
    def test_article_create_defaults(self) -> None:
        a = ArticleCreate(title="t", slug="s", topic_brief="b")
        assert a.tags == []
        assert a.assigned_to is None

    def test_article_read_from_orm(self) -> None:
        article = _article()
        read = ArticleRead.model_validate(article)
        assert read.state == ArticleState.QUEUED

    def test_approve_request_requires_created_by(self) -> None:
        with pytest.raises(Exception):
            ApproveRequest()  # type: ignore[call-arg]

    def test_reject_request_requires_target_state(self) -> None:
        with pytest.raises(Exception):
            RejectRequest(created_by=uuid.uuid4())  # type: ignore[call-arg]

    def test_state_transition_request_fields(self) -> None:
        req = StateTransitionRequest(
            new_state=ArticleState.RESEARCH_REVIEW,
            created_by=uuid.uuid4(),
        )
        assert req.note is None


class TestImageSchemas:
    def test_image_slot_read_default_variants(self) -> None:
        slot_id = uuid.uuid4()
        read = ImageSlotRead(
            id=slot_id,
            article_id=uuid.uuid4(),
            slot_name="hero",
            width=1200,
            height=630,
            format="webp",
            approved_prompt=None,
            selected_variant_id=None,
        )
        assert read.variants == []


# ---------------------------------------------------------------------------
# Project route handlers (mock DB)
# ---------------------------------------------------------------------------


class TestProjectRoutes:
    @pytest.mark.asyncio
    async def test_get_project_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_project(uuid.uuid4(), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_returns_project(self) -> None:
        db = _mock_db()
        proj = _project()
        db.get.return_value = proj
        result = await get_project(proj.id, db)
        assert result is proj

    @pytest.mark.asyncio
    async def test_list_projects_returns_list(self) -> None:
        db = _mock_db()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [_project()]
        db.execute.return_value = mock_result
        result = await list_projects(db)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_project(self) -> None:
        db = _mock_db()
        body = ProjectCreate(name="P", slug="p", workflow_config_id=uuid.uuid4())
        result = await create_project(body, db)
        db.add.assert_called_once()
        db.commit.assert_called_once()
        assert result.name == "P"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await update_project(uuid.uuid4(), ProjectUpdate(name="X"), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_applies_changes(self) -> None:
        db = _mock_db()
        proj = _project()
        db.get.return_value = proj
        result = await update_project(proj.id, ProjectUpdate(name="NewName"), db)
        assert result.name == "NewName"

    @pytest.mark.asyncio
    async def test_get_content_guide_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_content_guide(uuid.uuid4(), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_content_guide_returns_dict(self) -> None:
        db = _mock_db()
        proj = _project()
        proj.content_guide = {"tone": "casual"}
        db.get.return_value = proj
        result = await get_content_guide(proj.id, db)
        assert result["tone"] == "casual"

    @pytest.mark.asyncio
    async def test_list_project_articles_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await list_project_articles(uuid.uuid4(), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_project_articles_returns_articles(self) -> None:
        db = _mock_db()
        proj = _project()
        db.get.return_value = proj
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [_article()]
        db.execute.return_value = mock_result
        result = await list_project_articles(proj.id, db)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Article route handlers (mock DB)
# ---------------------------------------------------------------------------


class TestArticleRoutes:
    @pytest.mark.asyncio
    async def test_get_article_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_article(uuid.uuid4(), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_article_returns_article(self) -> None:
        db = _mock_db()
        article = _article()
        db.get.return_value = article
        result = await get_article(article.id, db)
        assert result is article

    @pytest.mark.asyncio
    async def test_create_article_project_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        body = ArticleCreate(title="T", slug="t", topic_brief="b")
        with pytest.raises(HTTPException) as exc:
            await create_article(uuid.uuid4(), body, db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_article_seeds_image_slots(self) -> None:
        db = _mock_db()
        proj = _project()
        proj.style_guide = {
            "image_slots": [
                {"name": "hero", "width": 1200, "height": 630, "format": "webp"}
            ]
        }
        db.get.return_value = proj
        body = ArticleCreate(title="T", slug="t", topic_brief="b")
        await create_article(proj.id, body, db)
        # db.add called twice: once for article, once for image slot
        assert db.add.call_count == 2

    @pytest.mark.asyncio
    async def test_update_article_applies_fields(self) -> None:
        db = _mock_db()
        article = _article()
        db.get.return_value = article
        result = await update_article(
            article.id, ArticleUpdate(title="New", tags=["x"]), db
        )
        assert result.title == "New"
        assert result.tags == ["x"]

    @pytest.mark.asyncio
    async def test_start_article_not_queued_raises_422(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.RESEARCHING)
        db.get.return_value = article
        body = ApproveRequest(created_by=uuid.uuid4())
        with pytest.raises(HTTPException) as exc:
            await start_article(article.id, body, db, _mock_adapters())
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_start_article_dispatches_research_task(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.QUEUED)
        db.get.return_value = article
        adapters = _mock_adapters()
        body = ApproveRequest(created_by=uuid.uuid4())
        await start_article(article.id, body, db, adapters)
        adapters.broker.dispatch_task.assert_called_once_with(
            "research",
            {"article_id": str(article.id), "project_id": str(article.project_id)},
        )
        assert article.state == ArticleState.RESEARCHING

    @pytest.mark.asyncio
    async def test_approve_article_no_transition_raises_422(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.QUEUED)
        db.get.return_value = article
        with pytest.raises(HTTPException) as exc:
            await approve_article(
                article.id,
                ApproveRequest(created_by=uuid.uuid4()),
                db,
                _mock_adapters(),
            )
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_approve_article_advances_state(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.RESEARCH_REVIEW)
        db.get.return_value = article
        await approve_article(
            article.id, ApproveRequest(created_by=uuid.uuid4()), db, _mock_adapters()
        )
        assert article.state == ArticleState.WRITING

    @pytest.mark.asyncio
    async def test_reject_article_invalid_transition_raises_422(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.QUEUED)
        db.get.return_value = article
        body = RejectRequest(
            target_state=ArticleState.PUBLISHED, created_by=uuid.uuid4()
        )
        with pytest.raises(HTTPException) as exc:
            await reject_article(article.id, body, db, _mock_adapters())
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_reject_article_returns_to_prior_state(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.RESEARCH_REVIEW)
        db.get.return_value = article
        body = RejectRequest(
            target_state=ArticleState.RESEARCHING,
            note="needs more work",
            created_by=uuid.uuid4(),
        )
        await reject_article(article.id, body, db, _mock_adapters())
        assert article.state == ArticleState.RESEARCHING

    @pytest.mark.asyncio
    async def test_worker_transition_valid(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.RESEARCHING)
        db.get.return_value = article
        body = StateTransitionRequest(
            new_state=ArticleState.RESEARCH_REVIEW, created_by=uuid.uuid4()
        )
        await worker_state_transition(article.id, body, db, _mock_adapters())
        assert article.state == ArticleState.RESEARCH_REVIEW

    @pytest.mark.asyncio
    async def test_worker_transition_invalid_raises_422(self) -> None:
        db = _mock_db()
        article = _article(ArticleState.QUEUED)
        db.get.return_value = article
        body = StateTransitionRequest(
            new_state=ArticleState.PUBLISHED, created_by=uuid.uuid4()
        )
        with pytest.raises(HTTPException) as exc:
            await worker_state_transition(article.id, body, db, _mock_adapters())
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_get_article_package_no_checkpoint(self) -> None:
        db = _mock_db()
        article = _article()
        db.get.return_value = article
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute.return_value = mock_result
        result = await get_article_package(article.id, db)
        assert result["checkpoint"] is None
        assert result["image_slots"] == []


# ---------------------------------------------------------------------------
# Image route handlers (mock DB)
# ---------------------------------------------------------------------------


class TestImageRoutes:
    @pytest.mark.asyncio
    async def test_list_image_slots_article_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await list_image_slots(uuid.uuid4(), db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_image_slots_empty(self) -> None:
        db = _mock_db()
        article = _article()
        db.get.return_value = article
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute.return_value = mock_result
        result = await list_image_slots(article.id, db)
        assert result == []

    @pytest.mark.asyncio
    async def test_regenerate_slot_article_not_found(self) -> None:
        db = _mock_db()
        db.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await regenerate_image_slot(
                uuid.uuid4(), uuid.uuid4(), db, _mock_adapters()
            )
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_regenerate_slot_wrong_article(self) -> None:
        db = _mock_db()
        article = _article()
        slot = ImageSlot(
            id=uuid.uuid4(),
            article_id=uuid.uuid4(),  # different article
            slot_name="hero",
            width=1200,
            height=630,
            format="webp",
        )

        def get_side_effect(model: Any, pk: Any) -> Any:
            if model is Article:
                return article
            return slot

        db.get.side_effect = get_side_effect
        with pytest.raises(HTTPException) as exc:
            await regenerate_image_slot(article.id, slot.id, db, _mock_adapters())
        assert exc.value.status_code == 404
