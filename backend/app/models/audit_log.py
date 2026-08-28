from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    """
    Records every meaningful state change on a ticket — status
    change, reassignment, urgency override, etc. This is both
    a production-readiness requirement (traceability) and
    genuinely useful for you during development to debug
    unexpected ticket states.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    ticket = relationship("Ticket", back_populates="audit_logs")

    actor_email = Column(String(255), nullable=True)  # who made the change (or "system")
    action = Column(String(100), nullable=False)       # e.g. "status_changed", "reassigned"
    details = Column(Text, nullable=True)               # human-readable description

    created_at = Column(DateTime(timezone=True), server_default=func.now())