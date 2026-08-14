from __future__ import annotations

import os
from typing import Any


class LegalKnowledgeGraph:
    def __init__(self) -> None:
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver: Any | None = None
        try:
            from neo4j import GraphDatabase

            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception:
            self.driver = None

    def register_case(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = """
        MERGE (c:LegalCase {id:$id})
        SET c.domain = $domain,
            c.risk = $risk,
            c.status = $status,
            c.updated_at = datetime()
        """

        if self.driver is None:
            return {"backend": "memory", "saved": False, "payload": payload}

        with self.driver.session() as session:
            session.run(
                query,
                id=payload["id"],
                domain=payload["domain"],
                risk=payload["risk"],
                status=payload["status"],
            )
        return {"backend": "neo4j", "saved": True, "case_id": payload["id"]}
