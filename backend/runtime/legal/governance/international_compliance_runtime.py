from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class InternationalComplianceRuntime:
    """Validate international and interplanetary compliance controls."""

    def __init__(self) -> None:
        self._assessments: list[dict[str, Any]] = []

    def assess(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ["jurisdiction", "frameworks", "controls"]
        missing_fields = [field for field in required if not payload.get(field)]

        controls = payload.get("controls") or {}
        control_gaps = [name for name, is_enabled in controls.items() if not is_enabled]

        penalty = len(missing_fields) * 20.0 + len(control_gaps) * 10.0
        score = max(0.0, 100.0 - penalty)
        status = "approved" if score >= 85.0 else "attention"

        result = {
            "international_compliance_validation": len(missing_fields) == 0 and len(control_gaps) == 0,
            "status": status,
            "score": round(score, 2),
            "jurisdiction": payload.get("jurisdiction", "interplanetary"),
            "frameworks": payload.get("frameworks", []),
            "control_gaps": control_gaps,
            "missing_fields": missing_fields,
            "validated_at": datetime.now(UTC).isoformat(),
        }
        self._assessments.append(result)
        return result

    def metrics(self) -> dict[str, Any]:
        total = len(self._assessments)
        approved = sum(1 for item in self._assessments if item["international_compliance_validation"])
        ratio = (approved / total) if total else 1.0

        return {
            "total_assessments": total,
            "approved_assessments": approved,
            "international_compliance_ratio": round(ratio, 4),
        }
