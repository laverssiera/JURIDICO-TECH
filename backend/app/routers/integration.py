from fastapi import APIRouter

router = APIRouter(prefix="/integration")

@router.post("/from-mae/legal-policy")
def receive_policy(payload: dict):
    return {"status": "policy received"}

@router.post("/from-mae/legal-request")
def receive_request(payload: dict):
    return {"status": "request received"}
