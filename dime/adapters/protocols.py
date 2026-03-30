from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BrokerAdapter(Protocol):
    """Task queue and event bus. Implementations: Redis, RabbitMQ, GCP Pub/Sub."""

    async def dispatch_task(self, task_type: str, payload: dict[str, Any]) -> None: ...

    async def consume(
        self,
        task_type: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        max_count: int = 10,
        block_ms: int = 5000,
    ) -> None: ...


@runtime_checkable
class FileSystemAdapter(Protocol):
    """Abstracts local disk vs. GCS. Sync — agents use thread executor for async contexts."""

    def read(self, path: str) -> str: ...

    def write(self, path: str, content: str) -> None: ...

    def exists(self, path: str) -> bool: ...

    def list(self, prefix: str) -> list[str]: ...


@runtime_checkable
class PublishingAdapter(Protocol):
    """Signal interface for publishing targets."""

    async def emit(
        self,
        article_id: uuid.UUID,
        content: str,
        frontmatter: dict[str, Any],
    ) -> None: ...

    def signal(self) -> None: ...

    def preview_url(self) -> str | None: ...


@runtime_checkable
class NotificationAdapter(Protocol):
    """Out-of-band notification delivery."""

    async def notify(
        self,
        event: str,
        user_id: uuid.UUID,
        message: str,
    ) -> None: ...
