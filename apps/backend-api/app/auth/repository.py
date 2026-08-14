from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_utils import hash_password, hash_refresh_token
from app.db.models import RefreshToken, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, email: str, plain_password: str, role: str, tenant_id: str | None) -> User:
        from uuid import uuid4
        user = User(
            id=str(uuid4()),
            email=email,
            hashed_password=hash_password(plain_password),
            role=role,
            tenant_id=tenant_id,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: str, raw_token: str, expires_at: datetime) -> RefreshToken:
        from uuid import uuid4
        rt = RefreshToken(
            id=str(uuid4()),
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=expires_at,
        )
        self.session.add(rt)
        await self.session.commit()
        await self.session.refresh(rt)
        return rt

    async def get_valid(self, raw_token: str) -> RefreshToken | None:
        h = hash_refresh_token(raw_token)
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == h,
                RefreshToken.revoked == False,  # noqa: E712
                RefreshToken.expires_at > datetime.now(UTC),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, raw_token: str) -> None:
        rt = await self.get_valid(raw_token)
        if rt:
            rt.revoked = True
            await self.session.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
        )
        for rt in result.scalars().all():
            rt.revoked = True
        await self.session.commit()
