from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ClaimsRuntime:
    """Aggregate legal claim exposure from structured claim events."""

    def analyze(self, claims: list[dict[str, Any]]) -> dict[str, Any]:
        normalized_claims = claims or []
        total_amount = float(sum(float(item.get("amount", 0.0)) for item in normalized_claims))
        high_severity = [item for item in normalized_claims if str(item.get("severity", "")).lower() == "high"]

        return {
            "total_claims": len(normalized_claims),
            "high_severity_claims": len(high_severity),
            "exposure_amount": round(total_amount, 2),
            "analyzed_at": datetime.now(UTC).isoformat(),
        }
