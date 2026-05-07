from datetime import datetime

from pydantic import BaseModel


class OutboxEventResponse(BaseModel):
    id: str
    subject: str
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
