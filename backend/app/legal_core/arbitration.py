"""
LICEU 6.0 — Domain: Arbitration
Módulo de Arbitragem — câmaras, casos, fases processuais, laudos.
Lei n.º 9.307/1996 (Lei de Arbitragem Brasileira).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


ARBITRATION_PHASES = [
    "instauração",
    "nomeação_árbitros",
    "termos_de_arbitragem",
    "instrução",
    "alegações_finais",
    "laudo",
    "encerrado",
]

REGISTERED_CHAMBERS = [
    {"id": "CAMARB", "name": "Câmara de Arbitragem Empresarial – Brasil", "specialty": "empresarial"},
    {"id": "FGV_CAM", "name": "FGV – Centro de Arbitragem e Mediação", "specialty": "geral"},
    {"id": "CAM_CCBC", "name": "Centro de Arbitragem e Mediação da CCBC", "specialty": "internacional"},
    {"id": "CAM_SP", "name": "Câmara de Arbitragem do Mercado (B3)", "specialty": "mercado_capitais"},
    {"id": "CBMAE", "name": "Câmara Brasileira de Mediação e Arbitragem Empresarial", "specialty": "imobiliário"},
]


class ArbitrationDomain:
    def __init__(self) -> None:
        self._cases: dict[str, dict] = {}

    # ── Caso ──────────────────────────────────────────────────────────────────

    def open_case(
        self,
        claimant: str,
        respondent: str,
        contract_id: str,
        dispute_description: str,
        amount_in_dispute: float,
        chamber_id: str = "CAMARB",
    ) -> dict:
        case_id = f"ARB-{uuid4().hex[:8].upper()}"
        chamber = next((c for c in REGISTERED_CHAMBERS if c["id"] == chamber_id), REGISTERED_CHAMBERS[0])
        case = {
            "case_id": case_id,
            "claimant": claimant,
            "respondent": respondent,
            "contract_id": contract_id,
            "dispute_description": dispute_description,
            "amount_in_dispute": amount_in_dispute,
            "chamber": chamber,
            "phase": ARBITRATION_PHASES[0],
            "arbitrators": [],
            "timeline": [{"phase": ARBITRATION_PHASES[0], "at": utc_now()}],
            "award": None,
            "status": "open",
            "opened_at": utc_now(),
        }
        self._cases[case_id] = case
        return case

    def advance_phase(self, case_id: str) -> dict:
        case = self._cases.get(case_id)
        if not case:
            raise KeyError(f"Caso {case_id} não encontrado")
        current_idx = ARBITRATION_PHASES.index(case["phase"])
        if current_idx >= len(ARBITRATION_PHASES) - 1:
            raise ValueError("Caso já encerrado")
        next_phase = ARBITRATION_PHASES[current_idx + 1]
        case["phase"] = next_phase
        case["timeline"].append({"phase": next_phase, "at": utc_now()})
        if next_phase == "encerrado":
            case["status"] = "closed"
        return case

    def appoint_arbitrator(self, case_id: str, arbitrator_name: str, role: str = "único") -> dict:
        case = self._cases.get(case_id)
        if not case:
            raise KeyError(f"Caso {case_id} não encontrado")
        case["arbitrators"].append({"name": arbitrator_name, "role": role, "appointed_at": utc_now()})
        return case

    def issue_award(self, case_id: str, decision: str, awarded_amount: float | None = None) -> dict:
        case = self._cases.get(case_id)
        if not case:
            raise KeyError(f"Caso {case_id} não encontrado")
        case["award"] = {
            "decision": decision,
            "awarded_amount": awarded_amount,
            "issued_at": utc_now(),
        }
        case["phase"] = "laudo"
        case["timeline"].append({"phase": "laudo", "at": utc_now()})
        return case

    def get_case(self, case_id: str) -> dict:
        case = self._cases.get(case_id)
        if not case:
            raise KeyError(f"Caso {case_id} não encontrado")
        return case

    def list_cases(self) -> list[dict]:
        return list(self._cases.values())

    def list_chambers(self) -> list[dict]:
        return REGISTERED_CHAMBERS
