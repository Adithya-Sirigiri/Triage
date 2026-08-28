from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.enums import UserRole

# This tells FastAPI's auto-generated docs (/docs) that routes
# using this expect a Bearer token, and gives us a reusable
# way to extract "Authorization: Bearer <token>" from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Runs before any route that declares it as a dependency.
    Decodes the JWT, looks up the user it refers to, and returns
    it — or raises 401 if anything is invalid. Routes never have
    to think about tokens directly; they just receive a User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    A stricter version of get_current_user — use this on routes
    that only admins should access. Reuses get_current_user first
    (so an invalid token still correctly returns 401), then adds
    a role check on top (403 if the user isn't an admin).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges",
        )
    return current_user