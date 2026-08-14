"""
LICEU 6.0 — Router: Litigation Engine
Gestão de processos, prazos, peças, evidências, analytics e tribunais.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.litigation import LitigationDomain

router = APIRouter()
_lit = LitigationDomain()


@router.post("/processes")
def open_process(payload: dict) -> dict:
    try:
        return _lit.open_process(
            process_type=payload["process_type"],
            plaintiff=payload["plaintiff"],
            defendant=payload["defendant"],
            description=payload["description"],
            tribunal=payload["tribunal"],
            tribunal_system=payload.get("tribunal_system", "PJe"),
            amount_in_dispute=payload.get("amount_in_dispute", 0.0),
            process_number=payload.get("process_number"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/processes")
def list_processes(status: str | None = None) -> dict:
    return {"processes": _lit.list_processes(status)}


@router.get("/processes/{process_id}")
def get_process(process_id: str) -> dict:
    try:
        return _lit.get_process(process_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/processes/{process_id}/advance")
def advance_phase(process_id: str) -> dict:
    try:
        return _lit.advance_phase(process_id)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/processes/{process_id}/deadlines")
def add_deadline(process_id: str, payload: dict) -> dict:
    try:
        return _lit.add_deadline(
            process_id=process_id,
            description=payload["description"],
            due_date=payload["due_date"],
            type_=payload.get("type", "processual"),
            assignee=payload.get("assignee"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/processes/{process_id}/deadlines")
def list_deadlines(process_id: str) -> dict:
    return {"deadlines": _lit.list_deadlines(process_id)}


@router.get("/deadlines/overdue")
def overdue_deadlines() -> dict:
    return {"overdue": _lit.overdue_deadlines()}


@router.post("/processes/{process_id}/pieces")
def add_piece(process_id: str, payload: dict) -> dict:
    try:
        return _lit.add_piece(
            process_id=process_id,
            piece_type=payload["piece_type"],
            content_summary=payload["content_summary"],
            author=payload["author"],
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/processes/{process_id}/evidence")
def add_evidence(process_id: str, payload: dict) -> dict:
    try:
        return _lit.add_evidence(
            process_id=process_id,
            description=payload["description"],
            evidence_type=payload["evidence_type"],
            source=payload["source"],
            hash_sha256=payload.get("hash_sha256"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/processes/{process_id}/evidence")
def list_evidence(process_id: str) -> dict:
    return {"evidence": _lit.list_evidence(process_id)}


@router.get("/analytics")
def litigation_analytics() -> dict:
    return _lit.litigation_analytics()


@router.get("/tribunals")
def list_tribunal_integrations() -> dict:
    return {"tribunals": _lit.list_tribunal_integrations()}
