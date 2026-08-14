from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from runtime.legal.governance.continental_compliance_runtime import ContinentalComplianceRuntime
from runtime.legal.governance.continental_contract_runtime import ContinentalContractRuntime
from runtime.legal.governance.continental_ip_runtime import ContinentalIPRuntime
from runtime.legal.governance.continental_regulatory_runtime import ContinentalRegulatoryRuntime


class ContinentalLegalGovernanceRuntime:
    """Produce the consolidated Legal State Continental for a cross-border operation."""

    def __init__(self) -> None:
        self._contracts = ContinentalContractRuntime()
        self._regulatory = ContinentalRegulatoryRuntime()
        self._ip = ContinentalIPRuntime()
        self._compliance = ContinentalComplianceRuntime()

    def build_state(
        self,
        *,
        countries: list[str],
        contracts: list[dict[str, Any]] | None = None,
        assets: list[dict[str, Any]] | None = None,
        data: list[dict[str, Any]] | None = None,
        investments: list[dict[str, Any]] | None = None,
        suppliers: list[dict[str, Any]] | None = None,
        infrastructure: list[dict[str, Any]] | None = None,
        controls: dict[str, bool] | None = None,
        sectors: list[str] | None = None,
        operation_id: str | None = None,
    ) -> dict[str, Any]:
        normalized_countries = list(dict.fromkeys(country.strip().upper() for country in countries if country.strip()))
        regulatory = self._regulatory.assess(countries=normalized_countries, sectors=sectors)
        contract_state = self._contracts.assess(countries=normalized_countries, contracts=contracts or [])
        ip_state = self._ip.assess(countries=normalized_countries, assets=assets or [])
        compliance = self._compliance.assess(
            countries=normalized_countries,
            controls=controls or {},
            required_rules=regulatory["rules"],
        )
        return {
            "legal_state_id": operation_id or f"CLS-{uuid4().hex[:12].upper()}",
            "state_type": "legal_state_continental",
            "status": compliance["status"],
            "countries": normalized_countries,
            "route": [{"sequence": index, "country": country} for index, country in enumerate(normalized_countries, start=1)],
            "contracts": contract_state,
            "regulatory": regulatory,
            "intellectual_property": ip_state,
            "data": data or [],
            "assets": assets or [],
            "investments": investments or [],
            "suppliers": suppliers or [],
            "infrastructure": infrastructure or [],
            "compliance": compliance,
            "updated_at": datetime.now(UTC).isoformat(),
        }