from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database URL; stored in the project root by default
SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

# For SQLite, check_same_thread=False is required when using it with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy session.
    The session is closed automatically after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


