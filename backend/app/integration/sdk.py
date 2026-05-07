from __future__ import annotations

from app.schemas import SPERequest
from app.services.legal_engine import legal_engine


class SPEFactory:
    def start_closing_workflow(
        self,
        *,
        contract_id: str,
        monolito_id: str,
        spe_name: str,
        partners: list[str],
        purpose: str,
    ) -> dict:
        spe_draft = legal_engine.create_spe(
            SPERequest(
                name=spe_name,
                partners=partners,
                purpose=purpose,
            )
        )
        compliance = legal_engine.compliance_check(monolito_id)

        return {
            "event": "contract.signed",
            "contract_id": contract_id,
            "status": "closing_started",
            "spe_draft": spe_draft,
            "compliance": compliance,
            "next_steps": [
                "Protocolar ato constitutivo",
                "Consolidar assinatura dos sócios",
                "Agendar registro no órgão competente",
            ],
        }


spe_factory = SPEFactory()
