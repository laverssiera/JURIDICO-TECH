"""
LICEU 6.x — Global Legal Simulation
Teoria dos jogos jurídica para simular disputas, impactos, cenários regulatórios e riscos futuros.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.persistence.store import PersistenceStore

UTC = timezone.utc
_DOMAIN = "global_legal_simulation"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class GlobalLegalSimulationDomain:
    def __init__(self, store: "PersistenceStore | None" = None) -> None:
        self._store = store
        self._scenarios: dict[str, dict] = {}
        if store:
            for record in store.list(_DOMAIN):
                self._scenarios[record["scenario_id"]] = record

    def simulate_supplier_failure(
        self,
        supplier_id: str,
        affected_works: int,
        affected_contracts: int,
        financial_exposure: float,
        contingency_ready: bool = False,
    ) -> dict:
        scenario_id = f"SIM-{uuid4().hex[:8].upper()}"
        legal_risk_score = self._risk_from_exposure(
            affected_works,
            affected_contracts,
            financial_exposure,
            contingency_ready,
        )
        impact = self._impact_vector(affected_works, affected_contracts, financial_exposure)

        result = {
            "scenario_id": scenario_id,
            "scenario_type": "supplier_failure",
            "input": {
                "supplier_id": supplier_id,
                "affected_works": affected_works,
                "affected_contracts": affected_contracts,
                "financial_exposure": financial_exposure,
                "contingency_ready": contingency_ready,
            },
            "legal_risk_score": legal_risk_score,
            "risk_level": self._risk_level(legal_risk_score),
            "impact": impact,
            "recommended_actions": self._recommended_actions(legal_risk_score, contingency_ready),
            "simulated_at": utc_now(),
        }
        self._scenarios[scenario_id] = result
        if self._store:
            self._store.set(_DOMAIN, scenario_id, result)
        return result

    def simulate_regulatory_change(
        self,
        regulation_name: str,
        impacted_units: list[str],
        adaptation_days: int,
        penalty_estimate: float,
    ) -> dict:
        scenario_id = f"SIM-{uuid4().hex[:8].upper()}"
        base = min(impacted_units.__len__() * 12 + int(penalty_estimate / 150_000), 100)
        if adaptation_days <= 15:
            base = max(base - 15, 0)
        elif adaptation_days > 45:
            base = min(base + 15, 100)

        result = {
            "scenario_id": scenario_id,
            "scenario_type": "regulatory_change",
            "input": {
                "regulation_name": regulation_name,
                "impacted_units": impacted_units,
                "adaptation_days": adaptation_days,
                "penalty_estimate": penalty_estimate,
            },
            "legal_risk_score": base,
            "risk_level": self._risk_level(base),
            "impact": {
                "units": impacted_units,
                "penalty_estimate": penalty_estimate,
                "adaptation_urgency": "high" if adaptation_days <= 15 else "medium",
            },
            "recommended_actions": [
                "Ativar plano de adequação normativa",
                "Disparar treinamento obrigatório por unidade impactada",
                "Atualizar cláusulas e checklists de compliance",
            ],
            "simulated_at": utc_now(),
        }
        self._scenarios[scenario_id] = result
        if self._store:
            self._store.set(_DOMAIN, scenario_id, result)
        return result

    def list_scenarios(self, scenario_type: str | None = None) -> list[dict]:
        values = list(self._scenarios.values())
        if scenario_type:
            values = [v for v in values if v.get("scenario_type") == scenario_type]
        return values

    def get_scenario(self, scenario_id: str) -> dict:
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise KeyError("Cenário não encontrado")
        return scenario

    def _risk_from_exposure(
        self,
        affected_works: int,
        affected_contracts: int,
        financial_exposure: float,
        contingency_ready: bool,
    ) -> int:
        score = 0
        score += min(affected_works * 10, 35)
        score += min(affected_contracts * 6, 30)
        score += min(int(financial_exposure / 250_000), 35)
        if contingency_ready:
            score = max(score - 20, 0)
        return min(score, 100)

    def _impact_vector(self, works: int, contracts: int, exposure: float) -> dict:
        return {
            "works_disrupted": works,
            "contracts_at_risk": contracts,
            "financial_exposure": exposure,
            "cascade_probability": min(int((works * 8 + contracts * 5) / 2), 100),
        }

    def _risk_level(self, score: int) -> str:
        if score >= 80:
            return "CRITICAL"
        if score >= 60:
            return "HIGH"
        if score >= 35:
            return "MEDIUM"
        return "LOW"

    def _recommended_actions(self, score: int, contingency_ready: bool) -> list[str]:
        actions = ["Mapear contratos alternativos de contingência"]
        if score >= 80:
            actions.extend([
                "Ativar Legal War Room imediatamente",
                "Bloquear novas ordens ao fornecedor em risco",
                "Escalar para Governança AI e Comitê Executivo",
            ])
        elif score >= 60:
            actions.extend([
                "Executar plano de substituição de fornecedor",
                "Negociar aditivos de prazo e garantias",
            ])
        else:
            actions.append("Manter monitoramento semanal")

        if not contingency_ready:
            actions.append("Formalizar plano de contingência operacional-jurídica")
        return actions
