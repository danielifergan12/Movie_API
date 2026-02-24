from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .movie import Movie


class MovieList(Base):
    """
    A curated list (playlist) of movies.

    Lists are identified by a human-friendly unique name and contain an
    ordered collection of movies via MovieListItem rows.
    """

    __tablename__ = "movie_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    items: Mapped[List["MovieListItem"]] = relationship(
        "MovieListItem",
        back_populates="movie_list",
        cascade="all, delete-orphan",
        order_by="MovieListItem.position",
        lazy="selectin",
    )


class MovieListItem(Base):
    """
    Association table linking MovieList to Movie with an explicit position.
    """

    __tablename__ = "movie_list_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(
        ForeignKey("movie_lists.id", ondelete="CASCADE"), index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    movie_list: Mapped[MovieList] = relationship(
        "MovieList", back_populates="items"
    )
    movie: Mapped[Movie] = relationship(Movie, lazy="joined")

