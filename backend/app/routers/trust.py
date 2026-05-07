from fastapi import APIRouter, HTTPException

from app.legal_core.trust_engine import TrustEngineDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_trust = TrustEngineDomain()


@router.post("/score")
def trust_score(payload: dict) -> dict:
    try:
        result = _trust.score(
            entity_id=payload["entity_id"],
            entity_type=payload["entity_type"],
            metrics=payload.get("metrics", {}),
        )
        event_bus.publish("trust.score.updated", result)
        return result
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")
