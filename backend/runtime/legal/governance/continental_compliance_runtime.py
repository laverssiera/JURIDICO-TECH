from __future__ import annotations

from typing import Any


class ContinentalComplianceRuntime:
    """Evaluate controls once for a multi-country legal state."""

    def assess(self, *, countries: list[str], controls: dict[str, bool], required_rules: list[str]) -> dict[str, Any]:
        missing = sorted(name for name, active in (controls or {}).items() if not active)
        if len(countries) > 1 and "cross_border_transfer" not in controls:
            missing.append("cross_border_transfer")
        score = max(0.0, 100.0 - (len(set(missing)) * 15.0))
        return {
            "status": "approved" if score >= 85.0 else "attention",
            "score": round(score, 2),
            "countries": [country.upper() for country in countries],
            "required_rules": sorted(set(required_rules)),
            "missing_controls": sorted(set(missing)),
        }