from datetime import date
from typing import Optional

from pydantic import BaseModel


class MatchBase(BaseModel):
    title: str
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    released: Optional[bool] = None
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


class MatchCreate(MatchBase):
    pass


class MatchRead(MatchBase):
    id: int

    class Config:
        orm_mode = True


