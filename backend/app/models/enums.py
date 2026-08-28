import enum

class UserRole(str, enum.Enum):
    """
    Distinguishes agents (who resolve tickets) from admins
    (who manage teams, view analytics, configure SLA rules).
    Stored as a string in the DB so it's human-readable if you
    ever query the table directly.
    """
    AGENT = "agent"
    ADMIN = "admin"

class TicketStatus(str, enum.Enum):
    """
    The lifecycle a ticket moves through. Kept explicit and small
    on purpose — every status here should map to a real UI state.
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketUrgency(str, enum.Enum):
    """
    This gets set initially by the ML classifier (Phase 3),
    but can be overridden by an agent — so it's a mutable field,
    not a permanent label.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketCategory(str, enum.Enum):
    """
    Starting with a fixed set of categories relevant to a generic
    SaaS support context. This can be expanded later without
    breaking existing data, since it's just a string constraint.
    """
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"