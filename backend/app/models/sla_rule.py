from sqlalchemy import Column, Integer, Enum
from app.db.database import Base
from app.models.enums import TicketUrgency

class SLARule(Base):
    """
    Defines the response-time expectation (in minutes) for each
    urgency level. Stored as data, not hardcoded, so support-leads
    could eventually change policy without a code deployment.

    Example row: urgency=CRITICAL, first_response_minutes=60,
    resolution_minutes=240
    """
    __tablename__ = "sla_rules"

    id = Column(Integer, primary_key=True, index=True)
    urgency = Column(Enum(TicketUrgency), unique=True, nullable=False)
    first_response_minutes = Column(Integer, nullable=False)
    resolution_minutes = Column(Integer, nullable=False)