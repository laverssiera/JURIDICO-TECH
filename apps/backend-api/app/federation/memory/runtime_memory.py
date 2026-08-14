from __future__ import annotations

import json
from threading import RLock
from typing import Any

from app.federation.config import settings


class LegalMemory:
    _cases: dict[str, dict[str, Any]] = {}
    _journal: list[dict[str, Any]] = []
    _lock = RLock()
    _redis_client: Any | None = None
    _redis_initialized = False

    @classmethod
    def _should_try_redis(cls) -> bool:
        backend = settings.FEDERATION_MEMORY_BACKEND.lower()
        return backend in {"auto", "redis"}

    @classmethod
    def _redis(cls) -> Any | None:
        if cls._redis_initialized:
            return cls._redis_client
        cls._redis_initialized = True

        if not cls._should_try_redis():
            cls._redis_client = None
            return None

        try:
            import redis
        except Exception:
            cls._redis_client = None
            return None

        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            client.ping()
            cls._redis_client = client
        except Exception:
            cls._redis_client = None

        return cls._redis_client

    @classmethod
    def save_case(cls, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {"case_id": case_id, **payload}
        with cls._lock:
            cls._cases[case_id] = json.loads(json.dumps(record))
            cls._journal.append({"type": "case", "case_id": case_id, "payload": record})

        redis_client = cls._redis()
        if redis_client is not None:
            redis_client.set(f"legal:case:{case_id}", json.dumps(record))

        return record

    @classmethod
    def remember(cls, label: str, payload: dict[str, Any]) -> dict[str, Any]:
        entry = {"label": label, "payload": payload}
        with cls._lock:
            cls._journal.append(entry)

        redis_client = cls._redis()
        if redis_client is not None:
            redis_client.rpush("legal:journal", json.dumps(entry))

        return entry

    @classmethod
    def get_case(cls, case_id: str) -> dict[str, Any] | None:
        redis_client = cls._redis()
        if redis_client is not None:
            raw = redis_client.get(f"legal:case:{case_id}")
            if raw:
                return json.loads(raw)

        with cls._lock:
            record = cls._cases.get(case_id)
            return None if record is None else json.loads(json.dumps(record))

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        redis_client = cls._redis()
        with cls._lock:
            backend = "redis" if redis_client is not None else "memory"
            return {
                "backend": backend,
                "cases_total": len(cls._cases),
                "journal_total": len(cls._journal),
                "cases": list(cls._cases.values()),
            }

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._cases = {}
            cls._journal = []

        redis_client = cls._redis()
        if redis_client is not None:
            for key in redis_client.scan_iter(match="legal:case:*"):
                redis_client.delete(key)
            redis_client.delete("legal:journal")
