from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from dime.pipeline.states import ArticleState


class ArticleCreate(BaseModel):
    title: str
    slug: str
    topic_brief: str
    tags: list[str] = []
    assigned_to: uuid.UUID | None = None


class ArticleUpdate(BaseModel):
    title: str | None = None
    topic_brief: str | None = None
    tags: list[str] | None = None


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    slug: str
    state: ArticleState
    topic_brief: str
    tags: list[str]
    assigned_to: uuid.UUID | None
    current_draft_id: uuid.UUID | None
    created_at: datetime
    published_at: datetime | None


class StateTransitionRequest(BaseModel):
    """Used by workers to push a state transition via POST /articles/{id}/state."""

    new_state: ArticleState
    note: str | None = None
    created_by: uuid.UUID


class ApproveRequest(BaseModel):
    """Human approval at a review checkpoint."""

    note: str | None = None
    created_by: uuid.UUID


class RejectRequest(BaseModel):
    """Human rejection — must specify a valid prior state to return to."""

    target_state: ArticleState
    note: str | None = None
    created_by: uuid.UUID
