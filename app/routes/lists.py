from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ..api.deps import get_db
from .. import crud
from ..schemas.movie_list import (
    MovieListCreate,
    MovieListRead,
    MovieListSummary,
    MovieListUpdate,
)

router = APIRouter(
    prefix="/lists",
    tags=["lists"],
)


@router.post(
    "",
    response_model=MovieListRead,
    status_code=status.HTTP_201_CREATED,
    summary="CREATE: curated movie list",
    description=(
        "CREATE a new curated movie list (playlist) by providing a **unique list name**, "
        "an optional description, and a list of movie titles. Titles are matched "
        "against existing movies in the database."
    ),
)
def create_movie_list(
    payload: MovieListCreate,
    db: Session = Depends(get_db),
) -> MovieListRead:
    existing = crud.movie_list.get_list_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"List with name '{payload.name}' already exists",
        )

    movie_list = crud.movie_list.create_list(
        db,
        name=payload.name,
        description=payload.description,
        movie_titles=payload.movie_titles,
    )

    return MovieListRead(
        id=movie_list.id,
        name=movie_list.name,
        description=movie_list.description,
        movies=[item.movie for item in movie_list.items],
    )


@router.get(
    "",
    response_model=List[MovieListSummary],
    summary="READ: list all curated movie lists",
    description="READ all curated movie lists with basic information and the number of movies in each list.",
)
def list_movie_lists(
    db: Session = Depends(get_db),
) -> List[MovieListSummary]:
    lists = crud.movie_list.get_lists(db)
    return [
        MovieListSummary(
            id=ml.id,
            name=ml.name,
            description=ml.description,
            size=len(ml.items),
        )
        for ml in lists
    ]


@router.get(
    "/{name}",
    response_model=MovieListRead,
    summary="READ: get a curated movie list by name",
    description="READ a single curated movie list by its unique **name** (not by ID).",
)
def get_movie_list(
    name: str = Path(..., description="Unique name of the curated movie list.", example="Christopher Nolan Essentials"),
    db: Session = Depends(get_db),
) -> MovieListRead:
    movie_list = crud.movie_list.get_list_by_name(db, name)
    if not movie_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with name '{name}' not found",
        )

    return MovieListRead(
        id=movie_list.id,
        name=movie_list.name,
        description=movie_list.description,
        movies=[item.movie for item in movie_list.items],
    )


@router.put(
    "/{name}",
    response_model=MovieListRead,
    summary="UPDATE: curated movie list",
    description=(
        "UPDATE an existing curated movie list. You can change the description and/or "
        "replace the list of movies by providing a new set of movie titles."
    ),
)
def update_movie_list(
    name: str = Path(..., description="Unique name of the curated movie list to update."),
    payload: MovieListUpdate = ...,
    db: Session = Depends(get_db),
) -> MovieListRead:
    movie_list = crud.movie_list.get_list_by_name(db, name)
    if not movie_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with name '{name}' not found",
        )

    updated = crud.movie_list.update_list(
        db,
        movie_list=movie_list,
        description=payload.description,
        movie_titles=payload.movie_titles,
    )

    return MovieListRead(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        movies=[item.movie for item in updated.items],
    )


@router.delete(
    "/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="DELETE: curated movie list",
    description="DELETE a curated movie list by its unique **name** (and all its items).",
)
def delete_movie_list(
    name: str = Path(..., description="Unique name of the curated movie list to delete."),
    db: Session = Depends(get_db),
) -> None:
    movie_list = crud.movie_list.get_list_by_name(db, name)
    if not movie_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with name '{name}' not found",
        )

    crud.movie_list.delete_list(db, movie_list)

