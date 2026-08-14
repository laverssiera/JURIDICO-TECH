from __future__ import annotations


class LegalTrustGraph:
    def __init__(self) -> None:
        self._edges: dict[str, dict[str, float]] = {}

    def link(self, source: str, target: str, trust: float) -> None:
        self._edges.setdefault(source, {})[target] = max(0.0, min(100.0, trust))

    def aggregate_score(self, entity_id: str) -> float:
        neighbors = self._edges.get(entity_id, {})
        if not neighbors:
            return 75.0
        return round(sum(neighbors.values()) / len(neighbors), 4)

    def size(self) -> dict:
        nodes = len(self._edges)
        edges = sum(len(v) for v in self._edges.values())
        return {"nodes": nodes, "edges": edges}
