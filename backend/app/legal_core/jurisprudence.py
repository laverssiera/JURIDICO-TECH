"""
LICEU 6.0 — Domain: Jurisprudência & Normas
Radar legislativo, alimentação de base de jurisprudência, alertas normativos.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


NORM_DATABASE: list[dict] = [
    {
        "id": "LGPD",
        "title": "Lei Geral de Proteção de Dados",
        "number": "13.709/2018",
        "scope": ["dados", "privacidade", "tecnologia"],
        "status": "vigente",
        "last_update": "2020-08-26",
    },
    {
        "id": "NR18",
        "title": "NR-18 — Segurança no Trabalho na Construção",
        "number": "NR-18/MTE",
        "scope": ["construção", "segurança", "trabalhista"],
        "status": "vigente",
        "last_update": "2022-04-01",
    },
    {
        "id": "LEI_ARBITRAGEM",
        "title": "Lei de Arbitragem",
        "number": "9.307/1996",
        "scope": ["arbitragem", "conflito", "contratos"],
        "status": "vigente",
        "last_update": "2015-06-26",
    },
    {
        "id": "LEI_SPE",
        "title": "Sociedade de Propósito Específico — Regime Jurídico",
        "number": "CC Arts. 981-1.092 + Lei 4.591/1964",
        "scope": ["SPE", "incorporação", "societário"],
        "status": "vigente",
        "last_update": "2002-01-10",
    },
    {
        "id": "CODIGO_CIVIL",
        "title": "Código Civil — Responsabilidade em Contratos de Empreitada",
        "number": "10.406/2002 Art. 618",
        "scope": ["contratos", "construção", "responsabilidade"],
        "status": "vigente",
        "last_update": "2002-01-10",
    },
    {
        "id": "ESG_FRAMEWORK",
        "title": "Marco Legal ESG Brasileiro — Resolução CMN 4.945/2021",
        "number": "CMN 4.945/2021",
        "scope": ["ESG", "financeiro", "sustentabilidade"],
        "status": "vigente",
        "last_update": "2021-09-29",
    },
]


class JurisprudenceDomain:
    def __init__(self) -> None:
        self._precedents: list[dict] = []

    def search_norms(self, tags: list[str]) -> list[dict]:
        result = []
        for norm in NORM_DATABASE:
            if any(tag in norm["scope"] for tag in tags):
                result.append(norm)
        return result

    def add_precedent(
        self,
        title: str,
        court: str,
        decision: str,
        tags: list[str],
        case_number: str | None = None,
    ) -> dict:
        precedent = {
            "id": f"JUR-{uuid4().hex[:8].upper()}",
            "title": title,
            "court": court,
            "decision": decision,
            "case_number": case_number,
            "tags": tags,
            "added_at": utc_now(),
        }
        self._precedents.append(precedent)
        return precedent

    def search_precedents(self, tags: list[str]) -> list[dict]:
        return [p for p in self._precedents if any(t in p["tags"] for t in tags)]

    def norm_alert(self, entity_scope: list[str]) -> list[dict]:
        """Retorna normas relevantes para o escopo da entidade (radar normativo)."""
        return self.search_norms(entity_scope)
