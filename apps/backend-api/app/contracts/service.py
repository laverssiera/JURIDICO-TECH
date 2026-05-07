from uuid import uuid4

from app.ai.clause_engine import ClauseEngine
from app.db.models import LegalClause
from app.db.models import LegalContract


class ContractService:
    @staticmethod
    def estimate_risk(content: str) -> float:
        lowered = content.lower()
        risk = 10.0

        triggers = {
            "multa": 8,
            "rescisao unilateral": 12,
            "sem lgpd": 10,
            "embargo": 15,
            "trabalhista": 7,
            "ambiental": 9,
            "nr18": 6,
        }

        for term, points in triggers.items():
            if term in lowered:
                risk += points

        return min(risk, 100.0)

    @staticmethod
    def build_contract(title: str, contract_type: str, content: str, tenant_id: str | None) -> LegalContract:
        return LegalContract(
            id=str(uuid4()),
            contract_number=f"CTR-{str(uuid4())[:8].upper()}",
            title=title,
            contract_type=contract_type,
            status="created",
            tenant_id=tenant_id,
            risk_score=ContractService.estimate_risk(content),
            content=content,
        )


class ClauseService:
    def __init__(self) -> None:
        self.engine = ClauseEngine()

    async def build_clause(self, contract_id: str, clause_type: str, clause_text: str) -> tuple[LegalClause, str]:
        analysis = await self.engine.analyze_clause(clause_text)
        risk_score = float(analysis["risk_score"])
        litigation_probability = float(analysis["litigation_probability"])
        recommendation = str(analysis["recommendation"])

        clause = LegalClause(
            id=str(uuid4()),
            contract_id=contract_id,
            clause_type=clause_type,
            clause_text=clause_text,
            litigation_score=litigation_probability,
            recommended=risk_score <= 35,
        )
        return clause, recommendation
