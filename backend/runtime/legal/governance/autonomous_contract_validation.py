from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


@dataclass(slots=True)
class ContractValidationResult:
    deterministic_hash: str
    valid: bool
    integrity_score: float
    checks: list[str]


class AutonomousContractValidation:
    def _deterministic_hash(self, payload: dict) -> str:
        canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def validate(self, contract_payload: dict) -> ContractValidationResult:
        clauses = contract_payload.get("clauses") or []
        checks: list[str] = []

        has_parties = bool(contract_payload.get("parties"))
        if has_parties:
            checks.append("parties_present")

        has_clauses = isinstance(clauses, list) and len(clauses) > 0
        if has_clauses:
            checks.append("clauses_present")

        deterministic = self._deterministic_hash(contract_payload)
        checks.append("deterministic_hash_generated")

        valid = has_parties and has_clauses
        integrity_score = round((len(checks) / 3.0) * 100.0, 2)

        return ContractValidationResult(
            deterministic_hash=deterministic,
            valid=valid,
            integrity_score=integrity_score,
            checks=checks,
        )
