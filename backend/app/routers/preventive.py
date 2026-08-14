"""
LICEU 6.0 — Router: Preventivo
Score jurídico vivo para qualquer entidade do ecossistema.
Obras, contratos, fornecedores, SPEs, investidores, colaboradores.
"""
from fastapi import APIRouter

from app.services.preventive_module import preventive_module

router = APIRouter()


@router.post("/score")
def score_entity(payload: dict) -> dict:
    """
    Score jurídico vivo.
    Payload: { entity_id, entity_type, active_risks: [], context?: {} }
    """
    return preventive_module.score_entity(
        entity_id=payload.get("entity_id", ""),
        entity_type=payload.get("entity_type", "geral"),
        active_risks=payload.get("active_risks", []),
        extra_context=payload.get("context"),
    )


@router.post("/score/obra")
def score_obra(payload: dict) -> dict:
    return preventive_module.score_obra(
        obra_id=payload["obra_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.post("/score/contrato")
def score_contrato(payload: dict) -> dict:
    return preventive_module.score_contrato(
        contract_id=payload["contract_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.post("/score/fornecedor")
def score_fornecedor(payload: dict) -> dict:
    return preventive_module.score_fornecedor(
        supplier_id=payload["supplier_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.post("/score/spe")
def score_spe(payload: dict) -> dict:
    return preventive_module.score_spe(
        spe_id=payload["spe_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.post("/score/investidor")
def score_investidor(payload: dict) -> dict:
    return preventive_module.score_investidor(
        investor_id=payload["investor_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.post("/score/colaborador")
def score_colaborador(payload: dict) -> dict:
    return preventive_module.score_colaborador(
        collab_id=payload["collaborator_id"],
        active_risks=payload.get("active_risks", []),
        context=payload.get("context"),
    )


@router.get("/factors")
def list_factors(scope: str | None = None) -> dict:
    return {"factors": preventive_module.available_risk_factors(scope)}


@router.get("/history")
def score_history() -> dict:
    return {"history": preventive_module.score_history()}
