"""
LICEU 6.x — Legal Operating System Runtime
Nenhuma operação crítica deve ser executada sem passar pelo runtime jurídico.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


CRITICAL_ACTIONS = {
    "create_spe",
    "approve_investment",
    "sign_contract",
    "hire_supplier",
    "start_project_phase",
    "tokenize_asset",
    "release_payment",
}


class LegalOSRuntimeDomain:
    def __init__(self) -> None:
        self._decisions: list[dict] = []

    def gate(self, operation_type: str, payload: dict) -> dict:
        decision_id = f"LRT-{uuid4().hex[:8].upper()}"
        risk_score = int(payload.get("risk_score", 0))
        trust_score = int(payload.get("trust_score", 50))
        mandatory_docs_ok = bool(payload.get("mandatory_docs_ok", False))

        allow = True
        reasons = []

        if operation_type in CRITICAL_ACTIONS and not mandatory_docs_ok:
            allow = False
            reasons.append("Documentação obrigatória incompleta")
        if risk_score >= 80:
            allow = False
            reasons.append("Risco jurídico crítico")
        if trust_score < 50:
            allow = False
            reasons.append("Trust Score insuficiente")

        if allow and operation_type in CRITICAL_ACTIONS and risk_score >= 60:
            reasons.append("Aprovado com monitoramento reforçado")

        decision = {
            "decision_id": decision_id,
            "operation_type": operation_type,
            "allow": allow,
            "reasons": reasons or ["Aprovado"],
            "risk_score": risk_score,
            "trust_score": trust_score,
            "evaluated_at": utc_now(),
        }
        self._decisions.append(decision)
        return decision

    def list_decisions(self) -> list[dict]:
        return self._decisions
