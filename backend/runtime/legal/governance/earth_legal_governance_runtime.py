from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class EarthLegalGovernanceRuntime:
    """Evaluate Earth-scale legal governance readiness for major planetary interventions."""

    _DOMAIN_ORDER = [
        "environmental",
        "construction",
        "land",
        "water",
        "energy",
        "labor",
        "procurement",
        "data",
        "cross-border",
    ]

    _CRITICAL_DOMAINS = {"environmental", "labor", "data", "cross-border"}
    _CONDITIONAL_DOMAINS = {"construction", "land", "water", "energy", "procurement"}

    def __init__(self) -> None:
        self._evaluations: list[dict[str, Any]] = []

    def validate(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        domains_payload = payload.get("domains") or {}
        if isinstance(domains_payload, list):
            domain_values = {name: True for name in domains_payload}
        elif isinstance(domains_payload, dict):
            domain_values = {str(name): bool(value) for name, value in domains_payload.items()}
        else:
            domain_values = {}

        domain_results: dict[str, str] = {}
        for domain in self._DOMAIN_ORDER:
            value = domain_values.get(domain)
            if value is None:
                value = False

            if domain in self._CRITICAL_DOMAINS:
                status = "COMPLIANT" if bool(value) else "BLOCKED"
            elif domain in self._CONDITIONAL_DOMAINS:
                status = "COMPLIANT" if bool(value) else "CONDITIONAL"
            else:
                status = "COMPLIANT" if bool(value) else "CONDITIONAL"

            domain_results[domain] = status

        if any(status == "BLOCKED" for status in domain_results.values()):
            overall_status = "BLOCKED"
        elif any(status == "CONDITIONAL" for status in domain_results.values()):
            overall_status = "CONDITIONAL"
        else:
            overall_status = "COMPLIANT"

        result = {
            "overall_status": overall_status,
            "domain_results": domain_results,
            "validated_at": datetime.now(UTC).isoformat(),
        }
        self._evaluations.append(result)
        return result

    def metrics(self) -> dict[str, Any]:
        total = len(self._evaluations)
        compliant = sum(1 for item in self._evaluations if item["overall_status"] == "COMPLIANT")
        conditional = sum(1 for item in self._evaluations if item["overall_status"] == "CONDITIONAL")
        blocked = sum(1 for item in self._evaluations if item["overall_status"] == "BLOCKED")

        return {
            "total_evaluations": total,
            "compliant_evaluations": compliant,
            "conditional_evaluations": conditional,
            "blocked_evaluations": blocked,
        }
