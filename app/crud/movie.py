from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.config import MAX_LIMIT
from ..models.movie import Movie
from ..schemas.movie import MovieCreate, MovieUpdate


def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    return db.get(Movie, movie_id)


def get_movies(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    title: Optional[str] = None,
    adult: Optional[bool] = None,
    status: Optional[str] = None,
    min_vote_average: Optional[float] = None,
) -> Tuple[List[Movie], int]:
    """
    Return a list of movies and the total count, applying pagination and filters.
    """
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    query = select(Movie)

    if title:
        query = query.where(Movie.title.ilike(f"%{title}%"))
    if adult is not None:
        query = query.where(Movie.adult.is_(adult))
    if status:
        # status is already normalised by Pydantic, but normalise again defensively
        query = query.where(Movie.status == status.strip().lower())
    if min_vote_average is not None:
        query = query.where(Movie.vote_average >= min_vote_average)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    result = db.execute(query.offset(skip).limit(limit))
    movies = list(result.scalars().all())
    return movies, total


def create_movie(db: Session, movie_in: MovieCreate) -> Movie:
    movie = Movie(**movie_in.dict())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, db_movie: Movie, movie_in: MovieUpdate) -> Movie:
    data = movie_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_movie, field, value)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, db_movie: Movie) -> None:
    db.delete(db_movie)
    db.commit()


