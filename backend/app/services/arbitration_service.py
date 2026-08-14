"""
LICEU 6.0 — Serviço de Arbitragem
Orquestra o ArbitrationDomain com persistência em memória e eventos.
"""
from __future__ import annotations

from app.legal_core.arbitration import ArbitrationDomain

_domain = ArbitrationDomain()


class ArbitrationService:
    def __init__(self) -> None:
        self._domain = _domain

    def open_case(
        self,
        claimant: str,
        respondent: str,
        contract_id: str,
        dispute_description: str,
        amount_in_dispute: float,
        chamber_id: str = "CAMARB",
    ) -> dict:
        return self._domain.open_case(
            claimant, respondent, contract_id,
            dispute_description, amount_in_dispute, chamber_id
        )

    def advance_phase(self, case_id: str) -> dict:
        return self._domain.advance_phase(case_id)

    def appoint_arbitrator(self, case_id: str, arbitrator_name: str, role: str = "único") -> dict:
        return self._domain.appoint_arbitrator(case_id, arbitrator_name, role)

    def issue_award(self, case_id: str, decision: str, awarded_amount: float | None = None) -> dict:
        return self._domain.issue_award(case_id, decision, awarded_amount)

    def get_case(self, case_id: str) -> dict:
        return self._domain.get_case(case_id)

    def list_cases(self) -> list[dict]:
        return self._domain.list_cases()

    def list_chambers(self) -> list[dict]:
        return self._domain.list_chambers()


arbitration_service = ArbitrationService()
