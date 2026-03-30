from __future__ import annotations

import json
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import redis.asyncio as aioredis


class RedisBrokerAdapter:
    """BrokerAdapter implementation using Redis Streams."""

    _GROUP = "dime-workers"

    def __init__(self, url: str) -> None:
        self._url = url
        self._client: aioredis.Redis[str] = aioredis.from_url(  # type: ignore[type-arg]
            url, decode_responses=True
        )

    def _stream_key(self, task_type: str) -> str:
        return f"dime:tasks:{task_type}"

    async def _ensure_group(self, stream_key: str) -> None:
        try:
            await self._client.xgroup_create(
                stream_key, self._GROUP, id="0", mkstream=True
            )
        except aioredis.ResponseError:
            pass  # Group already exists

    async def dispatch_task(self, task_type: str, payload: dict[str, Any]) -> None:
        key = self._stream_key(task_type)
        await self._client.xadd(key, {"payload": json.dumps(payload)})

    async def consume(
        self,
        task_type: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        max_count: int = 10,
        block_ms: int = 5000,
    ) -> None:
        key = self._stream_key(task_type)
        await self._ensure_group(key)
        consumer_name = f"consumer-{uuid.uuid4().hex[:8]}"
        messages: list[Any] = await self._client.xreadgroup(  # type: ignore[assignment]
            self._GROUP,
            consumer_name,
            {key: ">"},
            count=max_count,
            block=block_ms,
        )
        if not messages:
            return
        for _stream, entries in messages:
            for entry_id, data in entries:
                payload: dict[str, Any] = json.loads(data["payload"])
                await handler(payload)
                await self._client.xack(key, self._GROUP, entry_id)

    async def close(self) -> None:
        await self._client.aclose()
