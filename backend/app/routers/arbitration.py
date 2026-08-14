"""
LICEU 6.0 — Router: Arbitragem
Câmaras, casos, fases processuais, laudos — Lei 9.307/1996.
"""
from fastapi import APIRouter, HTTPException

from app.services.arbitration_service import arbitration_service

router = APIRouter()


@router.get("/chambers")
def list_chambers() -> dict:
    return {"chambers": arbitration_service.list_chambers()}


@router.post("/cases")
def open_case(payload: dict) -> dict:
    try:
        return arbitration_service.open_case(
            claimant=payload["claimant"],
            respondent=payload["respondent"],
            contract_id=payload["contract_id"],
            dispute_description=payload["dispute_description"],
            amount_in_dispute=payload.get("amount_in_dispute", 0.0),
            chamber_id=payload.get("chamber_id", "CAMARB"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/cases")
def list_cases() -> dict:
    return {"cases": arbitration_service.list_cases()}


@router.get("/cases/{case_id}")
def get_case(case_id: str) -> dict:
    try:
        return arbitration_service.get_case(case_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cases/{case_id}/advance")
def advance_phase(case_id: str) -> dict:
    try:
        return arbitration_service.advance_phase(case_id)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{case_id}/arbitrators")
def appoint_arbitrator(case_id: str, payload: dict) -> dict:
    try:
        return arbitration_service.appoint_arbitrator(
            case_id,
            arbitrator_name=payload["arbitrator_name"],
            role=payload.get("role", "único"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{case_id}/award")
def issue_award(case_id: str, payload: dict) -> dict:
    try:
        return arbitration_service.issue_award(
            case_id,
            decision=payload["decision"],
            awarded_amount=payload.get("awarded_amount"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
