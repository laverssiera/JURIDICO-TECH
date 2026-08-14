from __future__ import annotations

from datetime import datetime, UTC
import hashlib
import json


class SovereignLegalAudit:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def record(self, category: str, payload: dict) -> dict:
        previous_hash = self._entries[-1]["entry_hash"] if self._entries else ""
        canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        material = f"{category}|{canonical}|{previous_hash}".encode("utf-8")
        entry_hash = hashlib.sha256(material).hexdigest()

        entry = {
            "category": category,
            "payload": payload,
            "entry_hash": entry_hash,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        self._entries.append(entry)
        return entry

    def continuity(self) -> dict:
        return {
            "audit_entries": len(self._entries),
            "audit_continuity": "active",
        }
