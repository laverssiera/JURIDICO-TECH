from __future__ import annotations

import os
from typing import Any

import jwt


class UnifiedLegalIdentity:
    def __init__(self) -> None:
        self.secret = os.getenv("LEGAL_IDENTITY_SECRET", "LICEU_IDENTITY")

    def issue_identity(self, subject: str, roles: list[str]) -> dict[str, Any]:
        claims = {
            "subject": subject,
            "roles": roles,
            "namespace": "juridicotech.legal.identity",
        }
        token = jwt.encode(claims, self.secret, algorithm="HS256")
        return {"claims": claims, "token": token}
