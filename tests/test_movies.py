from __future__ import annotations

from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.database import Base
from app.main import app
from app.models.movie import Movie

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


def test_create_movie() -> None:
    payload = {
        "title": "Inception",
        "status": "released",
        "vote_average": 8.7,
    }
    response = client.post("/movies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Inception"
    assert data["status"] == "released"
    assert "id" in data


def test_get_movies_by_title() -> None:
    # create movie first
    payload = {
        "title": "The Matrix",
        "status": "released",
    }
    client.post("/movies", json=payload)

    # Test partial match
    resp = client.get("/movies/by-title/Matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(m["title"] == "The Matrix" for m in data)

    # Test exact match
    resp_exact = client.get("/movies/by-title/The Matrix", params={"exact": True})
    assert resp_exact.status_code == 200
    data_exact = resp_exact.json()
    assert isinstance(data_exact, list)
    assert any(m["title"] == "The Matrix" for m in data_exact)

    # Test not found
    resp_not_found = client.get("/movies/by-title/NonexistentMovie12345")
    assert resp_not_found.status_code == 404


def test_get_movies_by_genre() -> None:
    # create movies with genres
    client.post(
        "/movies",
        json={
            "title": "Action Movie",
            "status": "released",
            "genres": "Action, Thriller",
        },
    )
    client.post(
        "/movies",
        json={
            "title": "Drama Movie",
            "status": "released",
            "genres": "Drama, Romance",
        },
    )

    resp = client.get("/movies/by-genre/Action")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0
    assert any("Action" in m.get("genres", "") for m in data["items"])


def test_get_movies_by_rating() -> None:
    # create movies with different ratings
    client.post(
        "/movies",
        json={
            "title": "High Rated Movie",
            "status": "released",
            "vote_average": 9.0,
        },
    )
    client.post(
        "/movies",
        json={
            "title": "Medium Rated Movie",
            "status": "released",
            "vote_average": 7.0,
        },
    )
    client.post(
        "/movies",
        json={
            "title": "Low Rated Movie",
            "status": "released",
            "vote_average": 5.0,
        },
    )

    # Test min rating
    resp = client.get("/movies/by-rating", params={"min_rating": 7.0})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert all(m["vote_average"] >= 7.0 for m in data["items"] if m.get("vote_average"))

    # Test rating range
    resp_range = client.get("/movies/by-rating", params={"min_rating": 6.0, "max_rating": 8.0})
    assert resp_range.status_code == 200
    data_range = resp_range.json()
    assert "items" in data_range
    for m in data_range["items"]:
        if m.get("vote_average"):
            assert 6.0 <= m["vote_average"] <= 8.0

    # Test error when no params
    resp_error = client.get("/movies/by-rating")
    assert resp_error.status_code == 422


def test_list_movies_pagination() -> None:
    # ensure there are some movies
    for i in range(3):
        client.post(
            "/movies",
            json={
                "title": f"Movie {i}",
                "status": "released",
                "vote_average": 7.0 + i,
                "genres": f"Genre{i}, Action",
            },
        )

    resp = client.get("/movies", params={"skip": 0, "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["limit"] == 2
    assert len(data["items"]) <= 2

    # Test genre filter
    resp_genre = client.get("/movies", params={"genre": "Action"})
    assert resp_genre.status_code == 200
    data_genre = resp_genre.json()
    assert "items" in data_genre


