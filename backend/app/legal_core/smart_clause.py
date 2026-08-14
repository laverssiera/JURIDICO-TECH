"""
LICEU 6.x — Smart Clause Engine
Cláusulas vivas com histórico de performance e recomendação por redução de litígio.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class SmartClauseDomain:
    def __init__(self) -> None:
        self._clauses: dict[str, dict] = {}

    def register_clause(self, type_: str, text: str, tags: list[str] | None = None) -> dict:
        cid = f"CLS-{uuid4().hex[:6].upper()}"
        clause = {
            "clause_id": cid,
            "type": type_,
            "text": text,
            "tags": tags or [],
            "performance_history": [],
            "litigation_reduction": 0,
            "recommended": False,
            "created_at": utc_now(),
        }
        self._clauses[cid] = clause
        return clause

    def record_performance(self, clause_id: str, prevented_litigation: bool, contract_value: float | None = None) -> dict:
        clause = self._get(clause_id)
        entry = {
            "prevented_litigation": prevented_litigation,
            "contract_value": contract_value,
            "at": utc_now(),
        }
        clause["performance_history"].append(entry)

        total = len(clause["performance_history"])
        hits = sum(1 for e in clause["performance_history"] if e["prevented_litigation"])
        clause["litigation_reduction"] = int((hits / total) * 100) if total else 0
        clause["recommended"] = clause["litigation_reduction"] >= 30 and total >= 3
        clause["updated_at"] = utc_now()
        return clause

    def list_clauses(self, recommended_only: bool = False) -> list[dict]:
        values = list(self._clauses.values())
        if recommended_only:
            values = [c for c in values if c.get("recommended")]
        return values

    def _get(self, clause_id: str) -> dict:
        c = self._clauses.get(clause_id)
        if not c:
            raise KeyError("Cláusula não encontrada")
        return c
