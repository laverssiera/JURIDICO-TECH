from __future__ import annotations

from typing import Any


class JohnBrasileiroHooks:
    """Cognitive hooks for the John's legal war room persona."""

    def profile(self) -> dict[str, Any]:
        return {
            "persona": "JOHN BRASILEIRO",
            "purpose": "legal_cognitive_hook",
            "modes": [
                "triage",
                "regulatory synthesis",
                "war room escalation",
                "federated summarization",
            ],
            "enabled": True,
        }

    def annotate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "persona": "JOHN BRASILEIRO",
            "annotation": "federation_hook_applied",
            "payload": payload,
        }
