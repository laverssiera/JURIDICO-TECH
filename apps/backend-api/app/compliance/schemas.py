from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ComplianceAlertResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    check_id: str
    alert_type: str
    severity: str
    message: str
    resolved: bool
    created_at: datetime


class ComplianceCheckCreate(BaseModel):
    entity_id: str
    scope: str = "global"
    tenant_id: str | None = None


class ComplianceCheckResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    entity_id: str
    scope: str
    status: str
    score: float
    findings_json: str
    tenant_id: str | None
    created_at: datetime
    completed_at: datetime | None
    alerts: list[ComplianceAlertResponse] = []


class ComplianceListResponse(BaseModel):
    total: int
    items: list[ComplianceCheckResponse]


class AlertResolveResponse(BaseModel):
    id: str
    resolved: bool
