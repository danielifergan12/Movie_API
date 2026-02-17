from fastapi import FastAPI

from .db.database import Base, engine
from .models import match  # noqa: F401 - ensure models are imported for metadata
from .routers import matches as matches_router

# Create database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movies API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Movies API is running"}


app.include_router(matches_router.router)


