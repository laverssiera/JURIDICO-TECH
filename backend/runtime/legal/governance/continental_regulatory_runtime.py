from __future__ import annotations

from typing import Any


class ContinentalRegulatoryRuntime:
    """Build a country-by-country regulatory map for one legal operation."""

    _BUNDLES = {
        "BR": ["lgpd", "anti_corruption", "tax_registration"],
        "PT": ["gdpr", "anti_corruption", "tax_registration"],
        "ES": ["gdpr", "data_governance", "tax_registration"],
        "FR": ["gdpr", "data_governance", "foreign_investment_screening"],
        "DE": ["gdpr", "data_governance", "supply_chain_due_diligence"],
    }

    def assess(self, *, countries: list[str], sectors: list[str] | None = None) -> dict[str, Any]:
        normalized = [country.strip().upper() for country in countries if country.strip()]
        by_country = {
            country: self._BUNDLES.get(country, ["local_data_protection", "tax_registration", "anti_corruption"])
            for country in normalized
        }
        rules = sorted({rule for bundle in by_country.values() for rule in bundle})
        return {
            "countries": normalized,
            "sectors": sorted({sector.strip().lower() for sector in (sectors or []) if sector.strip()}),
            "rules": rules,
            "by_country": by_country,
            "regulatory_conflicts": ["data_transfer"] if len(normalized) > 1 else [],
        }