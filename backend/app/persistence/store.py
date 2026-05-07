"""
LICEU 6.x — Persistence Store
Camada de persistência SQLite para estados críticos dos domínios jurídicos.
Armazena dados como JSON em uma tabela KV genérica: (domain, key, data, updated_at).
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timezone

_DB_PATH = Path(__file__).parent.parent.parent / "liceu_state.db"

UTC = timezone.utc


def _now() -> str:
    return datetime.now(UTC).isoformat()


class PersistenceStore:
    """Thread-safe SQLite KV store para persistência de estado dos domínios LICEU."""

    def __init__(self, db_path: Path = _DB_PATH) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None

    def init(self) -> None:
        """Inicializa o banco e cria a tabela se não existir."""
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS liceu_state (
                domain      TEXT NOT NULL,
                key         TEXT NOT NULL,
                data        TEXT NOT NULL,
                updated_at  TEXT NOT NULL,
                PRIMARY KEY (domain, key)
            )
            """
        )
        self._conn.commit()

    def get(self, domain: str, key: str) -> dict | None:
        """Retorna o registro ou None se não encontrado."""
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM liceu_state WHERE domain = ? AND key = ?",
                (domain, key),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, domain: str, key: str, data: dict) -> None:
        """Insere ou atualiza um registro."""
        payload = json.dumps(data, ensure_ascii=False, default=str)
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO liceu_state (domain, key, data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(domain, key) DO UPDATE SET
                    data       = excluded.data,
                    updated_at = excluded.updated_at
                """,
                (domain, key, payload, _now()),
            )
            self._conn.commit()

    def list(self, domain: str) -> list[dict]:
        """Lista todos os registros de um domínio."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT data FROM liceu_state WHERE domain = ? ORDER BY updated_at",
                (domain,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def delete(self, domain: str, key: str) -> bool:
        """Remove um registro. Retorna True se encontrado."""
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM liceu_state WHERE domain = ? AND key = ?",
                (domain, key),
            )
            self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


# Singleton global — injetado nos domínios no lifespan do app
persistence_store = PersistenceStore()
