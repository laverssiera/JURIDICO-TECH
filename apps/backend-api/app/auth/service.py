from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_utils import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    verify_password,
)
from app.auth.repository import RefreshTokenRepository, UserRepository
from app.auth.schemas import TokenResponse, UserCreate, UserResponse
from app.core.settings import settings
from app.db.models import User
from app.db.session import get_session

bearer_scheme = HTTPBearer()


class AuthService:
    def __init__(self, session) -> None:
        self.users = UserRepository(session)
        self.tokens = RefreshTokenRepository(session)

    async def register(self, data: UserCreate) -> UserResponse:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        user = await self.users.create(
            email=data.email,
            plain_password=data.password,
            role=data.role,
            tenant_id=data.tenant_id,
        )
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account inactive")

        access_token = create_access_token(user.id, user.email, user.role, user.tenant_id)
        raw_rt, _ = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        await self.tokens.create(user.id, raw_rt, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_rt,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def refresh(self, raw_refresh_token: str) -> TokenResponse:
        rt = await self.tokens.get_valid(raw_refresh_token)
        if not rt:
            raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

        user = await self.users.get_by_id(rt.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="User not found or inactive")

        # Rotate: revoke old, issue new
        await self.tokens.revoke(raw_refresh_token)
        access_token = create_access_token(user.id, user.email, user.role, user.tenant_id)
        raw_new, _ = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        await self.tokens.create(user.id, raw_new, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_new,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(self, raw_refresh_token: str) -> None:
        await self.tokens.revoke(raw_refresh_token)


# ── Dependency: get current user from Bearer token ────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session=Depends(get_session),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Not an access token")

    user = await UserRepository(session).get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_roles(*roles: str):
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _check
