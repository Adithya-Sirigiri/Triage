from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.enums import TicketStatus, TicketUrgency, TicketCategory


class TicketCreate(BaseModel):
    subject: str
    description: str
    customer_email: EmailStr
    team_id: int | None = None


class TicketUpdate(BaseModel):
    """
    All fields optional — this schema is used for partial updates
    (e.g. an agent just changes status, without resending everything).
    """
    status: TicketStatus | None = None
    urgency: TicketUrgency | None = None
    category: TicketCategory | None = None
    assigned_agent_id: int | None = None
    team_id: int | None = None


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    customer_email: EmailStr
    status: TicketStatus
    category: TicketCategory | None
    urgency: TicketUrgency | None
    current_risk_score: float | None
    team_id: int | None
    assigned_agent_id: int | None
    created_at: datetime
    updated_at: datetime | None
    first_response_at: datetime | None
    resolved_at: datetime | None

    class Config:
        from_attributes = True