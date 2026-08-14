"""
LICEU 6.0 — Router: Evidence Vault
Cofre de evidências com SHA-256, cadeia de custódia, ancoragem blockchain e ICP.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.evidence_vault import EvidenceVaultDomain

router = APIRouter()
_vault = EvidenceVaultDomain()


@router.post("/deposit")
def deposit_evidence(payload: dict) -> dict:
    try:
        return _vault.deposit(
            title=payload["title"],
            content=payload["content"],
            depositor=payload["depositor"],
            tags=payload.get("tags", []),
            linked_entity=payload.get("linked_entity"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/{evidence_id}/verify")
def verify_integrity(evidence_id: str, payload: dict) -> dict:
    original_content = payload.get("original_content", "")
    if not original_content:
        raise HTTPException(status_code=422, detail="original_content é obrigatório")
    try:
        return _vault.verify_integrity(evidence_id, original_content)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{evidence_id}/custody/transfer")
def transfer_custody(evidence_id: str, payload: dict) -> dict:
    try:
        return _vault.transfer_custody(
            evidence_id=evidence_id,
            from_=payload["from"],
            to=payload["to"],
            reason=payload.get("reason", ""),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{evidence_id}")
def get_item(evidence_id: str) -> dict:
    try:
        return _vault.get_item(evidence_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_items(tag: str | None = None, linked_entity: str | None = None) -> dict:
    return {"items": _vault.list_items(tag, linked_entity)}
