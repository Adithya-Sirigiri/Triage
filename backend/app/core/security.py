from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# bcrypt is the industry-standard password hashing algorithm —
# it's deliberately slow, which makes brute-forcing leaked hashes
# impractical. We never store or compare raw passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Builds a signed JWT. 'data' typically contains the user's id
    and role. We add an expiry ('exp') claim — the JWT library
    automatically rejects expired tokens on decode, so we don't
    need to manually check expiry everywhere.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Verifies the token's signature and expiry. Returns the payload
    (user id, role) if valid, or None if the token is invalid/expired/
    tampered with. The signature check is what makes this secure —
    nobody can forge a token without knowing SECRET_KEY.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None