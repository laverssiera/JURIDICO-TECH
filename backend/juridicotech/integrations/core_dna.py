from __future__ import annotations

import os

import httpx


CORE_DNA_URL = os.getenv("CORE_DNA_URL", "http://localhost:7000/decide")


def local_legal_decision(payload: dict) -> dict:
    value = float(payload.get("value", payload.get("amount", 0)) or 0)
    if value > 1_000_000:
        return {
            "risk_level": "high",
            "score": 0.45,
            "decision": "block",
        }
    if value > 300_000:
        return {
            "risk_level": "medium",
            "score": 0.70,
            "decision": "review",
        }
    return {
        "risk_level": "low",
        "score": 0.90,
        "decision": "allow",
    }


def legal_decision(payload: dict) -> dict:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                CORE_DNA_URL,
                json={
                    "type": "LEGAL_ANALYSIS",
                    "data": payload,
                },
            )
            response.raise_for_status()
            return response.json()
    except Exception:
        return local_legal_decision(payload)
