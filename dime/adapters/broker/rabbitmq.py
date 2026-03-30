from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


class RabbitMQBrokerAdapter:
    """BrokerAdapter stub for RabbitMQ. Not yet implemented."""

    def __init__(self, url: str) -> None:
        self._url = url

    async def dispatch_task(self, task_type: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError("RabbitMQBrokerAdapter is not yet implemented")

    async def consume(
        self,
        task_type: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        max_count: int = 10,
        block_ms: int = 5000,
    ) -> None:
        raise NotImplementedError("RabbitMQBrokerAdapter is not yet implemented")
