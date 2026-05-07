from fastapi import APIRouter, HTTPException

from app.legal_core.legal_os_runtime import LegalOSRuntimeDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_runtime = LegalOSRuntimeDomain()


@router.post("/gate")
def gate(payload: dict) -> dict:
    operation_type = payload.get("operation_type")
    if not operation_type:
        raise HTTPException(status_code=422, detail="operation_type é obrigatório")
    decision = _runtime.gate(operation_type=operation_type, payload=payload)
    if decision.get("allow"):
        event_bus.publish("legal.approved", decision)
    else:
        event_bus.publish("legal_os.gate.blocked", decision)
    return decision


@router.get("/decisions")
def list_decisions() -> dict:
    return {"decisions": _runtime.list_decisions()}
