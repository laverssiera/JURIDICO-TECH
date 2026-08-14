from __future__ import annotations

from typing import Any


CANONICAL_NATS_EVENTS = [
    "liceu.legal.runtime.started",
    "liceu.legal.case.created",
    "liceu.legal.arbitration.executed",
    "liceu.legal.compliance.alert",
    "liceu.legal.ip.violation",
    "liceu.legal.interplanetary.regulation",
    "liceu.legal.collective_ai.sync",
    "liceu.legal.governance.decision",
]


class CausalLegalRuntime:
    def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        impact: list[str] = []

        if event["type"] == "contract_breach":
            impact.extend(
                [
                    "financial_risk",
                    "compliance_risk",
                    "reputation_risk",
                ]
            )

        if event["type"] == "unauthorized_patent_use":
            impact.extend(
                [
                    "ip_violation",
                    "global_litigation_risk",
                ]
            )

        return {
            "event": event["type"],
            "causal_impact": impact,
        }
