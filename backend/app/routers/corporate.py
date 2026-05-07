"""
LICEU 6.0 — Router: Corporate Engine
Abertura de empresas, SPEs, holdings, cap table, atas, tokenização.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.corporate import CorporateDomain

router = APIRouter()
_corp = CorporateDomain()


@router.get("/checklist")
def open_company_checklist(entity_type: str = "ltda") -> dict:
    return {"checklist": _corp.open_company_checklist(entity_type), "entity_type": entity_type}


@router.post("/entities")
def register_entity(payload: dict) -> dict:
    try:
        return _corp.register_entity(
            name=payload["name"],
            entity_type=payload["entity_type"],
            object_description=payload["object"],
            partners=payload["partners"],
            cnpj=payload.get("cnpj"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/entities")
def list_entities(entity_type: str | None = None) -> dict:
    return {"entities": _corp.list_entities(entity_type)}


@router.get("/entities/{entity_id}")
def get_entity(entity_id: str) -> dict:
    try:
        return _corp.get_entity(entity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/entities/{entity_id}/cap-table")
def get_cap_table(entity_id: str) -> dict:
    return _corp.get_cap_table(entity_id)


@router.post("/entities/{entity_id}/cap-table")
def update_cap_table(entity_id: str, payload: dict) -> dict:
    try:
        return _corp.update_cap_table(
            entity_id=entity_id,
            partner=payload["partner"],
            participation_pct=float(payload["participation_pct"]),
            operation=payload.get("operation", "add"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/entities/{entity_id}/atas")
def record_ata(entity_id: str, payload: dict) -> dict:
    try:
        return _corp.record_ata(
            entity_id=entity_id,
            tipo=payload["tipo"],
            pauta=payload["pauta"],
            resolucoes=payload["resolucoes"],
            presentes=payload["presentes"],
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/entities/{entity_id}/atas")
def list_atas(entity_id: str) -> dict:
    return {"atas": _corp.list_atas(entity_id)}


@router.post("/entities/{entity_id}/tokenization")
def tokenization_flow(entity_id: str, payload: dict) -> dict:
    try:
        return _corp.spe_tokenization_flow(
            spe_id=entity_id,
            token_supply=int(payload["token_supply"]),
            price_per_token=float(payload["price_per_token"]),
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
