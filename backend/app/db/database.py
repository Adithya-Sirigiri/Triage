from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# The engine manages the actual connection pool to Postgres
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own "session" — think of it as a
# temporary workspace for that request's DB operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our table models (Phase 1) will inherit from this Base
Base = declarative_base()

def get_db():
    """
    This function is used by FastAPI's dependency injection system.
    It opens a DB session for a request, hands it to the endpoint,
    and guarantees it's closed afterward — even if the request fails.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()