from __future__ import annotations

from datetime import datetime, UTC

from fastapi import APIRouter

from app.integration.event_bus import event_bus

router = APIRouter()


@router.post("/habitat/legal-check")
def habitat_legal_check(payload: dict) -> dict:
    result = {
        "habitat_id": payload.get("habitat_id"),
        "depth_zone": payload.get("depth_zone", "mesopelagic"),
        "status": payload.get("status", "compliant"),
        "checked_at": datetime.now(UTC).isoformat(),
    }
    if result["status"] == "compliant":
        event_bus.publish("oceanic.habitat.compliant", result)
    return result


@router.post("/material/compliance")
def material_compliance(payload: dict) -> dict:
    return {
        "material": payload.get("material"),
        "compliant": bool(payload.get("compliant", True)),
        "notes": payload.get("notes", ""),
    }


@router.post("/environmental-risk")
def environmental_risk(payload: dict) -> dict:
    return {
        "project_id": payload.get("project_id"),
        "risk_level": payload.get("risk_level", "medium"),
        "mitigation": payload.get("mitigation", []),
    }
