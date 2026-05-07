from fastapi import APIRouter, HTTPException

from app.legal_core.esg_human_rights import ESGHumanRightsDomain

router = APIRouter()
_esg = ESGHumanRightsDomain()


@router.post("/evaluate")
def evaluate(payload: dict) -> dict:
    entity_id = payload.get("entity_id")
    if not entity_id:
        raise HTTPException(status_code=422, detail="entity_id é obrigatório")
    return _esg.evaluate(entity_id, payload.get("indicators", {}))
