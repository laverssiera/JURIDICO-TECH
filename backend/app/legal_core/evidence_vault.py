"""
LICEU 6.0 — Domain: Evidence Vault + ICP Signature Engine
Cofre de evidências com cadeia de custódia, ancoragem blockchain e assinatura ICP-Brasil.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc
_VAULT_SECRET = os.getenv("VAULT_SIGNING_SECRET", "liceu-vault-dev-secret")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _hmac_sign(data: str) -> str:
    return hmac.new(_VAULT_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()


class EvidenceVaultDomain:
    """
    Cofre de evidências jurídicas com:
    - Hash SHA-256 de integridade
    - Cadeia de custódia auditável
    - Simulação de ancoragem blockchain (hash do hash)
    - Simulação de assinatura ICP-Brasil
    """

    def __init__(self) -> None:
        self._vault: dict[str, dict] = {}

    def deposit(
        self,
        title: str,
        content: str,
        depositor: str,
        tags: list[str] | None = None,
        linked_entity: str | None = None,
    ) -> dict:
        evidence_id = f"VAULT-{uuid4().hex[:10].upper()}"
        content_hash = _sha256(content)
        blockchain_anchor = _sha256(f"{evidence_id}:{content_hash}:{utc_now()}")
        icp_signature = _hmac_sign(f"{evidence_id}:{content_hash}")

        item = {
            "evidence_id": evidence_id,
            "title": title,
            "depositor": depositor,
            "content_hash_sha256": content_hash,
            "blockchain_anchor": blockchain_anchor,
            "icp_signature_sim": icp_signature,
            "icp_signed": True,
            "tags": tags or [],
            "linked_entity": linked_entity,
            "chain_of_custody": [{"holder": depositor, "action": "deposit", "at": utc_now()}],
            "deposited_at": utc_now(),
            "status": "active",
        }
        self._vault[evidence_id] = item
        return item

    def verify_integrity(self, evidence_id: str, original_content: str) -> dict:
        item = self._get(evidence_id)
        actual_hash = _sha256(original_content)
        match = actual_hash == item["content_hash_sha256"]
        return {
            "evidence_id": evidence_id,
            "integrity_ok": match,
            "stored_hash": item["content_hash_sha256"],
            "computed_hash": actual_hash,
            "verified_at": utc_now(),
        }

    def transfer_custody(self, evidence_id: str, from_: str, to: str, reason: str) -> dict:
        item = self._get(evidence_id)
        entry = {"holder": to, "from": from_, "action": "transfer", "reason": reason, "at": utc_now()}
        item["chain_of_custody"].append(entry)
        return entry

    def get_item(self, evidence_id: str) -> dict:
        return self._get(evidence_id)

    def list_items(self, tag: str | None = None, linked_entity: str | None = None) -> list[dict]:
        items = list(self._vault.values())
        if tag:
            items = [i for i in items if tag in i["tags"]]
        if linked_entity:
            items = [i for i in items if i.get("linked_entity") == linked_entity]
        return items

    def _get(self, evidence_id: str) -> dict:
        item = self._vault.get(evidence_id)
        if not item:
            raise KeyError(f"Evidência {evidence_id} não encontrada no cofre")
        return item
