from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from sqlalchemy import asc
from sqlalchemy.orm import Session, selectinload

from ..models.movie import Movie
from ..models.movie_list import MovieList, MovieListItem


def _resolve_titles_to_movies(db: Session, titles: Iterable[str]) -> List[Movie]:
    """Resolve a list of (case-insensitive) titles to Movie objects.

    Duplicates are removed while preserving the original order of first appearance.
    """
    # Normalise titles (strip/upper) and preserve order
    seen: set[str] = set()
    normalised_titles: List[str] = []
    for t in titles:
        key = t.strip()
        if not key:
            continue
        key_upper = key.upper()
        if key_upper in seen:
            continue
        seen.add(key_upper)
        normalised_titles.append(key)

    if not normalised_titles:
        return []

    movies: Sequence[Movie] = (
        db.query(Movie)
        .filter(Movie.title.in_(normalised_titles))
        .order_by(asc(Movie.title))
        .all()
    )

    # Preserve input order: map by title (case-insensitive)
    movies_by_title = {m.title.upper(): m for m in movies}
    ordered: List[Movie] = []
    for t in normalised_titles:
        m = movies_by_title.get(t.upper())
        if m:
            ordered.append(m)
    return ordered


def get_list_by_name(db: Session, name: str) -> Optional[MovieList]:
    """READ: fetch a single list by its unique name."""
    return (
        db.query(MovieList)
        .options(selectinload(MovieList.items).selectinload(MovieListItem.movie))
        .filter(MovieList.name == name)
        .first()
    )


def get_lists(db: Session) -> List[MovieList]:
    """READ: fetch all lists."""
    return (
        db.query(MovieList)
        .options(selectinload(MovieList.items).selectinload(MovieListItem.movie))
        .order_by(asc(MovieList.name))
        .all()
    )


def create_list(db: Session, name: str, description: Optional[str], movie_titles: List[str]) -> MovieList:
    """CREATE: create a new curated movie list."""
    movies = _resolve_titles_to_movies(db, movie_titles)

    movie_list = MovieList(name=name, description=description)
    db.add(movie_list)
    db.flush()  # assign id

    items: List[MovieListItem] = []
    for position, movie in enumerate(movies, start=1):
        items.append(
            MovieListItem(
                list_id=movie_list.id,
                movie_id=movie.id,
                position=position,
            )
        )
    if items:
        db.add_all(items)

    db.commit()
    db.refresh(movie_list)
    return movie_list


def update_list(
    db: Session,
    movie_list: MovieList,
    description: Optional[str] = None,
    movie_titles: Optional[List[str]] = None,
) -> MovieList:
    """UPDATE: update metadata and/or contents of an existing list."""
    if description is not None:
        movie_list.description = description

    if movie_titles is not None:
        # Clear existing items and rebuild positions from the new titles
        db.query(MovieListItem).filter(MovieListItem.list_id == movie_list.id).delete()
        movies = _resolve_titles_to_movies(db, movie_titles)
        items: List[MovieListItem] = []
        for position, movie in enumerate(movies, start=1):
            items.append(
                MovieListItem(
                    list_id=movie_list.id,
                    movie_id=movie.id,
                    position=position,
                )
            )
        if items:
            db.add_all(items)

    db.commit()
    db.refresh(movie_list)
    return movie_list


def delete_list(db: Session, movie_list: MovieList) -> None:
    """DELETE: permanently remove a list and its items."""
    db.delete(movie_list)
    db.commit()

