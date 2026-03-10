from __future__ import annotations

from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.database import Base
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_movies.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_genre_analytics() -> None:
    # Seed a few movies with genres and ratings
    client.post(
        "/movies",
        json={
            "title": "Action Movie 1",
            "status": "released",
            "genres": "Action, Thriller",
            "vote_average": 8.0,
            "runtime": 100,
            "popularity": 50.0,
        },
    )
    client.post(
        "/movies",
        json={
            "title": "Action Movie 2",
            "status": "released",
            "genres": "Action",
            "vote_average": 9.0,
            "runtime": 110,
            "popularity": 60.0,
        },
    )
    client.post(
        "/movies",
        json={
            "title": "Drama Movie 1",
            "status": "released",
            "genres": "Drama",
            "vote_average": 7.0,
            "runtime": 120,
            "popularity": 40.0,
        },
    )

    resp = client.get("/analytics/genres", params={"top_n": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # There should be at least Action and Drama genres
    genres = {g["genre"] for g in data}
    assert "Action" in genres
    assert "Drama" in genres

    # Find Action stats and check top_movies length
    action_stats = next(g for g in data if g["genre"] == "Action")
    assert action_stats["movie_count"] == 2
    assert len(action_stats["top_movies"]) <= 2
    # Ensure nested movie objects have expected fields
    assert "title" in action_stats["top_movies"][0]
    assert "id" in action_stats["top_movies"][0]

