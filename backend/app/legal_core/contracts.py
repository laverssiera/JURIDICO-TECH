"""
LICEU 6.0 — Domain: Contracts
Contratos inteligentes com ciclo de vida, versionamento e blindagem.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ContractDomain:
    CLAUSE_LIBRARY: dict[str, dict] = {
        "responsabilidade_tecnica": {
            "title": "Responsabilidade Técnica",
            "body": (
                "O CONTRATADO responde pelos danos técnicos decorrentes de falhas de execução, "
                "infiltrações e vícios construtivos pelo período de 5 (cinco) anos, nos termos "
                "do art. 618 do Código Civil Brasileiro."
            ),
            "tags": ["construção", "técnico", "garantia"],
        },
        "compliance_ambiental": {
            "title": "Compliance Ambiental",
            "body": (
                "As partes se comprometem a cumprir integralmente a legislação ambiental vigente, "
                "incluindo CONAMA, SISNAMA e demais normas aplicáveis. O descumprimento constitui "
                "infração grave e enseja rescisão imediata."
            ),
            "tags": ["ambiental", "ESG", "compliance"],
        },
        "nr18_seguranca": {
            "title": "Segurança do Trabalho — NR-18",
            "body": (
                "O CONTRATADO deve cumprir rigorosamente a NR-18 (Condições e Meio Ambiente de "
                "Trabalho na Indústria da Construção), responsabilizando-se integralmente por "
                "acidentes decorrentes de descumprimento desta norma."
            ),
            "tags": ["trabalhista", "segurança", "NR18"],
        },
        "lgpd_dados": {
            "title": "Proteção de Dados — LGPD",
            "body": (
                "As partes deverão tratar os dados pessoais compartilhados no âmbito deste contrato "
                "em estrita conformidade com a Lei n.º 13.709/2018 (LGPD), adotando medidas técnicas "
                "e organizacionais adequadas à proteção dos titulares."
            ),
            "tags": ["LGPD", "dados", "privacidade"],
        },
        "arbitragem": {
            "title": "Cláusula Compromissória de Arbitragem",
            "body": (
                "Fica eleita a arbitragem, nos termos da Lei n.º 9.307/1996, como método exclusivo "
                "de resolução de conflitos emergentes ou relacionados a este contrato, com sede na "
                "Câmara de Arbitragem indicada pelas partes."
            ),
            "tags": ["arbitragem", "conflito", "resolução"],
        },
        "multa_atraso": {
            "title": "Multa por Atraso na Entrega",
            "body": (
                "Em caso de atraso injustificado na entrega do objeto contratual, incidirá multa "
                "moratória de 0,5% (meio por cento) ao dia sobre o valor total do contrato, "
                "limitada a 20% (vinte por cento)."
            ),
            "tags": ["multa", "atraso", "prazo"],
        },
    }

    def suggest_clauses(self, context_tags: list[str]) -> list[dict]:
        """Sugere cláusulas relevantes com base em tags de contexto."""
        result = []
        for key, clause in self.CLAUSE_LIBRARY.items():
            if any(tag in clause["tags"] for tag in context_tags):
                result.append({"id": key, **clause})
        return result

    def draft_contract(
        self,
        title: str,
        parties: list[dict],
        object_description: str,
        value: float,
        tags: list[str],
        clause_ids: list[str] | None = None,
    ) -> dict:
        contract_id = f"CTR-{uuid4().hex[:8].upper()}"
        selected_clauses = clause_ids or list(self.CLAUSE_LIBRARY.keys())
        clauses = [
            {"id": cid, **self.CLAUSE_LIBRARY[cid]}
            for cid in selected_clauses
            if cid in self.CLAUSE_LIBRARY
        ]
        return {
            "contract_id": contract_id,
            "title": title,
            "parties": parties,
            "object": object_description,
            "value": value,
            "tags": tags,
            "clauses": clauses,
            "status": "draft",
            "created_at": utc_now(),
            "version": 1,
        }
