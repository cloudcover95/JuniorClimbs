from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.mvp.athletes import Athlete
from backend.database import SessionLocal
from backend.auth import get_current_user

router = APIRouter(prefix="/api/athletes", tags=["Coaching"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[dict])
def get_athletes(db: Session = Depends(get_db)):
    return db.query(Athlete).all()

@router.post("/", response_model=dict)
def create_athlete(athlete: dict, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    new = Athlete(**athlete)
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id, "name": new.name, "team": new.team}
