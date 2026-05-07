"""
LICEU 6.x — Legal Knowledge Graph
Grafo jurídico conectando pessoas, contratos, obras, fornecedores, processos, riscos e evidências.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class LegalKnowledgeGraphDomain:
    def __init__(self) -> None:
        self._nodes: dict[str, dict] = {}
        self._edges: list[dict] = []
        self._adj: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node_id: str, node_type: str, attributes: dict | None = None) -> dict:
        node = {
            "node_id": node_id,
            "node_type": node_type,
            "attributes": attributes or {},
            "updated_at": utc_now(),
        }
        self._nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, relation: str, weight: float = 1.0) -> dict:
        if source_id not in self._nodes or target_id not in self._nodes:
            raise KeyError("Nó de origem/destino não existe")
        edge = {
            "source_id": source_id,
            "target_id": target_id,
            "relation": relation,
            "weight": weight,
            "at": utc_now(),
        }
        self._edges.append(edge)
        self._adj[source_id].add(target_id)
        self._adj[target_id].add(source_id)
        return edge

    def neighbors(self, node_id: str) -> list[str]:
        return sorted(self._adj.get(node_id, set()))

    def detect_concentration_risk(self, node_type: str, threshold: int = 5) -> dict:
        risky = []
        for nid, node in self._nodes.items():
            if node["node_type"] != node_type:
                continue
            degree = len(self._adj.get(nid, set()))
            if degree >= threshold:
                risky.append({"node_id": nid, "connections": degree})
        return {
            "node_type": node_type,
            "threshold": threshold,
            "risky_nodes": sorted(risky, key=lambda x: x["connections"], reverse=True),
            "analyzed_at": utc_now(),
        }

    def graph_stats(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "generated_at": utc_now(),
        }
