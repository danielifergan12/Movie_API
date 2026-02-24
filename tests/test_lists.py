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


def test_create_and_read_movie_list() -> None:
    # First create a couple of movies to reference by title
    client.post("/movies", json={"title": "Inception", "status": "released"})
    client.post("/movies", json={"title": "Interstellar", "status": "released"})

    payload = {
        "name": "Nolan Favourites",
        "description": "Christopher Nolan sci-fi hits",
        "movie_titles": ["Inception", "Interstellar"],
    }
    resp = client.post("/lists", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Nolan Favourites"
    assert len(data["movies"]) == 2

    # READ all lists
    resp_all = client.get("/lists")
    assert resp_all.status_code == 200
    all_data = resp_all.json()
    assert isinstance(all_data, list)
    assert any(l["name"] == "Nolan Favourites" for l in all_data)

    # READ single list
    resp_single = client.get("/lists/Nolan Favourites")
    assert resp_single.status_code == 200
    single_data = resp_single.json()
    assert single_data["name"] == "Nolan Favourites"
    assert len(single_data["movies"]) == 2


def test_update_and_delete_movie_list() -> None:
    client.post("/movies", json={"title": "Movie A", "status": "released"})
    client.post("/movies", json={"title": "Movie B", "status": "released"})
    client.post("/movies", json={"title": "Movie C", "status": "released"})

    client.post(
        "/lists",
        json={
            "name": "My List",
            "description": "Original description",
            "movie_titles": ["Movie A", "Movie B"],
        },
    )

    # UPDATE: change description and movies
    resp_update = client.put(
        "/lists/My List",
        json={
            "description": "Updated description",
            "movie_titles": ["Movie C"],
        },
    )
    assert resp_update.status_code == 200
    update_data = resp_update.json()
    assert update_data["description"] == "Updated description"
    assert len(update_data["movies"]) == 1
    assert update_data["movies"][0]["title"] == "Movie C"

    # DELETE
    resp_delete = client.delete("/lists/My List")
    assert resp_delete.status_code == 204

    # Ensure it is gone
    resp_not_found = client.get("/lists/My List")
    assert resp_not_found.status_code == 404

