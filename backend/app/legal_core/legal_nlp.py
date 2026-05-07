"""
LICEU 6.0 — Domain: Legal NLP + AI Engine
O cérebro jurídico: análise de contratos, detecção de riscos em cláusulas,
resumo de processos, geração de documentos, comparação de jurisprudência.
Stack: Legal RAG + Embeddings (simulado) + Clause Intelligence + Risk NLP + Decision Graph.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ── Padrões de risco em linguagem natural de contratos ───────────────────────

RISK_PATTERNS: list[dict] = [
    {
        "pattern": r"responsabilidade\s+(do\s+)?contratante\s+é\s+ilimitada",
        "risk": "Responsabilidade ilimitada para o contratante — risco crítico",
        "severity": "critical",
        "suggestion": "Limitar a responsabilidade do contratante a um teto percentual sobre o valor do contrato.",
    },
    {
        "pattern": r"renúncia\s+a\s+(qualquer\s+)?direito\s+de\s+ressarcimento",
        "risk": "Renúncia a direito de ressarcimento — pode ser abusiva",
        "severity": "high",
        "suggestion": "Remover ou negociar cláusula de renúncia; verificar aderência ao CDC/CC.",
    },
    {
        "pattern": r"foro\s+(exclusivo|eleito)\s+(?!arbitragem)",
        "risk": "Foro de eleição sem previsão de arbitragem — aumenta risco de litigância judicial longa",
        "severity": "medium",
        "suggestion": "Incluir cláusula compromissória de arbitragem como método preferencial.",
    },
    {
        "pattern": r"prazo\s+(de\s+)?entrega[^.]{0,50}(a\s+critério|conforme\s+disponibilidade)",
        "risk": "Prazo de entrega indefinido — risco de atraso sem penalidade",
        "severity": "high",
        "suggestion": "Definir prazo determinado com cláusula de multa moratória.",
    },
    {
        "pattern": r"dados\s+pessoais[^.]{0,100}(sem|não|nenhuma)\s+(política|proteção|LGPD)",
        "risk": "Tratamento de dados pessoais sem menção à LGPD",
        "severity": "high",
        "suggestion": "Inserir cláusula de proteção de dados conforme Lei 13.709/2018.",
    },
    {
        "pattern": r"sem\s+(garantia|warranty|responsabilidade\s+técnica)",
        "risk": "Ausência de garantia técnica — vício construtivo não coberto",
        "severity": "high",
        "suggestion": "Incluir garantia mínima de 5 anos para vícios estruturais (CC Art. 618).",
    },
    {
        "pattern": r"multa[^.]{0,30}acima\s+de\s+20\s*%",
        "risk": "Multa contratual acima de 20% — pode ser considerada abusiva",
        "severity": "medium",
        "suggestion": "Limitar multa a 20% do valor contratual para conformidade com CC Art. 412.",
    },
]

# ── Templates de documentos jurídicos ────────────────────────────────────────

DOCUMENT_TEMPLATES: dict[str, str] = {
    "notificacao_extrajudicial": (
        "NOTIFICAÇÃO EXTRAJUDICIAL\n\n"
        "Ao Sr(a). {destinatario},\n\n"
        "Vimos, pelo presente instrumento, NOTIFICAR V.Sa. acerca de {assunto}, "
        "requerendo a adoção das seguintes providências no prazo de {prazo} dias úteis: "
        "{providencias}.\n\n"
        "O descumprimento da presente notificação ensejará a adoção das medidas cabíveis, "
        "incluindo ação judicial e/ou instauração de procedimento arbitral.\n\n"
        "Atenciosamente,\n{remetente}"
    ),
    "declaracao_compliance": (
        "DECLARAÇÃO DE CONFORMIDADE REGULATÓRIA\n\n"
        "A empresa {empresa}, CNPJ {cnpj}, declara para todos os fins de direito que: "
        "(i) cumpre integralmente a Lei 13.709/2018 (LGPD); "
        "(ii) possui Encarregado (DPO) devidamente designado; "
        "(iii) mantém programa de integridade e compliance ativo; "
        "(iv) não possui passivos tributários relevantes não provisionados.\n\n"
        "Local e data: {local}, {data}.\n\n"
        "[Assinatura ICP-Brasil]"
    ),
    "clausula_arbitragem": (
        "Fica eleita a arbitragem, nos termos da Lei n.º 9.307/1996, como método exclusivo "
        "de resolução de litígios emergentes ou relacionados ao presente instrumento, "
        "com sede na {camara_arbitral}. O processo arbitral será conduzido em língua portuguesa, "
        "com sede em {cidade}, observados os regulamentos da câmara eleita."
    ),
    "clausula_lgpd": (
        "As Partes declaram-se cientes de suas obrigações decorrentes da Lei n.º 13.709/2018 "
        "(LGPD) e se comprometem a tratar os dados pessoais compartilhados no âmbito deste "
        "contrato exclusivamente para as finalidades aqui previstas, adotando medidas de "
        "segurança adequadas, notificando incidentes em até 72h e respeitando os direitos "
        "dos titulares."
    ),
}


class LegalNLPDomain:
    """
    Motor de NLP Jurídico.
    Em produção: substituir pattern matching por LLM + Legal RAG + Embeddings.
    """

    # ── Análise de Contratos ──────────────────────────────────────────────────

    def analyze_contract_text(self, contract_text: str) -> dict:
        """Detecta riscos em texto de contrato via padrões NLP."""
        found_risks = []
        for rp in RISK_PATTERNS:
            if re.search(rp["pattern"], contract_text, re.IGNORECASE):
                found_risks.append({
                    "risk": rp["risk"],
                    "severity": rp["severity"],
                    "suggestion": rp["suggestion"],
                })

        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        found_risks.sort(key=lambda r: severity_order.get(r["severity"], 0), reverse=True)

        critical_count = sum(1 for r in found_risks if r["severity"] == "critical")
        high_count = sum(1 for r in found_risks if r["severity"] == "high")

        overall_risk = "low"
        if critical_count > 0:
            overall_risk = "critical"
        elif high_count >= 2:
            overall_risk = "high"
        elif high_count == 1 or len(found_risks) > 3:
            overall_risk = "medium"

        return {
            "risks_found": found_risks,
            "risk_count": len(found_risks),
            "overall_risk": overall_risk,
            "critical_count": critical_count,
            "high_count": high_count,
            "analysis_note": (
                "Análise por padrões NLP — em produção, use LLM + Legal RAG para análise semântica completa."
            ),
            "analyzed_at": utc_now(),
        }

    def extract_key_clauses(self, contract_text: str) -> dict:
        """Extrai e identifica cláusulas-chave do contrato."""
        clauses_detected: list[dict] = []
        clause_patterns = {
            "objeto": r"(objeto\s+do\s+contrato|cláusula\s+primeira)[:\s-]+(.{20,200})",
            "valor": r"(valor\s+(total|do\s+contrato)|preço)[:\s-]+(.{10,100})",
            "prazo": r"(prazo\s+de\s+(entrega|vigência|execução))[:\s-]+(.{10,100})",
            "foro": r"(foro\s+(competente|eleito|da\s+comarca))[:\s-]+(.{5,80})",
            "multa": r"(multa\s+(moratória|punitiva|compensatória))[:\s-]+(.{10,100})",
        }
        for clause_type, pattern in clause_patterns.items():
            m = re.search(pattern, contract_text, re.IGNORECASE)
            if m:
                clauses_detected.append({
                    "type": clause_type,
                    "excerpt": m.group(0)[:200],
                })
        return {
            "clauses_detected": clauses_detected,
            "clause_count": len(clauses_detected),
            "extracted_at": utc_now(),
        }

    # ── Geração de Documentos ─────────────────────────────────────────────────

    def generate_document(self, template_id: str, variables: dict) -> dict:
        template = DOCUMENT_TEMPLATES.get(template_id)
        if not template:
            return {
                "error": f"Template '{template_id}' não encontrado",
                "available": list(DOCUMENT_TEMPLATES.keys()),
            }
        try:
            rendered = template.format(**variables)
        except KeyError as e:
            return {"error": f"Variável obrigatória ausente: {e}"}
        return {
            "template_id": template_id,
            "document": rendered,
            "generated_at": utc_now(),
        }

    def list_templates(self) -> list[str]:
        return list(DOCUMENT_TEMPLATES.keys())

    # ── Resumo de Processo ────────────────────────────────────────────────────

    def summarize_process(self, process_data: dict) -> dict:
        """Gera resumo executivo de processo judicial/arbitral."""
        return {
            "process_id": process_data.get("process_id"),
            "executive_summary": (
                f"Processo {process_data.get('process_type','?')} entre "
                f"{process_data.get('plaintiff','?')} (autor) e "
                f"{process_data.get('defendant','?')} (réu), "
                f"no {process_data.get('tribunal','?')}, "
                f"fase atual: {process_data.get('phase','?')}, "
                f"valor em disputa: R$ {process_data.get('amount_in_dispute', 0):,.2f}."
            ),
            "risk_assessment": (
                "Alto risco financeiro" if process_data.get("amount_in_dispute", 0) > 500_000
                else "Risco financeiro moderado"
            ),
            "summarized_at": utc_now(),
        }

    # ── Comparação de Jurisprudência ──────────────────────────────────────────

    def compare_jurisprudence(self, issue_description: str, precedents: list[dict]) -> dict:
        """Compara um caso com precedentes jurisprudenciais (simulado)."""
        similarities = []
        issue_words = set(issue_description.lower().split())
        for p in precedents:
            p_words = set((p.get("decision", "") + " ".join(p.get("tags", []))).lower().split())
            similarity = len(issue_words & p_words) / max(len(issue_words), 1)
            if similarity > 0.1:
                similarities.append({
                    "precedent_id": p.get("id", p.get("title", "?")),
                    "relevance_score": round(similarity, 3),
                    "decision_excerpt": p.get("decision", "")[:200],
                })
        similarities.sort(key=lambda x: x["relevance_score"], reverse=True)
        return {
            "issue": issue_description,
            "relevant_precedents": similarities[:5],
            "compared_at": utc_now(),
        }
