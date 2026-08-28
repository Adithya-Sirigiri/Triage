from app.db.database import SessionLocal
from app.models.sla_rule import SLARule
from app.models.enums import TicketUrgency

def seed_sla_rules():
    """
    Baseline SLA policy: how fast each urgency level must get a
    first response and a full resolution, in minutes.
    These numbers are reasonable industry-typical defaults —
    adjustable later via the DB without touching code.
    """
    db = SessionLocal()
    defaults = [
        {"urgency": TicketUrgency.CRITICAL, "first_response_minutes": 30, "resolution_minutes": 240},
        {"urgency": TicketUrgency.HIGH, "first_response_minutes": 60, "resolution_minutes": 480},
        {"urgency": TicketUrgency.MEDIUM, "first_response_minutes": 240, "resolution_minutes": 1440},
        {"urgency": TicketUrgency.LOW, "first_response_minutes": 480, "resolution_minutes": 2880},
    ]

    for rule in defaults:
        exists = db.query(SLARule).filter(SLARule.urgency == rule["urgency"]).first()
        if not exists:
            db.add(SLARule(**rule))

    db.commit()
    db.close()
    print("SLA rules seeded successfully.")

if __name__ == "__main__":
    seed_sla_rules()