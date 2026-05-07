"""
LICEU 6.0 — Módulo Preventivo
Score jurídico vivo: obras, contratos, fornecedores, investidores,
colaboradores, SPEs, laudos e empreendimentos.
"""
from __future__ import annotations

from app.legal_core.legal_risk import LegalRiskDomain, RISK_FACTORS
from app.legal_core.legal_ai import LegalAIDomain

_risk = LegalRiskDomain()
_ai = LegalAIDomain()


class PreventiveModule:
    """Ponto de entrada unificado do Módulo Preventivo do LICEU 6.0."""

    def __init__(self) -> None:
        self._risk = _risk
        self._ai = _ai
        # Histórico de scores para aprendizado
        self._score_history: list[dict] = []

    # ── Score ─────────────────────────────────────────────────────────────────

    def score_entity(
        self,
        entity_id: str,
        entity_type: str,
        active_risks: list[str],
        extra_context: dict | None = None,
    ) -> dict:
        result = self._risk.score(entity_id, entity_type, active_risks, extra_context)
        interpretation = self._ai.interpret_risk(
            result["legal_risk_score"], entity_type, result["issues"]
        )
        action_plan = self._ai.suggest_action_plan(result["issues"])
        self._score_history.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "score": result["legal_risk_score"],
            "level": result["risk_level"],
        })
        return {
            **result,
            "interpretation": interpretation,
            "action_plan": action_plan,
        }

    def score_obra(self, obra_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(obra_id, "obra", active_risks, context)

    def score_contrato(self, contract_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(contract_id, "contrato", active_risks, context)

    def score_fornecedor(self, supplier_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(supplier_id, "fornecedor", active_risks, context)

    def score_spe(self, spe_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(spe_id, "spe", active_risks, context)

    def score_investidor(self, investor_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(investor_id, "investidor", active_risks, context)

    def score_colaborador(self, collab_id: str, active_risks: list[str], context: dict | None = None) -> dict:
        return self.score_entity(collab_id, "colaborador", active_risks, context)

    # ── Consultas ─────────────────────────────────────────────────────────────

    def available_risk_factors(self, scope: str | None = None) -> list[dict]:
        return self._risk.available_factors(scope)

    def score_history(self) -> list[dict]:
        return self._score_history


preventive_module = PreventiveModule()
