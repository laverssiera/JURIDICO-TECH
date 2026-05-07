"""
LICEU 6.0 — Router: Forensic Lab
Perícias, laudos, cadeia de custódia, timeline técnica.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.forensic import ForensicLabDomain

router = APIRouter()
_forensic = ForensicLabDomain()


@router.get("/types")
def list_types() -> dict:
    return {
        "pericia_types": _forensic.list_pericia_types(),
        "evidence_types": _forensic.list_evidence_types(),
    }


@router.post("/laudos")
def open_pericia(payload: dict) -> dict:
    try:
        return _forensic.open_pericia(
            pericia_type=payload["pericia_type"],
            requester=payload["requester"],
            subject=payload["subject"],
            location=payload.get("location"),
            linked_process_id=payload.get("linked_process_id"),
            perito_name=payload.get("perito_name"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/laudos")
def list_laudos(status: str | None = None) -> dict:
    return {"laudos": _forensic.list_laudos(status)}


@router.get("/laudos/{laudo_id}")
def get_laudo(laudo_id: str) -> dict:
    try:
        return _forensic.get_laudo(laudo_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/laudos/{laudo_id}/findings")
def add_finding(laudo_id: str, payload: dict) -> dict:
    try:
        return _forensic.add_finding(
            laudo_id=laudo_id,
            finding=payload["finding"],
            severity=payload.get("severity", "informational"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/laudos/{laudo_id}/evidence")
def add_evidence(laudo_id: str, payload: dict) -> dict:
    try:
        return _forensic.add_evidence_item(
            laudo_id=laudo_id,
            description=payload["description"],
            evidence_type=payload["evidence_type"],
            source_system=payload["source_system"],
            hash_sha256=payload.get("hash_sha256"),
            icp_signed=payload.get("icp_signed", False),
            blockchain_anchor=payload.get("blockchain_anchor"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/laudos/{laudo_id}/conclude")
def conclude(laudo_id: str, payload: dict) -> dict:
    try:
        return _forensic.conclude_laudo(
            laudo_id=laudo_id,
            conclusion=payload["conclusion"],
            perito=payload.get("perito"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/laudos/{laudo_id}/custody/transfer")
def transfer_custody(laudo_id: str, payload: dict) -> dict:
    try:
        return _forensic.transfer_custody(
            laudo_id=laudo_id,
            from_=payload["from"],
            to=payload["to"],
            reason=payload.get("reason", ""),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/laudos/{laudo_id}/custody")
def get_custody_chain(laudo_id: str) -> dict:
    try:
        return {"custody_chain": _forensic.get_custody_chain(laudo_id)}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/laudos/{laudo_id}/timeline")
def reconstruct_timeline(laudo_id: str) -> dict:
    try:
        return _forensic.reconstruct_event_timeline(laudo_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
