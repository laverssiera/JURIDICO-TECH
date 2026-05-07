from datetime import UTC, datetime
from uuid import uuid4


def build_event_envelope(payload: dict, origin: str = "juridicotech") -> dict:
    return {
        "meta": {
            "trace_id": str(uuid4()),
            "decision_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "origin": origin,
        },
        "payload": payload,
        "signature": "sha256",
    }
