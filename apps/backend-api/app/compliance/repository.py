from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.compliance.engine import run_compliance_engine
from app.db.models import ComplianceAlert, ComplianceCheck


class ComplianceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run_check(self, entity_id: str, scope: str, tenant_id: str | None) -> ComplianceCheck:
        score, findings = run_compliance_engine(entity_id, scope)
        status = "passed" if score >= 70 else ("review" if score >= 40 else "failed")

        check = ComplianceCheck(
            id=str(uuid4()),
            entity_id=entity_id,
            scope=scope,
            score=score,
            status=status,
            findings_json=json.dumps([f.rule for f in findings]),
            tenant_id=tenant_id,
            completed_at=datetime.now(UTC),
        )
        self.session.add(check)

        for f in findings:
            if not f.passed:
                alert = ComplianceAlert(
                    id=str(uuid4()),
                    check_id=check.id,
                    alert_type=f.alert_type,
                    severity=f.severity,
                    message=f.message,
                )
                self.session.add(alert)

        await self.session.commit()
        return await self.get(check.id)

    async def get(self, check_id: str) -> ComplianceCheck | None:
        result = await self.session.execute(
            select(ComplianceCheck)
            .where(ComplianceCheck.id == check_id)
            .options(selectinload(ComplianceCheck.alerts))
        )
        return result.scalar_one_or_none()

    async def list_all(self, entity_id: str | None = None, tenant_id: str | None = None) -> list[ComplianceCheck]:
        q = (
            select(ComplianceCheck)
            .options(selectinload(ComplianceCheck.alerts))
            .order_by(ComplianceCheck.created_at.desc())
        )
        if entity_id:
            q = q.where(ComplianceCheck.entity_id == entity_id)
        if tenant_id:
            q = q.where(ComplianceCheck.tenant_id == tenant_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def resolve_alert(self, alert_id: str) -> ComplianceAlert | None:
        alert = await self.session.get(ComplianceAlert, alert_id)
        if alert:
            alert.resolved = True
            await self.session.commit()
        return alert

    async def list_open_alerts(self, tenant_id: str | None = None) -> list[ComplianceAlert]:
        q = select(ComplianceAlert).where(ComplianceAlert.resolved == False)  # noqa: E712
        result = await self.session.execute(q)
        return list(result.scalars().all())
