"""
LICEU 6.0 — Domain: Governance
Governança corporativa, estruturas SPE/SCP, mandatos e deliberações.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class GovernanceDomain:
    def create_deliberation(
        self,
        entity_id: str,
        title: str,
        resolution: str,
        approvers: list[str],
        quorum_required: float = 0.51,
    ) -> dict:
        return {
            "deliberation_id": f"DEL-{uuid4().hex[:8].upper()}",
            "entity_id": entity_id,
            "title": title,
            "resolution": resolution,
            "approvers": approvers,
            "quorum_required": quorum_required,
            "votes": [],
            "status": "pending",
            "created_at": utc_now(),
        }

    def cast_vote(self, deliberation: dict, voter: str, approve: bool) -> dict:
        deliberation["votes"].append({"voter": voter, "approve": approve, "at": utc_now()})
        approved_count = sum(1 for v in deliberation["votes"] if v["approve"])
        total = len(deliberation["approvers"])
        ratio = approved_count / total if total else 0
        if ratio >= deliberation["quorum_required"]:
            deliberation["status"] = "approved"
        elif (total - approved_count) / total > (1 - deliberation["quorum_required"]):
            deliberation["status"] = "rejected"
        return deliberation

    def governance_health(self, entity: dict) -> dict:
        issues = []
        score = 100
        if not entity.get("bylaws_updated_at"):
            issues.append("Estatuto/Contrato social não atualizado")
            score -= 20
        if not entity.get("compliance_officer"):
            issues.append("Sem responsável de compliance designado")
            score -= 15
        if not entity.get("data_protection_officer"):
            issues.append("DPO (LGPD) não designado")
            score -= 15
        if not entity.get("internal_audit"):
            issues.append("Auditoria interna não estruturada")
            score -= 10
        return {
            "entity_id": entity.get("entity_id"),
            "governance_score": max(score, 0),
            "issues": issues,
            "evaluated_at": utc_now(),
        }
