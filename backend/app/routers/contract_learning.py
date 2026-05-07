"""
LICEU 6.0 — Router: Melhoria Contínua Contratual
Registra eventos de aprendizado e gerencia reforços de cláusulas.
"""
from fastapi import APIRouter, HTTPException

from app.services.contract_learning import contract_learning

router = APIRouter()


@router.post("/event")
def record_event(payload: dict) -> dict:
    """
    Registra evento de aprendizado.
    Payload: { source, issue_type, context_tags?, details?, contract_id? }
    """
    try:
        return contract_learning.record_event(
            source=payload["source"],
            issue_type=payload["issue_type"],
            context_tags=payload.get("context_tags", []),
            details=payload.get("details", ""),
            contract_id=payload.get("contract_id"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/events")
def list_events() -> dict:
    return {"events": contract_learning.list_events()}


@router.get("/reinforcements")
def list_reinforcements(status: str | None = None) -> dict:
    return {"reinforcements": contract_learning.list_reinforcements(status)}


@router.post("/reinforcements/{reinforcement_id}/approve")
def approve_reinforcement(reinforcement_id: str) -> dict:
    try:
        return contract_learning.approve_reinforcement(reinforcement_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats")
def learning_stats() -> dict:
    return contract_learning.learning_stats()


@router.get("/issue-summary")
def issue_summary() -> dict:
    return {"issue_summary": contract_learning.issue_summary()}
