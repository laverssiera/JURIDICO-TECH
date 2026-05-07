"""
LICEU 6.x — Legal Digital Twin
Gêmeo jurídico vivo por entidade: contratos, compliance, contencioso e comportamento operacional.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.persistence.store import PersistenceStore

UTC = timezone.utc
_DOMAIN = "legal_digital_twin"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class LegalDigitalTwinDomain:
    def __init__(self, store: "PersistenceStore | None" = None) -> None:
        self._store = store
        self._twins: dict[str, dict] = {}
        if store:
            for record in store.list(_DOMAIN):
                key = f"{record['entity_type']}:{record['entity_id']}"
                self._twins[key] = record

    def upsert_twin(
        self,
        entity_type: str,
        entity_id: str,
        contracts: dict | None = None,
        compliance: dict | None = None,
        litigation: dict | None = None,
        behavior: dict | None = None,
    ) -> dict:
        key = f"{entity_type}:{entity_id}"
        current = self._twins.get(key, {
            "twin_id": f"TWIN-{uuid4().hex[:10].upper()}",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "created_at": utc_now(),
        })
        current["contracts"] = contracts or current.get("contracts", {})
        current["compliance"] = compliance or current.get("compliance", {})
        current["litigation"] = litigation or current.get("litigation", {})
        current["behavior"] = behavior or current.get("behavior", {})
        current["legal_exposure"] = self._compute_exposure(current)
        current["predicted_claim_probability"] = self._predict_claim_probability(current)
        current["updated_at"] = utc_now()
        self._twins[key] = current
        if self._store:
            self._store.set(_DOMAIN, key, current)
        return current

    def get_twin(self, entity_type: str, entity_id: str) -> dict:
        key = f"{entity_type}:{entity_id}"
        twin = self._twins.get(key)
        if not twin:
            raise KeyError(f"Twin não encontrado para {key}")
        return twin

    def list_twins(self, entity_type: str | None = None) -> list[dict]:
        twins = list(self._twins.values())
        if entity_type:
            return [t for t in twins if t["entity_type"] == entity_type]
        return twins

    def _compute_exposure(self, twin: dict) -> int:
        score = 0
        contracts = twin.get("contracts", {})
        compliance = twin.get("compliance", {})
        litigation = twin.get("litigation", {})
        behavior = twin.get("behavior", {})

        if contracts.get("overdue", 0) > 0:
            score += min(contracts.get("overdue", 0) * 8, 30)
        if compliance.get("critical_non_conformities", 0) > 0:
            score += min(compliance.get("critical_non_conformities", 0) * 12, 36)
        if litigation.get("active_cases", 0) > 0:
            score += min(litigation.get("active_cases", 0) * 10, 30)
        if behavior.get("high_delay_risk"):
            score += 10
        if behavior.get("aggressive_pattern"):
            score += 8

        return min(score, 100)

    def _predict_claim_probability(self, twin: dict) -> int:
        exposure = twin.get("legal_exposure", 0)
        contracts = twin.get("contracts", {})
        behavior = twin.get("behavior", {})

        probability = exposure * 0.6
        probability += min(contracts.get("conflicts", 0) * 6, 20)
        if behavior.get("high_delay_risk"):
            probability += 8
        if behavior.get("litigious_trend"):
            probability += 10
        return min(int(probability), 100)
