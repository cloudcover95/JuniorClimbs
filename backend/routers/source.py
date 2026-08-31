"""JuniorSourceLedger routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_source import ALLOWED_LICENSES, SourceProject
from backend.source_ledger import SCHEMA, import_document, export_field

router = APIRouter(prefix="/source", tags=["JuniorSourceLedger"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProjectMeta(BaseModel):
    project_name: str
    license: str = "CC-BY-4.0"
    attribution: str = "anon"
    field_name: str = ""
    homepage: str = ""
    notes: str | None = None


@router.get("/schema")
def schema():
    return {"allowed_licenses": list(ALLOWED_LICENSES), "document": SCHEMA}


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(SourceProject).order_by(SourceProject.id.desc()).all()


@router.post("/projects")
def register_project(payload: ProjectMeta, db: Session = Depends(get_db)):
    if payload.license not in ALLOWED_LICENSES:
        raise HTTPException(400, f"license must be one of {ALLOWED_LICENSES}")
    row = SourceProject(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/import")
def ingest(doc: dict, db: Session = Depends(get_db)):
    result = import_document(db, doc)
    if not result.get("ok"):
        raise HTTPException(400, result)
    return result


@router.get("/export")
def export(field_id: int, db: Session = Depends(get_db)):
    result = export_field(db, field_id)
    if not result.get("format"):
        raise HTTPException(404, result)
    return result
