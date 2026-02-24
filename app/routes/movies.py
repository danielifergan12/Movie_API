from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..core.config import DEFAULT_LIMIT
from ..crud import movie as crud_movie
from ..models.movie import Movie
from ..schemas.movie import (
    GenreFilter,
    MovieCreate,
    MovieListResponse,
    MovieRead,
    SimilarMoviesResponse,
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post(
    "",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new movie",
    description="Add a new movie to the database. Only `title` is required; all other fields are optional.",
    response_description="The created movie object with assigned ID.",
)
def create_movie_endpoint(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
) -> MovieRead:
    """
    Create a new movie record.
    
    **Example Request:**
    ```json
    {
      "title": "The Matrix",
      "status": "released",
      "vote_average": 8.7,
      "genres": "Action, Science Fiction"
    }
    ```
    """
    movie = crud_movie.create_movie(db, movie_in)
    return movie


@router.get(
    "",
    response_model=MovieListResponse,
    summary="List movies with pagination and filters",
    description="Get a paginated list of movies with optional filters. Use `skip` and `limit` for pagination.",
    response_description="A paginated list of movies with total count.",
)
def list_movies_endpoint(
    skip: int = Query(
        0,
        ge=0,
        description="**Skip** - Number of movies to skip (for pagination). Example: `skip=20` starts at the 21st movie.",
        example=0,
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        gt=0,
        description="**Limit** - Maximum number of movies to return. Example: `limit=10` returns up to 10 movies.",
        example=20,
    ),
    title: Optional[str] = Query(
        None,
        description="**Title Filter** - Search for movies containing this text (case-insensitive). Example: `title=matrix`",
        example="matrix",
    ),
    genre: Optional[GenreFilter] = Query(
        None,
        description="**Genre Filter** - Filter by genre. Select from dropdown menu.",
        example=GenreFilter.ACTION,
    ),
    adult: Optional[bool] = Query(
        None,
        description="**Adult Filter** - Filter by adult content flag. `true` = adult movies only, `false` = non-adult only.",
        example=False,
    ),
    status: Optional[str] = Query(
        None,
        description="**Status Filter** - Filter by release status. Options: `released` or `not released`.",
        example="released",
    ),
    min_vote_average: Optional[float] = Query(
        None,
        ge=0,
        le=10,
        description="**Minimum Rating** - Only return movies with rating >= this value (0-10 scale).",
        example=7.5,
    ),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    """
    Get a paginated list of movies with optional filters.
    
    **Examples:**
    - Get first 20 movies: `/movies?skip=0&limit=20`
    - Get next page: `/movies?skip=20&limit=20`
    - Filter by genre: `/movies?genre=Action&limit=10`
    - Search by title: `/movies?title=matrix`
    - Highly-rated movies: `/movies?min_vote_average=8.0&limit=10`
    """
    # Convert enum to plain string for the CRUD layer
    genre_value: Optional[str] = genre.value if isinstance(genre, GenreFilter) else genre

    movies, total = crud_movie.get_movies(
        db,
        skip=skip,
        limit=limit,
        title=title,
        genre=genre_value,
        adult=adult,
        status=status.strip().lower() if status else None,
        min_vote_average=min_vote_average,
    )
    return MovieListResponse(items=movies, total=total, skip=skip, limit=limit)


@router.get(
    "/by-title/{title}",
    response_model=List[MovieRead],
    summary="Find movies by title",
    description="Search for movies by title. Supports both exact and partial matching.",
    response_description="List of movies matching the title (may be empty).",
)
def get_movies_by_title_endpoint(
    title: str,
    exact: bool = Query(
        False,
        description="**Exact Match** - If `true`, matches exact title only. If `false` (default), matches titles containing the text.",
        example=False,
    ),
    db: Session = Depends(get_db),
) -> List[MovieRead]:
    """
    Find movies by title.
    
    **Examples:**
    - Partial match (default): `/movies/by-title/matrix` finds "The Matrix", "Matrix Reloaded", etc.
    - Exact match: `/movies/by-title/Inception?exact=true` finds only "Inception"
    
    Returns a list of matching movies (may be empty if no matches found).
    """
    movies = crud_movie.get_movies_by_title(db, title, exact=exact)
    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No movies found with title '{title}'",
        )
    return movies


@router.get(
    "/by-genre/{genre}",
    response_model=MovieListResponse,
    summary="Find movies by genre",
    description="Get movies filtered by a specific genre. Select genre from dropdown menu.",
    response_description="Paginated list of movies in the specified genre.",
)
def get_movies_by_genre_endpoint(
    genre: GenreFilter,
    skip: int = Query(
        0,
        ge=0,
        description="**Skip** - Number of movies to skip (for pagination). Example: `skip=20` starts at the 21st movie.",
        example=0,
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        gt=0,
        description="**Limit** - Maximum number of movies to return. Example: `limit=10` returns up to 10 movies.",
        example=20,
    ),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    """
    Find movies filtered by genre.
    
    **Examples:**
    - Get Comedy movies: `/movies/by-genre/Comedy`
    - Get first 10 Action movies: `/movies/by-genre/Action?limit=10`
    - Get next page: `/movies/by-genre/Action?skip=20&limit=20`
    
    Genre matching is case-insensitive and checks if the genre appears in the movie's genres list.
    """
    movies, total = crud_movie.get_movies_by_genre(
        db, genre.value, skip=skip, limit=limit
    )
    return MovieListResponse(items=movies, total=total, skip=skip, limit=limit)


@router.get(
    "/by-rating",
    response_model=MovieListResponse,
    summary="Find movies by rating range",
    description="Get movies filtered by rating (vote_average). Results are sorted by rating (highest first).",
    response_description="Paginated list of movies sorted by rating (highest to lowest).",
)
def get_movies_by_rating_endpoint(
    min_rating: Optional[float] = Query(
        None,
        ge=0,
        le=10,
        description="**Minimum Rating** - Only return movies with rating >= this value (0-10 scale). Example: `8.0`",
        example=8.0,
    ),
    max_rating: Optional[float] = Query(
        None,
        ge=0,
        le=10,
        description="**Maximum Rating** - Only return movies with rating <= this value (0-10 scale). Example: `9.0`",
        example=9.0,
    ),
    skip: int = Query(
        0,
        ge=0,
        description="**Skip** - Number of movies to skip (for pagination). Example: `skip=20` starts at the 21st movie.",
        example=0,
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        gt=0,
        description="**Limit** - Maximum number of movies to return. Example: `limit=10` returns up to 10 movies.",
        example=20,
    ),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    """
    Find movies filtered by rating range.
    
    **Examples:**
    - Highly-rated movies (8+): `/movies/by-rating?min_rating=8.0`
    - Rating range (7-9): `/movies/by-rating?min_rating=7.0&max_rating=9.0`
    - Top 10 highest rated: `/movies/by-rating?min_rating=0&limit=10`
    
    **Note:** At least one of `min_rating` or `max_rating` must be provided.
    Results are sorted by rating descending (highest rated first).
    """
    if min_rating is None and max_rating is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one of min_rating or max_rating must be provided",
        )
    movies, total = crud_movie.get_movies_by_rating(
        db, min_rating=min_rating, max_rating=max_rating, skip=skip, limit=limit
    )
    return MovieListResponse(items=movies, total=total, skip=skip, limit=limit)


@router.get(
    "/by-title/{title}/similar",
    response_model=SimilarMoviesResponse,
    summary="Find similar movies by title",
    description="Discover movies similar to a given movie based on shared genres and keywords. Results sorted by rating (highest first).",
    response_description="List of similar movies with shared genres/keywords and similarity scores.",
)
def get_similar_movies_by_title_endpoint(
    title: str,
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="**Limit** - Maximum number of similar movies to return (1-50).",
        example=10,
    ),
    min_shared_tokens: int = Query(
        1,
        ge=1,
        description="**Minimum Shared Tokens** - Minimum similarity score required (based on shared genres/keywords). Higher = more similar.",
        example=1,
    ),
    db: Session = Depends(get_db),
) -> SimilarMoviesResponse:
    """
    Find movies similar to a given movie.
    
    **How it works:**
    - Matches movies by overlapping genres and keywords
    - Genres are weighted more heavily than keywords
    - Results are sorted by **rating (highest first)**, then similarity score
    
    **Examples:**
    - Find movies similar to Inception: `/movies/by-title/Inception/similar`
    - Get top 5 similar movies: `/movies/by-title/Interstellar/similar?limit=5`
    - Only highly similar movies: `/movies/by-title/The Matrix/similar?min_shared_tokens=3`
    
    Returns movies with shared genres/keywords, sorted by rating (highest to lowest).
    """
    ref = crud_movie.get_movie_by_title(db, title)
    if not ref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with title '{title}' not found",
        )

    items = crud_movie.get_similar_movies(
        db, ref_movie=ref, limit=limit, min_shared_tokens=min_shared_tokens
    )

    return SimilarMoviesResponse(
        movie_id=ref.id,
        reference_title=ref.title,
        items=items,
    )



