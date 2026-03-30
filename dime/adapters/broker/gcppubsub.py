from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


class GCPPubSubBrokerAdapter:
    """BrokerAdapter stub for GCP Pub/Sub. Not yet implemented."""

    def __init__(self, project_id: str, topic_prefix: str = "dime") -> None:
        self._project_id = project_id
        self._topic_prefix = topic_prefix

    async def dispatch_task(self, task_type: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError("GCPPubSubBrokerAdapter is not yet implemented")

    async def consume(
        self,
        task_type: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        max_count: int = 10,
        block_ms: int = 5000,
    ) -> None:
        raise NotImplementedError("GCPPubSubBrokerAdapter is not yet implemented")
