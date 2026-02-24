from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from .movie import MovieRead


class MovieListCreate(BaseModel):
    """CREATE: payload for creating a new movie list."""

    name: str
    description: Optional[str] = None
    movie_titles: List[str]


class MovieListUpdate(BaseModel):
    """UPDATE: payload for updating an existing movie list."""

    description: Optional[str] = None
    movie_titles: Optional[List[str]] = None


class MovieListSummary(BaseModel):
    """READ: summary view used when listing movie lists."""

    id: int
    name: str
    description: Optional[str] = None
    size: int


class MovieListRead(BaseModel):
    """READ: detailed view of a movie list with the movies included."""

    id: int
    name: str
    description: Optional[str] = None
    movies: List[MovieRead]

