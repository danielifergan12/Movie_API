from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..core.config import DEFAULT_LIMIT
from ..crud import movie as crud_movie
from ..models.movie import Movie
from ..schemas.movie import MovieCreate, MovieListResponse, MovieRead, MovieUpdate

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post(
    "",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a movie",
)
def create_movie_endpoint(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
) -> MovieRead:
    """
    Create a new movie record.
    """
    movie = crud_movie.create_movie(db, movie_in)
    return movie


@router.get(
    "",
    response_model=MovieListResponse,
    summary="List movies with pagination and filters",
)
def list_movies_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        DEFAULT_LIMIT,
        gt=0,
        description="Maximum number of records to return (capped by server)",
    ),
    title: Optional[str] = Query(
        None, description="Filter by title substring (case-insensitive)"
    ),
    adult: Optional[bool] = Query(
        None, description="Filter by adult flag (true/false)"
    ),
    status: Optional[str] = Query(
        None, description="Filter by movie status (released/not released)"
    ),
    min_vote_average: Optional[float] = Query(
        None, ge=0, le=10, description="Filter by minimum vote_average"
    ),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    """
    Return a paginated list of movies, optionally filtered by title, adult flag,
    status, and minimum vote_average.
    """
    movies, total = crud_movie.get_movies(
        db,
        skip=skip,
        limit=limit,
        title=title,
        adult=adult,
        status=status.strip().lower() if status else None,
        min_vote_average=min_vote_average,
    )
    return MovieListResponse(items=movies, total=total, skip=skip, limit=limit)


@router.get(
    "/{movie_id}",
    response_model=MovieRead,
    summary="Get a movie by ID",
)
def get_movie_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
) -> MovieRead:
    """
    Retrieve a single movie by its ID.
    """
    movie = crud_movie.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie


@router.put(
    "/{movie_id}",
    response_model=MovieRead,
    summary="Update a movie",
)
def update_movie_endpoint(
    movie_id: int,
    movie_in: MovieUpdate,
    db: Session = Depends(get_db),
) -> MovieRead:
    """
    Update an existing movie.
    All provided fields will overwrite the stored values.
    """
    db_movie = crud_movie.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    updated = crud_movie.update_movie(db, db_movie, movie_in)
    return updated


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie",
)
def delete_movie_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a movie by its ID.
    """
    db_movie = crud_movie.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    crud_movie.delete_movie(db, db_movie)
    return None


