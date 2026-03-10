from typing import Final, Set
import os

APP_NAME: Final[str] = "Movies API"

# SQLite database in the project root by default
DATABASE_URL: Final[str] = "sqlite:///./movies.db"

# Pagination defaults
DEFAULT_LIMIT: Final[int] = 20
MAX_LIMIT: Final[int] = 100

# Allowed movie status values (normalised to lowercase)
MOVIE_STATUS_VALUES: Final[Set[str]] = {"released", "not released"}


# Simple API key authentication
# Default key is suitable for local development and tests.
# In production, override via the MOVIES_API_KEY environment variable.
API_KEY_HEADER_NAME: Final[str] = "X-API-Key"
API_KEY: Final[str] = os.getenv("MOVIES_API_KEY", "dev-secret-key")


