from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..crud import movie as crud_movie
from ..schemas.movie import GenreStats

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get(
    "/genres",
    response_model=List[GenreStats],
    summary="READ: genre analytics",
    description=(
        "Return per-genre analytics including movie count, average rating, average runtime, "
        "average popularity, and a few top example movies for each genre."
    ),
    response_description="List of genres with aggregated statistics and top example movies.",
)
def get_genre_analytics_endpoint(
    top_n: int = Query(
        3,
        ge=1,
        le=10,
        description="**Top N** - Number of top movies to include for each genre (1-10).",
        example=3,
    ),
    db: Session = Depends(get_db),
) -> List[GenreStats]:
    """
    Compute analytics per genre.

    **Examples:**
    - `/analytics/genres` – default 3 top movies per genre
    - `/analytics/genres?top_n=5` – show 5 top movies per genre
    """
    return crud_movie.get_genre_analytics(db, top_n=top_n)

