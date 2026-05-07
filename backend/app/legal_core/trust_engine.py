"""
LICEU 6.x — Trust Engine
Motor de confiança para fornecedores, investidores, parceiros, clientes e colaboradores.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.persistence.store import PersistenceStore

UTC = timezone.utc
_DOMAIN = "trust_engine"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class TrustEngineDomain:
    def __init__(self, store: "PersistenceStore | None" = None) -> None:
        self._store = store
    def score(self, entity_id: str, entity_type: str, metrics: dict) -> dict:
        # Pesos calibráveis por estratégia de risco do ecossistema
        weights = {
            "compliance": 0.2,
            "historico": 0.15,
            "litigios": 0.15,
            "performance": 0.15,
            "esg": 0.1,
            "financeiro": 0.1,
            "comportamento": 0.1,
            "reputacao": 0.05,
        }
        total = 0.0
        missing = []
        for key, weight in weights.items():
            value = metrics.get(key)
            if value is None:
                missing.append(key)
                value = 50
            total += float(value) * weight

        trust_score = max(0, min(int(total), 100))
        tier = "LOW"
        if trust_score >= 80:
            tier = "HIGH"
        elif trust_score >= 60:
            tier = "MEDIUM"

        result = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "trust_score": trust_score,
            "trust_tier": tier,
            "missing_metrics": missing,
            "recommended_policy": self._policy(trust_score),
            "evaluated_at": utc_now(),
        }
        self._persist_score(entity_id, entity_type, result)
        return result

    def _persist_score(self, entity_id: str, entity_type: str, result: dict) -> None:
        if self._store:
            self._store.set(_DOMAIN, f"{entity_type}:{entity_id}", result)

    def _policy(self, score: int) -> str:
        if score >= 80:
            return "Fast-track habilitado com auditoria trimestral"
        if score >= 60:
            return "Operação permitida com monitoramento reforçado"
        return "Bloqueio preventivo até plano de correção"
