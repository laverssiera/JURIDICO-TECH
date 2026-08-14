"""
LICEU 6.0 — Domain: Legal Risk
Score jurídico vivo para obras, contratos, fornecedores, SPEs, etc.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    MEDIUM_HIGH = "MEDIUM_HIGH"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def _level_from_score(score: int) -> RiskLevel:
    if score <= 20:
        return RiskLevel.LOW
    if score <= 40:
        return RiskLevel.MEDIUM
    if score <= 60:
        return RiskLevel.MEDIUM_HIGH
    if score <= 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


RISK_FACTORS: dict[str, dict] = {
    # Obra / Empreendimento
    "nr18_incomplete": {"weight": 12, "label": "NR-18 incompleta", "scope": ["obra"]},
    "no_environmental_license": {"weight": 15, "label": "Licença ambiental ausente/vencida", "scope": ["obra", "empreendimento"]},
    "weak_env_clause": {"weight": 8, "label": "Cláusula ambiental fraca no contrato", "scope": ["obra", "contrato"]},
    "no_pcmat": {"weight": 10, "label": "PCMAT não elaborado", "scope": ["obra"]},
    # Contrato
    "no_arbitration_clause": {"weight": 10, "label": "Sem cláusula compromissória de arbitragem", "scope": ["contrato"]},
    "no_penalty_clause": {"weight": 8, "label": "Sem cláusula de multa por atraso", "scope": ["contrato"]},
    "no_lgpd_clause": {"weight": 7, "label": "Sem cláusula LGPD", "scope": ["contrato"]},
    "expired_contract": {"weight": 20, "label": "Contrato vencido sem renovação", "scope": ["contrato"]},
    # Fornecedor
    "supplier_no_compliance": {"weight": 15, "label": "Fornecedor sem compliance documentado", "scope": ["fornecedor"]},
    "supplier_debt_cnd": {"weight": 18, "label": "Fornecedor com CND negativa/irregular", "scope": ["fornecedor"]},
    "supplier_labor_issues": {"weight": 12, "label": "Fornecedor com passivo trabalhista", "scope": ["fornecedor"]},
    # SPE / Societário
    "spe_no_bylaws": {"weight": 10, "label": "SPE sem estatuto atualizado", "scope": ["spe"]},
    "spe_no_dpo": {"weight": 8, "label": "SPE sem DPO (LGPD)", "scope": ["spe"]},
    "spe_no_compliance_officer": {"weight": 10, "label": "SPE sem responsável de compliance", "scope": ["spe"]},
    # Colaborador / Investidor
    "collaborator_no_nda": {"weight": 6, "label": "Colaborador sem NDA assinado", "scope": ["colaborador"]},
    "investor_unverified": {"weight": 14, "label": "Investidor sem KYC/AML verificado", "scope": ["investidor"]},
}


class LegalRiskDomain:
    def score(
        self,
        entity_id: str,
        entity_type: str,
        active_risks: list[str],
        extra_context: dict | None = None,
    ) -> dict:
        issues = []
        total_weight = 0
        for risk_key in active_risks:
            factor = RISK_FACTORS.get(risk_key)
            if factor:
                issues.append({"key": risk_key, "label": factor["label"], "weight": factor["weight"]})
                total_weight += factor["weight"]

        # Normalizar para 0–100
        max_possible = sum(f["weight"] for f in RISK_FACTORS.values())
        score = min(int((total_weight / max_possible) * 100), 100)
        level = _level_from_score(score)

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "legal_risk_score": score,
            "risk_level": level.value,
            "issues": [i["label"] for i in issues],
            "issue_details": issues,
            "total_weight": total_weight,
            "context": extra_context or {},
            "evaluated_at": utc_now(),
        }

    def available_factors(self, scope: str | None = None) -> list[dict]:
        result = []
        for key, factor in RISK_FACTORS.items():
            if scope is None or scope in factor["scope"]:
                result.append({"key": key, **factor})
        return result
