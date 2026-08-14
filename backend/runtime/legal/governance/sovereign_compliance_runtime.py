from __future__ import annotations

from datetime import datetime, UTC


class SovereignComplianceRuntime:
    def __init__(self) -> None:
        self._validations: list[dict] = []

    def validate(self, payload: dict) -> dict:
        required = ["jurisdiction", "risk_level", "policy_bundle"]
        missing = [field for field in required if not payload.get(field)]

        result = {
            "autonomous_compliance_validation": len(missing) == 0,
            "missing_fields": missing,
            "jurisdiction": payload.get("jurisdiction", "earth"),
            "risk_level": payload.get("risk_level", "medium"),
            "policy_bundle": payload.get("policy_bundle", "baseline"),
            "validated_at": datetime.now(UTC).isoformat(),
        }
        self._validations.append(result)
        return result

    def metrics(self) -> dict:
        total = len(self._validations)
        passed = sum(1 for item in self._validations if item["autonomous_compliance_validation"])
        ratio = (passed / total) if total else 1.0
        return {
            "total_validations": total,
            "passed_validations": passed,
            "compliance_propagation_ratio": round(ratio, 4),
        }
