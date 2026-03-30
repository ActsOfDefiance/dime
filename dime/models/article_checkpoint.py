from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from dime.models.base import Base
from dime.pipeline.states import ArticleState


class ArticleCheckpoint(Base):
    __tablename__ = "article_checkpoint"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # article.current_draft_id points back to us via use_alter; no Python import cycle
    article_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("article.id"), nullable=False
    )
    state_at_checkpoint: Mapped[ArticleState] = mapped_column(
        SAEnum(ArticleState, name="articlestate", create_type=False), nullable=False
    )
    git_commit_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("user.id"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
