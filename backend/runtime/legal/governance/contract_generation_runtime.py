from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class ContractGenerationRuntime:
    """Generate deterministic legal contract drafts from supported governance templates."""

    _SUPPORTED_TEMPLATES: dict[str, dict[str, Any]] = {
        "MSA": {
            "label": "Master Service Agreement",
            "mandatory_clauses": ["scope", "fees", "liability", "term", "termination"],
        },
        "SOW": {
            "label": "Statement of Work",
            "mandatory_clauses": ["deliverables", "timeline", "acceptance_criteria", "change_control"],
        },
        "NDA": {
            "label": "Non-Disclosure Agreement",
            "mandatory_clauses": ["confidential_information", "permitted_use", "exceptions", "term"],
        },
        "EPC": {
            "label": "Engineering Procurement Construction",
            "mandatory_clauses": ["performance_guarantee", "liquidated_damages", "handover", "safety"],
        },
        "PPP": {
            "label": "Public Private Partnership",
            "mandatory_clauses": ["public_interest", "service_levels", "governance", "audit_rights"],
        },
        "BOT": {
            "label": "Build Operate Transfer",
            "mandatory_clauses": ["concession_period", "asset_reversion", "opex", "handover"],
        },
        "CONCESSAO": {
            "label": "Concessao",
            "mandatory_clauses": ["service_standard", "tariff_rules", "regulatory_supervision", "rebalancing"],
        },
    }

    def __init__(self) -> None:
        self._generated_contracts: list[dict[str, Any]] = []

    def supported_contracts(self) -> list[str]:
        return ["MSA", "SoW", "NDA", "EPC", "PPP", "BOT", "Concessao"]

    def _normalize_contract_type(self, contract_type: str) -> str:
        normalized = (contract_type or "").strip().upper()
        if normalized == "SOW":
            return "SOW"
        if normalized in {"CONCESSAO", "CONCESSION"}:
            return "CONCESSAO"
        return normalized

    def generate(
        self,
        *,
        contract_type: str,
        parties: list[str],
        objective: str,
        jurisdiction: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_type = self._normalize_contract_type(contract_type)
        template = self._SUPPORTED_TEMPLATES.get(normalized_type)
        if template is None:
            return {
                "generated": False,
                "reason": "unsupported_contract_type",
                "supported_contracts": self.supported_contracts(),
            }

        payload = {
            "contract_id": f"LG-{uuid4().hex[:10].upper()}",
            "contract_type": normalized_type,
            "template_label": template["label"],
            "jurisdiction": (jurisdiction or "BR").upper(),
            "parties": parties,
            "objective": objective,
            "mandatory_clauses": template["mandatory_clauses"],
            "draft": {
                "header": f"{template['label']} - {objective}",
                "context": context or {},
            },
            "generated": True,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        self._generated_contracts.append(payload)
        return payload

    def metrics(self) -> dict[str, Any]:
        return {
            "generated_contracts": len(self._generated_contracts),
            "supported_contracts": self.supported_contracts(),
        }
