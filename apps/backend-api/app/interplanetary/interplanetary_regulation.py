from __future__ import annotations


class InterplanetaryRegulationRuntime:
    def evaluate(self, operation: str) -> dict[str, object]:
        planetary_rules = {
            "mars_mining": {
                "requires_authorization": True,
                "environmental_risk": "high",
            },
            "lunar_extraction": {
                "requires_authorization": True,
                "environmental_risk": "medium",
            },
        }

        rule = planetary_rules.get(
            operation,
            {
                "requires_authorization": False,
                "environmental_risk": "low",
            },
        )

        return {
            "operation": operation,
            "compliance_required": rule["requires_authorization"],
            "risk": rule["environmental_risk"],
        }
