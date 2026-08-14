from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import sqlite3
from threading import RLock
from urllib.parse import urlparse


UTC = timezone.utc


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class LegalCoreStore:
    """Small JSON-document store backed by SQLite or PostgreSQL for Legal Core snapshots."""

    def __init__(self, db_path: str | None = None) -> None:
        configured_dsn = db_path or os.getenv("LEGAL_CORE_DB_URL") or os.getenv("DATABASE_URL")
        self.db_path = configured_dsn or os.getenv("LEGAL_CORE_DB_PATH", "/tmp/juridico_legal_core.db")
        self.backend = self._detect_backend(self.db_path)
        self._lock = RLock()
        self._ensure_schema()

    def _detect_backend(self, target: str) -> str:
        parsed = urlparse(target)
        if parsed.scheme in {"postgres", "postgresql"}:
            return "postgres"
        return "sqlite"

    def _connect_sqlite(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _connect_postgres(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL backend requested but psycopg is not installed. Run pip install -r requirements.txt."
            ) from exc

        return psycopg.connect(self.db_path, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        if self.backend == "postgres":
            with self._connect_postgres() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS legal_state (
                            state_key TEXT PRIMARY KEY,
                            payload_json TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        )
                        """
                    )
                connection.commit()
            return

        with self._connect_sqlite() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS legal_state (
                    state_key TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def load(self, state_key: str, default: object) -> object:
        with self._lock:
            if self.backend == "postgres":
                with self._connect_postgres() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT payload_json FROM legal_state WHERE state_key = %s",
                            (state_key,),
                        )
                        row = cursor.fetchone()
                        if not row:
                            return default
                        return json.loads(row["payload_json"])

            with self._connect_sqlite() as connection:
                row = connection.execute(
                    "SELECT payload_json FROM legal_state WHERE state_key = ?",
                    (state_key,),
                ).fetchone()
                if not row:
                    return default
                return json.loads(row["payload_json"])

    def save(self, state_key: str, payload: object) -> None:
        with self._lock:
            serialized = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
            now = utc_now_iso()
            if self.backend == "postgres":
                with self._connect_postgres() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO legal_state (state_key, payload_json, updated_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT(state_key) DO UPDATE SET
                                payload_json = excluded.payload_json,
                                updated_at = excluded.updated_at
                            """,
                            (state_key, serialized, now),
                        )
                    connection.commit()
                return

            with self._connect_sqlite() as connection:
                connection.execute(
                    """
                    INSERT INTO legal_state (state_key, payload_json, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(state_key) DO UPDATE SET
                        payload_json = excluded.payload_json,
                        updated_at = excluded.updated_at
                    """,
                    (state_key, serialized, now),
                )
                connection.commit()


legal_core_store = LegalCoreStore()
