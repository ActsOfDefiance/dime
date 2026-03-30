from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dime.adapters.factory import AdapterSet
from dime.api.deps import Adapters, DbSession
from dime.api.schemas.article import (
    ApproveRequest,
    ArticleCreate,
    ArticleRead,
    ArticleUpdate,
    RejectRequest,
    StateTransitionRequest,
)
from dime.api.state_machine import (
    APPROVE_TRANSITIONS,
    get_worker_task,
    is_valid_transition,
)
from dime.models.article import Article
from dime.models.article_checkpoint import ArticleCheckpoint
from dime.models.image_slot import ImageSlot
from dime.models.image_variant import ImageVariant
from dime.models.project import Project
from dime.pipeline.states import ArticleState

router = APIRouter(tags=["articles"])


async def _get_article_or_404(article_id: uuid.UUID, db: AsyncSession) -> Article:
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


async def _apply_transition(
    article: Article,
    to_state: ArticleState,
    created_by: uuid.UUID,
    note: str | None,
    db: AsyncSession,
    adapters: AdapterSet,
) -> None:
    """Validate + apply a state transition, create a checkpoint, dispatch worker if needed."""
    if not is_valid_transition(article.state, to_state):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid transition: {article.state.value} → {to_state.value}",
        )
    article.state = to_state
    checkpoint = ArticleCheckpoint(
        id=uuid.uuid4(),
        article_id=article.id,
        state_at_checkpoint=to_state,
        created_by=created_by,
        note=note,
    )
    db.add(checkpoint)
    await db.flush()
    article.current_draft_id = checkpoint.id
    await db.commit()
    await db.refresh(article)

    task = get_worker_task(to_state)
    if task is not None:
        await adapters.broker.dispatch_task(
            task,
            {"article_id": str(article.id), "project_id": str(article.project_id)},
        )

    await adapters.notification.notify(
        "state_changed",
        article.project_id,
        f"Article {article.id} transitioned to {to_state.value}",
    )


@router.post(
    "/projects/{project_id}/articles", response_model=ArticleRead, status_code=201
)
async def create_article(
    project_id: uuid.UUID, body: ArticleCreate, db: DbSession
) -> Article:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    article = Article(
        id=uuid.uuid4(),
        project_id=project_id,
        title=body.title,
        slug=body.slug,
        state=ArticleState.QUEUED,
        topic_brief=body.topic_brief,
        tags=body.tags,
        assigned_to=body.assigned_to,
    )
    db.add(article)

    # Seed image slots from project style_guide if present
    slot_defs: list[Any] = project.style_guide.get("image_slots", [])
    for slot_def in slot_defs:
        slot = ImageSlot(
            id=uuid.uuid4(),
            article_id=article.id,
            slot_name=str(slot_def.get("name", "")),
            width=int(slot_def.get("width", 0)),
            height=int(slot_def.get("height", 0)),
            format=str(slot_def.get("format", "webp")),
        )
        db.add(slot)

    await db.commit()
    await db.refresh(article)
    return article


@router.get("/articles/{article_id}", response_model=ArticleRead)
async def get_article(article_id: uuid.UUID, db: DbSession) -> Article:
    return await _get_article_or_404(article_id, db)


@router.patch("/articles/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: uuid.UUID, body: ArticleUpdate, db: DbSession
) -> Article:
    article = await _get_article_or_404(article_id, db)
    if body.title is not None:
        article.title = body.title
    if body.topic_brief is not None:
        article.topic_brief = body.topic_brief
    if body.tags is not None:
        article.tags = body.tags
    await db.commit()
    await db.refresh(article)
    return article


@router.post("/articles/{article_id}/start", response_model=ArticleRead)
async def start_article(
    article_id: uuid.UUID,
    body: ApproveRequest,
    db: DbSession,
    adapters: Adapters,
) -> Article:
    """Transition QUEUED → RESEARCHING and dispatch the research worker task."""
    article = await _get_article_or_404(article_id, db)
    if article.state != ArticleState.QUEUED:
        raise HTTPException(
            status_code=422,
            detail=f"Article must be QUEUED to start (current: {article.state.value})",
        )
    await _apply_transition(
        article, ArticleState.RESEARCHING, body.created_by, body.note, db, adapters
    )
    return article


@router.post("/articles/{article_id}/approve", response_model=ArticleRead)
async def approve_article(
    article_id: uuid.UUID,
    body: ApproveRequest,
    db: DbSession,
    adapters: Adapters,
) -> Article:
    """Advance from a review/generation checkpoint to the next pipeline state."""
    article = await _get_article_or_404(article_id, db)
    next_state = APPROVE_TRANSITIONS.get(article.state)
    if next_state is None:
        raise HTTPException(
            status_code=422,
            detail=f"State {article.state.value} has no approve transition",
        )
    await _apply_transition(
        article, next_state, body.created_by, body.note, db, adapters
    )
    return article


@router.post("/articles/{article_id}/reject", response_model=ArticleRead)
async def reject_article(
    article_id: uuid.UUID,
    body: RejectRequest,
    db: DbSession,
    adapters: Adapters,
) -> Article:
    """Return an article to a prior state with an optional note."""
    article = await _get_article_or_404(article_id, db)
    await _apply_transition(
        article, body.target_state, body.created_by, body.note, db, adapters
    )
    return article


@router.post("/articles/{article_id}/state", response_model=ArticleRead)
async def worker_state_transition(
    article_id: uuid.UUID,
    body: StateTransitionRequest,
    db: DbSession,
    adapters: Adapters,
) -> Article:
    """Internal worker endpoint: push a validated state transition."""
    article = await _get_article_or_404(article_id, db)
    await _apply_transition(
        article, body.new_state, body.created_by, body.note, db, adapters
    )
    return article


@router.get("/articles/{article_id}/package")
async def get_article_package(
    article_id: uuid.UUID, db: DbSession
) -> dict[str, object]:
    """Package Dashboard: article data + current checkpoint + image slots + variants."""
    article = await _get_article_or_404(article_id, db)

    checkpoint_data: dict[str, object] | None = None
    if article.current_draft_id is not None:
        checkpoint = await db.get(ArticleCheckpoint, article.current_draft_id)
        if checkpoint is not None:
            checkpoint_data = {
                "id": str(checkpoint.id),
                "state_at_checkpoint": checkpoint.state_at_checkpoint.value,
                "note": checkpoint.note,
                "created_at": checkpoint.created_at.isoformat(),
            }

    slots_result = await db.execute(
        select(ImageSlot).where(ImageSlot.article_id == article_id)
    )
    slots = list(slots_result.scalars().all())

    slot_data: list[dict[str, object]] = []
    for slot in slots:
        variants_result = await db.execute(
            select(ImageVariant).where(ImageVariant.slot_id == slot.id)
        )
        variants = list(variants_result.scalars().all())
        slot_data.append(
            {
                "id": str(slot.id),
                "slot_name": slot.slot_name,
                "width": slot.width,
                "height": slot.height,
                "format": slot.format,
                "approved_prompt": slot.approved_prompt,
                "selected_variant_id": str(slot.selected_variant_id)
                if slot.selected_variant_id
                else None,
                "variants": [
                    {
                        "id": str(v.id),
                        "file_path": v.file_path,
                        "prompt_used": v.prompt_used,
                        "provider": v.provider,
                        "generation_meta": v.generation_meta,
                        "created_at": v.created_at.isoformat(),
                    }
                    for v in variants
                ],
            }
        )

    return {
        "article": ArticleRead.model_validate(article).model_dump(mode="json"),
        "checkpoint": checkpoint_data,
        "image_slots": slot_data,
    }
