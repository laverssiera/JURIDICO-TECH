import asyncio

from fastapi import APIRouter, Depends
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.session import SessionLocal
from app.db.models import LegalContract, LegalEventOutbox
from app.events.repository import OutboxRepository
from app.events.schemas import (
    OutboxListResponse,
    OutboxEventResponse,
    OutboxFlushResponse,
    WarRoomActionRequest,
    WarRoomActionResponse,
)
from app.events.service import OutboxService

router = APIRouter()


@router.get("/outbox/pending", response_model=OutboxListResponse)
async def list_pending_outbox(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> OutboxListResponse:
    repo = OutboxRepository(session)
    events = await repo.list_pending(limit=limit)
    items = [
        OutboxEventResponse(
            id=e.id,
            subject=e.subject,
            payload_json=e.payload_json,
            status=e.status,
            attempts=e.attempts,
            created_at=e.created_at,
            published_at=e.published_at,
            last_error=e.last_error,
        )
        for e in events
    ]
    return OutboxListResponse(items=items, total=len(items))

@router.get("/outbox", response_model=OutboxListResponse)
async def list_outbox_events(
    limit: int = 200,
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> OutboxListResponse:
    repo = OutboxRepository(session)
    events = await repo.list_events(limit=limit, status=status)
    items = [
        OutboxEventResponse(
            id=e.id,
            subject=e.subject,
            payload_json=e.payload_json,
            status=e.status,
            attempts=e.attempts,
            created_at=e.created_at,
            published_at=e.published_at,
            last_error=e.last_error,
        )
        for e in events
    ]
    return OutboxListResponse(items=items, total=len(items))


@router.post("/outbox/flush", response_model=OutboxFlushResponse)
async def flush_pending_outbox(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> OutboxFlushResponse:
    service = OutboxService(session)
    return await service.flush_pending(limit=limit)


@router.post("/war-room/actions", response_model=WarRoomActionResponse, status_code=201)
async def register_war_room_action(
    payload: WarRoomActionRequest,
    session: AsyncSession = Depends(get_session),
) -> WarRoomActionResponse:
    repo = OutboxRepository(session)
    subject = "legal.war_room.action"
    event = await repo.enqueue(
        subject=subject,
        payload={
            "action": payload.action,
            "source": payload.source,
            "incident_id": payload.incident_id,
            "metadata": payload.metadata,
        },
    )
    await session.commit()
    return WarRoomActionResponse(status="queued", event_id=event.id, subject=subject)


@router.websocket("/ws")
async def events_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            async with SessionLocal() as session:
                contracts_count = (
                    await session.execute(select(func.count(LegalContract.id)))
                ).scalar_one()
                pending_outbox = (
                    await session.execute(
                        select(func.count(LegalEventOutbox.id)).where(LegalEventOutbox.status.in_(["pending", "retry"]))
                    )
                ).scalar_one()

            await websocket.send_json(
                {
                    "type": "system.heartbeat",
                    "payload": {
                        "contracts_total": contracts_count,
                        "outbox_pending": pending_outbox,
                    },
                }
            )
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
