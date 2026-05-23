from __future__ import annotations

from datetime import datetime, UTC


class LegalConsensusRuntime:
    def __init__(self) -> None:
        self._history: list[dict] = []

    def build_consensus(self, proposal_id: str, votes: list[dict]) -> dict:
        approvals = sum(1 for vote in votes if vote.get("approve") is True)
        total = len(votes)
        ratio = approvals / total if total else 0.0
        reached = ratio >= 0.67

        result = {
            "proposal_id": proposal_id,
            "approvals": approvals,
            "total_votes": total,
            "consensus_ratio": round(ratio, 4),
            "sovereign_consensus": reached,
            "evaluated_at": datetime.now(UTC).isoformat(),
        }
        self._history.append(result)
        return result

    def history(self) -> list[dict]:
        return self._history
