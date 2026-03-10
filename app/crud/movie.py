from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.config import MAX_LIMIT
from ..models.movie import Movie
from ..schemas.movie import GenreStats, MovieCreate, MovieUpdate, SimilarMovie


def get_movies_by_title(
    db: Session,
    title: str,
    *,
    exact: bool = False,
) -> List[Movie]:
    """
    Return movies matching the given title.
    If exact=True, matches exact title (case-insensitive).
    If exact=False, matches titles containing the text (case-insensitive).
    """
    if exact:
        query = select(Movie).where(Movie.title.ilike(title))
    else:
        pattern = f"%{title}%"
        query = select(Movie).where(Movie.title.ilike(pattern))
    
    result = db.execute(query)
    return list(result.scalars().all())


def get_movie_by_title(db: Session, title: str) -> Optional[Movie]:
    """
    Return the first movie whose title contains the given text (case-insensitive).
    Used internally for similarity searches.
    """
    pattern = f"%{title}%"
    stmt = select(Movie).where(Movie.title.ilike(pattern))
    return db.execute(stmt).scalars().first()


def get_movies(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    title: Optional[str] = None,
    genre: Optional[str] = None,
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
    if genre:
        # Genre is stored as comma-separated string, e.g. "Action, Drama"
        query = query.where(Movie.genres.ilike(f"%{genre}%"))
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


def get_movies_by_genre(
    db: Session,
    genre: str,
    *,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Movie], int]:
    """
    Return movies filtered by genre.
    Genre matching is case-insensitive and checks if genre appears in comma-separated genres string.
    """
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    query = select(Movie).where(Movie.genres.ilike(f"%{genre}%"))
    
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    
    result = db.execute(query.offset(skip).limit(limit))
    movies = list(result.scalars().all())
    return movies, total


def get_movies_by_rating(
    db: Session,
    *,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Movie], int]:
    """
    Return movies filtered by rating range (vote_average).
    Results are sorted by rating descending (highest rated first).
    """
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    query = select(Movie).where(Movie.vote_average.is_not(None))
    
    if min_rating is not None:
        query = query.where(Movie.vote_average >= min_rating)
    if max_rating is not None:
        query = query.where(Movie.vote_average <= max_rating)
    
    # Sort by rating descending (highest first)
    query = query.order_by(Movie.vote_average.desc())
    
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    
    result = db.execute(query.offset(skip).limit(limit))
    movies = list(result.scalars().all())
    return movies, total


def _split_tokens(value: Optional[str]) -> set[str]:
    if not value:
        return set()
    return {t.strip() for t in value.split(",") if t.strip()}


def get_similar_movies(
    db: Session,
    ref_movie: Movie,
    *,
    limit: int = 10,
    min_shared_tokens: int = 1,
) -> List[SimilarMovie]:
    """
    Find movies similar to the reference movie based on overlapping genres and keywords.
    """
    ref_genres = _split_tokens(ref_movie.genres)
    ref_keywords = _split_tokens(ref_movie.keywords)

    query = (
        select(Movie)
        .where(Movie.id != ref_movie.id)
        .where(Movie.status == "released")
    )
    candidates = db.execute(query).scalars().all()

    items: List[SimilarMovie] = []
    for m in candidates:
        g = _split_tokens(m.genres)
        k = _split_tokens(m.keywords)
        shared_g = sorted(ref_genres & g)
        shared_k = sorted(ref_keywords & k)
        score = len(shared_g) * 2 + len(shared_k)  # weight genres higher

        if score >= min_shared_tokens:
            items.append(
                SimilarMovie(
                    id=m.id,
                    title=m.title,
                    shared_genres=shared_g,
                    shared_keywords=shared_k,
                    similarity_score=score,
                )
            )

    # Sort by rating (highest first), then similarity score, then title
    # Need to get vote_average from the Movie objects
    movie_dict = {m.id: m for m in candidates}
    items.sort(
        key=lambda x: (
            -(movie_dict[x.id].vote_average or 0),  # Rating descending (highest first)
            -x.similarity_score,  # Then similarity score
            x.title.lower()  # Then alphabetically
        )
    )
    return items[:limit]


def get_genre_analytics(
    db: Session,
    *,
    top_n: int = 3,
) -> List[GenreStats]:
    """
    Compute per-genre analytics: movie count and average rating/runtime/popularity,
    plus a few top example movies per genre.
    """
    # Load all movies that have at least one genre
    movies = (
        db.execute(select(Movie).where(Movie.genres.is_not(None)))
        .scalars()
        .all()
    )

    stats: Dict[str, Dict[str, object]] = {}

    for m in movies:
        if not m.genres:
            continue
        tokens = [t.strip() for t in m.genres.split(",") if t.strip()]
        for g in tokens:
            entry = stats.setdefault(
                g,
                {
                    "count": 0,
                    "vote_sum": 0.0,
                    "vote_count": 0,
                    "runtime_sum": 0.0,
                    "runtime_count": 0,
                    "popularity_sum": 0.0,
                    "popularity_count": 0,
                    "examples": [],
                },
            )
            entry["count"] = int(entry["count"]) + 1

            if m.vote_average is not None:
                entry["vote_sum"] = float(entry["vote_sum"]) + float(m.vote_average)
                entry["vote_count"] = int(entry["vote_count"]) + 1

            if m.runtime is not None:
                entry["runtime_sum"] = float(entry["runtime_sum"]) + float(m.runtime)
                entry["runtime_count"] = int(entry["runtime_count"]) + 1

            if m.popularity is not None:
                entry["popularity_sum"] = float(entry["popularity_sum"]) + float(
                    m.popularity
                )
                entry["popularity_count"] = int(entry["popularity_count"]) + 1

            examples: List[Movie] = entry["examples"]  # type: ignore[assignment]
            examples.append(m)

    results: List[GenreStats] = []
    for genre, e in stats.items():
        count = int(e["count"])
        vote_count = int(e["vote_count"])
        runtime_count = int(e["runtime_count"])
        popularity_count = int(e["popularity_count"])

        avg_vote = (
            float(e["vote_sum"]) / vote_count if vote_count > 0 else None
        )
        avg_runtime = (
            float(e["runtime_sum"]) / runtime_count if runtime_count > 0 else None
        )
        avg_popularity = (
            float(e["popularity_sum"]) / popularity_count
            if popularity_count > 0
            else None
        )

        examples: List[Movie] = e["examples"]  # type: ignore[assignment]
        # Sort examples by rating (highest first), then popularity, then title
        examples_sorted = sorted(
            examples,
            key=lambda m: (
                -(m.vote_average or 0.0),
                -(m.popularity or 0.0),
                m.title.lower(),
            ),
        )
        top_movies = examples_sorted[:top_n]

        results.append(
            GenreStats(
                genre=genre,
                movie_count=count,
                avg_vote_average=avg_vote,
                avg_runtime=avg_runtime,
                avg_popularity=avg_popularity,
                top_movies=top_movies,
            )
        )

    # Sort genres by average rating (highest first), then by movie_count
    results.sort(
        key=lambda s: (
            -(s.avg_vote_average or 0.0),
            -s.movie_count,
            s.genre.lower(),
        )
    )
    return results

