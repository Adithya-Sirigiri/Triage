from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Team(Base):
    """
    Represents a support team (e.g. 'Billing Support').
    Tickets get routed to a team; agents belong to a team.
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One team has many agents and many tickets.
    # These don't create DB columns — they let us do
    # `team.users` or `team.tickets` in Python code.
    users = relationship("User", back_populates="team")
    tickets = relationship("Ticket", back_populates="team")