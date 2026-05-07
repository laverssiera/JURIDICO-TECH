from datetime import datetime

from pydantic import BaseModel


class OutboxEventResponse(BaseModel):
    id: str
    subject: str
    payload_json: str
    status: str
    attempts: int
    created_at: datetime
    published_at: datetime | None
    last_error: str | None


class OutboxListResponse(BaseModel):
    items: list[OutboxEventResponse]
    total: int


class OutboxFlushResponse(BaseModel):
    scanned: int
    published: int
    pending: int


class WarRoomActionRequest(BaseModel):
    action: str
    source: str = "war_room"
    incident_id: str | None = None
    metadata: dict = {}


class WarRoomActionResponse(BaseModel):
    status: str
    event_id: str
    subject: str
