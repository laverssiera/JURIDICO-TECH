from fastapi import APIRouter, HTTPException

from app.legal_core.autonomous_arbitration import AutonomousArbitrationDomain

router = APIRouter()
_auto = AutonomousArbitrationDomain()


@router.post("/mediations")
def open_mediation(payload: dict) -> dict:
    try:
        return _auto.open_mediation(
            conflict_type=payload["conflict_type"],
            claimant=payload["claimant"],
            respondent=payload["respondent"],
            contract_id=payload["contract_id"],
            claimed_amount=float(payload["claimed_amount"]),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/mediations/{mediation_id}/evidence")
def add_evidence(mediation_id: str, payload: dict) -> dict:
    try:
        return _auto.add_evidence_event(
            mediation_id,
            source=payload["source"],
            event=payload["event"],
            weight=float(payload.get("weight", 1.0)),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mediations/{mediation_id}/settlement")
def settlement(mediation_id: str) -> dict:
    try:
        return _auto.ai_settlement_suggestion(mediation_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/mediations")
def list_mediations() -> dict:
    return {"mediations": _auto.list_mediations()}
