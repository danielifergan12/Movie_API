#!/bin/bash
# Setup script for Movies API
# This script automates the setup process for examiners

set -e  # Exit on error

echo "========================================="
echo "Movies API - Automated Setup"
echo "========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "Error: Python 3 is required but not found"; exit 1; }

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt --quiet
echo "  Dependencies installed"

# Create database tables
echo ""
echo "✓ Creating database tables..."
python - << 'PY'
from app.database import Base, engine
from app.models import movie  # register Movie model
Base.metadata.create_all(bind=engine)
print("  Database tables created")
PY

# Check if CSV file exists and import if found
echo ""
if [ -f "data/TMDB_movie_dataset_v11.csv" ]; then
    echo "✓ Found TMDB movie dataset CSV, importing data..."
    python -m app.utils.import_csv --csv data/TMDB_movie_dataset_v11.csv --db sqlite:///./movies.db
    echo "  Data imported successfully"
elif [ -f "data/movies.csv" ]; then
    echo "✓ Found CSV file, importing data..."
    python -m app.utils.import_csv --csv data/movies.csv --db sqlite:///./movies.db
    echo "  Data imported successfully"
elif [ -f "movies.csv" ]; then
    echo "✓ Found CSV file in root, importing data..."
    python -m app.utils.import_csv --csv movies.csv --db sqlite:///./movies.db
    echo "  Data imported successfully"
else
    echo "⚠ No CSV file found"
    echo "  Expected: data/TMDB_movie_dataset_v11.csv (included in repository)"
    echo "  Database is empty. You can import data later using:"
    echo "  python -m app.utils.import_csv --csv path/to/movies.csv --db sqlite:///./movies.db"
fi

# Verify database
echo ""
echo "✓ Verifying database..."
python - << 'PY'
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text("SELECT COUNT(*) FROM movies"))
    count = result.scalar()
    print(f"  Movies in database: {count}")
    if count == 0:
        print("  ⚠ Warning: Database is empty")
    else:
        print("  ✓ Database is populated")
finally:
    db.close()
PY

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "To start the API server, run:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Then open http://127.0.0.1:8000/docs in your browser"
echo ""

