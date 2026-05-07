from fastapi import APIRouter, HTTPException

from app.legal_core.legal_war_room import LegalWarRoomDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_wr = LegalWarRoomDomain()


@router.post("/incidents")
def open_incident(payload: dict) -> dict:
    try:
        incident = _wr.open_incident(
            title=payload["title"],
            severity=payload["severity"],
            category=payload["category"],
            summary=payload["summary"],
        )
        event_bus.publish("war_room.incident.opened", incident)
        return incident
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/incidents")
def list_incidents(status: str | None = None) -> dict:
    return {"incidents": _wr.list_incidents(status)}


@router.post("/incidents/{incident_id}/evidence")
def add_evidence(incident_id: str, payload: dict) -> dict:
    try:
        evidence = _wr.add_evidence(incident_id, payload["description"], payload["source"])
        event_bus.publish(
            "litigation.evidence.added",
            {"incident_id": incident_id, **evidence},
        )
        return evidence
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/incidents/{incident_id}/official-response")
def official_response(incident_id: str) -> dict:
    try:
        return _wr.official_response(incident_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
