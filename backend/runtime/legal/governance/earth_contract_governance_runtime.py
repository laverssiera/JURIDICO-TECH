from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


_DOMAIN_CONTRACT_TEMPLATES: dict[str, dict[str, Any]] = {
    "território": {
        "template": "contrato_uso_territorio",
        "mandatory_clauses": ["delimitação_geográfica", "prazo_vigência", "condições_reversão"],
        "compliance_frameworks": ["estatuto_cidade", "plano_diretor"],
    },
    "licenciamento": {
        "template": "contrato_licenciamento_operacional",
        "mandatory_clauses": ["escopo_atividade", "prazo_licença", "condições_renovação", "penalidades"],
        "compliance_frameworks": ["lei_licenciamento_ambiental", "resolucao_conama_237"],
    },
    "contratos": {
        "template": "contrato_gestao_contratual",
        "mandatory_clauses": ["objeto", "valor", "prazo", "garantias", "cláusula_arbitral"],
        "compliance_frameworks": ["lei_licitacoes_14133", "codigo_civil"],
    },
    "dados": {
        "template": "contrato_tratamento_dados",
        "mandatory_clauses": ["base_legal_lgpd", "finalidade", "retenção", "segurança", "dpo"],
        "compliance_frameworks": ["lgpd", "anpd_guidelines"],
    },
    "infraestrutura": {
        "template": "contrato_ppp_infraestrutura",
        "mandatory_clauses": ["especificação_técnica", "prazo_concessão", "sla", "matriz_riscos"],
        "compliance_frameworks": ["lei_ppp", "decreto_pnl"],
    },
    "ambiental": {
        "template": "contrato_gestao_ambiental",
        "mandatory_clauses": [
            "passivo_ambiental",
            "plano_recuperação",
            "monitoramento",
            "seguro_ambiental",
        ],
        "compliance_frameworks": ["politica_nacional_meio_ambiente", "lei_crimes_ambientais_9605"],
    },
    "construção": {
        "template": "contrato_empreitada_construção",
        "mandatory_clauses": ["projeto_aprovado", "art_rrt", "cronograma", "garantia_entrega"],
        "compliance_frameworks": ["nbr_15575", "codigo_obras_municipal"],
    },
    "energia": {
        "template": "contrato_fornecimento_energia",
        "mandatory_clauses": ["fonte_energia", "potência_contratada", "tarifa", "penalidades_interrupção"],
        "compliance_frameworks": ["lei_energia_eletrica_9074", "resolucao_aneel_482"],
    },
}

_REQUIRED_UNIVERSAL_CLAUSES = ["foro_eleito", "audit_trail", "resolucao_disputas"]


class EarthContractGovernanceRuntime:
    """Govern Earth-domain contracts: generate, validate, and produce auditable governance events."""

    def __init__(self) -> None:
        self._audit_log: list[dict[str, Any]] = []

    def generate(
        self,
        *,
        domain: str,
        parties: list[str],
        jurisdiction: str = "BR",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        template_config = _DOMAIN_CONTRACT_TEMPLATES.get(domain)
        if not template_config:
            return self._emit_audit_event(
                event_type="earth.contract.governance.domain_not_found",
                domain=domain,
                status="ERROR",
                details={"reason": f"domain '{domain}' not registered"},
                parties=parties,
                jurisdiction=jurisdiction,
            )

        all_clauses = template_config["mandatory_clauses"] + _REQUIRED_UNIVERSAL_CLAUSES
        contract_id = f"ecg-{uuid4().hex[:12]}"

        return self._emit_audit_event(
            event_type="earth.contract.governance.generated",
            domain=domain,
            status="GENERATED",
            details={
                "contract_id": contract_id,
                "template": template_config["template"],
                "parties": parties,
                "mandatory_clauses": all_clauses,
                "compliance_frameworks": template_config["compliance_frameworks"],
                "context": context or {},
            },
            parties=parties,
            jurisdiction=jurisdiction,
        )

    def validate(
        self,
        *,
        domain: str,
        clauses_present: list[str],
        parties: list[str] | None = None,
        jurisdiction: str = "BR",
    ) -> dict[str, Any]:
        template_config = _DOMAIN_CONTRACT_TEMPLATES.get(domain)
        if not template_config:
            return self._emit_audit_event(
                event_type="earth.contract.governance.domain_not_found",
                domain=domain,
                status="ERROR",
                details={"reason": f"domain '{domain}' not registered"},
                parties=parties or [],
                jurisdiction=jurisdiction,
            )

        required = set(template_config["mandatory_clauses"]) | set(_REQUIRED_UNIVERSAL_CLAUSES)
        present = set(clauses_present)
        missing = sorted(required - present)
        score = round(max(0.0, 100.0 - len(missing) * 12.5), 2)
        status = "APPROVED" if not missing else ("CONDITIONAL" if score >= 50.0 else "REJECTED")

        return self._emit_audit_event(
            event_type="earth.contract.governance.validated",
            domain=domain,
            status=status,
            details={
                "required_clauses": sorted(required),
                "missing_clauses": missing,
                "governance_score": score,
                "compliance_frameworks": template_config["compliance_frameworks"],
            },
            parties=parties or [],
            jurisdiction=jurisdiction,
        )

    def validate_all_domains(
        self,
        *,
        domain_clauses: dict[str, list[str]] | None = None,
        jurisdiction: str = "BR",
    ) -> dict[str, Any]:
        domain_clauses = domain_clauses or {}
        results = {}
        for domain in _DOMAIN_CONTRACT_TEMPLATES:
            clauses = domain_clauses.get(domain, [])
            results[domain] = self.validate(
                domain=domain,
                clauses_present=clauses,
                jurisdiction=jurisdiction,
            )

        overall_status = "APPROVED"
        if any(r["status"] == "REJECTED" for r in results.values()):
            overall_status = "REJECTED"
        elif any(r["status"] == "CONDITIONAL" for r in results.values()):
            overall_status = "CONDITIONAL"

        summary_event = self._emit_audit_event(
            event_type="earth.contract.governance.full_validation.completed",
            domain="ALL",
            status=overall_status,
            details={"domains_evaluated": list(results.keys())},
            parties=[],
            jurisdiction=(jurisdiction or "BR").upper(),
        )

        return {
            "event_id": summary_event["event_id"],
            "overall_status": overall_status,
            "jurisdiction": (jurisdiction or "BR").upper(),
            "domain_results": results,
            "validated_at": summary_event["emitted_at"],
        }

    def _emit_audit_event(
        self,
        *,
        event_type: str,
        domain: str,
        status: str,
        details: dict[str, Any],
        parties: list[str],
        jurisdiction: str,
    ) -> dict[str, Any]:
        event: dict[str, Any] = {
            "event_id": f"ecg-{uuid4().hex[:12]}",
            "event_type": event_type,
            "domain": domain,
            "status": status,
            "jurisdiction": (jurisdiction or "BR").upper(),
            "parties": parties,
            "details": details,
            "emitted_at": datetime.now(UTC).isoformat(),
        }
        self._audit_log.append(event)
        return event

    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def metrics(self) -> dict[str, Any]:
        total = len(self._audit_log)
        approved = sum(1 for e in self._audit_log if e["status"] == "APPROVED")
        conditional = sum(1 for e in self._audit_log if e["status"] == "CONDITIONAL")
        rejected = sum(1 for e in self._audit_log if e["status"] == "REJECTED")
        return {
            "total_events": total,
            "approved": approved,
            "conditional": conditional,
            "rejected": rejected,
            "approval_ratio": round(approved / total, 4) if total else 1.0,
        }


if __name__ == "__main__":
    import json

    runtime = EarthContractGovernanceRuntime()

    print("=== Geração de contratos por domínio ===")
    for domain in _DOMAIN_CONTRACT_TEMPLATES:
        result = runtime.generate(
            domain=domain,
            parties=["Parte A", "Parte B"],
            jurisdiction="BR",
        )
        print(f"\n[{domain}] → {result['status']}")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== Validação completa (sem cláusulas — cenário de stress) ===")
    full_validation = runtime.validate_all_domains(jurisdiction="BR")
    print(f"Overall: {full_validation['overall_status']}")
    for domain, r in full_validation["domain_results"].items():
        print(f"  {domain}: {r['status']} (score: {r['details'].get('governance_score', 'N/A')})")

    print("\n=== Validação completa (com todas as cláusulas) ===")
    all_clauses: dict[str, list[str]] = {}
    for domain, cfg in _DOMAIN_CONTRACT_TEMPLATES.items():
        all_clauses[domain] = list(cfg["mandatory_clauses"]) + list(_REQUIRED_UNIVERSAL_CLAUSES)
    full_ok = runtime.validate_all_domains(domain_clauses=all_clauses, jurisdiction="BR")
    print(f"Overall: {full_ok['overall_status']}")

    print("\n--- Métricas ---")
    print(json.dumps(runtime.metrics(), indent=2, ensure_ascii=False))
    print("\n--- Audit Log (últimos 3 eventos) ---")
    for event in runtime.audit_log()[-3:]:
        print(json.dumps(event, indent=2, ensure_ascii=False))
