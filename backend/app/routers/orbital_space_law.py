from __future__ import annotations

from datetime import datetime, UTC

from fastapi import APIRouter

from app.integration.event_bus import event_bus

router = APIRouter()


@router.post("/treaty/analyze")
def analyze_treaty(payload: dict) -> dict:
    result = {
        "treaty_id": payload.get("treaty_id"),
        "jurisdiction": payload.get("jurisdiction", "orbit"),
        "compliant": bool(payload.get("compliant", True)),
        "analyzed_at": datetime.now(UTC).isoformat(),
    }
    if not result["compliant"]:
        event_bus.publish("space.treaty.violation", result)
    else:
        event_bus.publish("planetary.treaty.registered", result)
    return result


@router.post("/habitat/compliance")
def habitat_compliance(payload: dict) -> dict:
    return {
        "habitat_id": payload.get("habitat_id"),
        "zone": payload.get("zone", "lunar"),
        "status": payload.get("status", "compliant"),
    }


@router.post("/mining/risk")
def mining_risk(payload: dict) -> dict:
    return {
        "mission_id": payload.get("mission_id"),
        "risk_level": payload.get("risk_level", "medium"),
        "recommendation": payload.get("recommendation", "additional_legal_review"),
    }


@router.post("/mission/legal-review")
def mission_legal_review(payload: dict) -> dict:
    review = {
        "mission_id": payload.get("mission_id"),
        "approved": bool(payload.get("approved", True)),
        "reviewed_at": datetime.now(UTC).isoformat(),
    }
    if review["approved"]:
        event_bus.publish("space.mission.legal.approved", review)
    return review
