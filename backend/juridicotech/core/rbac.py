from __future__ import annotations

from fastapi import HTTPException, status


RBAC_RULES: dict[str, list[str]] = {
    "JURIDICO_MASTER": ["all"],
    "JURIDICO_ANALYST": ["read", "analyze", "create_contract", "sign_contract"],
    "AUDITOR": ["read", "audit"],
    "SYSTEM_AUTOMATION": ["create_contract", "sign_contract", "analyze", "events"],
}


def check_permission(user_role: str, action: str) -> bool:
    allowed_actions = RBAC_RULES.get(user_role, [])
    return "all" in allowed_actions or action in allowed_actions


def require_permission(user_role: str, action: str) -> None:
    if not check_permission(user_role, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {user_role} cannot perform {action}",
        )
