from __future__ import annotations

from app.schemas import (
    BypassCheckRequest,
    BypassProtectRequest,
    ComplianceCheckRequest,
    ContractCreateV2Request,
    ContractSignV2Request,
    LegalGateRequest,
    PaymentAuthorizationRequest,
)
from app.services.legal_core import legal_core_engine
from app.services.legal_ecosystem import legal_ecosystem_service


class LegalAdapter:
    def validate_action(self, **kwargs) -> dict:
        return legal_core_engine.validate_action(LegalGateRequest(**kwargs))

    def check_compliance(self, **kwargs) -> dict:
        return legal_core_engine.check_compliance(ComplianceCheckRequest(**kwargs))

    def get_snapshot(self, entity_id: str) -> dict:
        return legal_core_engine.get_snapshot(entity_id)

    def authorize_payment(self, **kwargs) -> dict:
        return legal_core_engine.authorize_payment(PaymentAuthorizationRequest(**kwargs))

    # SDK global v2
    def create_contract(self, **kwargs) -> dict:
        return legal_ecosystem_service.create_contract(ContractCreateV2Request(**kwargs))

    def sign_contract(self, contract_id: str, **kwargs) -> dict:
        return legal_ecosystem_service.sign_contract(contract_id, ContractSignV2Request(**kwargs))

    def validate_contract(self, contract_id: str) -> dict:
        contract = legal_ecosystem_service.contracts.get(contract_id)
        if not contract:
            return {"valid": False, "reason": "contract_not_found"}
        return {
            "valid": contract["status"] in {"signed", "active", "completed"},
            "status": contract["status"],
            "contract_id": contract_id,
        }

    def check_bypass_risk(self, **kwargs) -> dict:
        return legal_ecosystem_service.check_bypass_risk(BypassCheckRequest(**kwargs))

    def protect_commission(self, **kwargs) -> dict:
        return legal_ecosystem_service.protect_commission(BypassProtectRequest(**kwargs))

    # aliases camelCase para SDK externo
    def createContract(self, **kwargs) -> dict:  # noqa: N802
        return self.create_contract(**kwargs)

    def signContract(self, contract_id: str, **kwargs) -> dict:  # noqa: N802
        return self.sign_contract(contract_id, **kwargs)

    def validateContract(self, contract_id: str) -> dict:  # noqa: N802
        return self.validate_contract(contract_id)

    def checkBypassRisk(self, **kwargs) -> dict:  # noqa: N802
        return self.check_bypass_risk(**kwargs)

    def protectCommission(self, **kwargs) -> dict:  # noqa: N802
        return self.protect_commission(**kwargs)


legal_adapter = LegalAdapter()
