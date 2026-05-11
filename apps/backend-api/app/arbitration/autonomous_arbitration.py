from __future__ import annotations


class AutonomousArbitrationEngine:
    def arbitrate(self, dispute: dict[str, float]) -> dict[str, str]:
        severity = dispute["severity"]

        if severity > 0.9:
            return {
                "decision": "critical_intervention",
                "priority": "maximum",
            }

        if severity > 0.7:
            return {
                "decision": "federated_mediation",
                "priority": "high",
            }

        return {
            "decision": "automated_resolution",
            "priority": "normal",
        }
