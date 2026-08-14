from __future__ import annotations

from datetime import datetime, UTC


class CivilizationLegalGovernance:
    def __init__(self) -> None:
        self._federations: dict[str, dict] = {}

    def synchronize(self, federation_id: str, nodes: list[str]) -> dict:
        synchronized = len(nodes) > 0
        state = {
            "federation_id": federation_id,
            "nodes": nodes,
            "synchronized": synchronized,
            "synchronization_level": "stable" if synchronized else "degraded",
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self._federations[federation_id] = state
        return state

    def snapshot(self) -> dict:
        synchronized_count = sum(1 for item in self._federations.values() if item.get("synchronized"))
        total = len(self._federations)
        consistency = (synchronized_count / total) if total else 1.0
        return {
            "total_federations": total,
            "synchronized_federations": synchronized_count,
            "legal_federation_consistency": round(consistency, 4),
            "federations": list(self._federations.values()),
        }
