from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.compliance.repository import ComplianceRepository
from app.compliance.runtime import ComplianceRuntime
from app.compliance.schemas import (
    AlertResolveResponse,
    ComplianceAlertResponse,
    ComplianceCheckCreate,
    ComplianceCheckResponse,
    ComplianceListResponse,
    RuntimeStartRequest,
    RuntimeStatusResponse,
    RuntimeStopResponse,
)
from app.db.session import get_session

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
async def runtime_start(data: RuntimeStartRequest) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.register(data.entity_id, data.scope)
    # perform first pulse immediately
    ComplianceRuntime.pulse(data.entity_id)
    updated = ComplianceRuntime.status(data.entity_id)
    assert updated is not None
    return RuntimeStatusResponse(
        entity_id=updated.entity_id,
        scope=updated.scope,
        active=updated.active,
        registered_at=updated.registered_at,
        last_checked_at=updated.last_checked_at,
        last_score=updated.last_score,
        check_count=updated.check_count,
        last_findings=updated.last_findings,
    )


@router.get("/runtime/{entity_id}/status", response_model=RuntimeStatusResponse)
async def runtime_status(entity_id: str) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.status(entity_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="entity_not_registered")
    return RuntimeStatusResponse(
        entity_id=entry.entity_id,
        scope=entry.scope,
        active=entry.active,
        registered_at=entry.registered_at,
        last_checked_at=entry.last_checked_at,
        last_score=entry.last_score,
        check_count=entry.check_count,
        last_findings=entry.last_findings,
    )


@router.post("/runtime/{entity_id}/pulse", response_model=RuntimeStatusResponse)
async def runtime_pulse(entity_id: str) -> RuntimeStatusResponse:
    entry = ComplianceRuntime.pulse(entity_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="entity_not_registered_or_inactive")
    return RuntimeStatusResponse(
        entity_id=entry.entity_id,
        scope=entry.scope,
        active=entry.active,
        registered_at=entry.registered_at,
        last_checked_at=entry.last_checked_at,
        last_score=entry.last_score,
        check_count=entry.check_count,
        last_findings=entry.last_findings,
    )


@router.delete("/runtime/{entity_id}", response_model=RuntimeStopResponse)
async def runtime_stop(entity_id: str) -> RuntimeStopResponse:
    stopped = ComplianceRuntime.deregister(entity_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="entity_not_found")
    return RuntimeStopResponse(entity_id=entity_id, stopped=True)
