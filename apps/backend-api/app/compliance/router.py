from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.compliance.repository import ComplianceRepository
from app.compliance.runtime import ComplianceRuntime
from app.compliance.schemas import (
    AlertResolveResponse,
    ComplianceAlertResponse,
    ComplianceCheckCreate,
    ComplianceCheckResponse,
    ComplianceListResponse,
    RuntimeListResponse,
    RuntimeScopeUpdateRequest,
    RuntimeStartRequest,
    RuntimeStatusResponse,
    RuntimeStopResponse,
)
from app.db.session import get_session
from app.events.repository import OutboxRepository

router = APIRouter()


def _repo(session=Depends(get_session)) -> ComplianceRepository:
    return ComplianceRepository(session)


@router.post("/check", response_model=ComplianceCheckResponse, status_code=201)
async def run_check(data: ComplianceCheckCreate, repo: ComplianceRepository = Depends(_repo)):
    return await repo.run_check(data.entity_id, data.scope, data.tenant_id)


@router.get("/checks", response_model=ComplianceListResponse)
async def list_checks(entity_id: str | None = None, repo: ComplianceRepository = Depends(_repo)):
    items = await repo.list_all(entity_id=entity_id)
    return ComplianceListResponse(total=len(items), items=items)


@router.get("/checks/{check_id}", response_model=ComplianceCheckResponse)
async def get_check(check_id: str, repo: ComplianceRepository = Depends(_repo)):
    check = await repo.get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    return check


@router.get("/alerts/open", response_model=list[ComplianceAlertResponse])
async def open_alerts(repo: ComplianceRepository = Depends(_repo)):
    return await repo.list_open_alerts()


@router.patch("/alerts/{alert_id}/resolve", response_model=AlertResolveResponse)
async def resolve_alert(alert_id: str, repo: ComplianceRepository = Depends(_repo)):
    alert = await repo.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResolveResponse(id=alert.id, resolved=alert.resolved)


# ── Runtime endpoints ─────────────────────────────────────────────────────────

@router.post("/runtime/start", response_model=RuntimeStatusResponse, status_code=201)
async def runtime_start(
    data: RuntimeStartRequest,
    session: AsyncSession = Depends(get_session),
) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.register(
        data.entity_id,
        data.scope,
        case_code=data.case_code,
        case_name=data.case_name,
        mission_profile=data.mission_profile,
        objective_tracks=data.objective_tracks,
    )
    # perform first pulse immediately
    ComplianceRuntime.pulse(data.entity_id)
    updated = ComplianceRuntime.status(data.entity_id)
    assert updated is not None

    outbox = OutboxRepository(session)
    await outbox.enqueue(
        subject="legal.compliance.runtime.started",
        payload={
            "entity_id": updated.entity_id,
            "scope": updated.scope,
            "case_code": updated.case_code,
            "case_name": updated.case_name,
            "mission_profile": updated.mission_profile,
            "objective_tracks": updated.objective_tracks,
            "active": updated.active,
            "check_count": updated.check_count,
            "last_score": updated.last_score,
        },
    )
    await session.commit()

    return RuntimeStatusResponse(
        entity_id=updated.entity_id,
        scope=updated.scope,
        case_code=updated.case_code,
        case_name=updated.case_name,
        mission_profile=updated.mission_profile,
        objective_tracks=updated.objective_tracks,
        active=updated.active,
        registered_at=updated.registered_at,
        last_checked_at=updated.last_checked_at,
        last_score=updated.last_score,
        check_count=updated.check_count,
        last_findings=updated.last_findings,
    )


@router.get("/runtime", response_model=RuntimeListResponse)
async def runtime_list(
    active: bool | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    order_by: Literal["registered_at", "last_checked_at"] = Query(default="registered_at"),
    direction: Literal["asc", "desc"] = Query(default="desc"),
) -> RuntimeListResponse:
    entries = ComplianceRuntime.list_all(
        active=active,
        order_by=order_by,
        direction=direction,
    )
    total = len(entries)
    paged_entries = entries[offset : offset + limit]
    items = [
        RuntimeStatusResponse(
            entity_id=entry.entity_id,
            scope=entry.scope,
            case_code=entry.case_code,
            case_name=entry.case_name,
            mission_profile=entry.mission_profile,
            objective_tracks=entry.objective_tracks,
            active=entry.active,
            registered_at=entry.registered_at,
            last_checked_at=entry.last_checked_at,
            last_score=entry.last_score,
            check_count=entry.check_count,
            last_findings=entry.last_findings,
        )
        for entry in paged_entries
    ]
    return RuntimeListResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/runtime/{entity_id}/status", response_model=RuntimeStatusResponse)
async def runtime_status(entity_id: str) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.status(entity_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="entity_not_registered")
    return RuntimeStatusResponse(
        entity_id=entry.entity_id,
        scope=entry.scope,
        case_code=entry.case_code,
        case_name=entry.case_name,
        mission_profile=entry.mission_profile,
        objective_tracks=entry.objective_tracks,
        active=entry.active,
        registered_at=entry.registered_at,
        last_checked_at=entry.last_checked_at,
        last_score=entry.last_score,
        check_count=entry.check_count,
        last_findings=entry.last_findings,
    )


@router.post("/runtime/{entity_id}/pulse", response_model=RuntimeStatusResponse)
async def runtime_pulse(
    entity_id: str,
    session: AsyncSession = Depends(get_session),
) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.pulse(entity_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="entity_not_registered_or_inactive")

    outbox = OutboxRepository(session)
    await outbox.enqueue(
        subject="legal.compliance.runtime.pulsed",
        payload={
            "entity_id": entry.entity_id,
            "scope": entry.scope,
            "active": entry.active,
            "check_count": entry.check_count,
            "last_score": entry.last_score,
            "findings_total": len(entry.last_findings),
        },
    )
    await session.commit()

    return RuntimeStatusResponse(
        entity_id=entry.entity_id,
        scope=entry.scope,
        case_code=entry.case_code,
        case_name=entry.case_name,
        mission_profile=entry.mission_profile,
        objective_tracks=entry.objective_tracks,
        active=entry.active,
        registered_at=entry.registered_at,
        last_checked_at=entry.last_checked_at,
        last_score=entry.last_score,
        check_count=entry.check_count,
        last_findings=entry.last_findings,
    )


@router.patch("/runtime/{entity_id}/scope", response_model=RuntimeStatusResponse)
async def runtime_update_scope(
    entity_id: str,
    data: RuntimeScopeUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.update_scope(entity_id, data.scope)
    if entry is None:
        raise HTTPException(status_code=404, detail="entity_not_registered_or_inactive")

    if data.pulse_after_update:
        pulsed = ComplianceRuntime.pulse(entity_id)
        if pulsed is not None:
            entry = pulsed

    outbox = OutboxRepository(session)
    await outbox.enqueue(
        subject="legal.compliance.runtime.scope_updated",
        payload={
            "entity_id": entry.entity_id,
            "scope": entry.scope,
            "active": entry.active,
            "check_count": entry.check_count,
            "last_score": entry.last_score,
        },
    )
    await session.commit()

    return RuntimeStatusResponse(
        entity_id=entry.entity_id,
        scope=entry.scope,
        case_code=entry.case_code,
        case_name=entry.case_name,
        mission_profile=entry.mission_profile,
        objective_tracks=entry.objective_tracks,
        active=entry.active,
        registered_at=entry.registered_at,
        last_checked_at=entry.last_checked_at,
        last_score=entry.last_score,
        check_count=entry.check_count,
        last_findings=entry.last_findings,
    )


@router.delete("/runtime/{entity_id}", response_model=RuntimeStopResponse)
async def runtime_stop(
    entity_id: str,
    session: AsyncSession = Depends(get_session),
) -> RuntimeStopResponse:
    stopped = ComplianceRuntime.deregister(entity_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="entity_not_found")

    outbox = OutboxRepository(session)
    await outbox.enqueue(
        subject="legal.compliance.runtime.stopped",
        payload={
            "entity_id": entity_id,
            "stopped": True,
        },
    )
    await session.commit()

    return RuntimeStopResponse(entity_id=entity_id, stopped=True)
