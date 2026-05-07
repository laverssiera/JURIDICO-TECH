"""
LICEU 6.x — Governance AI
Recomendações, bloqueios, alertas e escalonamento para governança.
"""
from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class GovernanceAIDomain:
    def evaluate_operation(self, operation: dict) -> dict:
        risk = int(operation.get("risk_score", 0))
        env_critical = operation.get("environmental_critical", False)
        fraud_signal = operation.get("fraud_signal", False)

        action = "approve"
        reason = "Risco em faixa aceitável"
        escalations = []

        if env_critical or fraud_signal or risk >= 80:
            action = "block"
            reason = "Risco crítico detectado"
            escalations = ["comite_governanca", "juridico_executivo", "compliance"]
        elif risk >= 60:
            action = "alert"
            reason = "Risco alto: exige auditoria e validação de governança"
            escalations = ["compliance", "gestao_riscos"]

        recommendations = self._recommendations(operation, action)
        return {
            "operation_id": operation.get("operation_id"),
            "action": action,
            "reason": reason,
            "escalations": escalations,
            "recommendations": recommendations,
            "evaluated_at": utc_now(),
        }

    def _recommendations(self, operation: dict, action: str) -> list[str]:
        recs = []
        if action == "block":
            recs.extend([
                "Bloquear expansão operacional imediatamente",
                "Exigir auditoria independente em 5 dias",
                "Emitir parecer jurídico obrigatório antes de retomada",
            ])
        elif action == "alert":
            recs.extend([
                "Aplicar plano de mitigação com responsáveis",
                "Monitorar indicadores críticos diariamente",
                "Submeter operação ao comitê em até 72h",
            ])
        else:
            recs.append("Manter monitoramento contínuo no Legal OS")
        return recs
