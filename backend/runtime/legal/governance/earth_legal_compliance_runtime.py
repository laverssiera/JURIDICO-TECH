from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


_EARTH_DOMAINS = [
    "território",
    "licenciamento",
    "contratos",
    "dados",
    "infraestrutura",
    "ambiental",
    "construção",
    "energia",
]

_CRITICAL_DOMAINS = {"ambiental", "dados", "contratos"}
_CONDITIONAL_DOMAINS = {"território", "licenciamento", "infraestrutura", "construção", "energia"}


class EarthLegalComplianceRuntime:
    """Validate Earth legal compliance across the eight sovereign domains."""

    def __init__(self) -> None:
        self._audit_log: list[dict[str, Any]] = []

    def validate(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        raw_domains = payload.get("domains") or {}

        if isinstance(raw_domains, list):
            domain_values: dict[str, bool] = {d: True for d in raw_domains}
        elif isinstance(raw_domains, dict):
            domain_values = {str(k): bool(v) for k, v in raw_domains.items()}
        else:
            domain_values = {}

        domain_results: dict[str, str] = {}
        for domain in _EARTH_DOMAINS:
            active = domain_values.get(domain, False)
            if domain in _CRITICAL_DOMAINS:
                domain_results[domain] = "COMPLIANT" if active else "BLOCKED"
            else:
                domain_results[domain] = "COMPLIANT" if active else "CONDITIONAL"

        if any(s == "BLOCKED" for s in domain_results.values()):
            overall_status = "BLOCKED"
        elif any(s == "CONDITIONAL" for s in domain_results.values()):
            overall_status = "CONDITIONAL"
        else:
            overall_status = "COMPLIANT"

        event = self._emit_audit_event(
            event_type="earth.legal.compliance.validated",
            overall_status=overall_status,
            domain_results=domain_results,
            payload=payload,
        )

        return {
            "event_id": event["event_id"],
            "overall_status": overall_status,
            "domain_results": domain_results,
            "validated_at": event["emitted_at"],
        }

    def _emit_audit_event(
        self,
        *,
        event_type: str,
        overall_status: str,
        domain_results: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        event: dict[str, Any] = {
            "event_id": f"elc-{uuid4().hex[:12]}",
            "event_type": event_type,
            "overall_status": overall_status,
            "domain_results": domain_results,
            "source_payload": payload,
            "emitted_at": datetime.now(UTC).isoformat(),
        }
        self._audit_log.append(event)
        return event

    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def metrics(self) -> dict[str, Any]:
        total = len(self._audit_log)
        compliant = sum(1 for e in self._audit_log if e["overall_status"] == "COMPLIANT")
        conditional = sum(1 for e in self._audit_log if e["overall_status"] == "CONDITIONAL")
        blocked = sum(1 for e in self._audit_log if e["overall_status"] == "BLOCKED")
        return {
            "total_validations": total,
            "compliant": compliant,
            "conditional": conditional,
            "blocked": blocked,
            "compliance_ratio": round(compliant / total, 4) if total else 1.0,
        }


if __name__ == "__main__":
    import json

    runtime = EarthLegalComplianceRuntime()

    scenarios = [
        {
            "label": "Todos os domínios ativos",
            "domains": {d: True for d in _EARTH_DOMAINS},
        },
        {
            "label": "Domínio crítico 'ambiental' inativo",
            "domains": {d: True for d in _EARTH_DOMAINS} | {"ambiental": False},
        },
        {
            "label": "Domínio condicional 'energia' inativo",
            "domains": {d: True for d in _EARTH_DOMAINS} | {"energia": False},
        },
    ]

    for scenario in scenarios:
        result = runtime.validate({"domains": scenario["domains"]})
        print(f"\n[{scenario['label']}]")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n--- Métricas ---")
    print(json.dumps(runtime.metrics(), indent=2, ensure_ascii=False))
    print("\n--- Audit Log ---")
    for event in runtime.audit_log():
        print(json.dumps(event, indent=2, ensure_ascii=False))
