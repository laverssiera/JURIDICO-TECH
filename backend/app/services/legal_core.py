from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4

from fastapi import HTTPException, status

from app.integration.event_bus import event_bus
from app.services.legal_store import legal_core_store
from app.schemas import (
    AuditEventRequest,
    BypassDetectionRequest,
    ComplianceCheckRequest,
    ContractCreateRequest,
    ContractLifecycleActionRequest,
    ContractSignRequest,
    ContractVersionRequest,
    DisputeRequest,
    JohnRiskRequest,
    LegalDecisionRequest,
    LegalEventRequest,
    LegalGateRequest,
    LegalLockRequest,
    LegalValidateRequest,
    MatchProposalRequest,
    PaymentAuthorizationRequest,
)


UTC = timezone.utc


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class LegalCoreEngine:
    def __init__(self) -> None:
        self.contracts: dict[str, dict] = legal_core_store.load("contracts", {})
        graph_payload = legal_core_store.load("relationship_graph", {})
        self.relationship_graph: dict[str, set[str]] = {
            key: set(value)
            for key, value in graph_payload.items()
        }
        self.audit_trail: list[dict] = legal_core_store.load("audit_trail", [])
        self.fraud_flags: list[dict] = legal_core_store.load("fraud_flags", [])
        self.blocked_deals: set[str] = set(legal_core_store.load("blocked_deals", []))
        self.commissions: dict[str, dict] = legal_core_store.load("commissions", {})
        self.locks: dict[str, list[dict]] = legal_core_store.load("locks", {})
        self.decisions: dict[str, dict] = legal_core_store.load("decisions", {})

        self.state_transitions: dict[str, set[str]] = {
            "draft": {"generated", "rejected", "breached"},
            "generated": {"sent", "rejected", "breached"},
            "sent": {"signed", "rejected", "breached"},
            "signed": {"locked", "breached"},
            "locked": {"executed", "breached"},
            "executed": set(),
            "rejected": set(),
            "breached": set(),
        }

        self.permissions: dict[str, set[str]] = {
            "LEGAL_ADMIN": {
                "contract.create",
                "contract.approve",
                "contract.sign",
                "contract.lock",
            },
            "LEGAL_OPERATOR": {
                "contract.create",
                "contract.approve",
                "contract.sign",
            },
            "AUDITOR": set(),
        }

    def _persist_all(self) -> None:
        legal_core_store.save("contracts", self.contracts)
        legal_core_store.save(
            "relationship_graph",
            {key: sorted(value) for key, value in self.relationship_graph.items()},
        )
        legal_core_store.save("audit_trail", self.audit_trail[-5000:])
        legal_core_store.save("fraud_flags", self.fraud_flags[-1000:])
        legal_core_store.save("blocked_deals", sorted(self.blocked_deals))
        legal_core_store.save("commissions", self.commissions)
        legal_core_store.save("locks", self.locks)
        legal_core_store.save("decisions", self.decisions)

    def _entity_contracts(
        self,
        *,
        entity_id: str | None = None,
        lead_id: str | None = None,
        deal_id: str | None = None,
        property_id: str | None = None,
    ) -> list[dict]:
        matches: list[dict] = []
        for contract in self.contracts.values():
            if lead_id and contract["lead_id"] != lead_id:
                continue
            if deal_id and contract["deal_id"] != deal_id:
                continue
            if property_id and contract["property_id"] != property_id:
                continue
            if entity_id and entity_id not in {
                contract["contract_id"],
                contract["lead_id"],
                contract["deal_id"],
                contract["property_id"],
            }:
                continue
            matches.append(contract)
        return matches

    def _signed_contract_exists(self, contracts: list[dict], contract_type: str) -> bool:
        return any(
            contract_type in contract["contract_type"]
            and contract["state"] in {"signed", "locked", "executed"}
            for contract in contracts
        )

    def _active_locks_for_entity(self, entity_id: str) -> list[dict]:
        return [lock for lock in self.locks.get(entity_id, []) if lock.get("active")]

    def _contract_purpose_label(self, contract_type: str) -> str:
        labels = {
            "nda": "Confidencialidade",
            "non_circ": "Nao Circunvencao",
            "intermediation": "Intermediacao",
            "final": "Fechamento contratual",
            "proposal": "Proposta comercial",
        }
        return labels.get(contract_type, contract_type)

    def _blocked_by_lock(self, entity_id: str, action: str) -> dict | None:
        action_lock_map = {
            "view_property": {"view", "all"},
            "create_deal": {"execute", "edit", "all"},
            "close_sale": {"execute", "all"},
            "edit_deal": {"edit", "all"},
            "authorize_payment": {"payment", "execute", "all"},
        }
        expected_types = action_lock_map.get(action, {"all"})
        for lock in self._active_locks_for_entity(entity_id):
            if lock["lock_type"] in expected_types:
                return lock
        return None

    def _hash_payload(self, payload: dict, previous_hash: str | None = None) -> str:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        base = f"{serialized}|{previous_hash or ''}".encode("utf-8")
        return hashlib.sha256(base).hexdigest()

    def _publish(self, event_name: str, payload: dict) -> None:
        event_bus.publish(event_name, payload)
        self.audit_trail.append(
            {
                "timestamp": utc_now_iso(),
                "event": event_name,
                "payload": payload,
            }
        )
        self._persist_all()

    def _require_permission(self, role: str, permission: str) -> None:
        role_permissions = self.permissions.get(role, set())
        if permission not in role_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {role} cannot perform {permission}",
            )

    def _assert_transition(self, current_state: str, target_state: str) -> None:
        if target_state not in self.state_transitions.get(current_state, set()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid transition {current_state} -> {target_state}",
            )

    def _link_entities(self, entities: list[str]) -> None:
        unique = [entity for entity in entities if entity]
        for entity in unique:
            self.relationship_graph.setdefault(entity, set())
        for source in unique:
            for target in unique:
                if source != target:
                    self.relationship_graph[source].add(target)
        self._persist_all()

    def _add_version(self, contract: dict, payload: dict, author_id: str, reason: str) -> dict:
        previous_hash = contract["versions"][-1]["content_hash"] if contract["versions"] else None
        content_hash = self._hash_payload(payload, previous_hash)
        version = {
            "version": len(contract["versions"]) + 1,
            "content_hash": content_hash,
            "payload": payload,
            "author_id": author_id,
            "reason": reason,
            "created_at": utc_now_iso(),
        }
        contract["versions"].append(version)
        contract["current_hash"] = content_hash
        contract["updated_at"] = utc_now_iso()
        self._persist_all()
        return version

    def _update_state(self, contract_id: str, new_state: str, event_name: str, metadata: dict | None = None) -> dict:
        contract = self.get_contract(contract_id)
        self._assert_transition(contract["state"], new_state)
        contract["state"] = new_state
        contract["updated_at"] = utc_now_iso()
        metadata_payload = metadata or {}
        event_payload = {
            "contract_id": contract_id,
            "state": new_state,
            "lead_id": contract["lead_id"],
            "deal_id": contract["deal_id"],
            "property_id": contract["property_id"],
            "metadata": metadata_payload,
        }
        event_payload.update(metadata_payload)
        self._publish(event_name, event_payload)
        return contract

    def create_contract(self, request: ContractCreateRequest) -> dict:
        contract_id = f"CTR-{uuid4().hex[:10].upper()}"
        contract = {
            "contract_id": contract_id,
            "title": request.title,
            "contract_type": request.contract_type,
            "lead_id": request.lead_id,
            "deal_id": request.deal_id,
            "property_id": request.property_id,
            "involved_users": request.involved_users,
            "created_by": request.created_by,
            "template_context": request.template_context,
            "broker_id": request.broker_id,
            "owner_id": request.owner_id,
            "commission_amount": request.commission_amount,
            "state": "draft",
            "locked": False,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "versions": [],
            "events": [],
            "digital_signatures": [],
        }
        self._add_version(
            contract,
            {
                "title": contract["title"],
                "contract_type": contract["contract_type"],
                "template_context": contract["template_context"],
                "lead_id": contract["lead_id"],
                "deal_id": contract["deal_id"],
                "property_id": contract["property_id"],
            },
            request.created_by,
            "initial",
        )
        self.contracts[contract_id] = contract

        entities = [request.lead_id, request.deal_id, request.property_id] + request.involved_users
        if request.broker_id:
            entities.append(request.broker_id)
        if request.owner_id:
            entities.append(request.owner_id)
        self._link_entities(entities)

        self._publish(
            "contract.created",
            {
                "contract_id": contract_id,
                "lead_id": request.lead_id,
                "deal_id": request.deal_id,
                "property_id": request.property_id,
                "users": request.involved_users,
            },
        )
        contract["events"].append({"event": "contract.created", "timestamp": utc_now_iso()})
        self._persist_all()
        return contract

    def get_contract(self, contract_id: str) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        return contract

    def get_contract_status(self, contract_id: str) -> dict:
        contract = self.get_contract(contract_id)
        return {
            "contract_id": contract["contract_id"],
            "state": contract["state"],
            "locked": contract["locked"],
            "current_hash": contract["current_hash"],
            "version": len(contract["versions"]),
        }

    def version_contract(self, contract_id: str, request: ContractVersionRequest) -> dict:
        contract = self.get_contract(contract_id)
        if contract["state"] in {"locked", "executed", "breached"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Locked/executed/breached contracts are not editable",
            )

        updated_payload = deepcopy(contract["versions"][-1]["payload"])
        updated_payload.update(request.changes)
        version = self._add_version(contract, updated_payload, request.author_id, request.reason)
        self._publish(
            "contract.versioned",
            {
                "contract_id": contract_id,
                "version": version["version"],
                "reason": request.reason,
            },
        )
        return {
            "contract_id": contract_id,
            "version": version["version"],
            "current_hash": contract["current_hash"],
            "diff": request.changes,
        }

    def rollback_contract(self, contract_id: str, target_version: int, actor_id: str) -> dict:
        contract = self.get_contract(contract_id)
        if contract["state"] in {"locked", "executed", "breached"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot rollback locked/executed/breached contracts",
            )
        if target_version < 1 or target_version > len(contract["versions"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target version")

        payload = deepcopy(contract["versions"][target_version - 1]["payload"])
        version = self._add_version(contract, payload, actor_id, f"rollback_to_{target_version}")
        self._publish(
            "contract.versioned",
            {
                "contract_id": contract_id,
                "version": version["version"],
                "reason": f"rollback_to_{target_version}",
            },
        )
        return {
            "contract_id": contract_id,
            "rolled_back_to": target_version,
            "new_version": version["version"],
            "current_hash": contract["current_hash"],
        }

    def generate_contract(self, contract_id: str, request: ContractLifecycleActionRequest) -> dict:
        self._require_permission(request.role, "contract.approve")
        contract = self._update_state(
            contract_id,
            "generated",
            "contract.generated",
            {"actor_id": request.actor_id},
        )
        return {
            "contract_id": contract_id,
            "state": contract["state"],
            "template": self.render_template(contract_id),
        }

    def send_contract(self, contract_id: str, request: ContractLifecycleActionRequest) -> dict:
        self._require_permission(request.role, "contract.approve")
        contract = self._update_state(
            contract_id,
            "sent",
            "contract.sent",
            {"actor_id": request.actor_id},
        )
        return {
            "contract_id": contract_id,
            "state": contract["state"],
        }

    def sign_contract(self, contract_id: str, request: ContractSignRequest) -> dict:
        self._require_permission(request.role, "contract.sign")
        contract = self.get_contract(contract_id)
        contract = self._update_state(
            contract_id,
            "signed",
            "contract.signed",
            {
                "actor_id": request.actor_id,
                "monolito_id": "backoffice",
                "spe_name": contract["title"],
                "partners": contract["involved_users"],
                "purpose": self._contract_purpose_label(contract["contract_type"]),
            },
        )
        signature_payload = {
            "ip": request.ip,
            "timestamp": utc_now_iso(),
            "provider": request.signature_provider,
            "hash": self._hash_payload({"contract_id": contract_id, "actor_id": request.actor_id, "ip": request.ip}),
        }
        contract["digital_signatures"].append(signature_payload)
        self._persist_all()
        return {
            "contract_id": contract_id,
            "state": contract["state"],
            "signature": signature_payload,
        }

    def lock_contract(self, contract_id: str, request: ContractLifecycleActionRequest) -> dict:
        self._require_permission(request.role, "contract.lock")
        contract = self._update_state(
            contract_id,
            "locked",
            "contract.locked",
            {"actor_id": request.actor_id},
        )
        contract["locked"] = True
        self._persist_all()
        return {
            "contract_id": contract_id,
            "state": contract["state"],
            "locked": True,
        }

    def execute_contract(self, contract_id: str, request: ContractLifecycleActionRequest) -> dict:
        self._require_permission(request.role, "contract.approve")
        contract = self._update_state(
            contract_id,
            "executed",
            "contract.executed",
            {"actor_id": request.actor_id},
        )
        commission_value = contract.get("commission_amount") or 0.0
        self.commissions[contract_id] = {
            "contract_id": contract_id,
            "amount": commission_value,
            "status": "protected",
            "lead_id": contract["lead_id"],
            "deal_id": contract["deal_id"],
            "created_at": utc_now_iso(),
        }
        self._publish(
            "commission.protected",
            {
                "contract_id": contract_id,
                "amount": commission_value,
                "deal_id": contract["deal_id"],
            },
        )
        self._publish(
            "financial.execution.triggered",
            {
                "contract_id": contract_id,
                "deal_id": contract["deal_id"],
                "amount": commission_value,
            },
        )
        self._persist_all()
        return {
            "contract_id": contract_id,
            "state": contract["state"],
            "commission": self.commissions[contract_id],
        }

    def breach_contract(self, contract_id: str, request: ContractLifecycleActionRequest) -> dict:
        contract = self.get_contract(contract_id)
        if contract["state"] in {"executed", "rejected", "breached"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contract cannot be breached now")
        contract["state"] = "breached"
        contract["updated_at"] = utc_now_iso()
        self.blocked_deals.add(contract["deal_id"])
        self._publish(
            "contract.breached",
            {
                "contract_id": contract_id,
                "deal_id": contract["deal_id"],
                "actor_id": request.actor_id,
            },
        )
        self._publish(
            "system.global_alert",
            {
                "kind": "breach",
                "contract_id": contract_id,
                "deal_id": contract["deal_id"],
                "targets": ["broker", "legal", "admin"],
            },
        )
        self._persist_all()
        return {
            "contract_id": contract_id,
            "state": contract["state"],
            "blocked_deal": contract["deal_id"],
        }

    def render_template(self, contract_id: str) -> dict:
        contract = self.get_contract(contract_id)
        context = contract.get("template_context", {})
        template = {
            "header": f"{contract['contract_type']} - {contract['title']}",
            "property_type": context.get("property_type", "unknown"),
            "negotiation_type": context.get("negotiation_type", "unknown"),
            "deal_value": context.get("deal_value", "not_set"),
            "parties_profile": context.get("parties_profile", "standard"),
            "clauses": [
                "non_circunvention",
                "commission_protection",
                "data_protection",
            ],
        }
        return template

    def validate_gate(self, request: LegalValidateRequest) -> dict:
        if request.deal_id in self.blocked_deals:
            return {
                "action": request.action,
                "allowed": False,
                "reason": "deal_blocked_by_breach",
            }

        requirements = {
            "view_property": "nda",
            "create_deal": "intermediation",
            "close_sale": "final",
        }
        required_type = requirements.get(request.action)

        if not required_type:
            return {
                "action": request.action,
                "allowed": True,
                "reason": "no_specific_legal_gate",
            }

        valid_contract_found = False
        for contract in self.contracts.values():
            if request.lead_id and contract["lead_id"] != request.lead_id:
                continue
            if request.deal_id and contract["deal_id"] != request.deal_id:
                continue
            if request.property_id and contract["property_id"] != request.property_id:
                continue
            if required_type in contract["contract_type"] and contract["state"] in {"signed", "locked", "executed"}:
                valid_contract_found = True
                break

        return {
            "action": request.action,
            "allowed": valid_contract_found,
            "reason": "ok" if valid_contract_found else f"missing_{required_type}_contract",
        }

    def validate_action(self, request: LegalGateRequest) -> dict:
        blocking_lock = self._blocked_by_lock(request.entity_id, request.action)
        if blocking_lock:
            response = {
                "allowed": False,
                "reason": blocking_lock["reason"],
            }
            self._publish(
                "legal.blocked",
                {
                    "entity_id": request.entity_id,
                    "action": request.action,
                    "reason": blocking_lock["reason"],
                    "module": request.module,
                },
            )
            return response

        if request.deal_id in self.blocked_deals or request.entity_id in self.blocked_deals:
            return {
                "allowed": False,
                "reason": "Deal blocked by legal breach",
            }

        compliance = self.check_compliance(
            ComplianceCheckRequest(
                user_id=request.user_id,
                role=request.role,
                action=request.action,
                module=request.module,
                entity_id=request.entity_id,
                lead_id=request.lead_id,
                deal_id=request.deal_id,
                property_id=request.property_id,
            )
        )
        if not compliance["allowed"]:
            self._publish(
                "legal.blocked",
                {
                    "entity_id": request.entity_id,
                    "action": request.action,
                    "reason": compliance["reason"],
                    "module": request.module,
                },
            )
            return {
                "allowed": False,
                "reason": compliance["reason"],
            }

        self._publish(
            "legal.approved",
            {
                "entity_id": request.entity_id,
                "action": request.action,
                "module": request.module,
            },
        )
        return {
            "allowed": True,
            "reason": None,
        }

    def create_lock(self, request: LegalLockRequest) -> dict:
        lock = {
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
            "lock_type": request.lock_type,
            "reason": request.reason,
            "active": request.active,
            "created_by": request.created_by,
            "created_at": utc_now_iso(),
        }
        self.locks.setdefault(request.entity_id, [])
        self.locks[request.entity_id].append(lock)
        self._persist_all()
        if request.active:
            self._publish(
                "legal.blocked",
                {
                    "entity_id": request.entity_id,
                    "lock_type": request.lock_type,
                    "reason": request.reason,
                },
            )
        return lock

    def get_locks(self, entity_id: str) -> dict:
        locks = self.locks.get(entity_id, [])
        return {
            "entity_id": entity_id,
            "locks": locks,
        }

    def check_compliance(self, request: ComplianceCheckRequest) -> dict:
        contracts = self._entity_contracts(
            entity_id=request.entity_id,
            lead_id=request.lead_id,
            deal_id=request.deal_id,
            property_id=request.property_id,
        )
        rbac_allowed = request.role in {"LEGAL_ADMIN", "LEGAL_OPERATOR", "ADMIN_OPERACIONAL", "BROKER", "FINANCE"}
        nda_signed = self._signed_contract_exists(contracts, "nda")
        intermediation_signed = self._signed_contract_exists(contracts, "intermediation")

        reason = None
        if not rbac_allowed:
            reason = "RBAC permission denied"
        elif request.action in {"create_deal", "view_property"} and not nda_signed:
            reason = "Missing NDA or contract not signed"
        elif request.action in {"create_deal", "close_sale", "authorize_payment"} and not intermediation_signed:
            reason = "Missing intermediation contract"
        elif request.action in {"close_sale", "release_property"} and not request.property_documents_ok:
            reason = "Property documents are incomplete"

        return {
            "allowed": reason is None,
            "reason": reason,
            "checks": {
                "nda_signed": nda_signed,
                "intermediation_signed": intermediation_signed,
                "property_documents_ok": request.property_documents_ok,
                "rbac_allowed": rbac_allowed,
            },
        }

    def get_snapshot(self, entity_id: str) -> dict:
        contracts = self._entity_contracts(entity_id=entity_id)
        nda_signed = self._signed_contract_exists(contracts, "nda")
        contract_signed = any(contract["state"] in {"signed", "locked", "executed"} for contract in contracts)
        locks = self._active_locks_for_entity(entity_id)

        if entity_id in self.blocked_deals or locks:
            legal_status = "blocked"
        elif nda_signed and contract_signed:
            legal_status = "approved"
        else:
            legal_status = "pending"

        risk_level = "low" if legal_status == "approved" else "high" if legal_status == "blocked" else "medium"

        return {
            "entity_id": entity_id,
            "legal_status": legal_status,
            "nda_signed": nda_signed,
            "contract_signed": contract_signed,
            "risk_level": risk_level,
            "locks": locks,
        }

    def resolve_legal_decision(self, request: LegalDecisionRequest) -> dict:
        resolution = {
            "entity_id": request.entity_id,
            "conflict_type": request.conflict_type,
            "requested_by": request.requested_by,
            "resolved_at": utc_now_iso(),
        }
        if request.brokers and request.lead_id and request.deal_id and request.property_id:
            dispute_result = self.resolve_dispute(
                DisputeRequest(
                    lead_id=request.lead_id,
                    deal_id=request.deal_id,
                    property_id=request.property_id,
                    brokers=request.brokers,
                )
            )
            resolution.update(dispute_result)
        else:
            resolution["decision"] = "manual_legal_resolution_required"

        self.decisions[request.entity_id] = resolution
        self._persist_all()
        self._publish("legal.approved", resolution)
        return resolution

    def authorize_payment(self, request: PaymentAuthorizationRequest) -> dict:
        contracts = self._entity_contracts(entity_id=request.entity_id, deal_id=request.deal_id)
        if request.contract_id:
            contracts = [contract for contract in contracts if contract["contract_id"] == request.contract_id]

        signed_contract = next(
            (
                contract
                for contract in contracts
                if contract["state"] in {"signed", "locked", "executed"}
            ),
            None,
        )

        active_decision = self.decisions.get(request.entity_id) or self.decisions.get(request.deal_id)
        has_dispute_block = len({contract.get("broker_id") for contract in contracts if contract.get("broker_id")}) > 1 and not active_decision

        if not signed_contract:
            return {"allowed": False, "reason": "Contract not signed"}
        if (signed_contract.get("commission_amount") or 0) <= 0:
            return {"allowed": False, "reason": "Commission not defined"}
        if has_dispute_block:
            return {"allowed": False, "reason": "Active dispute blocks payment"}
        if self._blocked_by_lock(request.entity_id, "authorize_payment"):
            return {"allowed": False, "reason": "Payment locked by legal"}

        self._publish(
            "legal.approved",
            {
                "entity_id": request.entity_id,
                "action": "authorize_payment",
                "deal_id": request.deal_id,
            },
        )
        return {
            "allowed": True,
            "reason": None,
            "contract_id": signed_contract["contract_id"],
            "commission_amount": signed_contract.get("commission_amount") or 0,
        }

    def detect_bypass(self, request: BypassDetectionRequest) -> dict:
        lead_neighbors = self.relationship_graph.get(request.lead_id, set())
        suspicious_owner_path = request.owner_id is not None and request.owner_id in lead_neighbors and request.broker_id not in lead_neighbors
        missing_origin = request.deal_id not in lead_neighbors and request.property_id not in lead_neighbors
        suspicious = suspicious_owner_path or missing_origin

        if suspicious:
            self.blocked_deals.add(request.deal_id)
            payload = {
                "entity_id": request.entity_id,
                "deal_id": request.deal_id,
                "lead_id": request.lead_id,
                "property_id": request.property_id,
                "broker_id": request.broker_id,
                "source": request.source,
            }
            self._persist_all()
            self._publish("bypass.detected", payload)
            self._publish("legal.blocked", payload)
            return {
                "detected": True,
                "blocked": True,
                "reason": "Bypass detected in legal graph",
            }

        return {
            "detected": False,
            "blocked": False,
            "reason": None,
        }

    def consume_event(self, request: LegalEventRequest) -> dict:
        payload = request.payload
        if request.type == "lead_created":
            self._link_entities([payload.get("lead_id", ""), payload.get("broker_id", "")])
            self._publish("legal.approved", {"event": request.type, "lead_id": payload.get("lead_id")})
            return {"status": "processed", "event": request.type}

        if request.type == "deal_created":
            has_origin = bool(payload.get("lead_id"))
            if not has_origin:
                self._publish(
                    "legal.blocked",
                    {"event": request.type, "entity_id": payload.get("deal_id"), "reason": "deal_without_origin"},
                )
                return {"status": "blocked", "reason": "deal_without_origin"}

            contracts = self._entity_contracts(deal_id=payload.get("deal_id"), lead_id=payload.get("lead_id"))
            if not self._signed_contract_exists(contracts, "intermediation"):
                self._publish(
                    "contract.required",
                    {
                        "event": request.type,
                        "deal_id": payload.get("deal_id"),
                        "lead_id": payload.get("lead_id"),
                        "required_contract": "intermediation",
                    },
                )
                return {"status": "requires_contract", "required_contract": "intermediation"}

            self._publish("legal.approved", {"event": request.type, "deal_id": payload.get("deal_id")})
            return {"status": "approved", "event": request.type}

        if request.type in {"match_generated", "deal_won"}:
            result = self.process_match_or_proposal(
                MatchProposalRequest(
                    event_name=request.type,
                    lead_id=payload["lead_id"],
                    deal_id=payload["deal_id"],
                    property_id=payload["property_id"],
                    broker_id=payload["broker_id"],
                    owner_id=payload.get("owner_id"),
                    involved_users=payload.get("involved_users", []),
                    requested_by=payload.get("requested_by", payload["broker_id"]),
                )
            )
            return {"status": "processed", "event": request.type, "result": result}

        return {"status": "ignored", "event": request.type}

    def _auto_contract(self, contract_type: str, request: MatchProposalRequest) -> dict:
        auto = self.create_contract(
            ContractCreateRequest(
                title=f"Auto {contract_type} {request.deal_id}",
                contract_type=contract_type,
                lead_id=request.lead_id,
                deal_id=request.deal_id,
                property_id=request.property_id,
                involved_users=list(set(request.involved_users + [request.broker_id, request.requested_by])),
                created_by=request.requested_by,
                broker_id=request.broker_id,
                owner_id=request.owner_id,
            )
        )
        generated = self.generate_contract(
            auto["contract_id"],
            ContractLifecycleActionRequest(
                actor_id=request.requested_by,
                role="LEGAL_ADMIN",
                ip=None,
            ),
        )
        return {
            "contract_id": auto["contract_id"],
            "state": generated["state"],
            "type": contract_type,
        }

    def _detect_bypass(self, request: MatchProposalRequest) -> dict:
        lead_neighbors = self.relationship_graph.get(request.lead_id, set())
        known_broker_path = any(neighbor.startswith("BRK-") for neighbor in lead_neighbors)
        suspicious = known_broker_path and request.broker_id not in lead_neighbors
        if suspicious:
            self.blocked_deals.add(request.deal_id)
            payload = {
                "deal_id": request.deal_id,
                "lead_id": request.lead_id,
                "property_id": request.property_id,
                "broker_id": request.broker_id,
                "alerts": ["broker", "legal", "admin"],
            }
            self._publish("bypass.detected", payload)
            self._persist_all()
            return {
                "detected": True,
                "blocked": True,
                "payload": payload,
            }
        return {
            "detected": False,
            "blocked": False,
        }

    def process_match_or_proposal(self, request: MatchProposalRequest) -> dict:
        event_contract_map = {
            "match_generated": "nda",
            "simulation_done": "proposal",
            "deal_created": "intermediation",
            "deal_won": "final",
        }
        trigger_contract_type = event_contract_map[request.event_name]

        # Relationship graph is used as anti-bypass evidence and dispute resolution input.
        entities = [
            request.lead_id,
            request.deal_id,
            request.property_id,
            request.broker_id,
            request.owner_id or "",
        ] + request.involved_users
        self._link_entities([entity for entity in entities if entity])

        contracts = [
            self._auto_contract("nda", request),
            self._auto_contract("non_circ", request),
            self._auto_contract("intermediation", request),
        ]

        if trigger_contract_type == "final":
            contracts.append(self._auto_contract("final", request))

        bypass = self._detect_bypass(request)
        self._publish(
            request.event_name,
            {
                "lead_id": request.lead_id,
                "deal_id": request.deal_id,
                "property_id": request.property_id,
                "contracts": contracts,
            },
        )

        return {
            "event": request.event_name,
            "contracts": contracts,
            "bypass": bypass,
            "blocked": bypass["blocked"],
        }

    def resolve_dispute(self, request: DisputeRequest) -> dict:
        candidate_contracts = [
            contract
            for contract in self.contracts.values()
            if contract["deal_id"] == request.deal_id and contract["lead_id"] == request.lead_id
        ]
        candidate_contracts.sort(key=lambda contract: contract["created_at"])

        winner = None
        for contract in candidate_contracts:
            if contract.get("broker_id") in request.brokers and contract["state"] in {"signed", "locked", "executed"}:
                winner = contract.get("broker_id")
                break

        if not winner and candidate_contracts:
            winner = candidate_contracts[0].get("broker_id")

        return {
            "lead_id": request.lead_id,
            "deal_id": request.deal_id,
            "property_id": request.property_id,
            "winner_broker": winner,
            "criteria": ["event_order", "active_contracts", "relationship_graph"],
        }

    def get_relationships(self, entity_id: str) -> dict:
        return {
            "entity_id": entity_id,
            "connections": sorted(self.relationship_graph.get(entity_id, set())),
        }

    def assess_legal_risk(self, request: JohnRiskRequest) -> dict:
        score = 0
        reasons: list[str] = []

        if not request.has_nda:
            score += 3
            reasons.append("nda_missing")
        if not request.has_non_circ:
            score += 4
            reasons.append("non_circ_missing")
        if not request.has_intermediation:
            score += 4
            reasons.append("intermediation_missing")

        if request.document_inconsistencies:
            score += min(4, len(request.document_inconsistencies))
            reasons.append("document_inconsistency")

        if request.hours_to_expected_signature is not None and request.hours_to_expected_signature < 24:
            score += 2
            reasons.append("urgent_signature_timing")

        bypass_risk = request.owner_id and request.broker_id and request.owner_id in self.relationship_graph.get(request.lead_id, set())
        if bypass_risk:
            score += 4
            reasons.append("possible_bypass")

        if score >= 10:
            level = "high"
        elif score >= 6:
            level = "medium"
        else:
            level = "low"

        response = {
            "risk_level": level,
            "score": score,
            "reasons": reasons,
            "suggestions": [
                "Gerar NDA e Non-Circ antes de seguir",
                "Solicitar saneamento documental",
                "Antecipar assinatura digital com trilha completa",
            ],
        }

        if level in {"medium", "high"}:
            self._publish("legal.risk_detected", response)

        return response

    def append_audit(self, request: AuditEventRequest) -> dict:
        payload = {
            "timestamp": utc_now_iso(),
            "user_id": request.user_id,
            "action": request.action,
            "ip": request.ip,
            "identity_key": request.identity_key,
            "module": request.module,
            "entity_id": request.entity_id,
            "legal_status": request.legal_status,
        }
        self.audit_trail.append(payload)

        same_ip_different_identities = {
            event["identity_key"]
            for event in self.audit_trail
            if event.get("ip") == request.ip and event.get("identity_key")
        }

        if len(same_ip_different_identities) >= 3:
            flag = {
                "kind": "multi_identity",
                "ip": request.ip,
                "identities": sorted(same_ip_different_identities),
                "timestamp": utc_now_iso(),
            }
            self.fraud_flags.append(flag)

        self._persist_all()

        return {
            "status": "logged",
            "total_events": len(self.audit_trail),
            "fraud_flags": len(self.fraud_flags),
        }

    def list_audit(self) -> dict:
        return {
            "total": len(self.audit_trail),
            "events": self.audit_trail[-200:],
        }

    def list_fraud_flags(self) -> dict:
        return {
            "total": len(self.fraud_flags),
            "flags": self.fraud_flags,
        }


legal_core_engine = LegalCoreEngine()
