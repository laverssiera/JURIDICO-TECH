from time import perf_counter

from runtime.legal.governance.autonomous_contract_validation import AutonomousContractValidation
from runtime.legal.governance.civilization_legal_governance import CivilizationLegalGovernance
from runtime.legal.governance.sovereign_compliance_runtime import SovereignComplianceRuntime
from runtime.legal.trust.adaptive_legal_scoring import AdaptiveLegalScoring
from runtime.legal.trust.deterministic_legal_validation import DeterministicLegalValidation


def test_benchmark_contract_validation_latency():
    validator = AutonomousContractValidation()
    payload = {
        "type": "sovereign_contract",
        "parties": ["A", "B"],
        "clauses": ["compliance", "audit", "enforcement"],
    }

    start = perf_counter()
    for _ in range(1000):
        result = validator.validate(payload)
        assert result.valid is True
    elapsed = perf_counter() - start

    avg_latency_ms = (elapsed / 1000) * 1000
    assert avg_latency_ms < 5.0


def test_benchmark_compliance_federation_throughput():
    runtime = SovereignComplianceRuntime()
    payload = {
        "jurisdiction": "interplanetary",
        "risk_level": "medium",
        "policy_bundle": "baseline",
    }

    operations = 2000
    start = perf_counter()
    for _ in range(operations):
        runtime.validate(payload)
    elapsed = perf_counter() - start

    throughput = operations / elapsed if elapsed else float("inf")
    assert throughput > 2000


def test_benchmark_legal_synchronization_consistency():
    governance = CivilizationLegalGovernance()

    for index in range(1, 51):
        federation_id = f"federation-{index}"
        result = governance.synchronize(federation_id, ["earth", "orbital", "lunar"])
        assert result["synchronized"] is True

    snapshot = governance.snapshot()
    assert snapshot["legal_federation_consistency"] == 1.0


def test_benchmark_trust_scoring_latency():
    scoring = AdaptiveLegalScoring()

    start = perf_counter()
    for _ in range(3000):
        score = scoring.score({"compliance": 92, "integrity": 94, "continuity": 90, "risk": 15})
        assert score > 0
    elapsed = perf_counter() - start

    avg_latency_ms = (elapsed / 3000) * 1000
    assert avg_latency_ms < 2.0


def test_benchmark_deterministic_legal_integrity():
    deterministic = DeterministicLegalValidation()
    payload = {
        "contract_id": "SO-1",
        "clauses": ["c1", "c2", "c3"],
        "jurisdiction": "interplanetary",
    }

    expected = deterministic.fingerprint(payload)
    for _ in range(500):
        result = deterministic.validate(payload, expected_fingerprint=expected)
        assert result["deterministic_legal_validation"] is True
        assert result["fingerprint"] == expected
