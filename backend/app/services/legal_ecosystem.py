from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import json
import os
from uuid import uuid4

from fastapi import HTTPException, status

from app.integration.event_bus import event_bus
from app.schemas import (
    AuditAppendRequest,
    BypassCheckRequest,
    BypassProtectRequest,
    ContractCreateV2Request,
    ContractCustodyVerifyRequest,
    ContractDigitalSignRequest,
    ContractSignV2Request,
    ContractSignatureVerifyRequest,
    ContractStatusActionRequest,
    ContractTemplateCreateRequest,
    ContractVersionCreateRequest,
    LegalEntityUpsertRequest,
    JohnDecisionRequest,
    KanbanStageUpdateRequest,
    ExternalRiskIngestRequest,
    LegalLearningCreateRequest,
    LegalRiskLevel,
    LegalRoleGrantRequest,
    LegalTaskCreateRequest,
    LegalTaskAutoDecisionRequest,
    LegalTaskPriority,
    LegalUserUpsertRequest,
    OverrideRequest,
    RiskAnalysisRequest,
    SLAUpsertRequest,
)
from app.services.legal_store import legal_core_store


UTC = timezone.utc
LEGAL_SIGNING_SECRET = os.getenv("LEGAL_SIGNING_SECRET", "juridicotech-dev-signing-secret")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class LegalEcosystemService:
    def __init__(self) -> None:
        self.legal_entities: dict[str, dict] = legal_core_store.load("legal_entities", {})
        self.legal_users: dict[str, dict] = legal_core_store.load("legal_users", {})
        self.legal_roles: dict[str, list[dict]] = legal_core_store.load("legal_roles", {})

        self.contract_templates: dict[str, dict] = legal_core_store.load("contract_templates", {})
        self.contracts: dict[str, dict] = legal_core_store.load("contracts_v2", {})
        self.contract_versions: dict[str, list[dict]] = legal_core_store.load("contract_versions_v2", {})

        self.relationship_protections: dict[str, dict] = legal_core_store.load("relationship_protections", {})
        self.legal_audit_logs: list[dict] = legal_core_store.load("legal_audit_logs_v2", [])
        self.risk_assessments: list[dict] = legal_core_store.load("risk_assessments", [])
        self.risk_center_feeds: list[dict] = legal_core_store.load("risk_center_feeds", [])

        self.legal_sla: dict[str, int] = legal_core_store.load(
            "legal_sla",
            {
                "contract.signature": 24,
                "legal.validation": 12,
            },
        )
        self.legal_tasks: dict[str, dict] = legal_core_store.load("legal_tasks", {})
        self.legal_overrides: list[dict] = legal_core_store.load("legal_overrides", [])
        self.legal_learning: list[dict] = legal_core_store.load("legal_learning", [])
        self.notifications: list[dict] = legal_core_store.load("legal_notifications", [])

        self.allowed_transitions: dict[str, set[str]] = {
            "draft": {"pending", "canceled"},
            "pending": {"signed", "canceled"},
            "signed": {"active", "canceled"},
            "active": {"completed", "canceled"},
            "completed": set(),
            "canceled": set(),
        }

    def _persist(self) -> None:
        legal_core_store.save("legal_entities", self.legal_entities)
        legal_core_store.save("legal_users", self.legal_users)
        legal_core_store.save("legal_roles", self.legal_roles)
        legal_core_store.save("contract_templates", self.contract_templates)
        legal_core_store.save("contracts_v2", self.contracts)
        legal_core_store.save("contract_versions_v2", self.contract_versions)
        legal_core_store.save("relationship_protections", self.relationship_protections)
        legal_core_store.save("legal_audit_logs_v2", self.legal_audit_logs[-10000:])
        legal_core_store.save("risk_assessments", self.risk_assessments[-2000:])
        legal_core_store.save("risk_center_feeds", self.risk_center_feeds[-5000:])
        legal_core_store.save("legal_sla", self.legal_sla)
        legal_core_store.save("legal_tasks", self.legal_tasks)
        legal_core_store.save("legal_overrides", self.legal_overrides[-2000:])
        legal_core_store.save("legal_learning", self.legal_learning[-3000:])
        legal_core_store.save("legal_notifications", self.notifications[-5000:])

    def _hash(self, payload: object) -> str:
        serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _hmac_sign(self, payload: str) -> str:
        return hmac.new(
            LEGAL_SIGNING_SECRET.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _contract_payload_hash(self, contract: dict) -> str:
        canonical = {
            "contract_id": contract["contract_id"],
            "contract_type": contract["contract_type"],
            "title": contract["title"],
            "status": contract["status"],
            "current_hash": contract.get("current_hash"),
            "parties": contract.get("parties", []),
            "metadata": contract.get("metadata", {}),
        }
        return self._hash(canonical)

    def _publish(self, event_name: str, payload: dict) -> None:
        event_bus.publish(event_name, payload)

    def _has_role(self, user_id: str, role: str) -> bool:
        grants = self.legal_roles.get(user_id, [])
        return any(entry["role"] == role for entry in grants)

    def _assert_role(self, user_id: str, role: str) -> None:
        if not self._has_role(user_id, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user_id} does not have role {role}",
            )

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:12].upper()}"

    def _emit_notification(self, kind: str, title: str, payload: dict) -> dict:
        notification = {
            "notification_id": self._new_id("NTF"),
            "kind": kind,
            "title": title,
            "payload": payload,
            "created_at": utc_now_iso(),
            "status": "new",
        }
        self.notifications.append(notification)
        return notification

    def _append_audit(self, event_type: str, actor_id: str, target_id: str, payload: dict) -> dict:
        previous_hash = self.legal_audit_logs[-1]["hash"] if self.legal_audit_logs else None
        raw = {
            "event_type": event_type,
            "actor_id": actor_id,
            "target_id": target_id,
            "payload": payload,
            "timestamp": utc_now_iso(),
            "previous_hash": previous_hash,
        }
        current_hash = self._hash(raw)
        entry = {**raw, "hash": current_hash}
        self.legal_audit_logs.append(entry)
        return entry

    def upsert_legal_entity(self, request: LegalEntityUpsertRequest) -> dict:
        existing = next(
            (
                entity
                for entity in self.legal_entities.values()
                if entity["entity_ref"] == request.entity_ref
            ),
            None,
        )

        legal_entity_id = existing["legal_entity_id"] if existing else self._new_id("LEGENT")
        entity = {
            "legal_entity_id": legal_entity_id,
            "entity_ref": request.entity_ref,
            "entity_type": request.entity_type,
            "document_hash": self._hash({"document": request.document}),
            "risk_profile": request.risk_profile,
            "jurisdiction": request.jurisdiction,
            "metadata": request.metadata,
            "updated_at": utc_now_iso(),
        }
        if not existing:
            entity["created_at"] = utc_now_iso()
        else:
            entity["created_at"] = existing["created_at"]

        self.legal_entities[legal_entity_id] = entity
        self._append_audit("legal.entity.upserted", "system", legal_entity_id, entity)
        self._persist()
        return entity

    def upsert_legal_user(self, request: LegalUserUpsertRequest) -> dict:
        if request.legal_entity_id not in self.legal_entities:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal entity not found")

        user = {
            "user_id": request.user_id,
            "legal_entity_id": request.legal_entity_id,
            "rbac_subject_id": request.rbac_subject_id or request.user_id,
            "email": request.email,
            "updated_at": utc_now_iso(),
        }
        if request.user_id in self.legal_users:
            user["created_at"] = self.legal_users[request.user_id]["created_at"]
        else:
            user["created_at"] = utc_now_iso()

        self.legal_users[request.user_id] = user
        self._append_audit("legal.user.upserted", request.user_id, request.legal_entity_id, user)
        self._persist()
        return user

    def grant_role(self, request: LegalRoleGrantRequest) -> dict:
        if request.user_id not in self.legal_users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal user not found")

        grants = self.legal_roles.setdefault(request.user_id, [])
        if not any(entry["role"] == request.role for entry in grants):
            grants.append(
                {
                    "role": request.role,
                    "granted_by": request.granted_by,
                    "granted_at": utc_now_iso(),
                }
            )
        self._append_audit("legal.role.granted", request.granted_by, request.user_id, {"role": request.role})
        self._persist()
        return {
            "user_id": request.user_id,
            "roles": grants,
        }

    def list_roles(self, user_id: str) -> dict:
        return {
            "user_id": user_id,
            "roles": self.legal_roles.get(user_id, []),
        }

    def create_template(self, request: ContractTemplateCreateRequest) -> dict:
        if request.template_key in self.contract_templates:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Template already exists")

        template = {
            "template_key": request.template_key,
            "contract_type": request.contract_type,
            "jurisdiction": request.jurisdiction,
            "body": request.body,
            "variables": sorted(set(request.variables)),
            "created_by": request.created_by,
            "created_at": utc_now_iso(),
        }
        self.contract_templates[request.template_key] = template
        self._append_audit("legal.contract_template.created", request.created_by, request.template_key, template)
        self._persist()
        return template

    def list_templates(self) -> dict:
        return {
            "total": len(self.contract_templates),
            "templates": sorted(self.contract_templates.values(), key=lambda item: item["template_key"]),
        }

    def _create_contract_version(self, contract_id: str, content: dict, author_id: str, reason: str) -> dict:
        versions = self.contract_versions.setdefault(contract_id, [])
        previous_hash = versions[-1]["content_hash"] if versions else None
        payload = {
            "contract_id": contract_id,
            "content": content,
            "author_id": author_id,
            "reason": reason,
            "previous_hash": previous_hash,
        }
        content_hash = self._hash(payload)
        version = {
            "version": len(versions) + 1,
            "content": content,
            "author_id": author_id,
            "reason": reason,
            "previous_hash": previous_hash,
            "content_hash": content_hash,
            "created_at": utc_now_iso(),
        }
        versions.append(version)
        return version

    def export_contract_custody(self, contract_id: str) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

        versions = sorted(self.contract_versions.get(contract_id, []), key=lambda item: item["version"])
        chain: list[dict] = []
        previous_hash = None
        for version in versions:
            payload = {
                "contract_id": contract_id,
                "content": version["content"],
                "author_id": version["author_id"],
                "reason": version["reason"],
                "previous_hash": previous_hash,
            }
            recomputed_hash = self._hash(payload)
            linked = version.get("previous_hash", previous_hash) == previous_hash
            hash_match = recomputed_hash == version["content_hash"]

            chain_entry = {
                "version": version["version"],
                "hash": version["content_hash"],
                "previous_hash": version.get("previous_hash"),
                "linked": linked,
                "hash_match": hash_match,
                "created_at": version["created_at"],
            }
            chain.append(chain_entry)
            previous_hash = version["content_hash"]

        chain_hashes = [entry["hash"] for entry in chain]
        proof_hash = self._hash({"contract_id": contract_id, "chain": chain_hashes})
        valid_chain = all(entry["linked"] and entry["hash_match"] for entry in chain)
        proof = {
            "proof_id": self._new_id("CUST"),
            "contract_id": contract_id,
            "root_hash": proof_hash,
            "total_versions": len(chain),
            "valid_chain": valid_chain,
            "generated_at": utc_now_iso(),
            "chain": chain,
        }
        self._append_audit("legal.contract.custody.exported", "system", contract_id, proof)
        self._persist()
        return proof

    def verify_contract_custody(self, contract_id: str, request: ContractCustodyVerifyRequest) -> dict:
        proof = self.export_contract_custody(contract_id)
        self._append_audit(
            "legal.contract.custody.verified",
            request.actor_id,
            contract_id,
            {"valid_chain": proof["valid_chain"], "root_hash": proof["root_hash"]},
        )
        self._persist()
        return {
            "contract_id": contract_id,
            "valid": proof["valid_chain"],
            "root_hash": proof["root_hash"],
            "total_versions": proof["total_versions"],
        }

    def create_contract(self, request: ContractCreateV2Request) -> dict:
        for party in request.parties:
            if party.legal_entity_id not in self.legal_entities:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Legal entity not found for party {party.display_name}",
                )

        contract_id = self._new_id("CTR2")
        contract = {
            "contract_id": contract_id,
            "title": request.title,
            "contract_type": request.contract_type,
            "template_key": request.template_key,
            "jurisdiction": request.jurisdiction,
            "status": "draft",
            "parties": [party.model_dump() for party in request.parties],
            "metadata": request.metadata,
            "created_by": request.created_by,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "signed_at": None,
        }

        if request.template_key and request.template_key not in self.contract_templates:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        if request.template_key:
            contract["template"] = self.contract_templates[request.template_key]

        version_payload = {
            "title": request.title,
            "contract_type": request.contract_type,
            "parties": [party.model_dump() for party in request.parties],
            "metadata": request.metadata,
        }
        version = self._create_contract_version(contract_id, version_payload, request.created_by, "initial")
        contract["current_version"] = version["version"]
        contract["current_hash"] = version["content_hash"]

        self.contracts[contract_id] = contract
        self._append_audit("legal.contract.created", request.created_by, contract_id, contract)
        self._publish("legal.contract.created", {"contract_id": contract_id, "status": "draft"})
        self._persist()
        return contract

    def create_contract_version(self, request: ContractVersionCreateRequest) -> dict:
        contract = self.contracts.get(request.contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        if contract["status"] in {"completed", "canceled"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contract is immutable")

        version = self._create_contract_version(
            request.contract_id,
            request.content,
            request.author_id,
            request.reason,
        )
        contract["current_version"] = version["version"]
        contract["current_hash"] = version["content_hash"]
        contract["updated_at"] = utc_now_iso()

        self._append_audit("legal.contract.versioned", request.author_id, request.contract_id, version)
        self._persist()
        return {
            "contract_id": request.contract_id,
            "version": version,
        }

    def _transition_contract(self, contract: dict, target_status: str, actor_id: str, reason: str | None) -> dict:
        current_status = contract["status"]
        if target_status not in self.allowed_transitions[current_status]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid transition {current_status} -> {target_status}",
            )

        contract["status"] = target_status
        contract["updated_at"] = utc_now_iso()
        if target_status == "signed":
            contract["signed_at"] = utc_now_iso()
            self._publish("legal.contract.signed", {"contract_id": contract["contract_id"], "status": "signed"})

        self._append_audit(
            "legal.contract.status_changed",
            actor_id,
            contract["contract_id"],
            {"from": current_status, "to": target_status, "reason": reason},
        )
        self._persist()
        return contract

    def change_contract_status(self, contract_id: str, request: ContractStatusActionRequest) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

        if request.target_status in {"active", "completed", "canceled"}:
            self._assert_role(request.actor_id, "JURIDICO_MASTER")

        updated = self._transition_contract(contract, request.target_status, request.actor_id, request.reason)
        return {
            "contract_id": contract_id,
            "status": updated["status"],
            "updated_at": updated["updated_at"],
        }

    def sign_contract(self, contract_id: str, request: ContractSignV2Request) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

        if contract["status"] == "draft":
            self._transition_contract(contract, "pending", request.actor_id, "auto_pending_before_sign")
        if contract["status"] != "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contract must be pending before sign")

        updated = self._transition_contract(contract, "signed", request.actor_id, "digital_signature")
        signature = {
            "provider": request.signature_provider,
            "signed_by": request.actor_id,
            "signed_at": updated["signed_at"],
        }
        updated.setdefault("signatures", []).append(signature)
        self._append_audit("legal.contract.signature", request.actor_id, contract_id, signature)
        self._emit_notification(
            "contract_pending",
            "Contrato assinado e pronto para ativacao",
            {"contract_id": contract_id, "status": "signed"},
        )
        self._persist()
        return {
            "contract_id": contract_id,
            "status": updated["status"],
            "signature": signature,
        }

    def digital_sign_contract(self, contract_id: str, request: ContractDigitalSignRequest) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

        if contract["status"] == "draft":
            self._transition_contract(contract, "pending", request.actor_id, "auto_pending_before_digital_sign")
        if contract["status"] == "pending":
            self._transition_contract(contract, "signed", request.actor_id, "qualified_digital_signature")

        payload_hash = self._contract_payload_hash(contract)
        signed_at = utc_now_iso()
        valid_until = (datetime.now(UTC) + timedelta(days=request.validity_days)).isoformat()
        signature_payload = "|".join(
            [
                contract_id,
                payload_hash,
                request.actor_id,
                request.signature_provider,
                request.certificate_ref,
                signed_at,
                valid_until,
            ]
        )
        signature_token = self._hmac_sign(signature_payload)

        legal_signature = {
            "type": "qualified_digital_signature",
            "provider": request.signature_provider,
            "certificate_ref": request.certificate_ref,
            "signed_by": request.actor_id,
            "signed_at": signed_at,
            "valid_until": valid_until,
            "signed_payload_hash": payload_hash,
            "signature_token": signature_token,
        }
        contract["legal_signature"] = legal_signature
        contract["legal_validity"] = "valid"
        contract.setdefault("signatures", []).append(legal_signature)
        contract["updated_at"] = utc_now_iso()

        self._append_audit("legal.contract.digital_signed", request.actor_id, contract_id, legal_signature)
        self._emit_notification(
            "contract_digitally_signed",
            "Contrato assinado digitalmente com validade juridica",
            {"contract_id": contract_id, "valid_until": valid_until},
        )
        self._persist()

        return {
            "contract_id": contract_id,
            "status": contract["status"],
            "legal_signature": legal_signature,
            "legal_validity": contract["legal_validity"],
        }

    def verify_contract_signature(self, contract_id: str, request: ContractSignatureVerifyRequest) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        signature = contract.get("legal_signature")
        if not signature:
            return {
                "contract_id": contract_id,
                "valid": False,
                "legal_validity": "invalid",
                "reason": "missing_digital_signature",
            }

        current_payload_hash = self._contract_payload_hash(contract)
        payload_unchanged = signature["signed_payload_hash"] == current_payload_hash

        signature_payload = "|".join(
            [
                contract_id,
                signature["signed_payload_hash"],
                signature["signed_by"],
                signature["provider"],
                signature["certificate_ref"],
                signature["signed_at"],
                signature["valid_until"],
            ]
        )
        expected_token = self._hmac_sign(signature_payload)
        signature_intact = hmac.compare_digest(signature["signature_token"], expected_token)

        check_time = datetime.now(UTC)
        if request.at_time:
            check_time = datetime.fromisoformat(request.at_time)
        not_expired = datetime.fromisoformat(signature["valid_until"]) >= check_time

        valid = payload_unchanged and signature_intact and not_expired
        legal_validity = "valid" if valid else "invalid"
        contract["legal_validity"] = legal_validity
        contract["updated_at"] = utc_now_iso()

        verify_payload = {
            "payload_unchanged": payload_unchanged,
            "signature_intact": signature_intact,
            "not_expired": not_expired,
            "legal_validity": legal_validity,
        }
        self._append_audit("legal.contract.signature_verified", request.actor_id, contract_id, verify_payload)
        self._persist()

        return {
            "contract_id": contract_id,
            "valid": valid,
            "legal_validity": legal_validity,
            **verify_payload,
        }

    def list_contracts(self) -> dict:
        contracts = sorted(self.contracts.values(), key=lambda item: item["created_at"], reverse=True)
        return {
            "total": len(contracts),
            "contracts": contracts,
        }

    def protect_commission(self, request: BypassProtectRequest) -> dict:
        relationship_hash = self._hash(
            {
                "lead_id": request.lead_id,
                "broker_id": request.broker_id,
                "asset_id": request.asset_id,
            }
        )
        until = request.protected_until or (datetime.now(UTC) + timedelta(days=180)).isoformat()

        protection = {
            "relationship_hash": relationship_hash,
            "lead_id": request.lead_id,
            "broker_id": request.broker_id,
            "asset_id": request.asset_id,
            "protected_until": until,
            "commission_owner_id": request.commission_owner_id,
            "created_at": utc_now_iso(),
        }
        self.relationship_protections[relationship_hash] = protection
        self._append_audit("legal.relationship.protected", "system", relationship_hash, protection)
        self._persist()
        return protection

    def check_bypass_risk(self, request: BypassCheckRequest) -> dict:
        relationship_hash = self._hash(
            {
                "lead_id": request.lead_id,
                "broker_id": request.broker_id,
                "asset_id": request.asset_id,
            }
        )
        protection = self.relationship_protections.get(relationship_hash)
        if not protection:
            return {
                "detected": False,
                "relationship_hash": relationship_hash,
                "reason": "not_protected",
            }

        protected_until = datetime.fromisoformat(protection["protected_until"])
        still_protected = protected_until > datetime.now(UTC)
        is_bypass = still_protected and request.candidate_broker_id != protection["broker_id"]

        payload = {
            "relationship_hash": relationship_hash,
            "protected_until": protection["protected_until"],
            "commission_owner_id": protection["commission_owner_id"],
            "source_event": request.source_event,
            "candidate_broker_id": request.candidate_broker_id,
        }

        if is_bypass:
            self._append_audit("legal.bypass.detected", "system", relationship_hash, payload)
            self._publish("legal.bypass.detected", payload)
            self._emit_notification("bypass_detected", "Bypass detectado", payload)
            self._persist()
            return {
                "detected": True,
                "blocked": True,
                **payload,
            }

        return {
            "detected": False,
            "blocked": False,
            **payload,
        }

    def append_audit(self, request: AuditAppendRequest) -> dict:
        entry = self._append_audit(request.event_type, request.actor_id, request.target_id, request.payload)
        self._persist()
        return entry

    def list_audit(self, limit: int = 200) -> dict:
        return {
            "total": len(self.legal_audit_logs),
            "events": self.legal_audit_logs[-limit:],
        }

    def analyze_risk(self, request: RiskAnalysisRequest) -> dict:
        score = 0
        flags: list[str] = []

        if not request.has_documents:
            score += 4
            flags.append("missing_document")
        if request.amount is not None and request.amount >= 1_000_000:
            score += 3
            flags.append("high_value")
        if request.user_age_days <= 30:
            score += 2
            flags.append("new_user")
        if len(request.actors) <= 1:
            score += 2
            flags.append("single_actor")

        risk_level: LegalRiskLevel
        if score >= 7:
            risk_level = "high"
        elif score >= 4:
            risk_level = "medium"
        else:
            risk_level = "low"

        confidence = round(min(0.98, 0.55 + (score * 0.06)), 2)
        result = {
            "risk_level": risk_level,
            "confidence": confidence,
            "flags": flags,
            "operation_type": request.operation_type,
            "deal_id": request.deal_id,
            "timestamp": utc_now_iso(),
        }
        self.risk_assessments.append(result)
        self._append_audit("legal.risk.flagged", "system", request.deal_id or "n/a", result)
        if risk_level in {"medium", "high"}:
            self._publish("legal.risk.flagged", result)
            self._emit_notification("high_risk", "Risco juridico elevado", result)
        self._persist()
        return result

    def ingest_external_risk(self, request: ExternalRiskIngestRequest) -> dict:
        item = {
            "monolith": request.monolith,
            "deal_id": request.deal_id,
            "risk_level": request.risk_level,
            "score": request.score,
            "flags": request.flags,
            "timestamp": utc_now_iso(),
        }
        self.risk_center_feeds.append(item)
        self._append_audit("legal.risk.external_ingested", "system", request.deal_id, item)
        if request.risk_level in {"medium", "high"}:
            self._publish("legal.risk.flagged", item)
        self._persist()
        return item

    def risk_center_snapshot(self, limit: int = 100) -> dict:
        merged = [
            {
                "monolith": "juridico",
                "deal_id": item.get("deal_id"),
                "risk_level": item.get("risk_level"),
                "score": item.get("confidence", 0),
                "flags": item.get("flags", []),
                "timestamp": item.get("timestamp"),
            }
            for item in self.risk_assessments[-limit:]
        ] + self.risk_center_feeds[-limit:]

        ranking = sorted(
            merged,
            key=lambda item: (
                3 if item["risk_level"] == "high" else 2 if item["risk_level"] == "medium" else 1,
                item.get("score", 0),
            ),
            reverse=True,
        )
        return {
            "total": len(merged),
            "top": ranking[:limit],
        }

    def list_risk(self) -> dict:
        return {
            "total": len(self.risk_assessments),
            "items": self.risk_assessments[-200:],
        }

    def upsert_sla(self, request: SLAUpsertRequest) -> dict:
        self.legal_sla[request.event_type] = request.sla_hours
        self._append_audit(
            "legal.sla.upserted",
            "system",
            request.event_type,
            {"sla_hours": request.sla_hours},
        )
        self._persist()
        return {
            "event_type": request.event_type,
            "sla_hours": request.sla_hours,
        }

    def create_task(self, request: LegalTaskCreateRequest) -> dict:
        sla_hours = self.legal_sla.get(request.event_type, 24)
        created_at = datetime.now(UTC)
        due_at = created_at + timedelta(hours=sla_hours)
        task_id = self._new_id("LTSK")

        derived_priority = request.priority or self._derive_priority(
            sla_hours=sla_hours,
            risk_level=request.risk_level,
        )
        derived_status = self._derive_status_by_risk(request.risk_level)

        task = {
            "task_id": task_id,
            "event_type": request.event_type,
            "target_id": request.target_id,
            "sla_hours": sla_hours,
            "created_by": request.created_by,
            "created_at": created_at.isoformat(),
            "due_at": due_at.isoformat(),
            "status": derived_status,
            "priority": derived_priority,
            "risk_level": request.risk_level,
        }
        self.legal_tasks[task_id] = task
        self._append_audit("legal.task.created", request.created_by, task_id, task)
        self._persist()
        return task

    def _derive_priority(self, *, sla_hours: int, risk_level: LegalRiskLevel | None) -> LegalTaskPriority:
        if risk_level == "high" or sla_hours <= 6:
            return "critical"
        if risk_level == "medium" or sla_hours <= 12:
            return "high"
        if sla_hours <= 24:
            return "medium"
        return "low"

    def _derive_status_by_risk(self, risk_level: LegalRiskLevel | None) -> str:
        if risk_level == "high":
            return "blocked"
        if risk_level == "medium":
            return "under_review"
        if risk_level == "low":
            return "approved"
        return "pending_legal"

    def list_tasks(self) -> dict:
        return {
            "total": len(self.legal_tasks),
            "tasks": sorted(self.legal_tasks.values(), key=lambda item: item["created_at"], reverse=True),
        }

    def kanban_snapshot(self) -> dict:
        now = datetime.now(UTC)
        columns = {
            "pending_legal": [],
            "under_review": [],
            "approved": [],
            "blocked": [],
        }

        for task in self.legal_tasks.values():
            stage = task.get("status", "pending_legal")
            if stage not in columns:
                continue
            due_at = datetime.fromisoformat(task["due_at"])
            enriched = {
                **task,
                "overdue": now > due_at and stage not in {"approved", "blocked"},
            }
            columns[stage].append(enriched)

        priorities = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        for task in self.legal_tasks.values():
            priority = task.get("priority", "medium")
            priorities[priority] = priorities.get(priority, 0) + 1

        return {
            "total": len(self.legal_tasks),
            "columns": columns,
            "priorities": priorities,
        }

    def auto_decide_task(self, request: LegalTaskAutoDecisionRequest) -> dict:
        risk = self.analyze_risk(
            RiskAnalysisRequest(
                operation_type=request.operation_type,
                deal_id=request.target_id,
                actors=request.actors,
                contract=request.contract,
                amount=request.amount,
                has_documents=request.has_documents,
                user_age_days=request.user_age_days,
            )
        )

        decision = "AUTO_APPROVE"
        if risk["risk_level"] == "high":
            decision = "BLOCK"
        elif risk["risk_level"] == "medium":
            decision = "REVIEW"

        task = self.create_task(
            LegalTaskCreateRequest(
                event_type=request.event_type,
                target_id=request.target_id,
                created_by=request.created_by,
                risk_level=risk["risk_level"],
                priority=None,
            )
        )
        task["auto_decision"] = decision
        task["decision_confidence"] = risk["confidence"]

        if decision == "BLOCK":
            self._emit_notification(
                "task_blocked",
                "Task juridica bloqueada automaticamente",
                {"task_id": task["task_id"], "target_id": request.target_id},
            )
        elif decision == "REVIEW":
            self._emit_notification(
                "task_review",
                "Task juridica enviada para revisao",
                {"task_id": task["task_id"], "target_id": request.target_id},
            )

        self._append_audit(
            "legal.task.auto_decided",
            request.created_by,
            task["task_id"],
            {"decision": decision, "risk": risk},
        )
        self.legal_tasks[task["task_id"]] = task
        self._persist()

        return {
            "task": task,
            "decision": decision,
            "risk": risk,
        }

    def update_task_stage(self, task_id: str, request: KanbanStageUpdateRequest) -> dict:
        task = self.legal_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        task["status"] = request.stage
        task["updated_at"] = utc_now_iso()
        if request.reason:
            task["reason"] = request.reason
        self._append_audit("legal.task.stage_changed", request.actor_id, task_id, task)
        self._persist()
        return task

    def create_override(self, request: OverrideRequest) -> dict:
        if request.approver_one == request.approver_two:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="approvers must be distinct")
        if request.requested_by in {request.approver_one, request.approver_two}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="requester cannot approve own override",
            )

        override = {
            "override_id": self._new_id("OVR"),
            "rule_code": request.rule_code,
            "target_id": request.target_id,
            "reason": request.reason,
            "requested_by": request.requested_by,
            "approvals": [request.approver_one, request.approver_two],
            "status": "approved",
            "created_at": utc_now_iso(),
        }
        self.legal_overrides.append(override)
        self._append_audit("legal.override.approved", request.requested_by, override["override_id"], override)
        self._persist()
        return override

    def john_decision_engine(self, request: JohnDecisionRequest) -> dict:
        risk = self.analyze_risk(
            RiskAnalysisRequest(
                operation_type="john_legal_decision",
                deal_id=request.deal_id,
                actors=request.actors,
                contract=request.contract,
                amount=request.amount,
                has_documents=request.has_documents,
                user_age_days=request.user_age_days,
            )
        )
        if risk["risk_level"] == "high":
            action = "bloquear_venda"
        elif risk["risk_level"] == "medium":
            action = "exigir_contrato"
        else:
            action = "alertar_risco"

        response = {
            "deal_id": request.deal_id,
            "action": action,
            "risk": risk,
        }
        self._append_audit("john.legal.decision", "john", request.deal_id, response)
        self._persist()
        return response

    def create_learning(self, request: LegalLearningCreateRequest) -> dict:
        record = {
            "learning_id": self._new_id("LRN"),
            "pattern_type": request.pattern_type,
            "description": request.description,
            "source_id": request.source_id,
            "outcome": request.outcome,
            "created_at": utc_now_iso(),
        }
        self.legal_learning.append(record)
        self._append_audit("legal.learning.created", "system", record["learning_id"], record)
        self._persist()
        return record

    def list_learning(self) -> dict:
        return {
            "total": len(self.legal_learning),
            "items": self.legal_learning[-200:],
        }

    def list_notifications(self) -> dict:
        return {
            "total": len(self.notifications),
            "items": self.notifications[-300:],
        }

    def list_admin_contracts(self) -> dict:
        return self.list_contracts()

    def list_admin_risk(self) -> dict:
        return self.list_risk()

    def list_admin_audit(self) -> dict:
        return self.list_audit()

    def process_core_dna_decision(self, request: RiskAnalysisRequest) -> dict:
        analysis = self.analyze_risk(request)
        decision = {
            "type": "LEGAL_RISK_ANALYSIS",
            "data": {
                "deal_id": request.deal_id,
                "actors": request.actors,
                "contract": request.contract,
            },
            "decision": "block" if analysis["risk_level"] == "high" else "review" if analysis["risk_level"] == "medium" else "allow",
            "risk": analysis,
        }
        self._append_audit("core_dna.legal.decision", "system", request.deal_id or "n/a", decision)
        self._persist()
        return decision


legal_ecosystem_service = LegalEcosystemService()
