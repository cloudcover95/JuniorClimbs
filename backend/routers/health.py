from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.beta_boot import health as beta_health

router = APIRouter(tags=["JuniorStoneField"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stonefield/health")
def stonefield_health(db: Session = Depends(get_db)):
    return beta_health(db)
