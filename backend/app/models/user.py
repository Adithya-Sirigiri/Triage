from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.enums import UserRole

class User(Base):
    """
    Represents both agents and admins, distinguished by `role`.
    We password-hash, never store plain text — non-negotiable
    even for a portfolio project, since it's the kind of detail
    that gets checked in interviews.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.AGENT)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="users")

    is_active = Column(Integer, default=1)  # 1 = active, 0 = deactivated
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assigned_tickets = relationship("Ticket", back_populates="assigned_agent")