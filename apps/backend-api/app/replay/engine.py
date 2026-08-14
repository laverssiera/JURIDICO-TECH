"""Legal Replay Engine — re-enqueues outbox events for reprocessing."""
from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LegalEventOutbox
from app.replay.schemas import ReplayEventItem, ReplayResult, ReplayStatusResponse


class ReplayEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replay(
        self,
        subject_filter: str | None,
        from_dt: datetime | None,
        to_dt: datetime | None,
        limit: int,
    ) -> ReplayResult:
        stmt = select(LegalEventOutbox).order_by(LegalEventOutbox.created_at.asc()).limit(limit)

        if subject_filter:
            stmt = stmt.where(LegalEventOutbox.subject.ilike(f"%{subject_filter}%"))
        if from_dt:
            stmt = stmt.where(LegalEventOutbox.created_at >= from_dt)
        if to_dt:
            stmt = stmt.where(LegalEventOutbox.created_at <= to_dt)

        result = await self.session.execute(stmt)
        source_events: list[LegalEventOutbox] = list(result.scalars().all())

        replayed_items: list[ReplayEventItem] = []
        skipped = 0

        for ev in source_events:
            try:
                payload = json.loads(ev.payload_json)
            except Exception:
                skipped += 1
                continue

            # Mark re-replay in payload
            payload["_replayed"] = True
            payload["_source_event_id"] = ev.id

            new_event = LegalEventOutbox(
                id=str(uuid4()),
                subject=ev.subject,
                payload_json=json.dumps(payload),
                status="pending",
                attempts=0,
            )
            self.session.add(new_event)
            replayed_items.append(
                ReplayEventItem(
                    id=new_event.id,
                    subject=new_event.subject,
                    payload_json=new_event.payload_json,
                    original_created_at=ev.created_at,
                    original_status=ev.status,
                )
            )

        await self.session.commit()

        return ReplayResult(
            replayed=len(replayed_items),
            skipped=skipped,
            events=replayed_items,
        )

    async def status(self) -> ReplayStatusResponse:
        total_stmt = select(func.count()).select_from(LegalEventOutbox)
        total = (await self.session.execute(total_stmt)).scalar_one()

        pending_stmt = select(func.count()).select_from(LegalEventOutbox).where(
            LegalEventOutbox.status == "pending"
        )
        pending = (await self.session.execute(pending_stmt)).scalar_one()

        published_stmt = select(func.count()).select_from(LegalEventOutbox).where(
            LegalEventOutbox.status == "published"
        )
        published = (await self.session.execute(published_stmt)).scalar_one()

        failed_stmt = select(func.count()).select_from(LegalEventOutbox).where(
            LegalEventOutbox.status == "failed"
        )
        failed = (await self.session.execute(failed_stmt)).scalar_one()

        return ReplayStatusResponse(
            total_outbox_events=total,
            pending=pending,
            published=published,
            failed=failed,
        )
