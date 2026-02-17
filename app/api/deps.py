from collections.abc import Generator

from sqlalchemy.orm import Session

from ..database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    The session is closed automatically after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


