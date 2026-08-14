from __future__ import annotations


class LitigationRiskRuntime:
    """Compute composite litigation risk score for governance monitoring."""

    def analyze(
        self,
        *,
        compliance_status: str,
        missing_controls: int,
        high_severity_claims: int,
        critical_regulation_findings: int,
    ) -> dict:
        score = 20
        if compliance_status != "approved":
            score += 25
        score += min(30, missing_controls * 10)
        score += min(30, high_severity_claims * 10)
        score += min(15, critical_regulation_findings * 5)
        normalized_score = min(100, score)

        if normalized_score >= 75:
            level = "high"
        elif normalized_score >= 45:
            level = "medium"
        else:
            level = "low"

        return {
            "risk_score": normalized_score,
            "risk_level": level,
        }
