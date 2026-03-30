from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    slug: str
    style_guide: dict[str, Any] = {}
    content_guide: dict[str, Any] = {}
    workflow_config_id: uuid.UUID
    default_adapter: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    style_guide: dict[str, Any] | None = None
    content_guide: dict[str, Any] | None = None
    default_adapter: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    style_guide: dict[str, Any]
    content_guide: dict[str, Any]
    workflow_config_id: uuid.UUID
    default_adapter: str | None
    created_at: datetime
