from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReplayRequest(BaseModel):
    subject_filter: str | None = None
    from_dt: datetime | None = None
    to_dt: datetime | None = None
    limit: int = 100


class ReplayEventItem(BaseModel):
    id: str
    subject: str
    payload_json: str
    original_created_at: datetime
    original_status: str


class ReplayResult(BaseModel):
    replayed: int
    skipped: int
    events: list[ReplayEventItem]


class ReplayStatusResponse(BaseModel):
    total_outbox_events: int
    pending: int
    published: int
    failed: int
