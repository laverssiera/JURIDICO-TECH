from __future__ import annotations

from datetime import UTC, datetime


class RegulatoryRuntime:
    """Resolve active regulation bundles for legal governance decisions."""

    _REGULATION_BUNDLES: dict[str, list[str]] = {
        "BR": ["lei_licitacoes", "lgpd", "marco_anticorrupcao"],
        "EU": ["gdpr", "public_procurement_directives", "whistleblower_directive"],
        "US": ["fcpA", "state_procurement_rules", "privacy_state_acts"],
        "INTL": ["uncitral", "world_bank_ppp_guidelines", "isao_compliance"],
    }

    def evaluate(self, *, jurisdiction: str, contract_type: str) -> dict:
        normalized_jurisdiction = (jurisdiction or "BR").upper()
        regulation_set = self._REGULATION_BUNDLES.get(normalized_jurisdiction, self._REGULATION_BUNDLES["INTL"])
        critical_rules = [rule for rule in regulation_set if "procurement" in rule or "licitacoes" in rule]
        return {
            "jurisdiction": normalized_jurisdiction,
            "contract_type": contract_type.upper(),
            "regulation_set": regulation_set,
            "critical_rules": critical_rules,
            "evaluated_at": datetime.now(UTC).isoformat(),
        }
