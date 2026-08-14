import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LegalEventOutbox


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def enqueue(self, subject: str, payload: dict) -> LegalEventOutbox:
        event = LegalEventOutbox(
            id=str(uuid4()),
            subject=subject,
            payload_json=json.dumps(payload),
            status="pending",
            attempts=0,
        )
        self.session.add(event)
        return event

    async def list_pending(self, limit: int = 100) -> list[LegalEventOutbox]:
        stmt = (
            select(LegalEventOutbox)
            .where(LegalEventOutbox.status == "pending")
            .order_by(LegalEventOutbox.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_events(self, limit: int = 100, status: str | None = None) -> list[LegalEventOutbox]:
        stmt = select(LegalEventOutbox).order_by(LegalEventOutbox.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(LegalEventOutbox.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_published(self, event: LegalEventOutbox) -> None:
        event.status = "published"
        event.attempts += 1
        event.last_error = None
        event.published_at = datetime.now(UTC)

    async def mark_retry(self, event: LegalEventOutbox, error: str) -> None:
        event.status = "pending"
        event.attempts += 1
        event.last_error = error[:500]
