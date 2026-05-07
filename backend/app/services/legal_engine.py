from __future__ import annotations

from uuid import uuid4

from app.schemas import ChecklistItem, ContractAuditRequest, Finding, NormAlert, SPERequest


class LegalEngine:
    def create_spe(self, request: SPERequest) -> dict:
        protocol = f"SPE-{uuid4().hex[:8].upper()}"
        return {
            "status": "draft_created",
            "protocol": protocol,
            "spe": {
                "name": request.name,
                "partners": request.partners,
                "purpose": request.purpose,
                "recommended_model": "SPE",
            },
            "next_steps": [
                "Validar objeto social",
                "Separar documentação dos sócios",
                "Emitir checklist de registro",
            ],
        }

    def audit_contract(self, request: ContractAuditRequest) -> dict:
        content = request.content.lower()
        findings: list[Finding] = []

        if "multa" in content:
            findings.append(
                Finding(
                    category="equilibrio-contratual",
                    severity="high",
                    description="Cláusula de multa exige revisão para evitar desequilíbrio excessivo.",
                    recommendation="Definir multa proporcional e critérios objetivos de rescisão.",
                )
            )

        if "dados" in content or "lgpd" in content:
            findings.append(
                Finding(
                    category="privacidade",
                    severity="medium",
                    description="Trecho relacionado a dados pessoais requer governança compatível com LGPD.",
                    recommendation="Inserir base legal, finalidade e regras de retenção de dados.",
                )
            )

        if not findings:
            findings.append(
                Finding(
                    category="conformidade-geral",
                    severity="low",
                    description="Nenhum risco crítico textual foi detectado na triagem inicial.",
                    recommendation="Prosseguir com revisão humana final antes da assinatura.",
                )
            )

        severities = {item.severity for item in findings}
        risk_level = "high" if "high" in severities else "medium" if "medium" in severities else "low"

        return {
            "title": request.title,
            "risk_level": risk_level,
            "findings": [item.model_dump() for item in findings],
            "summary": "Análise preliminar concluída pelo John Jurídico.",
        }

    def get_norm_alerts(self) -> dict:
        alerts = [
            NormAlert(
                id="CVM-2026-01",
                title="Atualização de diretrizes para ofertas de ativos estruturados",
                impact="Revisar documentos de captação e suitability.",
                source="CVM",
                action="Atualizar minutas e fluxo de aprovação interna.",
            ),
            NormAlert(
                id="LGPD-2026-02",
                title="Reforço de boas práticas para retenção mínima de dados",
                impact="Reduzir exposição em cadastros comerciais e contratuais.",
                source="ANPD",
                action="Aplicar revisão de retenção e descarte no ecossistema.",
            ),
        ]
        return {"total": len(alerts), "alerts": [item.model_dump() for item in alerts]}

    def compliance_check(self, monolito_id: str) -> dict:
        checklist = [
            ChecklistItem(area="LGPD", status="ok", note="Base legal e consentimento revisados."),
            ChecklistItem(area="Trabalhista", status="ok", note="Rotinas críticas sem indícios de passivo imediato."),
            ChecklistItem(area="Contratual", status="attention", note="Minutas padrão exigem atualização anual."),
        ]
        status = "attention" if any(item.status == "attention" for item in checklist) else "approved"
        return {
            "monolito_id": monolito_id,
            "status": status,
            "checklist": [item.model_dump() for item in checklist],
        }


legal_engine = LegalEngine()
