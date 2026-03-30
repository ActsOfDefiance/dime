from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ImageVariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slot_id: uuid.UUID
    file_path: str
    prompt_used: str
    provider: str
    generation_meta: dict[str, Any]
    created_at: datetime


class ImageSlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    article_id: uuid.UUID
    slot_name: str
    width: int
    height: int
    format: str
    approved_prompt: str | None
    selected_variant_id: uuid.UUID | None
    variants: list[ImageVariantRead] = []
