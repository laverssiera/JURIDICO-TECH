"""
LICEU 6.x — Universidade Jurídica LICEU
Treinamento jurídico para engenheiros, compradores, RH, fornecedores, diretores e investidores.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


TRACKS = {
    "engenheiros": ["NR-18", "Responsabilidade Técnica", "Vícios Construtivos"],
    "compradores": ["Due Diligence de Fornecedores", "Cláusulas de Garantia", "Compliance Contratual"],
    "rh": ["SST", "Assédio e Compliance", "LGPD Trabalhista"],
    "fornecedores": ["Compliance Operacional", "Documentação Fiscal", "Código de Conduta"],
    "diretores": ["Governança", "Risco Sistêmico", "Crisis Response"],
    "investidores": ["Estrutura SPE", "Risco Regulatório", "Tokenização e CVM"],
}


class LegalUniversityDomain:
    def __init__(self) -> None:
        self._enrollments: list[dict] = []

    def list_tracks(self) -> dict:
        return TRACKS

    def enroll(self, person_id: str, profile: str, track: str | None = None) -> dict:
        chosen_track = track or profile
        courses = TRACKS.get(chosen_track, [])
        enrollment = {
            "enrollment_id": f"UNI-{uuid4().hex[:8].upper()}",
            "person_id": person_id,
            "profile": profile,
            "track": chosen_track,
            "courses": courses,
            "status": "active",
            "enrolled_at": utc_now(),
        }
        self._enrollments.append(enrollment)
        return enrollment

    def list_enrollments(self, profile: str | None = None) -> list[dict]:
        if profile:
            return [e for e in self._enrollments if e["profile"] == profile]
        return self._enrollments
