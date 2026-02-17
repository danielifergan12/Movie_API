from fastapi import FastAPI

from .core.config import APP_NAME
from .database import Base, engine
from .models import movie  # noqa: F401 - ensure models are imported for metadata
from .routes import movies as movies_router


# Create database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME, version="0.1.0")


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {"message": "Movies API is running"}


app.include_router(movies_router.router)


