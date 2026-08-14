class ClauseEngine:
    async def analyze_clause(self, clause: str) -> dict[str, int | str]:
        return {
            "risk_score": 31,
            "litigation_probability": 18,
            "recommendation": "Adicionar clausula de retencao",
            "clause_preview": clause[:80],
        }
