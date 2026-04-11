from __future__ import annotations

import uuid
from typing import Any

from dime.adapters.protocols import BrokerAdapter
from dime.pipeline.state_machine import get_worker_task
from dime.pipeline.states import ArticleState


async def dispatch_worker_task(
    broker: BrokerAdapter,
    article_id: uuid.UUID,
    state: ArticleState,
    extra: dict[str, Any] | None = None,
) -> bool:
    """Dispatch a broker task for *state* if one is mapped, return True if dispatched.

    Returns False when the state has no associated worker task (e.g. checkpoint states).
    """
    task_type = get_worker_task(state)
    if task_type is None:
        return False
    payload: dict[str, Any] = dict(extra or {})
    payload["article_id"] = str(article_id)
    await broker.dispatch_task(task_type, payload)
    return True
