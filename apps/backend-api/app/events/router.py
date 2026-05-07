from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.events.repository import OutboxRepository
from app.events.schemas import OutboxListResponse, OutboxEventResponse, OutboxFlushResponse
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
