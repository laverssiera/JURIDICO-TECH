from __future__ import annotations

import json
import logging
from typing import Any

from juridicotech.core.db import get_connection


logger = logging.getLogger(__name__)


def log_action(action: str, actor: str | None, metadata: dict[str, Any] | None = None) -> None:
    payload = metadata or {}
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO legal_audit_logs (action, actor_id, metadata)
                    VALUES (%s, %s, %s::jsonb)
                    """,
                    (action, actor, json.dumps(payload, ensure_ascii=True)),
                )
            connection.commit()
    except Exception as exc:
        # Fallback to logs so legal flow still runs even if DB is temporarily unavailable.
        logger.warning("Audit persistence failed: %s", exc)
        logger.info(
            "AUDIT_FALLBACK action=%s actor=%s metadata=%s",
            action,
            actor,
            payload,
        )
