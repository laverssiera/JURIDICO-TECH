from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket

from app.integration.event_bus import event_bus


class EventStreamHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._subscribers_registered = False
        self._loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._loop = asyncio.get_running_loop()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)
        if not self._connections:
            self._loop = None

    async def broadcast(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self._connections:
            return
        message = json.dumps(
            {
                "type": event_type,
                "payload": payload,
            },
            ensure_ascii=True,
        )

        stale_connections: list[WebSocket] = []
        for websocket in self._connections:
            try:
                await websocket.send_text(message)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(websocket)

    def _handler_for(self, event_type: str):
        def _handler(payload: dict[str, Any]) -> dict[str, Any]:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.broadcast(event_type, payload))
            except RuntimeError:
                if self._loop and not self._loop.is_closed():
                    coro = self.broadcast(event_type, payload)
                    try:
                        asyncio.run_coroutine_threadsafe(coro, self._loop)
                    except RuntimeError:
                        coro.close()
            return {"streamed": True, "event": event_type}

        return _handler

    def register_subscribers(self) -> None:
        if self._subscribers_registered:
            return

        for event_type in (
            "legal.contract.created",
            "legal.risk.flagged",
            "legal.risk.update",
            "twin.updated",
            "radar.signal.ingested",
            "radar.signal.disseminated",
            "war_room.incident.opened",
            "legal_os.gate.blocked",
            "legal.approved",
            "trust.score.updated",
            "simulation.global.executed",
            "simulation.global.risk.high",
        ):
            event_bus.subscribe(event_type, self._handler_for(event_type))

        self._subscribers_registered = True


event_stream_hub = EventStreamHub()
