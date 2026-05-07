"""Compliance scoring engine — evaluates entity against regulatory frameworks."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass


SCOPE_RULES: dict[str, list[dict]] = {
    "global": [
        {"rule": "GDPR Art. 30 — Registro de atividades de tratamento", "alert_type": "data_privacy", "weight": 15},
        {"rule": "ISO 37001 — Anti-suborno", "alert_type": "regulatory", "weight": 10},
        {"rule": "FCPA — Foreign Corrupt Practices Act", "alert_type": "regulatory", "weight": 10},
        {"rule": "ESG Nível 1 — Divulgação ambiental", "alert_type": "esg", "weight": 10},
    ],
    "brasil": [
        {"rule": "LGPD Art. 7 — Base legal de tratamento", "alert_type": "data_privacy", "weight": 20},
        {"rule": "Lei 12.846/2013 — Anti-corrupção", "alert_type": "regulatory", "weight": 15},
        {"rule": "NR-1 — Programa de Gerenciamento de Riscos", "alert_type": "labor", "weight": 10},
        {"rule": "CF Art. 195 — Contribuições sociais", "alert_type": "tax", "weight": 10},
        {"rule": "Decreto 9.571/2018 — Diretrizes para empresas", "alert_type": "esg", "weight": 10},
    ],
    "esg": [
        {"rule": "GRI 305 — Emissões de carbono", "alert_type": "esg", "weight": 20},
        {"rule": "ODS 8 — Trabalho decente e crescimento econômico", "alert_type": "esg", "weight": 15},
        {"rule": "TCFD — Divulgação de riscos climáticos", "alert_type": "esg", "weight": 15},
        {"rule": "SA8000 — Responsabilidade social", "alert_type": "labor", "weight": 10},
    ],
    "labor": [
        {"rule": "CLT Art. 156 — NR emitidas pelo MTE", "alert_type": "labor", "weight": 20},
        {"rule": "NR-17 — Ergonomia", "alert_type": "labor", "weight": 15},
        {"rule": "NR-6 — EPI obrigatório", "alert_type": "labor", "weight": 15},
        {"rule": "Lei 9.029/1995 — Práticas discriminatórias", "alert_type": "labor", "weight": 10},
    ],
    "tax": [
        {"rule": "Código Tributário Nacional — Art. 150", "alert_type": "tax", "weight": 20},
        {"rule": "SPED — Escrituração digital", "alert_type": "tax", "weight": 15},
        {"rule": "Simples Nacional / Lucro Real", "alert_type": "tax", "weight": 10},
    ],
}

SEVERITY_MATRIX = {
    "data_privacy": "high",
    "regulatory": "high",
    "esg": "medium",
    "labor": "medium",
    "tax": "high",
}


@dataclass
class Finding:
    rule: str
    alert_type: str
    severity: str
    passed: bool
    message: str


def run_compliance_engine(entity_id: str, scope: str) -> tuple[float, list[Finding]]:
    """
    Simulated compliance engine. In production, replace with real checks
    against regulatory databases, entity data, and policy configs.
    Returns (score 0-100, list[Finding]).
    """
    rules = SCOPE_RULES.get(scope, SCOPE_RULES["global"])
    findings: list[Finding] = []
    total_weight = sum(r["weight"] for r in rules)
    earned = 0.0

    for rule in rules:
        # Simulated pass/fail — in prod this calls real validators
        passed = random.random() > 0.35
        severity = SEVERITY_MATRIX.get(rule["alert_type"], "medium") if not passed else "low"
        msg = (
            f"✓ {rule['rule']} — conforme"
            if passed
            else f"✗ {rule['rule']} — não conforme para entidade {entity_id}"
        )
        findings.append(Finding(
            rule=rule["rule"],
            alert_type=rule["alert_type"],
            severity=severity,
            passed=passed,
            message=msg,
        ))
        if passed:
            earned += rule["weight"]

    score = round((earned / total_weight) * 100, 2) if total_weight else 0.0
    return score, findings
