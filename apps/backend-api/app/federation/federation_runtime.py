from __future__ import annotations

import os
from typing import Any

import httpx
import jwt


class FederationRuntime:
    def __init__(self) -> None:
        self.monolith = "juridicotech"
        self.secret = os.getenv("FEDERATION_SECRET", "LICEU_SUPREME")
        self.registry = os.getenv("FEDERATION_REGISTRY", "http://liceu-runtime:9000")

    def token(self) -> str:
        return jwt.encode(
            {
                "monolith": self.monolith,
                "role": "legal_runtime",
            },
            self.secret,
            algorithm="HS256",
        )

    async def register(self) -> dict[str, Any]:
        payload = {
            "name": self.monolith,
            "capabilities": [
                "legal_runtime",
                "planetary_compliance",
                "patent_intelligence",
                "autonomous_arbitration",
                "causal_governance",
                "federated_legal_ai",
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.registry}/federation/register",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.token()}"},
                )
                response.raise_for_status()
            return {"registered": True, "registry": self.registry}
        except Exception as exc:
            return {
                "registered": False,
                "registry": self.registry,
                "error": str(exc),
            }