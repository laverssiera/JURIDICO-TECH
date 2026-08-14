"""
LICEU 6.0 — Domain: Compliance
LGPD, NR-18, compliance ambiental, trabalhista e regulatório.
"""
from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


COMPLIANCE_CHECKLIST: dict[str, list[dict]] = {
    "lgpd": [
        {"item": "DPO designado", "key": "dpo_assigned"},
        {"item": "Mapa de dados pessoais", "key": "data_map"},
        {"item": "Política de privacidade publicada", "key": "privacy_policy"},
        {"item": "Consentimento coletado dos titulares", "key": "consent_collected"},
        {"item": "Plano de resposta a incidentes", "key": "incident_response_plan"},
    ],
    "nr18": [
        {"item": "PCMAT elaborado", "key": "pcmat"},
        {"item": "EPI fornecido e documentado", "key": "epi_documented"},
        {"item": "Treinamentos NR-18 realizados", "key": "training_done"},
        {"item": "Instalações sanitárias conformes", "key": "sanitary_ok"},
        {"item": "Sinalização de segurança instalada", "key": "safety_signs"},
    ],
    "ambiental": [
        {"item": "Licença Ambiental válida", "key": "environmental_license"},
        {"item": "Plano de gestão de resíduos", "key": "waste_management"},
        {"item": "Relatório de impacto atualizado", "key": "impact_report"},
        {"item": "Compensação ambiental documentada", "key": "compensation"},
    ],
    "trabalhista": [
        {"item": "CAGED em dia", "key": "caged_ok"},
        {"item": "PPP dos funcionários", "key": "ppp_ok"},
        {"item": "FGTS recolhido", "key": "fgts_ok"},
        {"item": "Jornada de trabalho controlada", "key": "work_hours_control"},
        {"item": "Acordo coletivo vigente", "key": "collective_agreement"},
    ],
}


class ComplianceDomain:
    def check(self, domain: str, entity_data: dict) -> dict:
        items = COMPLIANCE_CHECKLIST.get(domain, [])
        passed = []
        failed = []
        for item in items:
            if entity_data.get(item["key"]):
                passed.append(item["item"])
            else:
                failed.append(item["item"])
        score = int((len(passed) / len(items)) * 100) if items else 0
        return {
            "domain": domain,
            "entity_id": entity_data.get("entity_id"),
            "compliance_score": score,
            "passed": passed,
            "failed": failed,
            "status": "compliant" if score >= 80 else "non_compliant",
            "evaluated_at": utc_now(),
        }

    def full_compliance_report(self, entity_data: dict) -> dict:
        results = {}
        total = 0
        for domain in COMPLIANCE_CHECKLIST:
            r = self.check(domain, entity_data)
            results[domain] = r
            total += r["compliance_score"]
        avg = total // len(COMPLIANCE_CHECKLIST)
        return {
            "entity_id": entity_data.get("entity_id"),
            "overall_score": avg,
            "overall_status": "compliant" if avg >= 80 else "non_compliant",
            "domains": results,
            "generated_at": utc_now(),
        }
