#!/usr/bin/env python3
"""
Setup script for Movies API (cross-platform alternative to setup.sh)
Run with: python setup.py
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a shell command and print status."""
    print(f"✓ {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  {description} completed")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 40)
    print("Movies API - Automated Setup")
    print("=" * 40)
    print()

    # Check Python version
    print(f"✓ Python version: {sys.version}")
    if sys.version_info < (3, 11):
        print("  ⚠ Warning: Python 3.11+ recommended")

    # Create virtual environment
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("✓ Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", ".venv"], "Creating venv")
    else:
        print("✓ Virtual environment already exists")

    # Determine activation script path
    if sys.platform == "win32":
        activate_script = ".venv\\Scripts\\activate.bat"
        pip_path = ".venv\\Scripts\\pip"
        python_path = ".venv\\Scripts\\python"
    else:
        activate_script = ".venv/bin/activate"
        pip_path = ".venv/bin/pip"
        python_path = ".venv/bin/python"

    # Upgrade pip
    print()
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip", "--quiet"], "Upgrading pip")

    # Install dependencies
    print()
    run_command([pip_path, "install", "-r", "requirements.txt", "--quiet"], "Installing dependencies")

    # Create database tables
    print()
    print("✓ Creating database tables...")
    try:
        # Add project root to path
        sys.path.insert(0, str(Path.cwd()))
        from app.database import Base, engine
        from app.models import movie  # noqa: F401 - register model
        Base.metadata.create_all(bind=engine)
        print("  Database tables created")
    except Exception as e:
        print(f"  Error creating tables: {e}")
        return 1

    # Check for CSV files
    print()
    csv_files = ["data/TMDB_movie_dataset_v11.csv", "data/movies.csv", "movies.csv"]
    csv_found = None
    for csv_file in csv_files:
        if Path(csv_file).exists():
            csv_found = csv_file
            break

    if csv_found:
        print(f"✓ Found CSV file: {csv_found}")
        print("  Importing data...")
        run_command(
            [python_path, "-m", "app.utils.import_csv", "--csv", csv_found, "--db", "sqlite:///./movies.db"],
            "Importing CSV data"
        )
    else:
        print("⚠ No CSV file found")
        print("  Expected: data/TMDB_movie_dataset_v11.csv (included in repository)")
        print("  Database is empty. You can import data later using:")
        print("  python -m app.utils.import_csv --csv path/to/movies.csv --db sqlite:///./movies.db")

    # Verify database
    print()
    print("✓ Verifying database...")
    try:
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
    except Exception as e:
        print(f"  Error verifying database: {e}")

    print()
    print("=" * 40)
    print("✓ Setup complete!")
    print("=" * 40)
    print()
    print("To start the API server:")
    if sys.platform == "win32":
        print("  .venv\\Scripts\\activate")
        print("  uvicorn app.main:app --reload")
    else:
        print("  source .venv/bin/activate")
        print("  uvicorn app.main:app --reload")
    print()
    print("Then open http://127.0.0.1:8000/docs in your browser")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

