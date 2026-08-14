"""
LICEU 6.0 — Domain: Legal AI / Legal Education
John Jurídico como General Counsel Cognitivo do ecossistema.
Interpretação de riscos, sugestão de cláusulas, educação jurídica.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


LEGAL_KNOWLEDGE_BASE: dict[str, dict] = {
    "contratos": {
        "resumo": "Contratos são instrumentos de vinculação de vontades e responsabilidades.",
        "alertas": [
            "Sempre inclua cláusula de arbitragem em contratos de alto valor.",
            "Defina multas por atraso de entrega com percentual e teto.",
            "Inclua cláusula LGPD sempre que houver troca de dados pessoais.",
            "Revisão jurídica obrigatória antes de assinatura.",
        ],
        "normas": ["CC Art. 421 a 853", "CDC quando aplicável"],
    },
    "lgpd": {
        "resumo": "A LGPD (Lei 13.709/2018) regula o tratamento de dados pessoais no Brasil.",
        "alertas": [
            "Toda empresa que trata dados pessoais deve se adequar.",
            "DPO (Encarregado) é obrigatório para controladores.",
            "Incidentes de segurança devem ser notificados à ANPD em até 72h.",
            "Bases legais: consentimento, legítimo interesse, cumprimento de obrigação legal.",
        ],
        "normas": ["Lei 13.709/2018", "Resoluções ANPD"],
    },
    "spe": {
        "resumo": "SPE é sociedade criada para finalidade específica, comum em incorporações.",
        "alertas": [
            "SPE deve ter objeto social restrito ao propósito do empreendimento.",
            "Contrato social deve prever regime de afetação patrimonial.",
            "Sócios respondem nos limites do capital social (exceto abuso).",
            "Obrigatório registro na Junta Comercial e inscrição no CNPJ.",
        ],
        "normas": ["CC Arts. 981-1.092", "Lei 4.591/1964", "Lei 10.931/2004"],
    },
    "trabalhista": {
        "resumo": "Direito Trabalhista regula a relação de emprego e obrigações patronais.",
        "alertas": [
            "Falta de registro da jornada gera passivo trabalhista.",
            "Terceirização exige contrato formal e fiscalização do tomador.",
            "CAGED, eSocial e FGTS devem estar em dia.",
            "NR-18 é obrigatória em todos os canteiros de obras.",
        ],
        "normas": ["CLT", "NR-18", "eSocial"],
    },
    "arbitragem": {
        "resumo": "Arbitragem é método privado de resolução de conflitos com força de sentença.",
        "alertas": [
            "Cláusula compromissória deve ser clara sobre câmara eleita.",
            "Arbitragem é irrecorrível no mérito (salvo vícios formais).",
            "Laudo arbitral tem força executiva equivalente ao título judicial.",
            "Confidencialidade é característica essencial da arbitragem.",
        ],
        "normas": ["Lei 9.307/1996", "Lei 13.129/2015"],
    },
}


class LegalAIDomain:
    def educate(self, topic: str) -> dict:
        kb = LEGAL_KNOWLEDGE_BASE.get(topic.lower())
        if not kb:
            available = list(LEGAL_KNOWLEDGE_BASE.keys())
            return {
                "topic": topic,
                "found": False,
                "message": f"Tópico não encontrado. Tópicos disponíveis: {available}",
                "at": utc_now(),
            }
        return {
            "topic": topic,
            "found": True,
            "resumo": kb["resumo"],
            "alertas": kb["alertas"],
            "normas": kb["normas"],
            "at": utc_now(),
        }

    def interpret_risk(self, risk_score: int, entity_type: str, issues: list[str]) -> dict:
        urgency = "baixa"
        recommendation = "Monitorar periodicamente"
        if risk_score >= 80:
            urgency = "crítica"
            recommendation = "AÇÃO IMEDIATA: Paralise operações de risco e busque assessoria jurídica urgente."
        elif risk_score >= 60:
            urgency = "alta"
            recommendation = "AÇÃO NECESSÁRIA: Corrija as não-conformidades identificadas no prazo de 30 dias."
        elif risk_score >= 40:
            urgency = "moderada"
            recommendation = "ATENÇÃO: Elabore plano de ação corretiva para os itens identificados."
        elif risk_score >= 20:
            urgency = "baixa-moderada"
            recommendation = "Monitore os itens pendentes e inclua em revisão trimestral de compliance."

        return {
            "entity_type": entity_type,
            "risk_score": risk_score,
            "urgency": urgency,
            "recommendation": recommendation,
            "issues": issues,
            "interpreted_at": utc_now(),
        }

    def suggest_action_plan(self, issues: list[str]) -> list[dict]:
        actions = []
        action_map = {
            "NR-18 incompleta": {"action": "Elaborar/atualizar PCMAT e fornecer EPIs documentados", "deadline_days": 7},
            "Licença ambiental ausente/vencida": {"action": "Protocolar renovação/obtenção de licença ambiental junto ao órgão competente", "deadline_days": 15},
            "Cláusula ambiental fraca no contrato": {"action": "Aditamento contratual com cláusula ambiental reforçada", "deadline_days": 10},
            "Sem cláusula compromissória de arbitragem": {"action": "Incluir cláusula compromissória via aditamento contratual", "deadline_days": 10},
            "Sem cláusula LGPD": {"action": "Incluir cláusula de tratamento de dados pessoais via aditamento", "deadline_days": 10},
            "Fornecedor sem compliance documentado": {"action": "Solicitar documentação de compliance ao fornecedor (certidões, políticas)", "deadline_days": 20},
            "SPE sem DPO (LGPD)": {"action": "Designar e registrar DPO (Encarregado) junto à ANPD", "deadline_days": 30},
        }
        for issue in issues:
            if issue in action_map:
                actions.append({"issue": issue, **action_map[issue]})
            else:
                actions.append({"issue": issue, "action": "Consultar assessoria jurídica especializada", "deadline_days": 30})
        return actions
