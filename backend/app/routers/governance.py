"""
LICEU 6.0 — Router: Governance
Deliberações, votações e saúde de governança corporativa.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.governance import GovernanceDomain

router = APIRouter()
_gov = GovernanceDomain()
_deliberations: dict[str, dict] = {}


@router.post("/deliberations")
def create_deliberation(payload: dict) -> dict:
    try:
        d = _gov.create_deliberation(
            entity_id=payload["entity_id"],
            title=payload["title"],
            resolution=payload["resolution"],
            approvers=payload["approvers"],
            quorum_required=payload.get("quorum_required", 0.51),
        )
        _deliberations[d["deliberation_id"]] = d
        return d
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/deliberations/{deliberation_id}/vote")
def cast_vote(deliberation_id: str, payload: dict) -> dict:
    d = _deliberations.get(deliberation_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deliberação não encontrada")
    return _gov.cast_vote(d, voter=payload["voter"], approve=payload["approve"])


@router.get("/deliberations/{deliberation_id}")
def get_deliberation(deliberation_id: str) -> dict:
    d = _deliberations.get(deliberation_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deliberação não encontrada")
    return d


@router.get("/deliberations")
def list_deliberations() -> dict:
    return {"deliberations": list(_deliberations.values())}


@router.post("/health")
def governance_health(entity: dict) -> dict:
    return _gov.governance_health(entity)
