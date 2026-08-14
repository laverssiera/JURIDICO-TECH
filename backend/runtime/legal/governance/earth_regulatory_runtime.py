from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


_DOMAIN_REGULATIONS: dict[str, list[str]] = {
    "território": ["estatuto_da_cidade", "lei_parcelamento_solo", "plano_diretor_municipal"],
    "licenciamento": ["lei_licenciamento_ambiental", "resolucao_conama_237", "licenca_previa_instalacao"],
    "contratos": ["lei_licitacoes_14133", "codigo_civil_contratos", "lei_concessoes"],
    "dados": ["lgpd", "decreto_10474_anpd", "iso_27001_framework"],
    "infraestrutura": ["lei_ppp", "decreto_pnl_infraestrutura", "normas_abnt_infraestrutura"],
    "ambiental": ["lei_crimes_ambientais_9605", "politica_nacional_meio_ambiente", "resolucao_conama_420"],
    "construção": ["nbr_15575", "codigo_obras_municipal", "lei_regularizacao_fundiaria"],
    "energia": ["lei_energia_eletrica_9074", "resolucao_aneel_482", "politica_nacional_eficiencia_energetica"],
}

_CRITICAL_REGULATIONS: set[str] = {
    "lgpd",
    "lei_crimes_ambientais_9605",
    "politica_nacional_meio_ambiente",
    "lei_licitacoes_14133",
}


class EarthRegulatoryRuntime:
    """Resolve and audit active Earth regulatory bundles per domain and jurisdiction."""

    _JURISDICTION_OVERRIDES: dict[str, dict[str, list[str]]] = {
        "EU": {
            "dados": ["gdpr", "nis2_directive", "ai_act"],
            "ambiental": ["eu_taxonomy_regulation", "ets_directive", "reach_regulation"],
        },
        "US": {
            "dados": ["ccpa", "hipaa", "glba"],
            "energia": ["ferc_regulations", "nerc_cip_standards"],
        },
        "INTL": {
            "contratos": ["uncitral_model_law", "unidroit_principles", "new_york_convention"],
        },
    }

    def __init__(self) -> None:
        self._audit_log: list[dict[str, Any]] = []

    def evaluate_domain(
        self,
        *,
        domain: str,
        jurisdiction: str = "BR",
    ) -> dict[str, Any]:
        normalized_jur = (jurisdiction or "BR").upper()
        overrides = self._JURISDICTION_OVERRIDES.get(normalized_jur, {})
        regulations = overrides.get(domain) or _DOMAIN_REGULATIONS.get(domain, [])
        critical = [r for r in regulations if r in _CRITICAL_REGULATIONS]

        event = self._emit_audit_event(
            event_type="earth.regulatory.domain.evaluated",
            domain=domain,
            jurisdiction=normalized_jur,
            regulations=regulations,
            critical_regulations=critical,
        )

        return {
            "event_id": event["event_id"],
            "domain": domain,
            "jurisdiction": normalized_jur,
            "regulations": regulations,
            "critical_regulations": critical,
            "requires_critical_compliance": len(critical) > 0,
            "evaluated_at": event["emitted_at"],
        }

    def evaluate_all_domains(self, *, jurisdiction: str = "BR") -> dict[str, Any]:
        results = {}
        for domain in _DOMAIN_REGULATIONS:
            results[domain] = self.evaluate_domain(domain=domain, jurisdiction=jurisdiction)

        summary_event = self._emit_audit_event(
            event_type="earth.regulatory.full_evaluation.completed",
            domain="ALL",
            jurisdiction=(jurisdiction or "BR").upper(),
            regulations=list(_DOMAIN_REGULATIONS.keys()),
            critical_regulations=[],
        )

        return {
            "event_id": summary_event["event_id"],
            "jurisdiction": (jurisdiction or "BR").upper(),
            "domains_evaluated": list(results.keys()),
            "results": results,
            "evaluated_at": summary_event["emitted_at"],
        }

    def _emit_audit_event(
        self,
        *,
        event_type: str,
        domain: str,
        jurisdiction: str,
        regulations: list[str],
        critical_regulations: list[str],
    ) -> dict[str, Any]:
        event: dict[str, Any] = {
            "event_id": f"err-{uuid4().hex[:12]}",
            "event_type": event_type,
            "domain": domain,
            "jurisdiction": jurisdiction,
            "regulations": regulations,
            "critical_regulations": critical_regulations,
            "emitted_at": datetime.now(UTC).isoformat(),
        }
        self._audit_log.append(event)
        return event

    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def metrics(self) -> dict[str, Any]:
        total = len(self._audit_log)
        with_critical = sum(1 for e in self._audit_log if e["critical_regulations"])
        return {
            "total_evaluations": total,
            "evaluations_with_critical_regulations": with_critical,
            "domains_covered": list(_DOMAIN_REGULATIONS.keys()),
        }


if __name__ == "__main__":
    import json

    runtime = EarthRegulatoryRuntime()

    print("=== Avaliação completa de todos os domínios (BR) ===")
    full = runtime.evaluate_all_domains(jurisdiction="BR")
    for domain, result in full["results"].items():
        print(f"\n[{domain}]")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== Avaliação domínio 'dados' (EU) ===")
    eu_dados = runtime.evaluate_domain(domain="dados", jurisdiction="EU")
    print(json.dumps(eu_dados, indent=2, ensure_ascii=False))

    print("\n--- Métricas ---")
    print(json.dumps(runtime.metrics(), indent=2, ensure_ascii=False))
    print("\n--- Audit Log ---")
    for event in runtime.audit_log():
        print(json.dumps(event, indent=2, ensure_ascii=False))
