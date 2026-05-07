from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.compliance.repository import ComplianceRepository
from app.compliance.schemas import (
    AlertResolveResponse,
    ComplianceAlertResponse,
    ComplianceCheckCreate,
    ComplianceCheckResponse,
    ComplianceListResponse,
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
