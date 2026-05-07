from fastapi import APIRouter, HTTPException

from app.legal_core.smart_clause import SmartClauseDomain

router = APIRouter()
_clause = SmartClauseDomain()


@router.post("/")
def register_clause(payload: dict) -> dict:
    try:
        return _clause.register_clause(payload["type"], payload["text"], payload.get("tags"))
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/{clause_id}/performance")
def record_performance(clause_id: str, payload: dict) -> dict:
    try:
        return _clause.record_performance(
            clause_id,
            prevented_litigation=payload["prevented_litigation"],
            contract_value=payload.get("contract_value"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def list_clauses(recommended_only: bool = False) -> dict:
    return {"clauses": _clause.list_clauses(recommended_only)}
