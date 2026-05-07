from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.auth.service import AuthService, get_current_user
from app.db.session import get_session

router = APIRouter()


def _svc(session=Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, svc: AuthService = Depends(_svc)):
    return await svc.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, svc: AuthService = Depends(_svc)):
    return await svc.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, svc: AuthService = Depends(_svc)):
    return await svc.refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: LogoutRequest, svc: AuthService = Depends(_svc)):
    await svc.logout(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user
