# Importing all models here ensures Alembic's autogenerate
# can detect every table when we create migrations.
from app.db.database import Base
from app.models.team import Team
from app.models.user import User
from app.models.sla_rule import SLARule
from app.models.ticket import Ticket
from app.models.escalation_risk_log import EscalationRiskLog
from app.models.audit_log import AuditLog