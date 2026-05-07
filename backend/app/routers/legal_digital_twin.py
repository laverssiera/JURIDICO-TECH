from fastapi import APIRouter, HTTPException

from app.legal_core.legal_digital_twin import LegalDigitalTwinDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_twin = LegalDigitalTwinDomain()


@router.post("/upsert")
def upsert_twin(payload: dict) -> dict:
    try:
        twin = _twin.upsert_twin(
            entity_type=payload["entity_type"],
            entity_id=payload["entity_id"],
            contracts=payload.get("contracts"),
            compliance=payload.get("compliance"),
            litigation=payload.get("litigation"),
            behavior=payload.get("behavior"),
        )
        event_bus.publish("twin.updated", twin)
        if twin.get("legal_exposure", 0) >= 80:
            event_bus.publish("twin.risk.critical", twin)
        return twin
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/")
def list_twins(entity_type: str | None = None) -> dict:
    return {"twins": _twin.list_twins(entity_type)}


@router.get("/{entity_type}/{entity_id}")
def get_twin(entity_type: str, entity_id: str) -> dict:
    try:
        return _twin.get_twin(entity_type, entity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
