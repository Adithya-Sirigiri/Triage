import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.ml.inference import classify_ticket
from app.ml.risk_inference import score_ticket_risk
from app.models.escalation_risk_log import EscalationRiskLog
from app.db.database import get_db
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.api.deps import get_current_user
from app.api.ws import publish_ticket_event


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Category and urgency are left null here on purpose — they get
    filled in by the ML classifier in Phase 3, right after creation.
    This keeps ticket creation fast and decoupled from ML inference.
    """
    predictions = classify_ticket(ticket_in.subject, ticket_in.description)

    new_ticket = Ticket(
        subject=ticket_in.subject,
        description=ticket_in.description,
        customer_email=ticket_in.customer_email,
        team_id=ticket_in.team_id,
        category=predictions["category"],
        urgency=predictions["urgency"],
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    _log_action(db, new_ticket.id, current_user.email, "ticket_created",
                f"Ticket '{new_ticket.subject}' created")

    await publish_ticket_event("ticket_created", {
        "id": new_ticket.id,
        "subject": new_ticket.subject,
        "category": new_ticket.category.value if new_ticket.category else None,
        "urgency": new_ticket.urgency.value if new_ticket.urgency else None,
    })

    return new_ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admins see every ticket. Agents only see tickets assigned to
    them — this mirrors how a real support dashboard scopes an
    agent's view to their own queue.
    """
    if current_user.role == UserRole.ADMIN:
        return db.query(Ticket).all()
    return db.query(Ticket).filter(Ticket.assigned_agent_id == current_user.id).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != UserRole.ADMIN and ticket.assigned_agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    update_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Partial update. Only admins can reassign a ticket to a
    different agent (assigned_agent_id) or change its team —
    agents can update status/urgency/category on tickets that
    are theirs. Every change is written to the audit log.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    is_admin = current_user.role == UserRole.ADMIN
    is_owner = ticket.assigned_agent_id == current_user.id

    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")

    update_data = update_in.model_dump(exclude_unset=True)

    if not is_admin:
        # Agents cannot reassign tickets or move them between teams
        update_data.pop("assigned_agent_id", None)
        update_data.pop("team_id", None)

    changes = []
    for field, value in update_data.items():
        old_value = getattr(ticket, field)
        if old_value != value:
            setattr(ticket, field, value)
            changes.append(f"{field}: {old_value} -> {value}")

    db.commit()
    db.refresh(ticket)

    if changes:
        _log_action(db, ticket.id, current_user.email, "ticket_updated", "; ".join(changes))

    return ticket

@router.get("/{ticket_id}/risk")
async def get_ticket_risk(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Scores the ticket's current escalation risk on demand, updates
    the ticket's cached current_risk_score, and logs the snapshot
    to EscalationRiskLog for historical tracking (per our Phase 1
    design — this is what lets us later evaluate whether the model's
    predictions were actually correct).
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != UserRole.ADMIN and ticket.assigned_agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    result = score_ticket_risk(ticket)

    ticket.current_risk_score = result["risk_score"]
    db.commit()

    log = EscalationRiskLog(
        ticket_id=ticket.id,
        risk_score=result["risk_score"],
        contributing_factors=json.dumps(result["factors"]),
    )
    db.add(log)
    db.commit()

    await publish_ticket_event("risk_updated", {
        "id": ticket.id,
        "risk_score": result["risk_score"],
    })

    return result

@router.get("/{ticket_id}/audit")
def get_ticket_audit(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.ticket_id == ticket_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return [
        {"id": l.id, "actor_email": l.actor_email, "action": l.action, "details": l.details, "created_at": l.created_at}
        for l in logs
    ]


@router.get("/{ticket_id}/risk-history")
def get_ticket_risk_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    logs = (
        db.query(EscalationRiskLog)
        .filter(EscalationRiskLog.ticket_id == ticket_id)
        .order_by(EscalationRiskLog.scored_at.asc())
        .all()
    )
    return [{"id": l.id, "risk_score": l.risk_score, "scored_at": l.scored_at} for l in logs]

def _log_action(db: Session, ticket_id: int, actor_email: str, action: str, details: str):
    """Small internal helper so every route doesn't repeat this boilerplate."""
    log = AuditLog(ticket_id=ticket_id, actor_email=actor_email, action=action, details=details)
    db.add(log)
    db.commit()