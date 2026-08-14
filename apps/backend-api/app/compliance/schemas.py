from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


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
    alerts: list[ComplianceAlertResponse] = Field(default_factory=list)


class ComplianceListResponse(BaseModel):
    total: int
    items: list[ComplianceCheckResponse]


class AlertResolveResponse(BaseModel):
    id: str
    resolved: bool


# ── Runtime schemas ───────────────────────────────────────────────────────────

class RuntimeStartRequest(BaseModel):
    entity_id: str
    scope: str = "global"


class RuntimeFinding(BaseModel):
    rule: str
    alert_type: str
    severity: str
    passed: bool
    message: str


class RuntimeStatusResponse(BaseModel):
    entity_id: str
    scope: str
    active: bool
    registered_at: datetime
    last_checked_at: datetime | None
    last_score: float | None
    check_count: int
    last_findings: list[RuntimeFinding] = Field(default_factory=list)


class RuntimeStopResponse(BaseModel):
    entity_id: str
    stopped: bool
