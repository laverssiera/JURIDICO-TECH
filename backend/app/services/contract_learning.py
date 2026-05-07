"""
LICEU 6.0 — Módulo de Melhoria Contínua Contratual
O sistema aprende com litígios, falhas, arbitragem, feedbacks e jurisprudência
e evolui automaticamente as cláusulas do ecossistema.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# Limiar de ocorrências para disparar reforço automático de cláusula
REINFORCEMENT_THRESHOLD = 3


class LearningEvent:
    """Evento de aprendizado gerado por falha, litígio, arbitragem ou feedback."""

    def __init__(
        self,
        source: str,
        issue_type: str,
        context_tags: list[str],
        details: str,
        contract_id: str | None = None,
    ) -> None:
        self.id = f"EVT-{uuid4().hex[:8].upper()}"
        self.source = source          # "litigio" | "arbitragem" | "feedback" | "auditoria"
        self.issue_type = issue_type  # e.g. "infiltracao", "atraso_entrega", "inadimplencia"
        self.context_tags = context_tags
        self.details = details
        self.contract_id = contract_id
        self.at = utc_now()


class ContractContinuousImprovementModule:
    """
    Aprende com os eventos do ecossistema e reforça cláusulas automaticamente.

    Fluxo:
      1. Eventos de falha/litígio são registrados via record_event().
      2. Quando um issue_type atinge o limiar, o sistema gera uma
         sugestão de reforço de cláusula (ClauseReinforcement).
      3. A biblioteca de cláusulas aprendidas cresce ao longo do tempo.
    """

    def __init__(self) -> None:
        self._events: list[dict] = []
        self._issue_counts: defaultdict[str, int] = defaultdict(int)
        self._reinforcements: list[dict] = []
        # Mapa issue_type → instrução de reforço de cláusula
        self._reinforcement_rules: dict[str, dict] = {
            "infiltracao": {
                "clause_id": "responsabilidade_tecnica",
                "title": "Responsabilidade Técnica — Infiltrações",
                "reinforcement": (
                    "Acrescentar cláusula específica de responsabilidade por infiltrações: "
                    "O CONTRATADO responsabiliza-se pela impermeabilização, respondendo por "
                    "infiltrações decorrentes de falha técnica pelo prazo de 5 anos (CC Art. 618). "
                    "Inclui obrigação de laudo pericial de impermeabilização pré-entrega."
                ),
                "tags": ["construção", "técnico", "garantia", "impermeabilização"],
            },
            "atraso_entrega": {
                "clause_id": "multa_atraso",
                "title": "Multa por Atraso — Reforçada",
                "reinforcement": (
                    "Elevar cláusula de multa moratória para 1% ao dia sobre o valor do contrato, "
                    "limitada a 20%, e incluir cláusula penal compensatória de 10% sobre o valor total "
                    "em caso de descumprimento definitivo do prazo."
                ),
                "tags": ["multa", "atraso", "prazo", "penalidade"],
            },
            "inadimplencia": {
                "clause_id": "garantia_pagamento",
                "title": "Garantia de Pagamento — Seguro-Garantia",
                "reinforcement": (
                    "Exigir seguro-garantia de 30% do valor contratual, apólice aprovada pela SUSEP, "
                    "cobrindo inadimplência total e parcial. Cláusula de vencimento antecipado em caso "
                    "de protesto ou execução judicial do CONTRATADO."
                ),
                "tags": ["garantia", "pagamento", "inadimplência", "seguro"],
            },
            "nr18_violation": {
                "clause_id": "nr18_seguranca",
                "title": "NR-18 — Responsabilidade Solidária",
                "reinforcement": (
                    "Estabelecer responsabilidade solidária do CONTRATANTE na fiscalização do cumprimento "
                    "da NR-18, com inspeções mínimas semanais documentadas. Penalidade de 5% do valor "
                    "do contrato em caso de autuação do órgão fiscalizador por descumprimento."
                ),
                "tags": ["NR18", "segurança", "trabalhista", "solidariedade"],
            },
            "fornecedor_inadimplente": {
                "clause_id": "compliance_fornecedor",
                "title": "Compliance de Fornecedor — Due Diligence",
                "reinforcement": (
                    "Incluir declaração de compliance periódica (a cada 90 dias) do fornecedor, "
                    "com apresentação de: CND Federal e Estadual, CRF FGTS, CNDT Trabalhista, "
                    "e política de conformidade assinada. Descumprimento enseja rescisão imediata."
                ),
                "tags": ["fornecedor", "compliance", "due_diligence", "certidões"],
            },
            "lgpd_breach": {
                "clause_id": "lgpd_dados",
                "title": "LGPD — Proteção Ampliada com SLA",
                "reinforcement": (
                    "Reforçar cláusula LGPD incluindo: SLA de notificação de incidents em até 12h, "
                    "multa contratual de R$ 50.000 por incidente de vazamento, obrigação de "
                    "relatório de impacto (RIPD) e auditoria anual de conformidade."
                ),
                "tags": ["LGPD", "dados", "privacidade", "incidente"],
            },
        }

    # ── Registro de Eventos ──────────────────────────────────────────────────

    def record_event(
        self,
        source: str,
        issue_type: str,
        context_tags: list[str],
        details: str,
        contract_id: str | None = None,
    ) -> dict:
        evt = LearningEvent(source, issue_type, context_tags, details, contract_id)
        self._events.append(evt.__dict__)
        self._issue_counts[issue_type] += 1

        triggered = None
        if self._issue_counts[issue_type] == REINFORCEMENT_THRESHOLD:
            triggered = self._generate_reinforcement(issue_type)

        return {
            "event_id": evt.id,
            "recorded": True,
            "issue_count_for_type": self._issue_counts[issue_type],
            "reinforcement_triggered": triggered,
        }

    # ── Geração de Reforço ───────────────────────────────────────────────────

    def _generate_reinforcement(self, issue_type: str) -> dict | None:
        rule = self._reinforcement_rules.get(issue_type)
        if not rule:
            rule = {
                "clause_id": f"custom_{issue_type}",
                "title": f"Cláusula Gerada — {issue_type.replace('_', ' ').title()}",
                "reinforcement": (
                    f"O sistema detectou {REINFORCEMENT_THRESHOLD} ocorrências de '{issue_type}'. "
                    "Recomenda-se revisão contratual especializada para mitigação."
                ),
                "tags": [issue_type],
            }
        reinforcement = {
            "reinforcement_id": f"RFR-{uuid4().hex[:8].upper()}",
            "issue_type": issue_type,
            "occurrences": self._issue_counts[issue_type],
            **rule,
            "generated_at": utc_now(),
            "status": "pending_review",
        }
        self._reinforcements.append(reinforcement)
        return reinforcement

    # ── Consultas ────────────────────────────────────────────────────────────

    def approve_reinforcement(self, reinforcement_id: str) -> dict:
        for r in self._reinforcements:
            if r["reinforcement_id"] == reinforcement_id:
                r["status"] = "approved"
                r["approved_at"] = utc_now()
                return r
        raise KeyError(f"Reforço {reinforcement_id} não encontrado")

    def list_events(self) -> list[dict]:
        return self._events

    def list_reinforcements(self, status: str | None = None) -> list[dict]:
        if status:
            return [r for r in self._reinforcements if r["status"] == status]
        return self._reinforcements

    def issue_summary(self) -> dict:
        return dict(self._issue_counts)

    def learning_stats(self) -> dict:
        total_events = len(self._events)
        reinforcements_generated = len(self._reinforcements)
        approved = sum(1 for r in self._reinforcements if r["status"] == "approved")
        return {
            "total_learning_events": total_events,
            "reinforcements_generated": reinforcements_generated,
            "reinforcements_approved": approved,
            "issue_summary": dict(self._issue_counts),
            "threshold": REINFORCEMENT_THRESHOLD,
        }


contract_learning = ContractContinuousImprovementModule()
