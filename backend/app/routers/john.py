from fastapi import APIRouter
from app.john.john_juridico import john_legal_decision

router = APIRouter(prefix="/john")

@router.post("/legal/decision")
def legal_decision(payload: dict):
    return john_legal_decision(payload)
