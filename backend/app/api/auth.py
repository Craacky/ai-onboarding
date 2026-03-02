from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password
)
from app.core.settings import settings
from app.models.enums import UserRoleEnum, PlanEnum
from app.models.invitation import Invitation
from app.models.organization import Organization
from app.models.refresh_session import RefreshSession
from app.models.user import User
from app.schemas.auth import (
    AcceptInviteRequest,
    RefreshRequest,
    RegisterOwnerRequest,
    TokenPairResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


def create_refresh_session(db: Session, user_id: UUID,
                           request: Request) -> str:
    refresh_token = create_refresh_token(user_id)
    db.add(RefreshSession(
        user_id=user_id,
        token_hash=hash_token(refresh_token),
        user_agent=request.headers.get("user-Agent"),
        ip_address=request.client.host if request.client
        else None,
        expires_at=datetime.now(timezone.utc) +
                   timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    return refresh_token


@router.post("/register-owner", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
def register_owner(payload: RegisterOwnerRequest, request: Request, db: Session = Depends(get_db)) -> TokenPairResponse:
    if db.scalar(select(Organization).where(Organization.slug == payload.organization_slug)):
        raise HTTPException(status_code=400, detail="Organization slug already exists")
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(
        name=payload.organization_name,
        slug=payload.organization_slug,
        plan=PlanEnum.free,
        max_documents=100,
        max_members=5,
    )
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRoleEnum.admin,
        full_name=payload.full_name,
        is_active=True,
    )
    db.add(user)
    db.flush()

    refresh_token = create_refresh_session(db, user.id, request)
    db.commit()
    access_token = create_access_token(user.id, org.id, user.role.value)
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPairResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)) -> TokenPairResponse:
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    refresh_token = create_refresh_session(db, user.id, request)
    db.commit()
    access_token = create_access_token(user.id, user.organization.id, user.role.value)
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    token_payload = decode_token(payload.refresh_token)
    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = UUID(token_payload["sub"])
    token_hash_value = hash_token(payload.refresh_token)

    session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.token_hash == token_hash_value,
            RefreshSession.revoked_at.is_(None)
        )
    )

    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

    user = db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    session.revoked_at = datetime.now(timezone.utc)
    new_refresh = create_refresh_token(user.id)
    new_refresh_hash = hash_token(new_refresh)
    db.add(RefreshSession(
        user_id=user.id,
        token_hash=new_refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()
    new_access = create_access_token(user.id, user.organization.id, user.role.value)
    return TokenPairResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:
    token_hash_value = hash_token(payload.refresh_token)
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash_value))
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()


@router.post("/accept-invite", response_model=TokenPairResponse)
def accept_invite(payload: AcceptInviteRequest, request: Request, db: Session = Depends(get_db)) -> TokenPairResponse:
    invitation = db.scalar(select(Invitation).where(Invitation.token == payload.token))
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.accepted_at is not None:
        raise HTTPException(status_code=400, detail="Invitation already accepted")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation expired")
    if db.scalar(select(User).where(User.email == invitation.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        organization_id=invitation.organization.id,
        email=invitation.email,
        hashed_password=hash_password(payload.password),
        role=invitation.role,
        full_name=payload.full_name,
        is_active=True,
    )

    db.add(user)
    invitation.accepted_at = datetime.now(timezone.utc)
    db.flush()
    refresh_token = create_refresh_session(db, user.id, request)
    db.commit()
    access_token = create_access_token(user.id, user.organization.id, user.role.value)
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)
