from __future__ import annotations


class AdaptiveLegalScoring:
    def score(self, payload: dict) -> float:
        compliance = float(payload.get("compliance", 80.0))
        integrity = float(payload.get("integrity", 80.0))
        continuity = float(payload.get("continuity", 80.0))
        risk = float(payload.get("risk", 20.0))
        blended = (compliance * 0.35) + (integrity * 0.35) + (continuity * 0.2) - (risk * 0.1)
        return round(max(0.0, min(100.0, blended)), 4)
