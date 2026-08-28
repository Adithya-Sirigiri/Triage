from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=201)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),  # only admins can create teams
):
    existing = db.query(Team).filter(Team.name == team_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")

    new_team = Team(name=team_in.name, description=team_in.description)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


@router.get("/", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # any logged-in user can view teams
):
    return db.query(Team).all()