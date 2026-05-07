from fastapi import APIRouter, HTTPException

from app.legal_core.psycholegal import PsycholegalDomain

router = APIRouter()
_psy = PsycholegalDomain()


@router.post("/assess")
def assess(payload: dict) -> dict:
    entity_id = payload.get("entity_id")
    if not entity_id:
        raise HTTPException(status_code=422, detail="entity_id é obrigatório")
    return _psy.assess(entity_id, payload.get("signals", {}))
