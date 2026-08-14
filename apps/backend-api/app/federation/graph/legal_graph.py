from __future__ import annotations

from threading import RLock
from typing import Any

from app.federation.config import settings


class LegalKnowledgeGraph:
    _nodes: dict[str, dict[str, Any]] = {}
    _edges: list[dict[str, Any]] = []
    _lock = RLock()
    _neo4j_driver: Any | None = None
    _neo4j_initialized = False

    @classmethod
    def _should_try_neo4j(cls) -> bool:
        backend = settings.FEDERATION_GRAPH_BACKEND.lower()
        return backend in {"auto", "neo4j"}

    @classmethod
    def _driver(cls) -> Any | None:
        if cls._neo4j_initialized:
            return cls._neo4j_driver
        cls._neo4j_initialized = True

        if not cls._should_try_neo4j():
            cls._neo4j_driver = None
            return None

        try:
            from neo4j import GraphDatabase
        except Exception:
            cls._neo4j_driver = None
            return None

        try:
            driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            with driver.session() as session:
                session.run("RETURN 1")
            cls._neo4j_driver = driver
        except Exception:
            cls._neo4j_driver = None

        return cls._neo4j_driver

    @classmethod
    def register_treaty(cls, treaty_name: str, jurisdiction: str, legal_scope: str) -> dict[str, Any]:
        with cls._lock:
            node_id = f"treaty:{treaty_name}"
            cls._nodes[node_id] = {
                "id": node_id,
                "type": "Treaty",
                "name": treaty_name,
                "jurisdiction": jurisdiction,
                "legal_scope": legal_scope,
            }
            treaty = cls._node_payload(node_id)

        driver = cls._driver()
        if driver is not None:
            query = """
            MERGE (t:Treaty {name: $treaty_name})
            SET t.jurisdiction = $jurisdiction,
                t.legal_scope = $legal_scope
            """
            with driver.session() as session:
                session.run(
                    query,
                    treaty_name=treaty_name,
                    jurisdiction=jurisdiction,
                    legal_scope=legal_scope,
                )

        return treaty

    @classmethod
    def register_relationship(cls, source: str, relation: str, target: str) -> None:
        with cls._lock:
            cls._edges.append({"source": source, "target": target, "relation": relation})

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        driver = cls._driver()
        if driver is not None:
            with driver.session() as session:
                counts = session.run(
                    "MATCH (n) WITH count(n) AS nodes "
                    "OPTIONAL MATCH ()-[r]->() "
                    "RETURN nodes, count(r) AS edges"
                ).single()
                treaties = session.run(
                    "MATCH (t:Treaty) "
                    "RETURN t.name AS name, t.jurisdiction AS jurisdiction, t.legal_scope AS legal_scope"
                )
                return {
                    "backend": "neo4j",
                    "nodes": int(counts["nodes"] if counts else 0),
                    "edges": int(counts["edges"] if counts else 0),
                    "treaties": [
                        {
                            "type": "Treaty",
                            "name": row["name"],
                            "jurisdiction": row["jurisdiction"],
                            "legal_scope": row["legal_scope"],
                        }
                        for row in treaties
                    ],
                }

        with cls._lock:
            treaties = [data for data in cls._nodes.values() if data.get("type") == "Treaty"]
            return {
                "backend": "internal",
                "nodes": len(cls._nodes),
                "edges": len(cls._edges),
                "treaties": treaties,
            }

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._nodes = {}
            cls._edges = []

    @classmethod
    def _node_payload(cls, node_id: str) -> dict[str, Any]:
        return dict(cls._nodes[node_id])
