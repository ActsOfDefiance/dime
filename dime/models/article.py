from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from dime.models.base import Base
from dime.pipeline.states import ArticleState


class Article(Base):
    __tablename__ = "article"
    __table_args__ = (Index("ix_article_project_id_state", "project_id", "state"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("project.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[ArticleState] = mapped_column(
        SAEnum(ArticleState, name="articlestate"), nullable=False
    )
    topic_brief: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("user.id"), nullable=True
    )
    # Nullable FK back to article_checkpoint — use_alter avoids circular DDL
    current_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "article_checkpoint.id",
            use_alter=True,
            name="fk_article_current_draft_id",
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
