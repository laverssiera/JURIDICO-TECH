from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ComplianceAlertResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    check_id: str
    alert_type: str
    severity: str
    message: str = Field(min_length=1)
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
    case_code: str | None = None
    case_name: str | None = None
    mission_profile: dict[str, Any] = Field(default_factory=dict)
    objective_tracks: list[str] = Field(default_factory=list)


class RuntimeScopeUpdateRequest(BaseModel):
    scope: str = "global"
    pulse_after_update: bool = True


class RuntimeFinding(BaseModel):
    rule: str
    alert_type: str
    severity: str
    passed: bool
    message: str = Field(min_length=1)


class RuntimeStatusResponse(BaseModel):
    entity_id: str
    scope: str
    case_code: str | None = None
    case_name: str | None = None
    mission_profile: dict[str, Any] = Field(default_factory=dict)
    objective_tracks: list[str] = Field(default_factory=list)
    active: bool
    registered_at: datetime
    last_checked_at: datetime | None
    last_score: float | None
    check_count: int
    last_findings: list[RuntimeFinding] = Field(default_factory=list)


class RuntimeListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[RuntimeStatusResponse] = Field(default_factory=list)


class RuntimeStopResponse(BaseModel):
    entity_id: str
    stopped: bool
