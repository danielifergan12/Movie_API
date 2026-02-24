from __future__ import annotations

import argparse
import csv
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session, sessionmaker

from ..models.movie import Movie


def parse_bool(value: str | None) -> Optional[bool]:
    if value is None:
        return None
    v = value.strip().lower()
    if v in {"true", "t", "1", "yes"}:
        return True
    if v in {"false", "f", "0", "no"}:
        return False
    return None


def normalise_status(value: str | None) -> Optional[str]:
    if value is None:
        return None
    v = value.strip().lower()
    if "released" in v:
        return "released"
    if "not released" in v or "unreleased" in v:
        return "not released"
    return None


def parse_int(value: str | None) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_float(value: str | None) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_date(value: str | None) -> Optional[datetime.date]:
    if value is None or value == "":
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def import_csv(csv_path: str, db_url: str) -> None:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    session: Session = SessionLocal()
    inserted = 0
    batch_size = 1000
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                values = dict(
                    id=parse_int(row.get("id")),
                    title=(row.get("title") or "").strip(),
                    vote_average=parse_float(row.get("vote_average")),
                    vote_count=parse_int(row.get("vote_count")),
                    status=normalise_status(row.get("status")),
                    release_date=parse_date(row.get("release_date")),
                    revenue=parse_int(row.get("revenue")),
                    runtime=parse_int(row.get("runtime")),
                    adult=parse_bool(row.get("adult")),
                    backdrop_path=row.get("backdrop_path") or None,
                    budget=parse_int(row.get("budget")),
                    homepage=row.get("homepage") or None,
                    imdb_id=row.get("imdb_id") or None,
                    original_language=row.get("original_language") or None,
                    original_title=row.get("original_title") or None,
                    overview=row.get("overview") or None,
                    popularity=parse_float(row.get("popularity")),
                    poster_path=row.get("poster_path") or None,
                    tagline=row.get("tagline") or None,
                    genres=row.get("genres") or None,
                    production_companies=row.get("production_companies") or None,
                    spoken_languages=row.get("spoken_languages") or None,
                    keywords=row.get("keywords") or None,
                )

                stmt = insert(Movie).values(**values).prefix_with("OR REPLACE")
                session.execute(stmt)
                inserted += 1

                if inserted % batch_size == 0:
                    session.commit()

            session.commit()
        print(f"Imported {inserted} movies from {csv_path}")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import movies from a CSV file.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        required=True,
        help="Path to the CSV file containing movies data.",
    )
    parser.add_argument(
        "--db",
        dest="db_url",
        default="sqlite:///./movies.db",
        help="Database URL (default: sqlite:///./movies.db).",
    )
    args = parser.parse_args()
    import_csv(args.csv_path, args.db_url)


if __name__ == "__main__":
    main()


