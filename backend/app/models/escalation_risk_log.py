from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class EscalationRiskLog(Base):
    """
    Every time the escalation-risk model scores a ticket, we
    store a snapshot here rather than overwriting a single field.

    Why this matters: it's the dataset you'll use in Phase 4 to
    evaluate whether the model's predictions were actually correct
    (did tickets it flagged high-risk really escalate?). Without
    this history, you can't prove your model works — you'd just
    be asserting it does.
    """
    __tablename__ = "escalation_risk_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    ticket = relationship("Ticket", back_populates="risk_logs")

    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    contributing_factors = Column(Text, nullable=True)  # JSON string of SHAP-style explanation

    scored_at = Column(DateTime(timezone=True), server_default=func.now())