from fastapi import APIRouter

from app.legal_core.governance_ai import GovernanceAIDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_gai = GovernanceAIDomain()


@router.post("/evaluate")
def evaluate_operation(payload: dict) -> dict:
    result = _gai.evaluate_operation(payload)
    if result.get("action") == "block":
        event_bus.publish("governance_ai.block", result)
    return result
