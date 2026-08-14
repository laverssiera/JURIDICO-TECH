from __future__ import annotations


class ComplianceReputationEngine:
    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def update(self, entity_id: str, compliant: bool) -> float:
        current = self._scores.get(entity_id, 80.0)
        delta = 2.5 if compliant else -5.0
        score = max(0.0, min(100.0, current + delta))
        self._scores[entity_id] = score
        return score

    def get(self, entity_id: str) -> float:
        return self._scores.get(entity_id, 80.0)
