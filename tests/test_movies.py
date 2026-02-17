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


def test_get_movie() -> None:
    # create movie first
    payload = {
        "title": "The Matrix",
        "status": "released",
    }
    create_resp = client.post("/movies", json=payload)
    movie_id = create_resp.json()["id"]

    get_resp = client.get(f"/movies/{movie_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == movie_id
    assert data["title"] == "The Matrix"


def test_list_movies_pagination() -> None:
    # ensure there are some movies
    for i in range(3):
        client.post(
            "/movies",
            json={"title": f"Movie {i}", "status": "released", "vote_average": 7.0 + i},
        )

    resp = client.get("/movies", params={"skip": 0, "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


