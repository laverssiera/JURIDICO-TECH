from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status

from app.services.legal_store import legal_core_store

from runtime.legal.governance.claims_runtime import ClaimsRuntime
from runtime.legal.governance.compliance_runtime import ComplianceRuntime
from runtime.legal.governance.continental_legal_governance_runtime import ContinentalLegalGovernanceRuntime
from runtime.legal.governance.contract_generation_runtime import ContractGenerationRuntime
from runtime.legal.governance.global_compliance_runtime import GlobalComplianceRuntime
from runtime.legal.governance.litigation_risk_runtime import LitigationRiskRuntime
from runtime.legal.governance.regulatory_runtime import RegulatoryRuntime


class MissionLegalRuntime:
    """Orchestrates legal governance capabilities used by /legal endpoints."""

    def __init__(self) -> None:
        self._contract_generation = ContractGenerationRuntime()
        self._compliance = ComplianceRuntime()
        self._regulatory = RegulatoryRuntime()
        self._global_compliance = GlobalComplianceRuntime()
        self._continental = ContinentalLegalGovernanceRuntime()
        self._claims = ClaimsRuntime()
        self._litigation_risk = LitigationRiskRuntime()

    def generate_contract(
        self,
        *,
        contract_type: str,
        parties: list[str],
        objective: str,
        jurisdiction: str,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return self._contract_generation.generate(
            contract_type=contract_type,
            parties=parties,
            objective=objective,
            jurisdiction=jurisdiction,
            context=context,
        )

    def check_compliance(
        self,
        *,
        jurisdiction: str,
        contract_type: str,
        obligations: list[str],
        controls: dict[str, bool],
        frameworks: list[str] | None = None,
    ) -> dict[str, Any]:
        regulation = self._regulatory.evaluate(jurisdiction=jurisdiction, contract_type=contract_type)
        compliance = self._compliance.check(
            jurisdiction=jurisdiction,
            contract_type=contract_type,
            obligations=obligations,
            controls=controls,
        )
        global_compliance = self._global_compliance.validate_contract(
            {
                "jurisdiction": jurisdiction,
                "contract_type": contract_type,
                "frameworks": frameworks or [],
                "controls": controls,
            }
        )
        return {
            "compliance": compliance,
            "regulatory": regulation,
            "global_compliance": global_compliance,
        }

    def analyze_risk(
        self,
        *,
        jurisdiction: str,
        contract_type: str,
        obligations: list[str],
        controls: dict[str, bool],
        claims: list[dict[str, Any]],
    ) -> dict[str, Any]:
        compliance_bundle = self.check_compliance(
            jurisdiction=jurisdiction,
            contract_type=contract_type,
            obligations=obligations,
            controls=controls,
        )
        claims_summary = self._claims.analyze(claims)
        risk = self._litigation_risk.analyze(
            compliance_status=compliance_bundle["compliance"]["status"],
            missing_controls=len(compliance_bundle["compliance"]["missing_controls"]),
            high_severity_claims=claims_summary["high_severity_claims"],
            critical_regulation_findings=len(compliance_bundle["regulatory"]["critical_rules"]),
        )

        return {
            "risk": risk,
            "compliance": compliance_bundle["compliance"],
            "regulatory": compliance_bundle["regulatory"],
            "global_compliance": compliance_bundle["global_compliance"],
            "claims": claims_summary,
        }

    def assess_implications(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Assess the legal dimensions of an operation or change proposal."""
        dimensions = {
            "affected_contracts": payload.get("affected_contracts", []),
            "obligations": payload.get("obligations", []),
            "regulatory_risk": payload.get("regulatory_risk", False),
            "liability": payload.get("liability", False),
            "force_majeure": payload.get("force_majeure", False),
            "insurance": payload.get("insurance", False),
            "compliance": payload.get("compliance", False),
            "licensing": payload.get("licensing", False),
        }
        risk_points = 0
        required_actions: list[str] = []

        if dimensions["affected_contracts"]:
            risk_points += 15
            required_actions.append("Revisar contratos afetados e obrigações de notificação")
        if dimensions["obligations"]:
            risk_points += 10
            required_actions.append("Mapear obrigações vencidas, futuras e evidências de cumprimento")
        if self._implication_is_risky(dimensions["regulatory_risk"]):
            risk_points += 20
            required_actions.append("Obter parecer regulatório e atualizar o plano de adequação")
        if self._implication_is_risky(dimensions["liability"]):
            risk_points += 15
            required_actions.append("Delimitar responsabilidade, indenização e direito de regresso")
        if self._implication_is_risky(dimensions["force_majeure"]):
            risk_points += 10
            required_actions.append("Validar cláusula de força maior, nexo causal e dever de mitigação")
        if not self._implication_is_positive(dimensions["insurance"]):
            risk_points += 10
            required_actions.append("Confirmar cobertura, limites, exclusões e vigência dos seguros")
        if not self._implication_is_positive(dimensions["compliance"]):
            risk_points += 15
            required_actions.append("Executar controles de compliance e preservar trilha de auditoria")
        if not self._implication_is_positive(dimensions["licensing"]):
            risk_points += 15
            required_actions.append("Regularizar licenças, autorizações e condicionantes aplicáveis")

        risk_level = "critical" if risk_points >= 75 else "high" if risk_points >= 50 else "medium" if risk_points >= 25 else "low"
        legal_status = "blocked" if risk_level == "critical" else "pending" if risk_level in {"high", "medium"} else "approved"
        if not required_actions:
            required_actions.append("Manter monitoramento jurídico e revisão periódica")

        return {
            "legal_status": legal_status,
            "risk_level": risk_level,
            "required_actions": required_actions,
        }

    def assess_assurance(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Generate a draft and assess its compliance, liability and insurance posture."""
        contract = self.generate_contract(
            contract_type=payload["contract_type"],
            parties=payload.get("parties", []),
            objective=payload["objective"],
            jurisdiction=payload.get("jurisdiction", "BR"),
            context=payload.get("context", {}),
        )
        if not contract.get("generated"):
            return {"contract": contract, "decision": "blocked", "risk_level": "critical", "required_actions": ["Escolher um tipo de contrato suportado"]}

        compliance_bundle = self.check_compliance(
            jurisdiction=payload.get("jurisdiction", "BR"),
            contract_type=payload["contract_type"],
            obligations=payload.get("obligations", []),
            controls=payload.get("controls", {}),
            frameworks=payload.get("frameworks", []),
        )
        implications = self.assess_implications(
            {
                "affected_contracts": [contract["contract_id"]],
                "obligations": payload.get("obligations", []),
                "liability": payload.get("liability", False),
                "insurance": payload.get("insurance", False),
                "compliance": compliance_bundle["compliance"]["status"] == "approved",
            }
        )
        risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        compliance_risk = "low" if compliance_bundle["compliance"]["status"] == "approved" else "high"
        risk_level = max(compliance_risk, implications["risk_level"], key=risk_order.get)
        decision = "blocked" if risk_level == "critical" else "pending" if risk_level in {"medium", "high"} else "approved"
        return {
            "contract": contract,
            "compliance": compliance_bundle,
            "implications": implications,
            "decision": decision,
            "risk_level": risk_level,
            "required_actions": implications["required_actions"],
        }

    @staticmethod
    def _implication_is_risky(value: Any) -> bool:
        if isinstance(value, dict):
            return value.get("status", value.get("risk", False)) not in {False, None, "low", "LOW", "ok", "compliant"}
        if isinstance(value, str):
            return value.lower() in {"high", "critical", "medium", "alto", "crítico", "médio", "irregular", "true"}
        return bool(value)

    @staticmethod
    def _implication_is_positive(value: Any) -> bool:
        if isinstance(value, dict):
            return value.get("status", value.get("valid", value.get("covered", False))) in {True, "true", "valid", "ok", "compliant", "approved", "low"}
        if isinstance(value, str):
            return value.lower() in {"true", "valid", "ok", "compliant", "approved", "regular", "low"}
        return bool(value)

    def state(self) -> dict[str, Any]:
        return {
            "objective": "Governanca juridica",
            "capabilities": [
                "contract_generation_runtime.py",
                "compliance_runtime.py",
                "global_compliance_runtime.py",
                "regulatory_runtime.py",
                "continental_legal_governance_runtime.py",
                "continental_contract_runtime.py",
                "continental_regulatory_runtime.py",
                "continental_ip_runtime.py",
                "continental_compliance_runtime.py",
                "claims_runtime.py",
                "litigation_risk_runtime.py",
                "mission_legal_runtime.py",
            ],
            "contracts": self._contract_generation.supported_contracts(),
            "metrics": {
                "contract_generation": self._contract_generation.metrics(),
                "compliance": self._compliance.metrics(),
            },
        }

    def wave_43(self) -> dict[str, Any]:
        return {
            "wave": 43,
            "program": "JURIDICOTECH",
            "tracks": {
                "legal_state": {
                    "state_type": "legal_state_continental",
                    "endpoint": "/legal/continental/state",
                    "example_payload": {
                        "countries": ["BR", "PT"],
                        "contracts": [{"contract_id": "CTR-W43-001", "contract_type": "MSA"}],
                        "assets": [{"asset_id": "IP-W43-001", "type": "patent", "protected_in": ["BR"]}],
                        "controls": {"lgpd": True, "cross_border_transfer": True},
                    },
                },
                "contracts": {
                    "runtime": "continental_contract_runtime.py",
                    "focus": ["governing_law", "required_clauses", "cross_border_assessment"],
                    "example_payload": {"contract_id": "CTR-W43-001", "contract_type": "MSA", "operating_countries": ["BR", "PT"]},
                },
                "regulation": {
                    "runtime": "continental_regulatory_runtime.py",
                    "focus": ["country_bundles", "regulatory_conflicts", "rule_harmonization"],
                    "example_payload": {"countries": ["BR", "PT"], "sectors": ["infrastructure", "technology"]},
                },
                "ip": {
                    "runtime": "continental_ip_runtime.py",
                    "focus": ["protection_coverage", "protection_gaps", "coverage_ratio"],
                    "example_payload": {"asset_id": "IP-W43-001", "type": "patent", "protected_in": ["BR", "PT"]},
                },
                "compliance": {
                    "runtime": "continental_compliance_runtime.py",
                    "focus": ["required_rules", "missing_controls", "score"],
                    "example_payload": {"controls": {"lgpd": True, "gdpr": True, "cross_border_transfer": True}},
                },
            },
            "status": "active",
        }

    def wave_59(self) -> dict[str, Any]:
        return {
            "wave": 59,
            "program": "JURIDICOTECH",
            "tracks": {
                "contracts": {"focus": ["scope", "obligations", "remedies"]},
                "international_obligations": {"focus": ["treaties", "jurisdiction", "reporting"]},
                "regulatory_exposure": {"focus": ["applicable_rules", "licensing", "sanctions"]},
                "liability": {"focus": ["allocation", "indemnity", "recourse"]},
                "insurance": {"focus": ["coverage", "limits", "exclusions"]},
                "ip": {"focus": ["ownership", "licensing", "territorial_protection"]},
                "data_rights": {"focus": ["ownership", "access", "lawful_transfer"]},
                "cross_border_compliance": {"focus": ["transfer_controls", "screening", "auditability"]},
            },
            "evaluation_endpoint": "/legal/waves/59/evaluate",
            "status": "active",
        }

    def evaluate_wave_59(self, payload: dict[str, Any]) -> dict[str, Any]:
        dimensions = {
            "contracts": payload.get("contracts", False),
            "international_obligations": payload.get("international_obligations", False),
            "regulatory_exposure": payload.get("regulatory_exposure", False),
            "liability": payload.get("liability", False),
            "insurance": payload.get("insurance", False),
            "ip": payload.get("ip", False),
            "data_rights": payload.get("data_rights", False),
            "cross_border_compliance": payload.get("cross_border_compliance", False),
        }
        gaps = [name for name, value in dimensions.items() if not self._implication_is_positive(value)]
        score = round((len(dimensions) - len(gaps)) / len(dimensions) * 100, 2)
        risk_level = "low" if score == 100 else "medium" if score >= 75 else "high" if score >= 50 else "critical"
        return {
            "wave": 59,
            "status": "approved" if not gaps else "attention",
            "score": score,
            "risk_level": risk_level,
            "dimensions": dimensions,
            "gaps": gaps,
            "required_actions": [f"Avaliar o eixo {gap.replace('_', ' ')}" for gap in gaps],
        }

    def wave_70(self) -> dict[str, Any]:
        return {
            "wave": 70,
            "program": "JURIDICOTECH",
            "tracks": {
                "contracts": {"focus": ["scope", "obligations", "remedies"]},
                "compliance": {"focus": ["controls", "auditability", "monitoring"]},
                "liability": {"focus": ["allocation", "indemnity", "recourse"]},
                "insurance": {"focus": ["coverage", "limits", "exclusions"]},
                "regulatory_exposure": {"focus": ["applicable_rules", "licensing", "sanctions"]},
                "ip": {"focus": ["ownership", "licensing", "territorial_protection"]},
                "data_rights": {"focus": ["ownership", "access", "lawful_transfer"]},
                "cross_border_obligations": {"focus": ["jurisdiction", "transfer_controls", "reporting"]},
            },
            "validation_endpoint": "/legal/waves/70/validate",
            "status": "active",
        }

    def evaluate_wave_70(self, payload: dict[str, Any]) -> dict[str, Any]:
        dimensions = {
            "contracts": payload.get("contracts", False),
            "compliance": payload.get("compliance", False),
            "liability": payload.get("liability", False),
            "insurance": payload.get("insurance", False),
            "regulatory_exposure": payload.get("regulatory_exposure", False),
            "ip": payload.get("ip", False),
            "data_rights": payload.get("data_rights", False),
            "cross_border_obligations": payload.get("cross_border_obligations", False),
        }
        gaps = [name for name, value in dimensions.items() if not self._implication_is_positive(value)]
        score = round((len(dimensions) - len(gaps)) / len(dimensions) * 100, 2)
        risk_level = "low" if score == 100 else "medium" if score >= 75 else "high" if score >= 50 else "critical"
        legal_decision_id = f"LDEC-{uuid4().hex[:12].upper()}"
        return {
            "legal_decision_id": legal_decision_id,
            "wave": 70,
            "status": "approved" if not gaps else "attention",
            "score": score,
            "risk_level": risk_level,
            "dimensions": dimensions,
            "gaps": gaps,
            "required_actions": [f"Avaliar o eixo {gap.replace('_', ' ')}" for gap in gaps],
        }

    def evaluate_wave_84(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Consume a persisted W83 event and append a deterministic W84 assessment."""
        lineage = [
            "source_event_id",
            "trace_id",
            "decision_id",
            "governance_decision_id",
            "execution_id",
            "infrastructure_change_ids",
            "supplier_analysis_id",
            "procurement_plan_id",
            "economic_impact_id",
            "financial_exposure_id",
        ]
        if any(not payload.get(key) for key in lineage):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="W83 lineage must reach financial_exposure_id",
            )

        audit_events = legal_core_store.load("audit_trail", [])
        source_event = next(
            (
                event for event in audit_events
                if event.get("event_id") == payload["source_event_id"]
                and event.get("wave") == 83
            ),
            None,
        )
        if not source_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persisted W83 source_event_id was not found in the Event Store",
            )

        source_payload = source_event.get("payload", source_event)
        if source_payload.get("wave_lineage") != [79, 80, 81, 82, 83]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="W83 event is not causally linked to W79-W83",
            )
        if any(source_payload.get(key) != payload[key] for key in lineage[1:]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Submitted lineage does not match the persisted W83 event",
            )
        operational_validations = source_payload.get("validations", {})
        required_validations = ("replay", "idempotency", "rollback", "recovery", "audit")
        if any(operational_validations.get(name) is not True for name in required_validations):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="W83 event lacks required replay, rollback, recovery, and audit validation",
            )

        fingerprint_payload = {key: payload[key] for key in lineage}
        fingerprint_payload["legal_checks"] = payload.get("legal_checks", {})
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        assessments = legal_core_store.load("wave_84_assessments", {})
        existing = assessments.get(fingerprint)
        if existing:
            return existing["result"]

        legal_checks = payload.get("legal_checks", {})
        legal_fields = [
            "contract_valid",
            "compliance_valid",
            "regulatory_valid",
            "liability_valid",
            "insurance_valid",
        ]
        checks = {field: legal_checks.get(field, payload.get(field)) is True for field in legal_fields}
        legal_assessment_id = f"LASS-{fingerprint[:12].upper()}"
        result = {
            "wave": 84,
            "scope": "planetary",
            "origin": "JURIDICOTECH",
            **{key: payload[key] for key in lineage},
            "legal_assessment_id": legal_assessment_id,
            "contract_valid": checks["contract_valid"],
            "lineage_valid": True,
            "compliance_valid": checks["compliance_valid"],
            "regulatory_valid": checks["regulatory_valid"],
            "liability_valid": checks["liability_valid"],
            "insurance_valid": checks["insurance_valid"],
            "replay_valid": operational_validations["replay"],
            "idempotency_valid": operational_validations["idempotency"],
            "rollback_valid": operational_validations["rollback"],
            "recovery_valid": operational_validations["recovery"],
            "audit_valid": operational_validations["audit"],
            "status": "PASS" if all(checks.values()) else "FAIL",
        }
        assessments[fingerprint] = {
            "result": result,
            "source_event_id": payload["source_event_id"],
            "financial_exposure_id": payload["financial_exposure_id"],
        }
        legal_core_store.save("wave_84_assessments", assessments)
        audit_events.append(
            {
                "event_id": f"evt-w84-{fingerprint[:12]}",
                "event_type": "legal.assessment.completed",
                "wave": 84,
                "source_event_id": payload["source_event_id"],
                "trace_id": payload["trace_id"],
                "legal_assessment_id": legal_assessment_id,
                "payload": result,
            }
        )
        legal_core_store.save("audit_trail", audit_events[-5000:])
        return result

    def continental_state(self, **payload: Any) -> dict[str, Any]:
        return self._continental.build_state(**payload)
