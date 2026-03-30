from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dime.adapters.factory import AdapterSet
from dime.db import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closed on exit."""
    async with AsyncSessionLocal() as session:
        yield session


def get_adapters(request: Request) -> AdapterSet:
    """Return the AdapterSet stored on app.state at startup."""
    adapters: AdapterSet = request.app.state.adapters
    return adapters


DbSession = Annotated[AsyncSession, Depends(get_db)]
Adapters = Annotated[AdapterSet, Depends(get_adapters)]
