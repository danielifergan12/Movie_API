from sqlalchemy import Boolean, Column, Date, Float, Integer, String

from ..db.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    released = Column(Boolean, nullable=True)
    release_date = Column(Date, nullable=True)
    revenue = Column(Integer, nullable=True)
    runtime = Column(Integer, nullable=True)
    adult = Column(Boolean, nullable=True)
    backdrop_path = Column(String(500), nullable=True)
    budget = Column(Integer, nullable=True)
    homepage = Column(String(500), nullable=True)
    imdb_id = Column(String(50), nullable=True, index=True)
    original_language = Column(String(10), nullable=True)
    original_title = Column(String(255), nullable=True)
    overview = Column(String, nullable=True)
    popularity = Column(Float, nullable=True)
    poster_path = Column(String(500), nullable=True)
    tagline = Column(String(500), nullable=True)
    genres = Column(String, nullable=True)
    production_companies = Column(String, nullable=True)
    spoken_languages = Column(String, nullable=True)
    keywords = Column(String, nullable=True)


