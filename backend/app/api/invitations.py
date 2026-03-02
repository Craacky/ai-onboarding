import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth_deps import require_admin
from app.core.deps import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitations import CreateInvitationRequest, InvitationResponse

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("", response_model=InvitationResponse)
def create_invitation(
        payload: CreateInvitationRequest,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db),
) -> InvitationResponse:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=400, detail="Email already exists")
    token = secrets.token_urlsafe(32)
    invitation = Invitation(
        organization_id=current_user.organization.id,
        email=payload.email,
        role=payload.role,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return InvitationResponse(
        id=str(invitation.id),
        email=invitation.email,
        role=invitation.role,
        token=invitation.token,
    )
