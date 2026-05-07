from fastapi import APIRouter

from app.integration.event_bus import event_bus
from app.schemas import ContractSignedEvent

router = APIRouter()


@router.post("/events/contract.signed")
def on_contract_signed(event: ContractSignedEvent) -> dict:
	executions = event_bus.publish("contract.signed", event.model_dump())
	if not executions:
		return {"event": "contract.signed", "status": "ignored", "reason": "no_subscribers"}
	return executions[0]

# Endpoints de Integração com Mãe LICEU
# Enviar para Mãe
# POST /integration/mae/legal-decision
# POST /integration/mae/legal-risk
# POST /integration/mae/legal-opportunity
# POST /integration/mae/legal-context

# Receber da Mãe
# POST /integration/from-mae/legal-policy
# POST /integration/from-mae/legal-request
# POST /integration/from-mae/legal-priority
