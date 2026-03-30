from __future__ import annotations

import json
import uuid

from fastapi import WebSocket


class WebSocketNotificationAdapter:
    """NotificationAdapter that pushes events over WebSocket connections.

    Maintains an in-memory registry of active connections keyed by user_id.
    Always active in solo mode — no external service required.
    """

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, WebSocket] = {}

    def register(self, user_id: uuid.UUID, websocket: WebSocket) -> None:
        self._connections[user_id] = websocket

    def unregister(self, user_id: uuid.UUID) -> None:
        self._connections.pop(user_id, None)

    @property
    def connected_users(self) -> list[uuid.UUID]:
        return list(self._connections.keys())

    async def notify(self, event: str, user_id: uuid.UUID, message: str) -> None:
        websocket = self._connections.get(user_id)
        if websocket is None:
            return
        payload = json.dumps({"event": event, "message": message})
        await websocket.send_text(payload)
