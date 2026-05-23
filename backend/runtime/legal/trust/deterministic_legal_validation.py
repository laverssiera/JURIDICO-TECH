from __future__ import annotations

import hashlib
import json


class DeterministicLegalValidation:
    def fingerprint(self, payload: dict) -> str:
        canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def validate(self, payload: dict, expected_fingerprint: str | None = None) -> dict:
        current = self.fingerprint(payload)
        return {
            "fingerprint": current,
            "deterministic_legal_validation": expected_fingerprint in (None, current),
        }
