from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.match import Match
from ..schemas.match import MatchRead

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/", response_model=List[MatchRead])
def read_matches(db: Session = Depends(get_db)):
    """
    Return all movie matches from the database.
    """
    matches = db.query(Match).all()
    return matches


