from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, validator

from ..core.config import MOVIE_STATUS_VALUES


class MovieBase(BaseModel):
    title: str
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    status: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    tagline: Optional[str] = None
    genres: Optional[str] = None
    production_companies: Optional[str] = None
    spoken_languages: Optional[str] = None
    keywords: Optional[str] = None

    @validator("status")
    def normalise_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        value = v.strip().lower()
        if value not in MOVIE_STATUS_VALUES:
            raise ValueError(
                f"status must be one of {sorted(MOVIE_STATUS_VALUES)}, got '{v}'"
            )
        return value


class MovieCreate(MovieBase):
    """Schema for creating a new movie."""

    title: str


class MovieUpdate(BaseModel):
    """
    Schema for updating a movie.
    For simplicity, all fields are optional; provided fields overwrite existing ones.
    """

    title: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    status: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    tagline: Optional[str] = None
    genres: Optional[str] = None
    production_companies: Optional[str] = None
    spoken_languages: Optional[str] = None
    keywords: Optional[str] = None

    @validator("status")
    def normalise_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        value = v.strip().lower()
        if value not in MOVIE_STATUS_VALUES:
            raise ValueError(
                f"status must be one of {sorted(MOVIE_STATUS_VALUES)}, got '{v}'"
            )
        return value


class MovieRead(MovieBase):
    id: int

    class Config:
        orm_mode = True


class MovieListResponse(BaseModel):
    items: List[MovieRead]
    total: int
    skip: int
    limit: int


