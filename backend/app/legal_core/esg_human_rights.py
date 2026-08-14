"""
LICEU 6.x — ESG + Human Rights Engine
Monitoramento de direitos humanos, SST, acessibilidade, impacto social e cadeia de fornecedores.
"""
from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ESGHumanRightsDomain:
    def evaluate(self, entity_id: str, indicators: dict) -> dict:
        score = 100
        issues = []

        if indicators.get("analogous_slave_labor_risk"):
            score -= 40
            issues.append("Risco de trabalho análogo à escravidão")
        if not indicators.get("sst_compliant", True):
            score -= 20
            issues.append("Não conformidade em SST")
        if not indicators.get("accessibility_compliant", True):
            score -= 10
            issues.append("Não conformidade em acessibilidade")
        if not indicators.get("waste_disposal_compliant", True):
            score -= 10
            issues.append("Gestão de resíduos inadequada")
        if indicators.get("high_emissions", False):
            score -= 10
            issues.append("Nível de emissões acima da política")
        if indicators.get("supplier_chain_non_compliant", False):
            score -= 15
            issues.append("Cadeia de fornecedores com não conformidades ESG")

        score = max(score, 0)
        status = "GREEN" if score >= 80 else ("YELLOW" if score >= 60 else "RED")
        return {
            "entity_id": entity_id,
            "esg_human_rights_score": score,
            "status": status,
            "issues": issues,
            "recommended_actions": self._actions(status),
            "integrations": ["CIRCULUS", "OPERA", "RH", "ANCHOR"],
            "evaluated_at": utc_now(),
        }

    def _actions(self, status: str) -> list[str]:
        if status == "RED":
            return [
                "Bloquear operação crítica até regularização",
                "Abrir auditoria socioambiental externa",
                "Escalar para comitê ESG e jurídico executivo",
            ]
        if status == "YELLOW":
            return [
                "Plano de correção em 30 dias",
                "Treinamento obrigatório de fornecedores e equipes",
            ]
        return ["Manter monitoramento mensal"]
