# Movies API - Setup Guide for Examiners

**COMP3011: Web Services and Web Data - Coursework 1**

This is a data-driven RESTful API for a movies dataset, built with **FastAPI**, **SQLAlchemy 2.0**, and **SQLite**. The API implements full CRUD operations with pagination, filtering, and similarity-based recommendations.

---

## Prerequisites

- **Python 3.11 or higher** (check with `python3 --version`)
- **Git** (to clone the repository)
- **Terminal/Command Line** access
- **Internet connection** (for installing dependencies)

---

## Setup (macOS / Linux)

Copy and paste these commands in your terminal:

```bash
# 1. Clone and enter the repository
git clone https://github.com/danielifergan12/Movie_API.git
cd Movie_API

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create database tables
python - << 'PY'
from app.database import Base, engine
from app.models import movie  # register Movie model
from app.models import movie_list  # register MovieList models
Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully")
PY

# 5. Import movie data (sample CSV included in data/)
python -m app.utils.import_csv --csv data/TMDB_movie_dataset_v11.csv --db sqlite:///./movies.db

# 6. Start the API server
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` in your browser.

---

## Setup (Windows / PC)

Using PowerShell or Command Prompt, copy and paste:

```powershell
# 1. Clone and enter the repository
git clone https://github.com/danielifergan12/Movie_API.git
cd Movie_API

# 2. Create and activate virtual environment
py -m venv .venv
.\.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create database tables
py - << 'PY'
from app.database import Base, engine
from app.models import movie  # register Movie model
from app.models import movie_list  # register MovieList models
Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully")
PY

# 5. Import movie data (sample CSV included in data\)
py -m app.utils.import_csv --csv data\TMDB_movie_dataset_v11.csv --db sqlite:///./movies.db

# 6. Start the API server
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` in your browser.

**Notes:**
- The included CSV (`data/TMDB_movie_dataset_v11.csv`) is a sample dataset (~5000 movies).
- Import may take 1–2 minutes and will print a summary when complete.
- The database file (`movies.db`) will be created automatically if it does not exist.

---

## Running the API

**Important:** Always run from the **project root directory** (where the `app/` folder is located) and with your virtual environment activated.

1. **Start the server** (macOS / Linux):

   ```bash
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

   **Start the server** (Windows):

   ```powershell
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Verify it's running**:

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

4. **Access the API**:

- **Interactive API Documentation (Swagger UI)**: http://127.0.0.1:8000/docs
- **Alternative API Docs (ReDoc)**: http://127.0.0.1:8000/redoc
- **Health Check Endpoint**: http://127.0.0.1:8000/

---

## Testing the API

### Quick Test via Browser

1. Open http://127.0.0.1:8000/docs
2. Click on `GET /movies` endpoint
3. Click "Try it out" → "Execute"
4. You should see a JSON response with movie data

### Quick Test via Command Line

```bash
# Health check
curl http://127.0.0.1:8000/

# List first 5 movies
curl "http://127.0.0.1:8000/movies?limit=5"

# Find movies by title
curl "http://127.0.0.1:8000/movies/by-title/Inception"

# Find movies by genre
curl "http://127.0.0.1:8000/movies/by-genre/Action?limit=10"

# Find movies by rating
curl "http://127.0.0.1:8000/movies/by-rating?min_rating=8.0"
```

### Run Automated Tests

```bash
pytest
```

This runs the test suite in `tests/test_movies.py`, which covers:
- Creating a movie (`POST /movies`)
- Finding movies by title (`GET /movies/by-title/{title}`)
- Finding movies by genre (`GET /movies/by-genre/{genre}`)
- Finding movies by rating (`GET /movies/by-rating`)
- Listing movies with pagination (`GET /movies`)

---

## API Endpoints Summary

The API provides **7 endpoints** (exceeding the minimum requirement of 4):

### Health Check
- **GET /** - Returns API status, database connection status, and movie count

### Movies (CRUD Operations)
- **POST /movies** - Create a new movie (Status: 201 Created)
- **GET /movies** - List movies with pagination and filters (Status: 200 OK)
  - Filters: `title`, `genre`, `adult`, `status`, `min_vote_average`
  - Pagination: `skip`, `limit`

### Search Endpoints
- **GET /movies/by-title/{title}** - Find movies by title (Status: 200 OK, 404 Not Found)
  - Query param: `exact` (bool) - exact match vs partial match
- **GET /movies/by-genre/{genre}** - Find movies by genre (Status: 200 OK)
  - Query params: `skip`, `limit` for pagination
- **GET /movies/by-rating** - Find movies by rating range (Status: 200 OK, 422 Unprocessable Entity)
  - Query params: `min_rating`, `max_rating` (at least one required), `skip`, `limit`
  - Results sorted by rating descending (highest first)

### Advanced Features
- **GET /movies/by-title/{title}/similar** - Find similar movies by title (Status: 200 OK, 404 Not Found)
  - Query params: `limit`, `min_shared_tokens`
  - Results sorted by rating (highest to lowest), then similarity score

### Example Requests

**Create a movie:**
```bash
curl -X POST "http://127.0.0.1:8000/movies" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Movie", "status": "released", "vote_average": 7.5}'
```

**List movies with filters:**
```bash
curl "http://127.0.0.1:8000/movies?limit=10&status=released&min_vote_average=7.0&genre=Action"
```

**Find movies by title:**
```bash
# Partial match (default)
curl "http://127.0.0.1:8000/movies/by-title/Inception"

# Exact match
curl "http://127.0.0.1:8000/movies/by-title/Inception?exact=true"
```

**Find movies by genre:**
```bash
curl "http://127.0.0.1:8000/movies/by-genre/Action?limit=20"
```

**Find movies by rating:**
```bash
# Minimum rating
curl "http://127.0.0.1:8000/movies/by-rating?min_rating=8.0"

# Rating range
curl "http://127.0.0.1:8000/movies/by-rating?min_rating=7.0&max_rating=9.0"
```

**Find similar movies:**
```bash
curl "http://127.0.0.1:8000/movies/by-title/Inception/similar?limit=5"
```

**Full API documentation** is available at http://127.0.0.1:8000/docs with interactive testing capabilities.

---

## Database Information

- **Database Type**: SQLite (file-based, no separate server required)
- **Database File**: `movies.db` (located in project root)
- **Schema**: Defined by SQLAlchemy 2.0 models in `app/models/movie.py`
- **Creation**: Tables are created automatically via `Base.metadata.create_all(bind=engine)`

**Movie Model Fields:**
- `id` (primary key), `title`, `vote_average`, `vote_count`, `status`, `release_date`
- `revenue`, `runtime`, `adult`, `budget`, `popularity`
- `genres`, `keywords`, `production_companies`, `spoken_languages` (stored as comma-separated strings)
- Full field list available in `app/models/movie.py`

---

## Troubleshooting

### Error: "Could not import module 'app.main'"

**Solution:**
- Make sure you're in the project root directory (where `app/` folder exists)
- Verify virtual environment is activated: `which python` should show `.venv/bin/python`
- Test import: `python -c "import app.main; print('OK')"`

### Error: "No module named 'fastapi'" or similar

**Solution:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Database appears empty

**Solution:**
- Check if `movies.db` file exists: `ls -la movies.db`
- Verify data: Run the verification command from Step 6
- If empty, import CSV data using Step 5

### Port 8000 already in use

**Solution:**
- Stop any other process using port 8000
- Or use a different port: `uvicorn app.main:app --reload --port 8001`

### Import errors during CSV import

**Solution:**
- Verify CSV file path is correct
- Check CSV has required columns: `id, title, vote_average, vote_count, status, release_date, ...`
- Ensure CSV file is readable: `head -n 1 path/to/movies.csv`

---

## Project Structure

```
Movie_API/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # SQLAlchemy engine and session setup
│   ├── core/
│   │   └── config.py        # Application configuration
│   ├── models/
│   │   └── movie.py         # SQLAlchemy Movie model
│   ├── schemas/
│   │   └── movie.py         # Pydantic request/response schemas
│   ├── crud/
│   │   └── movie.py         # Database CRUD operations
│   ├── routes/
│   │   └── movies.py        # API route handlers
│   ├── api/
│   │   └── deps.py          # FastAPI dependencies
│   └── utils/
│       └── import_csv.py     # CSV import utility
├── tests/
│   └── test_movies.py       # Automated tests
├── data/
│   └── TMDB_movie_dataset_v11.csv  # Sample movie dataset (~5000 movies)
├── movies.db                # SQLite database (created by setup, not in repo)
├── requirements.txt         # Python dependencies
├── setup.sh                 # Automated setup script
└── README.md               # This file
```

---

## Technical Details

### Technology Stack
- **FastAPI**: Modern Python web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0**: ORM using DeclarativeBase and Mapped types
- **SQLite**: Lightweight, file-based database (no server required)
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running FastAPI

### Architecture
- **Layered Design**: Routes → CRUD Layer → SQLAlchemy ORM → SQLite Database
- **Separation of Concerns**: Models, schemas, routes, and business logic are separated
- **Dependency Injection**: Database sessions managed via FastAPI dependencies

### Key Features
- **Full CRUD**: Create, Read, Update, Delete operations
- **Pagination**: `skip` and `limit` parameters for large datasets
- **Filtering**: By title, status, adult flag, minimum vote average
- **Similarity Recommendations**: Based on genre and keyword overlap
- **Data Validation**: Pydantic schemas ensure type safety and validation
- **Error Handling**: Proper HTTP status codes (201, 200, 204, 404, 422)
- **Auto-generated Documentation**: Swagger UI and ReDoc available at `/docs` and `/redoc`

### Testing
- **Test Framework**: Pytest with FastAPI TestClient
- **Test Coverage**: Basic CRUD operations and pagination
- **Test Database**: Uses separate SQLite test database

---

## COMP3011 Requirements Compliance

This API meets all minimum technical requirements:

✅ **CRUD Operations**: Full Create, Read, Update, Delete functionality  
✅ **Multiple Endpoints**: 8 endpoints (exceeds minimum of 4)  
✅ **JSON Responses**: All endpoints return JSON  
✅ **Status Codes**: Correct HTTP status codes (201, 200, 204, 404, 422)  
✅ **Database Integration**: SQLite with SQLAlchemy ORM  
✅ **Error Handling**: Proper error responses with detail messages  
✅ **Documentation**: Auto-generated Swagger UI + this README  
✅ **Testing**: Pytest test suite included  
✅ **Version Control**: GitHub repository with commit history  

---

## Contact & Support

For questions about this coursework submission:
- **GitHub Repository**: https://github.com/danielifergan12/Movie_API
- **Module**: COMP3011 - Web Services and Web Data
- **University of Leeds**

---

**Last Updated**: February 2026
