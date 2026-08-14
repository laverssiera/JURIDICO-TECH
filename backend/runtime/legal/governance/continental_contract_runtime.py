from __future__ import annotations

from typing import Any


class ContinentalContractRuntime:
    """Resolve contract requirements across a chain of continental jurisdictions."""

    def assess(self, *, countries: list[str], contracts: list[dict[str, Any]]) -> dict[str, Any]:
        normalized_countries = [country.strip().upper() for country in countries if country.strip()]
        assessments = []
        for contract in contracts:
            governing_law = (contract.get("governing_law") or normalized_countries[0] if normalized_countries else "INTL")
            assessments.append(
                {
                    "contract_id": contract.get("contract_id", "unidentified"),
                    "contract_type": contract.get("contract_type", "unknown").upper(),
                    "governing_law": governing_law.upper(),
                    "operating_countries": [
                        country.upper() for country in contract.get("operating_countries", normalized_countries)
                    ],
                    "cross_border": len(normalized_countries) > 1,
                    "required_clauses": ["choice_of_law", "jurisdiction", "data_transfer", "dispute_resolution"]
                    if len(normalized_countries) > 1
                    else ["choice_of_law", "dispute_resolution"],
                }
            )
        return {
            "contract_count": len(assessments),
            "cross_border_contracts": sum(item["cross_border"] for item in assessments),
            "assessments": assessments,
        }