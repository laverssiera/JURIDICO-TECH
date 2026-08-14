import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.nats_client import publish_event
from app.events.repository import OutboxRepository
from app.events.schemas import OutboxFlushResponse


class OutboxService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OutboxRepository(session)

    async def flush_pending(self, limit: int = 100) -> OutboxFlushResponse:
        events = await self.repo.list_pending(limit=limit)
        published = 0

        for event in events:
            payload = json.loads(event.payload_json)
            result = await publish_event(event.subject, payload)
            if result["status"] == "published":
                await self.repo.mark_published(event)
                published += 1
            else:
                await self.repo.mark_retry(event, str(result["status"]))

        await self.session.commit()

        return OutboxFlushResponse(
            scanned=len(events),
            published=published,
            pending=len(events) - published,
        )
