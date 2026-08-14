from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter

from app.integration.event_bus import event_bus

router = APIRouter()
_reviews: list[dict] = []


@router.post("/compliance/check")
def compliance_check(payload: dict) -> dict:
    result = {
        "id": str(uuid4()),
        "research_type": payload.get("research_type", "general"),
        "risk_level": payload.get("risk_level", "medium"),
        "jurisdiction_scope": payload.get("jurisdiction_scope", "earth"),
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }
    _reviews.append(result)
    return {"status": "checked", "data": result}


@router.post("/compliance/approve")
def compliance_approve(payload: dict) -> dict:
    event = {
        "review_id": payload.get("review_id"),
        "approved_by": payload.get("approved_by"),
        "approved_at": datetime.now(UTC).isoformat(),
    }
    event_bus.publish("research.compliance.approved", event)
    return {"status": "approved", "data": event}


@router.post("/compliance/block")
def compliance_block(payload: dict) -> dict:
    event = {
        "review_id": payload.get("review_id"),
        "blocked_by": payload.get("blocked_by"),
        "reason": payload.get("reason", ""),
        "blocked_at": datetime.now(UTC).isoformat(),
    }
    event_bus.publish("research.compliance.blocked", event)
    return {"status": "blocked", "data": event}


@router.get("/compliance/history")
def compliance_history() -> dict:
    return {"items": _reviews}
