from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from dime.models.base import Base


class ImageSlot(Base):
    __tablename__ = "image_slot"
    __table_args__ = (Index("ix_image_slot_article_id", "article_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("article.id"), nullable=False
    )
    slot_name: Mapped[str] = mapped_column(String, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    approved_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Nullable FK back to image_variant — use_alter avoids circular DDL
    selected_variant_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "image_variant.id",
            use_alter=True,
            name="fk_image_slot_selected_variant_id",
        ),
        nullable=True,
    )
