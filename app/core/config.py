from typing import Final, Set

APP_NAME: Final[str] = "Movies API"

# SQLite database in the project root by default
DATABASE_URL: Final[str] = "sqlite:///./movies.db"

# Pagination defaults
DEFAULT_LIMIT: Final[int] = 20
MAX_LIMIT: Final[int] = 100

# Allowed movie status values (normalised to lowercase)
MOVIE_STATUS_VALUES: Final[Set[str]] = {"released", "not released"}


