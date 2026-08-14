from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.integration.ws_stream import event_stream_hub


router = APIRouter(prefix="/events", tags=["Event Stream"])


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket) -> None:
    await event_stream_hub.connect(websocket)
    try:
        while True:
            # Keep socket alive. Client messages are not used for now.
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_stream_hub.disconnect(websocket)
    except Exception:
        event_stream_hub.disconnect(websocket)
