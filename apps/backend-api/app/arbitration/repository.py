from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ArbitrationCase, ArbitrationEvent


def _case_number() -> str:
    import random
    return f"ARB-{random.randint(10000, 99999)}"


class ArbitrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        title: str,
        parties: list[str],
        arbitrator_id: str | None,
        tenant_id: str | None,
    ) -> ArbitrationCase:
        case = ArbitrationCase(
            id=str(uuid4()),
            case_number=_case_number(),
            title=title,
            parties_json=json.dumps(parties),
            arbitrator_id=arbitrator_id,
            tenant_id=tenant_id,
        )
        event = ArbitrationEvent(
            id=str(uuid4()),
            case_id=case.id,
            event_type="filed",
            description=f"Case '{title}' filed with {len(parties)} parties.",
        )
        self.session.add_all([case, event])
        await self.session.commit()
        await self.session.refresh(case)
        return await self.get(case.id)  # reload with events

    async def get(self, case_id: str) -> ArbitrationCase | None:
        result = await self.session.execute(
            select(ArbitrationCase)
            .where(ArbitrationCase.id == case_id)
            .options(selectinload(ArbitrationCase.events))
        )
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: str | None = None) -> list[ArbitrationCase]:
        q = select(ArbitrationCase).options(selectinload(ArbitrationCase.events)).order_by(ArbitrationCase.created_at.desc())
        if tenant_id:
            q = q.where(ArbitrationCase.tenant_id == tenant_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def update(self, case_id: str, **kwargs) -> ArbitrationCase | None:
        case = await self.get(case_id)
        if not case:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(case, k, v)
        await self.session.commit()
        return await self.get(case_id)

    async def add_event(self, case_id: str, event_type: str, description: str) -> ArbitrationEvent:
        ev = ArbitrationEvent(
            id=str(uuid4()),
            case_id=case_id,
            event_type=event_type,
            description=description,
        )
        self.session.add(ev)
        await self.session.commit()
        await self.session.refresh(ev)
        return ev

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(ArbitrationCase.id)))
        return result.scalar_one()
