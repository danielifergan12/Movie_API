## Movies API (COMP3011 – Web Services and Web Data)

This is a data-driven RESTful API for a movies dataset, built with **FastAPI**, **SQLAlchemy 2.0**, and **SQLite** for the COMP3011 “Web Services and Web Data” coursework.

The API exposes full CRUD operations for a single `Movie` model backed by SQLite, plus pagination and filtering on the list endpoint and a CSV import utility.

---

## Tech Stack

- FastAPI (web framework, automatic OpenAPI/Swagger docs)
- SQLAlchemy 2.0 (ORM, DeclarativeBase, Mapped/mapped_column)
- SQLite (lightweight file-based database)
- Pydantic (request/response validation)
- Uvicorn (ASGI server)
- Pytest (tests)

---

## Project Structure

```text
app/
  main.py               # FastAPI app, health check, router inclusion
  core/
    config.py           # App settings (DB URL, pagination, status values)
  database.py           # SQLAlchemy engine, SessionLocal, Declarative Base
  api/
    deps.py             # get_db dependency
  models/
    movie.py            # SQLAlchemy 2.0 Movie model
  schemas/
    movie.py            # Pydantic schemas for Movie
  crud/
    movie.py            # CRUD operations for Movie
  routes/
    movies.py           # /movies endpoints
  utils/
    import_csv.py       # CSV -> SQLite loader
tests/
  test_movies.py        # Minimal tests with TestClient
requirements.txt
README.md
```

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/danielifergan12/Movie_API.git
cd Movie_API
```

2. **Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the API

From the project root:

```bash
uvicorn app.main:app --reload
```

Then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Root health check: `http://127.0.0.1:8000/`

---

## Database Creation

The SQLite database is created automatically via:

- `Base.metadata.create_all(bind=engine)` in `app/main.py`

No migrations (Alembic) are used in this initial version; the schema is defined by the SQLAlchemy model `app/models/movie.py`.

Default database URL (in `app/core/config.py`):

```python
DATABASE_URL = "sqlite:///./movies.db"
```

---

## Movie Model and Field Conventions

The `Movie` model maps directly to your dataset columns:

- `id`: `int`, primary key
- `title`: `str`, required
- `vote_average`, `popularity`: `float`, nullable
- `vote_count`, `revenue`, `runtime`, `budget`: `int`, nullable
- `status`: `str`, nullable, validated to `"released"` or `"not released"` (case-insensitive input)
- `release_date`: `date`, nullable
- `adult`: `bool`, nullable, default `False`
- `backdrop_path`, `homepage`, `poster_path`, `tagline`, `imdb_id`, `original_language`, `original_title`: `str`, nullable
- `overview`: long `str`, nullable
- `genres`, `production_companies`, `spoken_languages`, `keywords`: stored as **comma-separated strings**, e.g. `"Action,Drama"`.

Indexes are defined on `title` and `imdb_id` for efficient lookup.

---

## Endpoints

### Health Check

- **GET /**  
  - Response: `{"message": "Movies API is running"}`

### Movies

All movie endpoints are under the `/movies` prefix.

#### POST /movies

- **Description**: Create a new movie  
- **Request body**: `MovieCreate`  
- **Response**: `MovieRead`  
- **Status codes**:
  - `201 Created` on success
  - `422 Unprocessable Entity` for validation errors

Example:

```bash
curl -X POST "http://127.0.0.1:8000/movies" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Inception",
        "status": "released",
        "vote_average": 8.7
      }'
```

#### GET /movies

- **Description**: List movies with pagination and filters  
- **Query parameters**:
  - `skip` (int, default `0`)
  - `limit` (int, default `20`, max `100` enforced server-side)
  - `title` (str, optional, substring filter, case-insensitive)
  - `adult` (bool, optional)
  - `status` (str, optional, `"released"` or `"not released"`, case-insensitive)
  - `min_vote_average` (float, optional, 0–10)
- **Response**: `MovieListResponse`
  - `items`: list of `MovieRead`
  - `total`: total number of matching records
  - `skip`, `limit`: echo query values
- **Status codes**:
  - `200 OK`

Example:

```bash
curl "http://127.0.0.1:8000/movies?skip=0&limit=20&title=star&status=released&min_vote_average=7.0"
```

#### GET /movies/{movie_id}

- **Description**: Get a single movie by ID  
- **Response**: `MovieRead`  
- **Status codes**:
  - `200 OK` on success
  - `404 Not Found` if movie does not exist

Example:

```bash
curl "http://127.0.0.1:8000/movies/1"
```

#### PUT /movies/{movie_id}

- **Description**: Update an existing movie  
- **Request body**: `MovieUpdate` (all fields optional; provided fields overwrite existing values)  
- **Response**: `MovieRead`  
- **Status codes**:
  - `200 OK` on success
  - `404 Not Found` if movie does not exist

Example:

```bash
curl -X PUT "http://127.0.0.1:8000/movies/1" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Inception (Updated)",
        "status": "released"
      }'
```

#### DELETE /movies/{movie_id}

- **Description**: Delete a movie by ID  
- **Response body**: empty  
- **Status codes**:
  - `204 No Content` on success
  - `404 Not Found` if movie does not exist

Example:

```bash
curl -X DELETE "http://127.0.0.1:8000/movies/1"
```

---

## CSV Import Utility

The utility `app/utils/import_csv.py` can import your CSV dataset into SQLite.

**Expected columns** (matching your dataset):  
`id, title, vote_average, vote_count, status, release_date, revenue, runtime, adult, backdrop_path, budget, homepage, imdb_id, original_language, original_title, overview, popularity, poster_path, tagline, genres, production_companies, spoken_languages, keywords`

- `adult`: `"TRUE"/"FALSE"` (or similar) is normalised to boolean
- `status`: any variation containing `"released"` or `"not released"` is normalised to `"released"` or `"not released"`

### Usage

From the project root:

```bash
python -m app.utils.import_csv --csv path/to/movies.csv --db sqlite:///./movies.db
```

This will upsert (via `session.merge`) rows into the `movies` table.

---

## Running Tests

Install dev dependencies (already in `requirements.txt`), then run:

```bash
pytest
```

`tests/test_movies.py` covers:

- Creating a movie (`POST /movies`)
- Retrieving a movie by ID (`GET /movies/{movie_id}`)
- Listing movies with pagination (`GET /movies`)

---

## Notes for Oral Exam

- Architecture: layered approach (routes → CRUD layer → SQLAlchemy ORM → SQLite).
- Validation: Pydantic schemas enforce field types and status values.
- Pagination & filtering: implemented in `GET /movies`.
- Data import: `import_csv.py` normalises `adult` and `status` and safely parses numeric and date fields.
