from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Movie(Base):
    """
    SQLAlchemy model representing a movie row in the dataset.

    Collection-like fields (genres, production_companies, spoken_languages, keywords)
    are stored as comma-separated strings, e.g. "Action,Drama".
    """

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), index=True)
    vote_average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vote_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    release_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    revenue: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    adult: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)

    backdrop_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    budget: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    homepage: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    imdb_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    original_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    popularity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    poster_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    genres: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    production_companies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    spoken_languages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


