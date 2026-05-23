from __future__ import annotations

from statistics import mean


class LegalMetricsRuntime:
    def __init__(self) -> None:
        self._contract_validation_latencies_ms: list[float] = []
        self._trust_scoring_latencies_ms: list[float] = []

    def record_contract_latency(self, latency_ms: float) -> None:
        self._contract_validation_latencies_ms.append(latency_ms)

    def record_trust_latency(self, latency_ms: float) -> None:
        self._trust_scoring_latencies_ms.append(latency_ms)

    def snapshot(self) -> dict:
        contract_avg = mean(self._contract_validation_latencies_ms) if self._contract_validation_latencies_ms else 0.0
        trust_avg = mean(self._trust_scoring_latencies_ms) if self._trust_scoring_latencies_ms else 0.0
        return {
            "contract_validation_latency_ms_avg": round(contract_avg, 4),
            "trust_scoring_latency_ms_avg": round(trust_avg, 4),
        }
