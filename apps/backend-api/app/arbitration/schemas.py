from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ArbitrationEventCreate(BaseModel):
    event_type: str
    description: str


class ArbitrationEventResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    case_id: str
    event_type: str
    description: str
    created_at: datetime


class ArbitrationCreate(BaseModel):
    title: str
    parties: list[str]
    arbitrator_id: str | None = None
    tenant_id: str | None = None


class ArbitrationUpdate(BaseModel):
    status: str | None = None
    arbitrator_id: str | None = None
    award_amount: float | None = None
    award_summary: str | None = None


class ArbitrationResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    case_number: str
    title: str
    status: str
    parties_json: str
    arbitrator_id: str | None
    tenant_id: str | None
    award_amount: float | None
    award_summary: str | None
    created_at: datetime
    updated_at: datetime
    events: list[ArbitrationEventResponse] = []


class ArbitrationListResponse(BaseModel):
    total: int
    items: list[ArbitrationResponse]
