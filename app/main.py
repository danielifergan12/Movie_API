from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .core.config import APP_NAME
from .database import Base, engine, SessionLocal
from .models import movie  # noqa: F401 - ensure models are imported for metadata
from .models import movie_list  # noqa: F401 - ensure lists models are imported
from .routes import movies as movies_router
from .routes import lists as lists_router
from sqlalchemy import text


# Create database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="""
    🎬 **Movies API** - A RESTful API for exploring movie data from TMDB.

    ## Features
    
    * 🔍 **Search by Title** - Find movies by exact or partial title match
    * 🎭 **Filter by Genre** - Browse movies by genre (Action, Drama, Comedy, etc.)
    * ⭐ **Filter by Rating** - Find highly-rated movies (sorted by rating)
    * 🎯 **Similar Movies** - Discover movies similar to your favorites (sorted by rating)
    * 📄 **Pagination** - Navigate through large result sets with `skip` and `limit`
    
    ## Quick Start
    
    1. Try **GET /movies** to see all movies with filters
    2. Use **GET /movies/by-title/{title}** to search by title
    3. Use **GET /movies/by-genre/{genre}** to filter by genre
    4. Use **GET /movies/by-rating** to find highly-rated movies
    
    All endpoints return JSON responses with clear error messages.
    """,
    contact={
        "name": "Movies API",
        "url": "http://127.0.0.1:8000/docs",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "health",
            "description": "Health check and API status endpoints.",
        },
        {
            "name": "movies",
            "description": """
            Movie operations. Search, filter, and discover movies.

            **No movie IDs required** - all endpoints use title, genre, or rating.
            """,
        },
        {
            "name": "lists",
            "description": """
            Curated movie lists (playlists) built from existing movies.

            Endpoints are explicitly labelled as **CREATE**, **READ**, **UPDATE**, and **DELETE**
            to make CRUD operations clear during your COMP3011 demo.
            """,
        },
    ],
)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str | int]:
    """
    Health check endpoint with database status.
    Returns API status and number of movies in the database.
    """
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM movies"))
        movie_count = result.scalar() or 0
        return {
            "message": "Movies API is running",
            "database_status": "connected",
            "movies_count": movie_count,
        }
    except Exception:
        return {
            "message": "Movies API is running",
            "database_status": "error",
            "movies_count": 0,
        }
    finally:
        db.close()


app.include_router(movies_router.router)
app.include_router(lists_router.router)

