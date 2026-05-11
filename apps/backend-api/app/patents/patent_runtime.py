from __future__ import annotations


class PatentIntelligenceRuntime:
    def validate(self, research: dict[str, float]) -> dict[str, float | bool]:
        novelty = research["innovation_score"] * 0.6 + research["market_potential"] * 0.4

        return {
            "patentable": novelty > 0.85,
            "novelty_score": round(novelty, 4),
            "global_priority": novelty > 0.95,
        }
