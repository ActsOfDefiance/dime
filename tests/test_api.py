"""
API integration tests.

All tests in this file are marked @pytest.mark.integration and require
a live PostgreSQL instance at the DATABASE_URL in conftest.test_env.

Run with: uv run pytest -m integration tests/test_api.py
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from dime.models.role import Role
from dime.models.user import User
from dime.models.workflow_config import WorkflowConfig


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


async def _create_workflow(session: AsyncSession) -> WorkflowConfig:
    wf = WorkflowConfig(
        id=uuid.uuid4(),
        name="test-workflow",
        is_default=True,
        checkpoints={},
        notification_rules={},
    )
    session.add(wf)
    await session.commit()
    await session.refresh(wf)
    return wf


async def _create_user(session: AsyncSession) -> User:
    role = Role(id=uuid.uuid4(), name=f"editor-{uuid.uuid4().hex[:6]}", permissions={})
    session.add(role)
    await session.flush()
    user = User(
        id=uuid.uuid4(),
        email=f"test-{uuid.uuid4().hex[:8]}@example.com",
        display_name="Test User",
        role_id=role.id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_project(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    wf = await _create_workflow(db_session)
    body = {
        "name": "Test Project",
        "slug": f"test-project-{uuid.uuid4().hex[:8]}",
        "workflow_config_id": str(wf.id),
    }
    resp = await api_client.post("/api/v1/projects", json=body)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Project"
    assert data["id"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_projects(api_client: AsyncClient, db_session: AsyncSession) -> None:
    wf = await _create_workflow(db_session)
    body = {
        "name": "Listed Project",
        "slug": f"listed-{uuid.uuid4().hex[:8]}",
        "workflow_config_id": str(wf.id),
    }
    await api_client.post("/api/v1/projects", json=body)
    resp = await api_client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_project(api_client: AsyncClient, db_session: AsyncSession) -> None:
    wf = await _create_workflow(db_session)
    create_resp = await api_client.post(
        "/api/v1/projects",
        json={
            "name": "Get Me",
            "slug": f"get-me-{uuid.uuid4().hex[:8]}",
            "workflow_config_id": str(wf.id),
        },
    )
    project_id = create_resp.json()["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_project_not_found(api_client: AsyncClient) -> None:
    resp = await api_client.get(f"/api/v1/projects/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_project(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    wf = await _create_workflow(db_session)
    create_resp = await api_client.post(
        "/api/v1/projects",
        json={
            "name": "Old Name",
            "slug": f"old-{uuid.uuid4().hex[:8]}",
            "workflow_config_id": str(wf.id),
        },
    )
    project_id = create_resp.json()["id"]
    resp = await api_client.patch(
        f"/api/v1/projects/{project_id}", json={"name": "New Name"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_content_guide(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    wf = await _create_workflow(db_session)
    guide: dict[str, Any] = {"audience": "test readers", "tone": "casual"}
    create_resp = await api_client.post(
        "/api/v1/projects",
        json={
            "name": "Guide Project",
            "slug": f"guide-{uuid.uuid4().hex[:8]}",
            "workflow_config_id": str(wf.id),
            "content_guide": guide,
        },
    )
    project_id = create_resp.json()["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}/content-guide")
    assert resp.status_code == 200
    assert resp.json()["audience"] == "test readers"


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------


async def _create_project_and_article(
    api_client: AsyncClient,
    db_session: AsyncSession,
    user_id: str,
    style_guide: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Helper: create a project + article. Returns (project_id, article_id)."""
    wf = await _create_workflow(db_session)
    project_resp = await api_client.post(
        "/api/v1/projects",
        json={
            "name": "Article Project",
            "slug": f"art-proj-{uuid.uuid4().hex[:8]}",
            "workflow_config_id": str(wf.id),
            "style_guide": style_guide or {},
        },
    )
    project_id = project_resp.json()["id"]
    article_resp = await api_client.post(
        f"/api/v1/projects/{project_id}/articles",
        json={
            "title": "Test Article",
            "slug": f"test-article-{uuid.uuid4().hex[:8]}",
            "topic_brief": "A brief about testing.",
            "tags": ["test", "integration"],
        },
    )
    article_id = article_resp.json()["id"]
    return project_id, article_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_article_queued(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    wf = await _create_workflow(db_session)
    user = await _create_user(db_session)
    project_resp = await api_client.post(
        "/api/v1/projects",
        json={
            "name": "P",
            "slug": f"p-{uuid.uuid4().hex[:8]}",
            "workflow_config_id": str(wf.id),
        },
    )
    project_id = project_resp.json()["id"]
    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/articles",
        json={
            "title": "My Article",
            "slug": f"my-article-{uuid.uuid4().hex[:8]}",
            "topic_brief": "A topic.",
            "assigned_to": str(user.id),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["state"] == "queued"
    assert data["project_id"] == project_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_article(api_client: AsyncClient, db_session: AsyncSession) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    resp = await api_client.get(f"/api/v1/articles/{article_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == article_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_article_not_found(api_client: AsyncClient) -> None:
    resp = await api_client.get(f"/api/v1/articles/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_article(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    resp = await api_client.patch(
        f"/api/v1/articles/{article_id}",
        json={"title": "Updated Title", "tags": ["updated"]},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"
    assert resp.json()["tags"] == ["updated"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_start_article(api_client: AsyncClient, db_session: AsyncSession) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/start",
        json={"created_by": str(user.id)},
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "researching"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_start_article_not_queued_returns_422(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # Start once
    await api_client.post(
        f"/api/v1/articles/{article_id}/start", json={"created_by": str(user.id)}
    )
    # Attempt to start again (not QUEUED anymore)
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/start", json={"created_by": str(user.id)}
    )
    assert resp.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_worker_state_transition(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # QUEUED → RESEARCHING
    await api_client.post(
        f"/api/v1/articles/{article_id}/start", json={"created_by": str(user.id)}
    )
    # Worker: RESEARCHING → RESEARCH_REVIEW
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/state",
        json={"new_state": "research_review", "created_by": str(user.id)},
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "research_review"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_state_transition_returns_422(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # QUEUED → PUBLISHED is invalid
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/state",
        json={"new_state": "published", "created_by": str(user.id)},
    )
    assert resp.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_approve_article(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # Advance to RESEARCH_REVIEW
    await api_client.post(
        f"/api/v1/articles/{article_id}/start", json={"created_by": str(user.id)}
    )
    await api_client.post(
        f"/api/v1/articles/{article_id}/state",
        json={"new_state": "research_review", "created_by": str(user.id)},
    )
    # Approve: RESEARCH_REVIEW → WRITING
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/approve",
        json={"created_by": str(user.id)},
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "writing"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reject_article(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # Advance to RESEARCH_REVIEW
    await api_client.post(
        f"/api/v1/articles/{article_id}/start", json={"created_by": str(user.id)}
    )
    await api_client.post(
        f"/api/v1/articles/{article_id}/state",
        json={"new_state": "research_review", "created_by": str(user.id)},
    )
    # Reject back to RESEARCHING
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/reject",
        json={
            "target_state": "researching",
            "note": "needs more sources",
            "created_by": str(user.id),
        },
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "researching"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_approve_from_non_review_state_returns_422(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    # Article is QUEUED — no approve transition
    resp = await api_client.post(
        f"/api/v1/articles/{article_id}/approve",
        json={"created_by": str(user.id)},
    )
    assert resp.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_article_package(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    style_guide = {
        "image_slots": [
            {"name": "hero", "width": 1200, "height": 630, "format": "webp"}
        ]
    }
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id), style_guide=style_guide
    )
    resp = await api_client.get(f"/api/v1/articles/{article_id}/package")
    assert resp.status_code == 200
    data = resp.json()
    assert data["article"]["id"] == article_id
    assert data["checkpoint"] is None
    assert isinstance(data["image_slots"], list)
    assert len(data["image_slots"]) == 1
    assert data["image_slots"][0]["slot_name"] == "hero"


# ---------------------------------------------------------------------------
# Image slots
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_image_slots(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    style_guide = {
        "image_slots": [
            {"name": "hero", "width": 1200, "height": 630, "format": "webp"},
            {"name": "thumbnail", "width": 400, "height": 300, "format": "jpeg"},
        ]
    }
    _, article_id = await _create_project_and_article(
        api_client, db_session, str(user.id), style_guide=style_guide
    )
    resp = await api_client.get(f"/api/v1/articles/{article_id}/image-slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) == 2
    slot_names = {s["slot_name"] for s in slots}
    assert slot_names == {"hero", "thumbnail"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_articles_for_project(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    user = await _create_user(db_session)
    project_id, _ = await _create_project_and_article(
        api_client, db_session, str(user.id)
    )
    resp = await api_client.get(f"/api/v1/projects/{project_id}/articles")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
