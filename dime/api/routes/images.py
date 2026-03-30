from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from dime.api.deps import Adapters, DbSession
from dime.api.schemas.image import ImageSlotRead, ImageVariantRead
from dime.models.article import Article
from dime.models.image_slot import ImageSlot
from dime.models.image_variant import ImageVariant

router = APIRouter(tags=["images"])


@router.get("/articles/{article_id}/image-slots", response_model=list[ImageSlotRead])
async def list_image_slots(article_id: uuid.UUID, db: DbSession) -> list[ImageSlotRead]:
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    slots_result = await db.execute(
        select(ImageSlot).where(ImageSlot.article_id == article_id)
    )
    slots = list(slots_result.scalars().all())

    result: list[ImageSlotRead] = []
    for slot in slots:
        variants_result = await db.execute(
            select(ImageVariant).where(ImageVariant.slot_id == slot.id)
        )
        variants = [
            ImageVariantRead.model_validate(v) for v in variants_result.scalars().all()
        ]
        slot_read = ImageSlotRead.model_validate(slot)
        slot_read.variants = variants
        result.append(slot_read)
    return result


@router.post(
    "/articles/{article_id}/image-slots/{slot_id}/regenerate",
    response_model=ImageSlotRead,
)
async def regenerate_image_slot(
    article_id: uuid.UUID,
    slot_id: uuid.UUID,
    db: DbSession,
    adapters: Adapters,
) -> ImageSlotRead:
    """Dispatch a new image generation task for the given slot."""
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    slot = await db.get(ImageSlot, slot_id)
    if slot is None or slot.article_id != article_id:
        raise HTTPException(status_code=404, detail="Image slot not found")

    await adapters.broker.dispatch_task(
        "generate_image",
        {
            "article_id": str(article_id),
            "slot_id": str(slot_id),
            "slot_name": slot.slot_name,
            "approved_prompt": slot.approved_prompt,
        },
    )

    variants_result = await db.execute(
        select(ImageVariant).where(ImageVariant.slot_id == slot_id)
    )
    variants = [
        ImageVariantRead.model_validate(v) for v in variants_result.scalars().all()
    ]
    slot_read = ImageSlotRead.model_validate(slot)
    slot_read.variants = variants
    return slot_read


@router.get(
    "/articles/{article_id}/image-slots/{slot_id}/variants",
    response_model=list[ImageVariantRead],
)
async def list_slot_variants(
    article_id: uuid.UUID, slot_id: uuid.UUID, db: DbSession
) -> list[ImageVariantRead]:
    slot = await db.get(ImageSlot, slot_id)
    if slot is None or slot.article_id != article_id:
        raise HTTPException(status_code=404, detail="Image slot not found")
    result = await db.execute(
        select(ImageVariant).where(ImageVariant.slot_id == slot_id)
    )
    return [ImageVariantRead.model_validate(v) for v in result.scalars().all()]
