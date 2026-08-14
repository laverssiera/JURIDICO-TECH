"""
LICEU 6.x — Autonomous Arbitration Engine
Mediação assistida por IA com timeline probatória e sugestão de acordo.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class AutonomousArbitrationDomain:
    def __init__(self) -> None:
        self._mediations: dict[str, dict] = {}

    def open_mediation(
        self,
        conflict_type: str,
        claimant: str,
        respondent: str,
        contract_id: str,
        claimed_amount: float,
    ) -> dict:
        mid = f"MED-{uuid4().hex[:8].upper()}"
        med = {
            "mediation_id": mid,
            "conflict_type": conflict_type,
            "claimant": claimant,
            "respondent": respondent,
            "contract_id": contract_id,
            "claimed_amount": claimed_amount,
            "status": "open",
            "evidence_timeline": [],
            "witness_graph": [],
            "ai_suggestion": None,
            "opened_at": utc_now(),
        }
        self._mediations[mid] = med
        return med

    def add_evidence_event(self, mediation_id: str, source: str, event: str, weight: float = 1.0) -> dict:
        med = self._get(mediation_id)
        entry = {"source": source, "event": event, "weight": weight, "at": utc_now()}
        med["evidence_timeline"].append(entry)
        return entry

    def add_witness_relation(self, mediation_id: str, person_a: str, person_b: str, relation: str) -> dict:
        med = self._get(mediation_id)
        rel = {"person_a": person_a, "person_b": person_b, "relation": relation, "at": utc_now()}
        med["witness_graph"].append(rel)
        return rel

    def ai_settlement_suggestion(self, mediation_id: str) -> dict:
        med = self._get(mediation_id)
        evidence_strength = sum(e.get("weight", 1.0) for e in med["evidence_timeline"]) 
        base = med["claimed_amount"]
        if evidence_strength >= 8:
            suggested = base * 0.85
        elif evidence_strength >= 4:
            suggested = base * 0.65
        else:
            suggested = base * 0.45
        proposal = {
            "suggested_amount": round(suggested, 2),
            "installments": 3 if suggested > 100_000 else 1,
            "conditions": [
                "Quitação total após cumprimento",
                "Confidencialidade bilateral",
                "Não judicialização sobre o mesmo objeto",
            ],
            "confidence": min(int(evidence_strength * 10), 95),
            "generated_at": utc_now(),
        }
        med["ai_suggestion"] = proposal
        return proposal

    def close_mediation(self, mediation_id: str, settlement_amount: float | None = None) -> dict:
        med = self._get(mediation_id)
        med["status"] = "closed"
        med["settlement_amount"] = settlement_amount
        med["closed_at"] = utc_now()
        return med

    def list_mediations(self) -> list[dict]:
        return list(self._mediations.values())

    def _get(self, mediation_id: str) -> dict:
        med = self._mediations.get(mediation_id)
        if not med:
            raise KeyError("Mediação não encontrada")
        return med
