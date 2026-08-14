from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class GlobalComplianceRuntime:
    """Validate cross-border and multi-jurisdiction contract compliance."""

    _FRAMEWORK_REQUIREMENTS: dict[str, set[str]] = {
        "LGPD": {"data_protection", "consent_management", "cross_border_transfer", "dpo_designation"},
        "GDPR": {"data_protection", "consent_management", "cross_border_transfer", "dpo_designation", "incident_reporting"},
        "Space Law": {"orbital_operations_authorization", "space_assets_registry", "collision_avoidance"},
        "Maritime Law": {"maritime_cargo_documentation", "marine_environment_compliance"},
        "International Treaties": {"treaty_obligations", "sovereignty_clauses", "dispute_resolution", "incident_reporting"},
    }

    def __init__(self) -> None:
        self._validations: list[dict[str, Any]] = []

    def validate_contract(self, payload: dict[str, Any]) -> dict[str, Any]:
        frameworks = payload.get("frameworks") or []
        controls = payload.get("controls") or {}

        normalized_frameworks = [str(item).strip() for item in frameworks if str(item).strip()]
        if not normalized_frameworks:
            normalized_frameworks = list(self._FRAMEWORK_REQUIREMENTS.keys())

        normalized_frameworks = [framework for framework in normalized_frameworks if framework in self._FRAMEWORK_REQUIREMENTS]
        missing_controls: list[str] = []
        framework_status: dict[str, list[str]] = {}

        for framework in normalized_frameworks:
            required_controls = self._FRAMEWORK_REQUIREMENTS[framework]
            missing_for_framework = [control for control in sorted(required_controls) if not controls.get(control, False)]
            if missing_for_framework:
                missing_controls.extend(missing_for_framework)
            framework_status[framework] = missing_for_framework

        score = max(0.0, 100.0 - (len(missing_controls) * 8.0))
        status = "approved" if score >= 85.0 else "attention"
        is_valid = len(missing_controls) == 0 and bool(normalized_frameworks)

        result = {
            "global_compliance_validation": is_valid,
            "status": status,
            "score": round(score, 2),
            "jurisdiction": str(payload.get("jurisdiction", "global") or "global").upper(),
            "contract_type": str(payload.get("contract_type", "contract") or "contract").upper(),
            "frameworks": normalized_frameworks,
            "framework_status": framework_status,
            "missing_controls": sorted(set(missing_controls)),
            "validated_at": datetime.now(UTC).isoformat(),
        }
        self._validations.append(result)
        return result

    def metrics(self) -> dict[str, Any]:
        total = len(self._validations)
        approved = sum(1 for item in self._validations if item["global_compliance_validation"])
        ratio = round((approved / total), 4) if total else 1.0

        return {
            "total_validations": total,
            "approved_validations": approved,
            "global_compliance_ratio": ratio,
        }
