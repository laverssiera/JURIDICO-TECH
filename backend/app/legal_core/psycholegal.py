"""
LICEU 6.x — Psycholegal Engine
Análise de padrões comportamentais com foco em conflito, fraude e tendência litigiosa.
"""
from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class PsycholegalDomain:
    def assess(self, entity_id: str, signals: dict) -> dict:
        score = 0
        findings = []

        if signals.get("pattern_change"):
            score += 20
            findings.append("Mudança abrupta de padrão operacional")
        if signals.get("contract_aggressiveness"):
            score += 20
            findings.append("Agressividade contratual elevada")
        if int(signals.get("recurring_delays", 0)) >= 3:
            score += 25
            findings.append("Atrasos recorrentes com impacto jurídico")
        if signals.get("toxic_communication"):
            score += 15
            findings.append("Sinal de ambiente comunicacional tóxico")
        if signals.get("fraud_indicators"):
            score += 30
            findings.append("Indicadores de potencial fraude")

        litigious_trend = min(int(score * 0.9), 100)
        risk_level = "LOW"
        if score >= 70:
            risk_level = "CRITICAL"
        elif score >= 50:
            risk_level = "HIGH"
        elif score >= 30:
            risk_level = "MEDIUM"

        return {
            "entity_id": entity_id,
            "psycholegal_risk_score": min(score, 100),
            "risk_level": risk_level,
            "litigious_trend": litigious_trend,
            "findings": findings,
            "recommended_actions": self._actions(risk_level),
            "evaluated_at": utc_now(),
        }

    def _actions(self, level: str) -> list[str]:
        if level == "CRITICAL":
            return [
                "Bloquear novas contratações com a entidade",
                "Abrir due diligence forense imediata",
                "Escalar para War Room e Governança",
            ]
        if level == "HIGH":
            return [
                "Aplicar mediação preventiva",
                "Reforçar cláusulas de garantia e penalidade",
                "Monitoramento semanal do comportamento",
            ]
        if level == "MEDIUM":
            return [
                "Plano de mitigação comportamental",
                "Monitoramento quinzenal",
            ]
        return ["Monitoramento de rotina"]
