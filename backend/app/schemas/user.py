from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.AGENT
    team_id: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    team_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this schema directly from a SQLAlchemy object


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"