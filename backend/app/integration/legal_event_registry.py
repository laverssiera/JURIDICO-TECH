from __future__ import annotations

from dataclasses import dataclass


INPUT_EVENTS = {
    "lead_created",
    "match_generated",
    "deal_created",
    "simulation_done",
    "deal_won",
}

OUTPUT_EVENTS = {
    "contract.required",
    "contract.generated",
    "contract.signed",
    "legal.blocked",
    "legal.approved",
    "bypass.detected",
    "commission.protected",
}


@dataclass(frozen=True)
class EventRouting:
    event_type: str
    subject: str


_EVENT_SUBJECTS = {
    "lead_created": "liceu.events.leads.created",
    "match_generated": "liceu.events.deals.match_generated",
    "deal_created": "liceu.events.deals.created",
    "simulation_done": "liceu.events.deals.simulation_done",
    "deal_won": "liceu.events.deals.won",
    "contract.required": "liceu.events.legal.contract.required",
    "contract.generated": "liceu.events.legal.contract.generated",
    "contract.signed": "liceu.events.legal.contract.signed",
    "legal.blocked": "liceu.events.legal.blocked",
    "legal.approved": "liceu.events.legal.approved",
    "bypass.detected": "liceu.events.legal.bypass.detected",
    "commission.protected": "liceu.events.legal.commission.protected",
    "legal.contract.created": "liceu.events.legal.contract.created",
    "legal.contract.signed": "liceu.events.legal.contract.signed",
    "legal.bypass.detected": "liceu.events.legal.bypass.detected",
    "legal.risk.flagged": "liceu.events.legal.risk.flagged",
    "legal.risk.update": "liceu.events.legal.risk.update",
    # ── LICEU 6.0 — Subjects por domínio ─────────────────────────────────────
    # Contratos
    "contract.created": "liceu.events.contract.created",
    "contract.draft": "liceu.events.contract.draft",
    "contract.clause.reinforced": "liceu.events.contract.clause.reinforced",
    "contract.learning.event": "liceu.events.contract.learning.event",
    # Compliance
    "compliance.check.passed": "liceu.events.compliance.check.passed",
    "compliance.check.failed": "liceu.events.compliance.check.failed",
    "compliance.alert": "liceu.events.compliance.alert",
    # Tributário
    "tax.risk.flagged": "liceu.events.tax.risk.flagged",
    "tax.regime.suggested": "liceu.events.tax.regime.suggested",
    "tax.obligation.due": "liceu.events.tax.obligation.due",
    # Arbitragem
    "arbitration.case.opened": "liceu.events.arbitration.case.opened",
    "arbitration.phase.advanced": "liceu.events.arbitration.phase.advanced",
    "arbitration.award.issued": "liceu.events.arbitration.award.issued",
    "arbitration.case.closed": "liceu.events.arbitration.case.closed",
    # Contencioso / Litigation
    "litigation.process.opened": "liceu.events.litigation.process.opened",
    "litigation.deadline.overdue": "liceu.events.litigation.deadline.overdue",
    "litigation.phase.advanced": "liceu.events.litigation.phase.advanced",
    "litigation.evidence.added": "liceu.events.litigation.evidence.added",
    # Forense
    "forensic.laudo.opened": "liceu.events.forensic.laudo.opened",
    "forensic.laudo.concluded": "liceu.events.forensic.laudo.concluded",
    "forensic.custody.transferred": "liceu.events.forensic.custody.transferred",
    "forensic.finding.critical": "liceu.events.forensic.finding.critical",
    # Governança Societária
    "governance.deliberation.created": "liceu.events.governance.deliberation.created",
    "governance.deliberation.approved": "liceu.events.governance.deliberation.approved",
    "governance.deliberation.rejected": "liceu.events.governance.deliberation.rejected",
    "governance.entity.registered": "liceu.events.governance.entity.registered",
    # Score / Risco
    "risk.score.computed": "liceu.events.legal.risk.score.computed",
    "risk.score.critical": "liceu.events.legal.risk.score.critical",
    # Evidence Vault
    "vault.evidence.deposited": "liceu.events.vault.evidence.deposited",
    "vault.integrity.failed": "liceu.events.vault.integrity.failed",
    # LICEU 6.x — Infraestrutura regulatória civilizacional
    "twin.updated": "liceu.events.legal.twin.updated",
    "twin.risk.critical": "liceu.events.legal.twin.risk.critical",
    "radar.signal.ingested": "liceu.events.legal.radar.signal.ingested",
    "radar.signal.disseminated": "liceu.events.legal.radar.signal.disseminated",
    "autonomous_arbitration.mediation.opened": "liceu.events.arbitration.mediation.opened",
    "autonomous_arbitration.settlement.suggested": "liceu.events.arbitration.settlement.suggested",
    "psycholegal.risk.critical": "liceu.events.legal.psycholegal.risk.critical",
    "war_room.incident.opened": "liceu.events.legal.warroom.incident.opened",
    "war_room.incident.closed": "liceu.events.legal.warroom.incident.closed",
    "esg_hr.alert": "liceu.events.compliance.esg_hr.alert",
    "smart_clause.recommended": "liceu.events.contract.smart_clause.recommended",
    "knowledge_graph.edge.added": "liceu.events.legal.graph.edge.added",
    "legal_os.gate.blocked": "liceu.events.legal.runtime.blocked",
    "trust.score.updated": "liceu.events.legal.trust.score.updated",
    "governance_ai.block": "liceu.events.governance.ai.block",
    "marketplace.request.created": "liceu.events.legal.marketplace.request.created",
    "university.enrollment.created": "liceu.events.legal.university.enrollment.created",
    "simulation.global.executed": "liceu.events.legal.simulation.executed",
    "simulation.global.risk.high": "liceu.events.legal.simulation.risk.high",
}


_ALIASES = {
    "juridicotech.contract.signed": "contract.signed",
    "juridicotech.lead_created": "lead_created",
    "juridicotech.deal_created": "deal_created",
    "juridicotech.match_generated": "match_generated",
    "juridicotech.deal_won": "deal_won",
    "deal.created": "deal_created",
    "lead.created": "lead_created",
    "simulation.done": "simulation_done",
    "deal.won": "deal_won",
}


def normalize_event_name(event_name: str) -> str:
    if event_name in _EVENT_SUBJECTS:
        return event_name
    return _ALIASES.get(event_name, event_name)


def subject_for_event(event_name: str) -> str:
    normalized = normalize_event_name(event_name)
    return _EVENT_SUBJECTS.get(normalized, f"liceu.events.legal.{normalized.replace('_', '.')}")


def subscription_subjects_for_event(event_name: str) -> list[str]:
    normalized = normalize_event_name(event_name)
    canonical = subject_for_event(normalized)
    legacy = f"juridicotech.{normalized}"
    # Keep backward compatibility for legacy streams while migrating monoliths.
    if canonical == legacy:
        return [canonical]
    return [canonical, legacy]
