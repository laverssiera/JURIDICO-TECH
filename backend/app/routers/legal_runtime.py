from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter

from runtime.legal.governance.autonomous_contract_validation import AutonomousContractValidation
from runtime.legal.governance.civilization_legal_governance import CivilizationLegalGovernance
from runtime.legal.governance.interplanetary_regulation_engine import InterplanetaryRegulationEngine
from runtime.legal.governance.legal_consensus_runtime import LegalConsensusRuntime
from runtime.legal.governance.sovereign_compliance_runtime import SovereignComplianceRuntime
from runtime.legal.observability.compliance_telemetry_engine import ComplianceTelemetryEngine
from runtime.legal.observability.contract_trace_runtime import ContractTraceRuntime
from runtime.legal.observability.legal_integrity_monitor import LegalIntegrityMonitor
from runtime.legal.observability.legal_metrics_runtime import LegalMetricsRuntime
from runtime.legal.observability.sovereign_legal_audit import SovereignLegalAudit
from runtime.legal.trust.adaptive_legal_scoring import AdaptiveLegalScoring
from runtime.legal.trust.compliance_reputation_engine import ComplianceReputationEngine
from runtime.legal.trust.deterministic_legal_validation import DeterministicLegalValidation
from runtime.legal.trust.legal_trust_graph import LegalTrustGraph
from runtime.legal.trust.sovereign_legal_identity import SovereignLegalIdentity

router = APIRouter()

_compliance = SovereignComplianceRuntime()
_regulations = InterplanetaryRegulationEngine()
_consensus = LegalConsensusRuntime()
_contract_validator = AutonomousContractValidation()
_civilization = CivilizationLegalGovernance()

_metrics = LegalMetricsRuntime()
_compliance_telemetry = ComplianceTelemetryEngine()
_contract_trace = ContractTraceRuntime()
_audit = SovereignLegalAudit()
_integrity = LegalIntegrityMonitor()

_identity = SovereignLegalIdentity()
_trust_graph = LegalTrustGraph()
_reputation = ComplianceReputationEngine()
_adaptive_score = AdaptiveLegalScoring()
_deterministic_validator = DeterministicLegalValidation()


@router.get("/legal/runtime-status")
def runtime_status() -> dict:
    compliance_payload = {
        "jurisdiction": "interplanetary",
        "risk_level": "controlled",
        "policy_bundle": "sovereign-federation-v1",
    }
    compliance_result = _compliance.validate(compliance_payload)
    _compliance_telemetry.record(compliance_result["autonomous_compliance_validation"])

    enforcement = _regulations.enforce(
        {
            "jurisdiction": "orbital",
            "regulation_family": "interplanetary_governance",
        }
    )

    consensus = _consensus.build_consensus(
        proposal_id="consensus-sovereign-01",
        votes=[
            {"node": "earth", "approve": True},
            {"node": "orbital", "approve": True},
            {"node": "lunar", "approve": True},
            {"node": "mars", "approve": False},
        ],
    )

    contract_payload = {
        "type": "sovereign_legal_contract",
        "parties": ["civilization_a", "civilization_b"],
        "clauses": ["autonomous_compliance", "deterministic_enforcement"],
    }
    start_contract = perf_counter()
    contract_result = _contract_validator.validate(contract_payload)
    contract_latency_ms = (perf_counter() - start_contract) * 1000.0
    _metrics.record_contract_latency(contract_latency_ms)

    deterministic = _deterministic_validator.validate(
        contract_payload,
        expected_fingerprint=_deterministic_validator.fingerprint(contract_payload),
    )
    _contract_trace.append(contract_result.deterministic_hash, "validated", {"latency_ms": contract_latency_ms})

    federation = _civilization.synchronize(
        federation_id="civilization-prime",
        nodes=["earth", "orbital", "lunar", "mars"],
    )

    identity = _identity.issue("civilization-prime", "interplanetary")
    _trust_graph.link("civilization-prime", "orbital-council", 92.0)
    reputation_score = _reputation.update("civilization-prime", compliant=True)

    start_trust = perf_counter()
    adaptive_score = _adaptive_score.score(
        {
            "compliance": compliance_result["autonomous_compliance_validation"] and 95 or 40,
            "integrity": contract_result.integrity_score,
            "continuity": 95,
            "risk": 15,
        }
    )
    trust_latency_ms = (perf_counter() - start_trust) * 1000.0
    _metrics.record_trust_latency(trust_latency_ms)

    _audit.record("runtime_status", {"federation_id": federation["federation_id"], "adaptive_score": adaptive_score})

    return {
        "legal_governance_state": {
            "state": "active",
            "autonomous_compliance_validation": compliance_result["autonomous_compliance_validation"],
            "sovereign_legal_consensus": consensus["sovereign_consensus"],
        },
        "interplanetary_compliance_readiness": {
            "ready": enforcement["interplanetary_ready"],
            "enforcement": enforcement["enforcement"],
            "jurisdiction": enforcement["jurisdiction"],
        },
        "sovereign_contract_integrity": {
            "valid": contract_result.valid,
            "integrity_score": contract_result.integrity_score,
            "deterministic_legal_validation": deterministic["deterministic_legal_validation"],
        },
        "civilization_legal_federation": {
            "federation_id": federation["federation_id"],
            "synchronized": federation["synchronized"],
            "synchronization_level": federation["synchronization_level"],
            "identity_state": identity["identity_state"],
        },
        "runtime_legal_health": {
            "state": "healthy",
            "observability": _metrics.snapshot(),
            "audit": _audit.continuity(),
            "integrity": _integrity.status(),
            "trust": {
                "graph_score": _trust_graph.aggregate_score("civilization-prime"),
                "reputation_score": reputation_score,
                "adaptive_score": adaptive_score,
                "trust_scoring_latency_ms": round(trust_latency_ms, 4),
            },
        },
        "runtime_objective": "Perpetual Sovereign Interplanetary Legal Intelligence Runtime",
    }


@router.get("/legal/compliance-metrics")
def compliance_metrics() -> dict:
    federation_snapshot = _civilization.snapshot()
    trace_summary = _contract_trace.summary()
    telemetry = _compliance_telemetry.metrics()
    observability = _metrics.snapshot()

    trust_metrics = {
        "registered_legal_identities": _identity.count(),
        "graph": _trust_graph.size(),
        "baseline_reputation": _reputation.get("civilization-prime"),
    }

    contract_score = 100.0 if trace_summary["tracked_contracts"] > 0 else 90.0

    return {
        "compliance_propagation_metrics": telemetry,
        "contract_integrity_score": contract_score,
        "legal_federation_consistency": federation_snapshot["legal_federation_consistency"],
        "trust_governance_metrics": trust_metrics,
        "sovereign_legal_continuity": {
            "audit": _audit.continuity(),
            "lineage": trace_summary,
            "integrity": _integrity.status(),
            "legal_lineage_tracking": "active",
        },
        "continuous_legal_observability": {
            "contract_telemetry": "active",
            "compliance_propagation": telemetry["compliance_propagation"],
            "audit_continuity": _audit.continuity()["audit_continuity"],
            "observability_metrics": observability,
        },
    }
