from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .core.config import APP_NAME
from .database import Base, engine, SessionLocal
from .models import movie  # noqa: F401 - ensure models are imported for metadata
from .models import movie_list  # noqa: F401 - ensure lists models are imported
from .routes import movies as movies_router
from .routes import lists as lists_router
from .routes import analytics as analytics_router
from sqlalchemy import text


# Create database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="""
    🎬 **Movies API** – COMP3011 coursework web service for exploring and curating movies.

    ## Features
    
    * 📃 **Curated Lists (CRUD)** – Build named movie playlists (Create, Read, Update, Delete) from existing movies
    * 🔍 **Search by Title** – Find movies by exact or partial title match
    * 🎭 **Filter by Genre** – Browse movies by genre using a dropdown in the docs
    * ⭐ **Filter by Rating** – Find highly‑rated movies (sorted by rating, highest first)
    * 🎯 **Similar Movies** – Discover movies similar to your favourites (based on genres and keywords)
    * 📊 **Genre Analytics** – Per‑genre statistics with average rating, runtime, popularity, and top example movies
    * 📄 **Pagination** – Navigate large result sets with `skip` and `limit`
    * 🔐 **Simple API Key** – Write operations (creating movies and lists) require an `X-API-Key` header
    
    ## Quick Start
    
    1. Use **POST /lists** to create a curated list (requires header `X-API-Key: dev-secret-key`)
    2. Use **GET /lists** and **GET /lists/{name}** to browse curated lists
    3. Use **GET /movies** or **GET /movies/by-genre/{genre}** to explore the movie catalogue
    4. Use **GET /analytics/genres** to see per‑genre statistics
    
    All endpoints return JSON responses with clear error messages and are fully documented below.
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
            "name": "lists",
            "description": """
            Curated movie lists (playlists) built from existing movies.

            Endpoints are explicitly labelled as **CREATE**, **READ**, **UPDATE**, and **DELETE**
            to make CRUD operations clear during your COMP3011 demo.
            """,
        },
        {
            "name": "movies",
            "description": """
            Movie operations. Search, filter, and discover movies.

            **No movie IDs required** – all endpoints use title, genre, or rating.
            """,
        },
        {
            "name": "analytics",
            "description": """
            Data-driven analytics endpoints that summarise the movie catalogue.

            Currently includes per-genre statistics (average rating, runtime, popularity,
            and top example movies for each genre).
            """,
        },
        {
            "name": "health",
            "description": "Health check and API status endpoints.",
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
app.include_router(analytics_router.router)

