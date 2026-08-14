from __future__ import annotations

from typing import Any


class ContinentalIPRuntime:
    """Track intellectual-property protection coverage across countries."""

    def assess(self, *, countries: list[str], assets: list[dict[str, Any]]) -> dict[str, Any]:
        normalized = [country.strip().upper() for country in countries if country.strip()]
        protected = []
        gaps = []
        for asset in assets:
            asset_id = asset.get("asset_id", "unidentified")
            protected_in = [country.upper() for country in asset.get("protected_in", [])]
            missing = [country for country in normalized if country not in protected_in]
            protected.append({"asset_id": asset_id, "type": asset.get("type", "unknown"), "protected_in": protected_in})
            if missing:
                gaps.append({"asset_id": asset_id, "missing_countries": missing})
        return {
            "asset_count": len(protected),
            "protected_assets": protected,
            "protection_gaps": gaps,
            "coverage_ratio": round((len(protected) - len(gaps)) / len(protected), 4) if protected else 1.0,
        }