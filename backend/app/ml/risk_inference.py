"""
Loads the trained risk model and exposes a function to score a
ticket's current escalation risk based on its live state (time
elapsed, assignment status, response status) — mirroring exactly
the partial-information features the model was trained on.
"""
import joblib
import os
import pandas as pd
from datetime import datetime, timezone

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_risk_model = joblib.load(os.path.join(MODEL_DIR, "risk_model.joblib"))


def score_ticket_risk(ticket) -> dict:
    """
    Takes a Ticket ORM object (with created_at, first_response_at,
    assigned_agent_id, urgency, category) and returns a risk score
    (0-1) plus the raw feature values used, for transparency.
    """
    now = datetime.now(timezone.utc)
    created_at = ticket.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    hours_open = (now - created_at).total_seconds() / 3600
    is_assigned = int(ticket.assigned_agent_id is not None)
    has_first_response = int(ticket.first_response_at is not None)

    if has_first_response:
        first_response = ticket.first_response_at
        if first_response.tzinfo is None:
            first_response = first_response.replace(tzinfo=timezone.utc)
        hours_since_last_update = (now - first_response).total_seconds() / 3600
    else:
        hours_since_last_update = hours_open

    sla_targets = {"critical": 0.5, "high": 1.0, "medium": 4.0, "low": 8.0}
    urgency = ticket.urgency.value if ticket.urgency else "medium"
    sla_target = sla_targets.get(urgency, 4.0)
    sla_breached_so_far = int(hours_open > sla_target and not has_first_response)

    features = pd.DataFrame([{
        "urgency": urgency,
        "category": ticket.category.value if ticket.category else "general",
        "hours_open": hours_open,
        "is_assigned": is_assigned,
        "has_first_response": has_first_response,
        "hours_since_last_update": hours_since_last_update,
        "sla_breached_so_far": sla_breached_so_far,
    }])

    risk_score = float(_risk_model.predict_proba(features)[0][1])

    return {
        "risk_score": round(risk_score, 3),
        "factors": {
            "hours_open": round(hours_open, 2),
            "is_assigned": bool(is_assigned),
            "has_first_response": bool(has_first_response),
            "sla_breached_so_far": bool(sla_breached_so_far),
        },
    }