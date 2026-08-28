from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.enums import TicketStatus, TicketUrgency, TicketCategory

class Ticket(Base):
    """
    The core entity of the system.

    Design notes:
    - `urgency` and `category` start nullable because they're
      filled in by the ML classifier (Phase 3) shortly after
      creation, not at creation time itself.
    - `current_risk_score` is a denormalized "latest score" field
      for fast reads (e.g. sorting the live queue). The full
      history of scores lives in EscalationRiskLog — this field
      is just a cache of the most recent one.
    - `customer_email` is kept simple (no separate Customer table)
      since customer accounts aren't the focus of this system;
      this can be normalized later if needed.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)

    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    category = Column(Enum(TicketCategory), nullable=True)
    urgency = Column(Enum(TicketUrgency), nullable=True)

    current_risk_score = Column(Float, nullable=True)  # 0.0 to 1.0

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="tickets")

    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_agent = relationship("User", back_populates="assigned_tickets")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    risk_logs = relationship("EscalationRiskLog", back_populates="ticket")
    audit_logs = relationship("AuditLog", back_populates="ticket")