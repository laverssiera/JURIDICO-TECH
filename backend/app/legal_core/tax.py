"""
LICEU 6.0 — Domain: Tax Intelligence
SPEs, holdings, incorporações, RET, lucro presumido/real, SCP,
incentivos fiscais, ESG fiscal e compliance tributário.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class TaxRegime(str, Enum):
    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"
    RET = "ret"                   # Regime Especial de Tributação para incorporações
    SCP = "scp"                   # Sociedade em Conta de Participação

    IMUNE = "imune"


# Alíquotas indicativas (referência 2025/2026)
TAX_RATES: dict[str, dict] = {
    TaxRegime.SIMPLES_NACIONAL: {
        "IRPJ": 0.0, "CSLL": 0.0, "PIS": 0.0, "COFINS": 0.0,
        "note": "Unificado no DAS — tabelas Anexo I–V da LC 123/2006",
    },
    TaxRegime.LUCRO_PRESUMIDO: {
        "IRPJ": 0.15, "adicional_IRPJ": 0.10,  # sobre base presumida
        "CSLL": 0.09, "PIS": 0.0065, "COFINS": 0.03,
        "presuncao_construcao": 0.08,  # base de cálculo IRPJ construção
        "presuncao_servicos": 0.32,
    },
    TaxRegime.LUCRO_REAL: {
        "IRPJ": 0.15, "adicional_IRPJ": 0.10,  # sobre lucro real
        "CSLL": 0.09, "PIS": 0.0165, "COFINS": 0.076,  # não-cumulativo
        "deducoes_permitidas": True,
    },
    TaxRegime.RET: {
        "aliquota_unica": 0.04,  # 4% RB para imóveis residenciais
        "aliquota_minha_casa": 0.01,
        "note": "Patrimônio de afetação obrigatório — Lei 10.931/2004",
    },
    TaxRegime.SCP: {
        "IRPJ": 0.15, "CSLL": 0.09,
        "note": "SCP não tem personalidade jurídica; lucros tributados no sócio ostensivo",
    },
}

REGIME_CRITERIA: dict[str, dict] = {
    TaxRegime.SIMPLES_NACIONAL: {
        "max_receita_bruta_anual": 4_800_000,
        "nota": "Vedado para incorporadoras com patrimônio de afetação",
    },
    TaxRegime.LUCRO_PRESUMIDO: {
        "max_receita_bruta_anual": 78_000_000,
        "nota": "Mais simples; pode ser desvantajoso com muitos custos dedutíveis",
    },
    TaxRegime.LUCRO_REAL: {
        "min_receita_obrigatorio": 78_000_000,
        "nota": "Obrigatório acima de R$ 78M/ano; permite créditos PIS/COFINS",
    },
    TaxRegime.RET: {
        "requisito": "SPE com regime de afetação registrado",
        "nota": "Alíquota 4% sobre receita bruta — muito vantajoso para incorporação",
    },
}

# Impostos sobre construção / incorporação
CONSTRUCTION_TAXES: list[dict] = [
    {"sigla": "ISS", "base": "serviços", "rate_range": "2-5%", "competencia": "municipal"},
    {"sigla": "INSS/patronal", "base": "folha ou RB (desoneração)", "rate_range": "20% folha ou 4.5% RB", "competencia": "federal"},
    {"sigla": "FGTS", "base": "folha", "rate": "8%", "competencia": "federal"},
    {"sigla": "ITBI", "base": "transmissão imóvel", "rate_range": "2-3%", "competencia": "municipal"},
    {"sigla": "ITCMD", "base": "herança/doação", "rate_range": "2-8%", "competencia": "estadual"},
]

INCENTIVOS_FISCAIS: list[dict] = [
    {
        "id": "PAT",
        "nome": "Programa de Alimentação do Trabalhador",
        "beneficio": "Dedução IRPJ + isenção contribuições sobre o benefício",
        "base_legal": "Lei 6.321/1976",
    },
    {
        "id": "LEI_ROUANET",
        "nome": "Lei Rouanet — Incentivo à Cultura",
        "beneficio": "Dedução até 4% IRPJ",
        "base_legal": "Lei 8.313/1991",
    },
    {
        "id": "ESG_VERDE_AMARELO",
        "nome": "Incentivos ESG / Verde e Amarelo",
        "beneficio": "Desoneração contribuições e redução FGTS em contratos especiais",
        "base_legal": "MP 1.116/2022 e legislação ESG emergente",
    },
    {
        "id": "RET_MINHA_CASA",
        "nome": "RET Minha Casa Minha Vida",
        "beneficio": "Alíquota RET reduzida a 1% sobre receita bruta",
        "base_legal": "Lei 10.931/2004 art. 4° §4°",
    },
    {
        "id": "DESONERACAO_FOLHA",
        "nome": "Desoneração da Folha — Construção Civil",
        "beneficio": "Substituição INSS patronal 20% por CPRB 4,5% sobre receita bruta",
        "base_legal": "Lei 12.546/2011",
    },
]


class TaxIntelligenceDomain:
    def suggest_regime(
        self,
        annual_revenue: float,
        entity_type: str,
        has_patrimonio_afetacao: bool = False,
        high_deductible_costs: bool = False,
    ) -> dict:
        """John Tributário sugere o regime mais vantajoso."""
        suggestions: list[dict] = []

        if entity_type in ("spe_incorporacao",) and has_patrimonio_afetacao:
            suggestions.append({
                "regime": TaxRegime.RET,
                "score": 95,
                "rationale": "SPE com patrimônio de afetação: RET é altamente vantajoso (4% sobre RB).",
                "rates": TAX_RATES[TaxRegime.RET],
            })

        if annual_revenue <= 4_800_000 and entity_type not in ("incorporadora",):
            suggestions.append({
                "regime": TaxRegime.SIMPLES_NACIONAL,
                "score": 80,
                "rationale": "Receita dentro do teto do Simples. Carga simplificada.",
                "rates": TAX_RATES[TaxRegime.SIMPLES_NACIONAL],
            })

        if annual_revenue <= 78_000_000:
            score = 70 if not high_deductible_costs else 50
            suggestions.append({
                "regime": TaxRegime.LUCRO_PRESUMIDO,
                "score": score,
                "rationale": "Presumido: simples mas menos atrativo com altos custos dedutíveis.",
                "rates": TAX_RATES[TaxRegime.LUCRO_PRESUMIDO],
            })

        lreal_score = 60 if not high_deductible_costs else 85
        suggestions.append({
            "regime": TaxRegime.LUCRO_REAL,
            "score": lreal_score,
            "rationale": "Real: obrigatório acima de R$ 78M/ano; ideal quando custos dedutíveis são elevados.",
            "rates": TAX_RATES[TaxRegime.LUCRO_REAL],
        })

        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return {
            "entity_type": entity_type,
            "annual_revenue": annual_revenue,
            "recommended": suggestions[0]["regime"],
            "suggestions": suggestions,
            "evaluated_at": utc_now(),
        }

    def estimate_tax_burden(
        self,
        regime: str,
        annual_revenue: float,
        annual_profit: float | None = None,
        annual_cost: float | None = None,
    ) -> dict:
        """Estima carga tributária para o regime informado."""
        rates = TAX_RATES.get(regime, {})
        burden: dict[str, float] = {}

        if regime == TaxRegime.RET:
            burden["RET_4pct"] = annual_revenue * 0.04
            total = burden["RET_4pct"]
        elif regime == TaxRegime.LUCRO_PRESUMIDO:
            base = annual_revenue * rates.get("presuncao_construcao", 0.08)
            burden["IRPJ"] = base * rates.get("IRPJ", 0.15)
            burden["adicional_IRPJ"] = max(0.0, base - 240_000) * rates.get("adicional_IRPJ", 0.10)
            burden["CSLL"] = annual_revenue * 0.12 * rates.get("CSLL", 0.09)
            burden["PIS"] = annual_revenue * rates.get("PIS", 0.0065)
            burden["COFINS"] = annual_revenue * rates.get("COFINS", 0.03)
            total = sum(burden.values())
        elif regime == TaxRegime.LUCRO_REAL:
            profit = annual_profit or annual_revenue * 0.10
            burden["IRPJ"] = profit * rates.get("IRPJ", 0.15)
            burden["adicional_IRPJ"] = max(0.0, profit - 240_000) * 0.10
            burden["CSLL"] = profit * rates.get("CSLL", 0.09)
            cost = annual_cost or annual_revenue * 0.75
            burden["PIS_nao_cumulativo"] = max(0.0, (annual_revenue - cost) * rates.get("PIS", 0.0165))
            burden["COFINS_nao_cumulativo"] = max(0.0, (annual_revenue - cost) * rates.get("COFINS", 0.076))
            total = sum(burden.values())
        else:
            total = annual_revenue * 0.06  # Simples genérico
            burden["DAS"] = total

        effective_rate = total / annual_revenue if annual_revenue else 0
        return {
            "regime": regime,
            "annual_revenue": annual_revenue,
            "estimated_taxes": burden,
            "total_tax_burden": round(total, 2),
            "effective_rate_pct": round(effective_rate * 100, 2),
            "calculated_at": utc_now(),
        }

    def tax_risk_check(self, entity_data: dict) -> dict:
        """Verifica riscos tributários para a entidade."""
        issues = []
        score = 0
        if not entity_data.get("regime_tributario"):
            issues.append("Regime tributário não definido")
            score += 20
        if not entity_data.get("sped_contabil_em_dia"):
            issues.append("SPED Contábil pendente")
            score += 15
        if not entity_data.get("pgfn_certidao_ok"):
            issues.append("Certidão PGFN irregular ou vencida")
            score += 25
        if not entity_data.get("rfb_certidao_ok"):
            issues.append("Certidão RFB irregular ou vencida")
            score += 25
        if not entity_data.get("parcelamentos_regularizados"):
            issues.append("Parcelamentos tributários em aberto")
            score += 15
        return {
            "entity_id": entity_data.get("entity_id"),
            "tax_risk_score": min(score, 100),
            "issues": issues,
            "status": "ok" if score == 0 else ("crítico" if score >= 50 else "atenção"),
            "checked_at": utc_now(),
        }

    def list_incentivos(self) -> list[dict]:
        return INCENTIVOS_FISCAIS

    def list_construction_taxes(self) -> list[dict]:
        return CONSTRUCTION_TAXES
