from pydantic import BaseModel, EmailStr

from app.models.enums import UserRoleEnum


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    role: UserRoleEnum

class InvitationResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRoleEnum
    token: str

    