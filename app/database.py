from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .core.config import DATABASE_URL


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session() -> Generator:
    """
    Yield a new SQLAlchemy session.
    Intended for internal usage; FastAPI dependency is defined in app.api.deps.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


