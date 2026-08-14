from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ComplianceRuntime:
    """Evaluate legal governance compliance controls for a mission or contract."""

    def __init__(self) -> None:
        self._checks: list[dict[str, Any]] = []

    def check(
        self,
        *,
        jurisdiction: str,
        contract_type: str,
        obligations: list[str],
        controls: dict[str, bool],
    ) -> dict[str, Any]:
        normalized_controls = controls or {}
        missing_controls = [name for name, active in normalized_controls.items() if not active]

        baseline_obligations = ["audit_trail", "data_protection", "dispute_clause"]
        required_obligations = sorted(set(baseline_obligations + obligations))

        score = max(0.0, 100.0 - (len(missing_controls) * 15.0))
        status = "approved" if score >= 85.0 else "attention"

        result = {
            "status": status,
            "score": round(score, 2),
            "jurisdiction": (jurisdiction or "BR").upper(),
            "contract_type": contract_type.upper(),
            "required_obligations": required_obligations,
            "missing_controls": missing_controls,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        self._checks.append(result)
        return result

    def metrics(self) -> dict[str, Any]:
        total = len(self._checks)
        approved = sum(1 for item in self._checks if item["status"] == "approved")
        return {
            "total_checks": total,
            "approved_checks": approved,
            "approval_ratio": round((approved / total), 4) if total else 1.0,
        }
