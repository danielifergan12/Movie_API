from collections.abc import Generator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from ..core.config import API_KEY, API_KEY_HEADER_NAME
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


def verify_api_key(x_api_key: str = Header("", alias=API_KEY_HEADER_NAME)) -> None:
    """
    Simple API key check using the X-API-Key header.

    The expected key value is configured in core.config.API_KEY and can be
    overridden with the MOVIES_API_KEY environment variable.
    """
    if not API_KEY:
        # If no API key is configured, treat all requests as authorised.
        return
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

