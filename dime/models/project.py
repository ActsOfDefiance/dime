from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from dime.models.base import Base


class Project(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    style_guide: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    content_guide: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    workflow_config_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workflow_config.id"), nullable=False
    )
    default_adapter: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
