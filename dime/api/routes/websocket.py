from __future__ import annotations

import uuid
from typing import cast

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dime.adapters.factory import AdapterSet
from dime.adapters.notification.websocket import WebSocketNotificationAdapter

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    project_id: uuid.UUID,
    websocket: WebSocket,
) -> None:
    """Push pipeline events to clients subscribed to a project."""
    adapters = cast(AdapterSet, websocket.app.state.adapters)  # type: ignore[reportUnknownMemberType]
    notification = cast(WebSocketNotificationAdapter, adapters.notification)
    await websocket.accept()
    notification.register(project_id, websocket)
    try:
        while True:
            # Keep the connection alive; clients are passive receivers.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notification.unregister(project_id)
