from fastapi import APIRouter
from app.services.legal_engine import legal_engine

router = APIRouter()

@router.post("/check/{monolito_id}")
def run_compliance_check(monolito_id: str) -> dict:
    return legal_engine.compliance_check(monolito_id)

# POST /legal/compliance/audit
